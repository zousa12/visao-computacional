import unittest

import numpy as np
from PIL import Image

from image_input import split_quadrants
from transformations import apply_rgb_matrix, filtered_q4, is_q4_correct, rgb_preview


INVERSE = [[1.5, -0.5, 0], [-0.5, 1.5, 0], [0, 0, 1]]


class RGBTests(unittest.TestCase):
    def test_known_rgb_column_vector_has_expected_channel_mixture(self):
        filtered = filtered_q4(Image.fromarray(np.array([[[100, 20, 7]]], dtype=np.uint8)))
        np.testing.assert_array_equal(filtered, [[[80.0, 40.0, 7.0]]])

    def test_inverse_recovers_extreme_and_fractional_channel_values(self):
        pixels = np.array([[[1, 0, 0], [0, 1, 0], [255, 0, 255]],
                           [[0, 255, 0], [255, 255, 255], [0, 0, 0]]], dtype=np.uint8)
        reference = Image.fromarray(pixels)
        altered = filtered_q4(reference)
        self.assertEqual(altered.dtype, np.float64)
        np.testing.assert_array_equal(altered[0, 0], [0.75, 0.25, 0])
        before = altered.copy()
        corrected = apply_rgb_matrix(altered, INVERSE)
        np.testing.assert_allclose(corrected, pixels, rtol=0, atol=1e-6)
        np.testing.assert_array_equal(altered, before)
        np.testing.assert_array_equal(np.asarray(reference), pixels)
        self.assertTrue(is_q4_correct(reference, corrected, INVERSE))

    def test_odd_source_and_minimum_quadrants_keep_all_pixels(self):
        for width, height in ((2, 2), (3, 5), (11, 7), (8, 6)):
            with self.subTest(size=(width, height)):
                pixels = np.random.default_rng(width).integers(0, 256, (height, width, 3), dtype=np.uint8)
                quadrants = split_quadrants(Image.fromarray(pixels))
                before = tuple(q.tobytes() for q in quadrants)
                corrected = apply_rgb_matrix(filtered_q4(quadrants[3]), INVERSE)
                np.testing.assert_allclose(corrected, pixels[height // 2:, width // 2:], rtol=0, atol=1e-6)
                self.assertEqual(rgb_preview(corrected).size, quadrants[3].size)
                self.assertEqual(tuple(q.tobytes() for q in quadrants), before)

    def test_rounding_and_clipping_are_display_only(self):
        pixels = np.array([[[-5.25, 127.6, 300.75]]])
        before = pixels.copy()
        preview = rgb_preview(pixels)
        self.assertEqual(preview.getpixel((0, 0)), (0, 128, 255))
        np.testing.assert_array_equal(pixels, before)
        np.testing.assert_array_equal(apply_rgb_matrix(pixels, np.eye(3)), before)

    def test_identity_is_wrong_even_when_image_is_black(self):
        for color in ((100, 20, 7), (0, 0, 0), (200, 200, 200)):
            reference = Image.new("RGB", (2, 3), color)
            corrected = apply_rgb_matrix(filtered_q4(reference), np.eye(3))
            self.assertFalse(is_q4_correct(reference, corrected, np.eye(3)))

    def test_numerical_tolerance_and_recovered_values_are_both_checked(self):
        reference = Image.new("RGB", (2, 2), (255, 1, 7))
        altered = filtered_q4(reference)
        nearly = np.asarray(INVERSE) + np.eye(3) * 1e-10
        self.assertTrue(is_q4_correct(reference, apply_rgb_matrix(altered, nearly), nearly))
        self.assertFalse(is_q4_correct(reference, apply_rgb_matrix(altered, INVERSE) + 0.001, INVERSE))
        self.assertFalse(is_q4_correct(reference, np.zeros((1, 1, 3)), INVERSE))

    def test_invalid_matrices_are_rejected_without_executing_text(self):
        for matrix in (np.zeros((3, 3)), np.eye(2), [[1, 0, 0]],
                       [[float("nan"), 0, 0], [0, 1, 0], [0, 0, 1]],
                       [[1, 0, 0], [0, float("inf"), 0], [0, 0, 1]],
                       [["print('unsafe')", 0, 0], [0, 1, 0], [0, 0, 1]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                apply_rgb_matrix(np.zeros((1, 1, 3)), matrix)
        with self.assertRaises(ValueError):
            apply_rgb_matrix(np.full((1, 1, 3), 255.0), np.eye(3) * 1e308)

    def test_invalid_rgb_arrays_are_rejected(self):
        for pixels in ([], np.zeros((2, 3)), np.zeros((1, 1, 4)), np.zeros((0, 1, 3)),
                       [[[0, float("nan"), 0]]], [[[0, 0, float("inf")]]]):
            with self.subTest(pixels=pixels), self.assertRaises(ValueError):
                apply_rgb_matrix(pixels, INVERSE)


if __name__ == "__main__":
    unittest.main()
