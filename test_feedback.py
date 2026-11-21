import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from answer_validation import q1_feedback, q2_feedback, q3_feedback, q4_feedback
from transformations import (
    RGB_FILTER, apply_centered_matrix, apply_rgb_matrix, compose_corrections,
    enlarged_q2, filtered_q4, scale_image, validate_matrix, validate_rgb_matrix,
)


class FeedbackTests(unittest.TestCase):
    def test_equivalent_answers_are_accepted_for_all_quadrants(self):
        angle = np.pi
        rotation = [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
        self.assertTrue(q1_feedback(rotation).correct)
        first = np.array([[2.0, 1.0], [0.0, 1.0]])
        second = np.diag([-1.0, 1.0]) @ np.linalg.inv(first)
        self.assertTrue(q3_feedback(compose_corrections(first, second)).correct)
        self.assertTrue(q2_feedback((240, 160), (480, 480), 1 / 2, 0.333333).correct)
        image = Image.new("RGB", (3, 5), (255, 1, 7))
        inverse = np.linalg.inv(RGB_FILTER)
        self.assertTrue(q4_feedback(image, apply_rgb_matrix(filtered_q4(image), inverse), inverse).correct)

    def test_q1_explains_which_axis_is_still_wrong(self):
        feedback = q1_feedback([[-1, 0], [0, 1]])
        self.assertFalse(feedback.correct)
        self.assertIn("eixo Y", feedback.message)

    def test_q2_reports_actual_expected_dimensions_and_wrong_axis(self):
        feedback = q2_feedback((240, 160), (480, 480), 0.5, 1)
        self.assertFalse(feedback.correct)
        self.assertIn("240 × 480", feedback.message)
        self.assertIn("240 × 160", feedback.message)
        self.assertIn("em Y", feedback.message)

    def test_matching_rounded_dimensions_are_not_sufficient(self):
        feedback = q2_feedback((1, 1), (2, 3), 0.6, 0.4)
        self.assertFalse(feedback.correct)
        self.assertIn("arredondamento", feedback.message)

    def test_interpolation_differences_do_not_invalidate_inverse_scale(self):
        checkerboard = (np.indices((5, 7)).sum(axis=0) % 2 * 255).astype(np.uint8)
        original = np.repeat(checkerboard[:, :, None], 3, axis=2)
        image = Image.fromarray(original)
        enlarged = enlarged_q2(image)
        corrected = scale_image(enlarged, 0.5, 1 / 3)
        self.assertFalse(np.array_equal(np.asarray(corrected), original))
        self.assertTrue(q2_feedback(image.size, enlarged.size, 0.5, 1 / 3).correct)

    def test_q3_explains_missing_reflection_after_rotation(self):
        feedback = q3_feedback(-np.eye(2))
        self.assertFalse(feedback.correct)
        self.assertIn("isolada", feedback.message)
        self.assertIn("reflexão vertical", feedback.message)

    def test_rgb_reports_channel_error_and_rejects_coincidental_pixel_match(self):
        image = Image.new("RGB", (2, 2), (255, 1, 7))
        feedback = q4_feedback(image, filtered_q4(image), np.eye(3))
        self.assertFalse(feedback.correct)
        self.assertIn("diferença máxima", feedback.message)
        self.assertIn("tolerância", feedback.message)
        black = Image.new("RGB", (2, 2))
        feedback = q4_feedback(black, filtered_q4(black), np.eye(3))
        self.assertFalse(feedback.correct)
        self.assertIn("pixels coincidem", feedback.message)

    def test_invalid_real_matrix_formats_values_and_overflow_have_clear_errors(self):
        invalid = (np.zeros((2, 2)), [[1]], [[1], [1, 2]], [[1, 0], [0, float("nan")]],
                   [[1, float("inf")], [0, 1]], [[10 ** 1000, 0], [0, 1]],
                   np.eye(2, dtype=complex), [["print('unsafe')", 0], [0, 1]])
        for matrix in invalid:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                validate_matrix(matrix)
        with self.assertRaises(ValueError):
            validate_rgb_matrix(np.eye(3, dtype=complex))
        for factor in (0, -1, float("nan"), float("inf"), "abc"):
            with self.subTest(factor=factor), self.assertRaises(ValueError):
                q2_feedback((10, 10), (20, 30), factor, 1 / 3)

    def test_extreme_geometry_is_rejected_before_generating_preview(self):
        image = Image.new("RGB", (480, 320))
        with patch.object(Image.Image, "transform") as transform:
            with self.assertRaisesRegex(ValueError, "limite numérico"):
                apply_centered_matrix(image, np.eye(2) * 1e-308)
            transform.assert_not_called()

    def test_absolute_tolerances_accept_roundoff_and_reject_real_errors(self):
        self.assertTrue(q1_feedback([[-1 + 5e-9, 0], [0, -1]]).correct)
        self.assertFalse(q1_feedback([[-1 + 2e-8, 0], [0, -1]]).correct)
        image = Image.new("RGB", (2, 2), (255, 1, 7))
        inverse = np.linalg.inv(RGB_FILTER)
        original = apply_rgb_matrix(filtered_q4(image), inverse)
        self.assertTrue(q4_feedback(image, original + 5e-7, inverse).correct)
        self.assertFalse(q4_feedback(image, original + 2e-6, inverse).correct)


if __name__ == "__main__":
    unittest.main()
