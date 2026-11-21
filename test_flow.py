"""Complete user flows through the actual upload widget and four forms."""

import importlib.util
from io import BytesIO
from pathlib import Path
import unittest
from test_support import IsolatedHistoryTestCase

import numpy as np
from PIL import Image

from image_input import load_image, split_quadrants
from session_progress import PROGRESS_KEY
from transformations import enlarged_q2, scale_image


def fixture_file(format: str = "PNG", *, size=(11, 7), orientation=None, seed=12):
    pixels = np.random.default_rng(seed).integers(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    image = Image.fromarray(pixels)
    buffer = BytesIO()
    options = {}
    if orientation is not None:
        exif = Image.Exif()
        exif[274] = orientation
        options["exif"] = exif
    image.save(buffer, format=format, **options)
    mime = "image/png" if format == "PNG" else "image/jpeg"
    return ("fixture.png" if format == "PNG" else "fixture.jpg", buffer.getvalue(), mime)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class CompleteFlowTests(IsolatedHistoryTestCase):
    def start_upload(self, fixture):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        app.file_uploader[0].set_value(fixture).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        return app

    def complete(self, app, *, compose=False):
        for target in range(4):
            self.assertFalse(any(s.value == "Imagem recomposta" for s in app.subheader))
            if target == 0:
                app.number_input(key="q1_00").set_value(-1.0)
                app.number_input(key="q1_11").set_value(-1.0)
            elif target == 1:
                app.number_input(key="q2_sx").set_value(0.5)
                app.number_input(key="q2_sy").set_value(0.333333)
            elif target == 2 and compose:
                app.radio(key="q3_mode").set_value("Composição de duas matrizes").run()
                app.number_input(key="q3_first_00").set_value(-1.0)
                app.number_input(key="q3_first_11").set_value(-1.0)
                app.number_input(key="q3_second_11").set_value(-1.0)
            elif target == 2:
                app.number_input(key="q3_direct_00").set_value(-1.0)
            else:
                inverse = ((1.5, -0.5, 0), (-0.5, 1.5, 0), (0, 0, 1))
                for row in range(3):
                    for column in range(3):
                        app.number_input(key=f"q4_{row}{column}").set_value(float(inverse[row][column]))
            app.button[target].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.error), 0)
            self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), target + 1)
        self.assertTrue(any(s.value == "Imagem recomposta" for s in app.subheader))
        return app.session_state[PROGRESS_KEY].reconstruct()

    def assert_reconstruction(self, result, reference):
        self.assertEqual(result.size, reference.size)
        originals = split_quadrants(reference)
        restored = split_quadrants(result)
        for index in (0, 2, 3):
            np.testing.assert_array_equal(np.asarray(restored[index]), np.asarray(originals[index]))
        expected_scale = scale_image(enlarged_q2(originals[1]), 0.5, 0.333333)
        np.testing.assert_array_equal(np.asarray(restored[1]), np.asarray(expected_scale))

    def test_png_odd_dimensions_wrong_invalid_correct_and_image_change(self):
        fixture = fixture_file()
        app = self.start_upload(fixture)
        app.button[0].click().run()
        self.assertEqual(len(app.warning), 1)
        self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 0)
        app.number_input(key="q2_sx").set_value(0.0)
        app.button[1].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 0)

        # Fix Q2's invalid attempt first so the complete-flow checks see no stale error.
        app.number_input(key="q2_sx").set_value(1.0)
        app.button[1].click().run()
        result = self.complete(app, compose=True)
        self.assert_reconstruction(result, load_image(fixture[1]))
        app.run()
        self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 4)

        app.file_uploader[0].set_value(fixture_file(seed=99)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state[PROGRESS_KEY].corrected, {})
        self.assertEqual(app.session_state[PROGRESS_KEY].attempts, {})
        self.assertEqual(app.number_input(key="q1_00").value, 1.0)
        self.assertFalse(any(s.value == "Imagem recomposta" for s in app.subheader))

    def test_jpeg_exif_orientation_complete_flow_and_filename_change(self):
        fixture = fixture_file("JPEG", orientation=6)
        app = self.start_upload(fixture)
        result = self.complete(app)
        reference = load_image(fixture[1])
        self.assertEqual(reference.size, (7, 11))
        self.assert_reconstruction(result, reference)
        app.file_uploader[0].set_value(("renamed.jpg", fixture[1], fixture[2])).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state[PROGRESS_KEY].corrected, {})
        self.assertEqual(app.number_input(key="q4_00").value, 1.0)

    def test_invalid_or_too_small_upload_clears_progress_and_allows_recovery(self):
        app = self.start_upload(fixture_file())
        for invalid in (("bad.png", b"not a PNG", "image/png"), fixture_file(size=(1, 1))):
            app.number_input(key="q1_00").set_value(-1.0)
            app.number_input(key="q1_11").set_value(-1.0)
            app.button[0].click().run()
            self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 1)
            app.file_uploader[0].set_value(invalid).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.error), 1)
            self.assertNotIn(PROGRESS_KEY, app.session_state)
            self.assertEqual(len(app.number_input), 0)
            app.file_uploader[0].set_value(fixture_file()).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.error), 0)
            self.assertEqual(app.session_state[PROGRESS_KEY].corrected, {})
        app.file_uploader[0].clear().run()
        self.assertNotIn(PROGRESS_KEY, app.session_state)
        self.assertEqual(len(app.error), 0)


if __name__ == "__main__":
    unittest.main()
