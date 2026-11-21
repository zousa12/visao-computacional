import unittest

import numpy as np
from PIL import Image

from answer_validation import AnswerFeedback, q1_feedback, q2_feedback, q3_feedback, q4_feedback
from image_input import split_quadrants
from session_progress import PROGRESS_KEY, clear_progress, ensure_progress, image_identity
from transformations import (
    RGB_FILTER, apply_centered_matrix, apply_rgb_matrix, enlarged_q2,
    filtered_q4, mirrored_q3, rgb_preview, rotated_q1, scale_image,
)


CORRECT = AnswerFeedback(True, "Correto!")
INCORRECT = AnswerFeedback(False, "Revise a resposta.")


class ProgressTests(unittest.TestCase):
    def test_same_image_preserves_attempts_corrections_and_inputs(self):
        image = Image.new("RGB", (11, 7))
        state = {}
        progress = ensure_progress(state, image, "example")
        progress.record(1, split_quadrants(image)[0], CORRECT)
        state["q1_00"] = -1.0
        self.assertIs(ensure_progress(state, image.copy(), "example"), progress)
        self.assertEqual(len(progress.corrected), 1)
        self.assertEqual(state["q1_00"], -1.0)

    def test_new_pixels_reset_progress_and_only_challenge_inputs(self):
        state = {"unrelated": "keep"}
        image = Image.new("RGB", (11, 7), "red")
        progress = ensure_progress(state, image)
        progress.record(1, split_quadrants(image)[0], CORRECT)
        state.update({"q1_00": -1, "q2_sx": 0.5, "q3_mode": "previous", "q4_00": 1.5})
        new = ensure_progress(state, Image.new("RGB", image.size, "blue"))
        self.assertIsNot(new, progress)
        self.assertEqual(new.attempts, {})
        self.assertEqual(new.corrected, {})
        self.assertEqual(state, {"unrelated": "keep", PROGRESS_KEY: new})

    def test_dimensions_and_source_identify_different_images(self):
        first = Image.new("RGB", (4, 6))
        reshaped = Image.new("RGB", (6, 4))
        self.assertEqual(first.tobytes(), reshaped.tobytes())
        self.assertNotEqual(image_identity(first), image_identity(reshaped))
        state = {}
        old = ensure_progress(state, first, "file-a.png")
        new = ensure_progress(state, first, "file-b.png")
        self.assertIsNot(old, new)

    def test_clear_progress_removes_attempts_and_fields(self):
        state = {}
        ensure_progress(state, Image.new("RGB", (2, 2)))
        state["q1_00"] = -1
        state["source"] = "upload"
        clear_progress(state)
        self.assertEqual(state, {"source": "upload"})

    def test_reconstruction_waits_for_four_and_preserves_odd_positions(self):
        progress = ensure_progress({}, Image.new("RGB", (7, 5)))
        colors = ("red", "green", "blue", "yellow")
        for quadrant, color in enumerate(colors, 1):
            self.assertIsNone(progress.reconstruct())
            progress.record(quadrant, Image.new("RGB", progress.expected_size(quadrant), color), CORRECT)
        result = progress.reconstruct()
        self.assertEqual(result.size, (7, 5))
        expected_colors = ((255, 0, 0), (0, 128, 0), (0, 0, 255), (255, 255, 0))
        for box, color in zip(((0, 0, 3, 2), (3, 0, 7, 2), (0, 2, 3, 5), (3, 2, 7, 5)), expected_colors):
            crop = np.asarray(result.crop(box))
            self.assertTrue(np.all(crop == color))

    def test_failed_attempts_do_not_complete_or_erase_a_previous_success(self):
        progress = ensure_progress({}, Image.new("RGB", (4, 4)))
        preview = Image.new("RGB", (2, 2), "red")
        progress.record(1, preview, INCORRECT)
        self.assertEqual(progress.corrected, {})
        progress.record_error(1, "Erro tratado")
        self.assertEqual(progress.corrected, {})
        progress.record(1, preview, CORRECT)
        progress.record(1, Image.new("RGB", (2, 2), "blue"), INCORRECT)
        progress.record_error(1, "Erro tratado")
        self.assertEqual(progress.corrected[1].getpixel((0, 0)), (255, 0, 0))
        self.assertEqual(progress.attempts[1].error, "Erro tratado")

    def test_accepted_dimensions_and_quadrant_numbers_are_checked(self):
        progress = ensure_progress({}, Image.new("RGB", (7, 5)))
        with self.assertRaises(ValueError):
            progress.record(1, Image.new("RGB", (4, 2)), CORRECT)
        with self.assertRaises(ValueError):
            progress.record_error(5, "invalid")
        self.assertEqual(progress.attempts, {})
        with self.assertRaises(ValueError):
            ensure_progress({}, Image.new("RGB", (1, 2)))

    def test_sessions_do_not_share_progress(self):
        image = Image.new("RGB", (4, 4))
        first = ensure_progress({}, image)
        second = ensure_progress({}, image)
        first.record(1, split_quadrants(image)[0], CORRECT)
        self.assertEqual(second.corrected, {})
        self.assertEqual(second.attempts, {})

    def test_saved_corrections_and_reconstruction_are_copies(self):
        progress = ensure_progress({}, Image.new("RGB", (2, 2)))
        preview = Image.new("RGB", (1, 1), "red")
        for quadrant in range(1, 5):
            progress.record(quadrant, preview, CORRECT)
        preview.putpixel((0, 0), (0, 0, 0))
        result = progress.reconstruct()
        self.assertTrue(np.all(np.asarray(result) == (255, 0, 0)))
        result.putpixel((0, 0), (0, 0, 0))
        self.assertEqual(progress.corrected[1].getpixel((0, 0)), (255, 0, 0))

    def test_real_corrections_reconstruct_without_replacing_scaled_pixels(self):
        pixels = np.random.default_rng(10).integers(0, 256, (7, 11, 3), dtype=np.uint8)
        image = Image.fromarray(pixels)
        q1, q2, q3, q4 = split_quadrants(image)
        progress = ensure_progress({}, image)
        first = apply_centered_matrix(rotated_q1(q1), -np.eye(2))
        progress.record(1, first, q1_feedback(-np.eye(2)))
        enlarged = enlarged_q2(q2)
        second = scale_image(enlarged, 0.5, 1 / 3)
        progress.record(2, second, q2_feedback(q2.size, enlarged.size, 0.5, 1 / 3))
        reflection = np.diag([-1.0, 1.0])
        third = apply_centered_matrix(mirrored_q3(q3), reflection)
        progress.record(3, third, q3_feedback(reflection))
        inverse = np.linalg.inv(RGB_FILTER)
        fourth = apply_rgb_matrix(filtered_q4(q4), inverse)
        progress.record(4, rgb_preview(fourth), q4_feedback(q4, fourth, inverse))
        result = progress.reconstruct()
        self.assertEqual(result.size, image.size)
        actual = split_quadrants(result)
        for restored, expected in zip(actual, (first, second, third, rgb_preview(fourth))):
            self.assertEqual(restored.tobytes(), expected.tobytes())
        self.assertNotEqual(second.tobytes(), q2.tobytes())


if __name__ == "__main__":
    unittest.main()
