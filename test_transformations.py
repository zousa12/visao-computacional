import unittest

import numpy as np
from PIL import Image

from image_input import split_quadrants
from transformations import apply_centered_matrix, is_q1_correct, rotated_q1


class RotationTests(unittest.TestCase):
    def test_correction_restores_every_pixel_and_preserves_reference(self):
        for width, height in ((1, 1), (4, 2), (5, 3), (3, 6)):
            with self.subTest(size=(width, height)):
                pixels = np.arange(width * height * 3, dtype=np.uint8).reshape(height, width, 3)
                reference = Image.fromarray(pixels)
                altered = rotated_q1(reference)
                np.testing.assert_array_equal(np.asarray(altered), pixels[::-1, ::-1])
                result = apply_centered_matrix(altered, [[-1, 0], [0, -1]])
                self.assertEqual(result.size, reference.size)
                np.testing.assert_array_equal(np.asarray(result), pixels)
                np.testing.assert_array_equal(np.asarray(reference), pixels)

    def test_odd_source_quadrant_is_restored(self):
        pixels = np.arange(7 * 11 * 3, dtype=np.uint8).reshape(7, 11, 3)
        reference = split_quadrants(Image.fromarray(pixels))[0]
        result = apply_centered_matrix(rotated_q1(reference), -np.eye(2))
        np.testing.assert_array_equal(np.asarray(result), pixels[:3, :5])

    def test_identity_keeps_challenge_rotated(self):
        reference = Image.fromarray(np.arange(18, dtype=np.uint8).reshape(2, 3, 3))
        altered = rotated_q1(reference)
        np.testing.assert_array_equal(np.asarray(apply_centered_matrix(altered, np.eye(2))), np.asarray(altered))
        self.assertFalse(is_q1_correct(np.eye(2)))

    def test_quarter_turn_uses_cartesian_axes_and_inverse_mapping(self):
        pixels = np.arange(27, dtype=np.uint8).reshape(3, 3, 3)
        result = apply_centered_matrix(Image.fromarray(pixels), [[0, -1], [1, 0]])
        np.testing.assert_array_equal(np.asarray(result), np.rot90(pixels))

    def test_geometry_validation_accepts_roundoff_but_rejects_wrong_answers(self):
        self.assertTrue(is_q1_correct([[-1, 0], [0, -1]]))
        self.assertTrue(is_q1_correct([[-1, -1e-16], [1e-16, -1]]))
        self.assertFalse(is_q1_correct([[-1, 0], [0, 1]]))
        self.assertFalse(is_q1_correct([[-0.99, 0], [0, -1]]))

    def test_invalid_matrices_have_clear_errors(self):
        invalid = ([[1, 2], [2, 4]], [[0, 0], [0, 0]], [[1, 0]],
                   [[float("nan"), 0], [0, 1]], [[1, 0], [0, float("inf")]],
                   [["abc", 0], [0, 1]], [[1], [1, 2]])
        for matrix in invalid:
            with self.subTest(matrix=matrix):
                with self.assertRaises(ValueError):
                    apply_centered_matrix(Image.new("RGB", (3, 2)), matrix)
                with self.assertRaises(ValueError):
                    is_q1_correct(matrix)


if __name__ == "__main__":
    unittest.main()
