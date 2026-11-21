import importlib.util
from pathlib import Path
import unittest
from test_support import IsolatedHistoryTestCase

from session_progress import PROGRESS_KEY


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class SessionInterfaceTests(IsolatedHistoryTestCase):
    def test_four_corrections_survive_reruns_and_reconstruct_only_at_the_end(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(app.session_state[PROGRESS_KEY].corrected, {})
        for target in range(4):
            self.assertFalse(any(s.value == "Imagem recomposta" for s in app.subheader))
            if target == 0:
                app.number_input(key="q1_00").set_value(-1.0)
                app.number_input(key="q1_11").set_value(-1.0)
            elif target == 1:
                app.number_input(key="q2_sx").set_value(0.5)
                app.number_input(key="q2_sy").set_value(0.333333)
            elif target == 2:
                app.number_input(key="q3_direct_00").set_value(-1.0)
            else:
                inverse = ((1.5, -0.5, 0), (-0.5, 1.5, 0), (0, 0, 1))
                for row in range(3):
                    for column in range(3):
                        app.number_input(key=f"q4_{row}{column}").set_value(float(inverse[row][column]))
            app.button[target].click().run()
            app.run()
            self.assertEqual(len(app.exception), 0)
            progress = app.session_state[PROGRESS_KEY]
            self.assertEqual(len(progress.corrected), target + 1)
            self.assertEqual(len(app.success), target + 1)
        self.assertTrue(any(s.value == "Imagem recomposta" for s in app.subheader))
        self.assertEqual(progress.reconstruct().size, (480, 320))
        self.assertEqual(len(app.image), 10)

        app.number_input(key="q4_22").set_value(0.0)
        app.button[3].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 4)
        self.assertTrue(any(s.value == "Imagem recomposta" for s in app.subheader))

        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(app.exception), 0)
        self.assertNotIn(PROGRESS_KEY, app.session_state)
        self.assertEqual(len(app.number_input), 0)
        app.radio[0].set_value("Imagem de exemplo").run()
        self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 0)
        self.assertEqual(app.number_input(key="q1_00").value, 1.0)

    def test_new_image_or_source_clears_attempts_and_widget_values(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_string('''
import streamlit as st
from PIL import Image
from challenge_ui import render_challenges
color = st.session_state.get("fixture_color", "red")
source = st.session_state.get("fixture_source", "first.png")
render_challenges(Image.new("RGB", (11, 7), color), source)
''').run()
        for key, value in (("fixture_color", "blue"), ("fixture_source", "second.png")):
            app.number_input(key="q1_00").set_value(-1.0)
            app.number_input(key="q1_11").set_value(-1.0)
            app.button[0].click().run()
            self.assertEqual(len(app.session_state[PROGRESS_KEY].corrected), 1)
            app.session_state[key] = value
            app.run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.session_state[PROGRESS_KEY].corrected, {})
            self.assertEqual(app.session_state[PROGRESS_KEY].attempts, {})
            self.assertEqual(app.number_input(key="q1_00").value, 1.0)
            self.assertEqual(len(app.success), 0)
            self.assertEqual(len(app.error), 0)


if __name__ == "__main__":
    unittest.main()
