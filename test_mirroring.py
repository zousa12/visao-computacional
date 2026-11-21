import unittest

import numpy as np
from PIL import Image

from image_input import split_quadrants
from transformations import (
    apply_centered_matrix, compose_corrections, is_q3_correct, mirrored_q3,
)


class MirroringTests(unittest.TestCase):
    def test_direct_and_composed_corrections_restore_all_pixels(self):
        direct = [[-1, 0], [0, 1]]
        composed = compose_corrections([[-1, 0], [0, -1]], [[1, 0], [0, -1]])
        for size in ((1, 1), (3, 5), (6, 2), (5, 4), (2, 7)):
            width, height = size
            pixels = np.arange(width * height * 3, dtype=np.uint8).reshape(height, width, 3)
            reference = Image.fromarray(pixels)
            altered = mirrored_q3(reference)
            np.testing.assert_array_equal(np.asarray(altered), pixels[:, ::-1])
            for matrix in (direct, composed):
                with self.subTest(size=size, matrix=matrix):
                    result = apply_centered_matrix(altered, matrix)
                    self.assertEqual(result.size, size)
                    np.testing.assert_array_equal(np.asarray(result), pixels)
                    self.assertTrue(is_q3_correct(matrix))
            np.testing.assert_array_equal(np.asarray(reference), pixels)

    def test_odd_source_and_other_quadrants_are_preserved(self):
        pixels = np.arange(7 * 11 * 3, dtype=np.uint8).reshape(7, 11, 3)
        quadrants = split_quadrants(Image.fromarray(pixels))
        before = tuple(q.tobytes() for q in quadrants)
        result = apply_centered_matrix(mirrored_q3(quadrants[2]), [[-1, 0], [0, 1]])
        np.testing.assert_array_equal(np.asarray(result), pixels[3:, :5])
        self.assertEqual(tuple(q.tobytes() for q in quadrants), before)

    def test_composition_order_uses_column_vectors(self):
        first = [[0, -1], [1, 0]]
        second = [[1, 0], [0, -1]]
        combined = compose_corrections(first, second)
        np.testing.assert_array_equal(combined @ [2, 3], [-3, -2])
        self.assertFalse(np.array_equal(combined, np.asarray(first) @ second))

    def test_identity_rotation_alone_and_vertical_reflection_are_wrong(self):
        for matrix in (np.eye(2), -np.eye(2), [[1, 0], [0, -1]], [[-0.99, 0], [0, 1]]):
            with self.subTest(matrix=matrix):
                self.assertFalse(is_q3_correct(matrix))
        self.assertTrue(is_q3_correct([[-1, 1e-16], [-1e-16, 1]]))

    def test_validation_is_geometric_even_for_symmetric_images(self):
        image = Image.new("RGB", (3, 3), "red")
        self.assertEqual(mirrored_q3(image).tobytes(), image.tobytes())
        self.assertFalse(is_q3_correct(np.eye(2)))

    def test_invalid_matrices_are_rejected_in_both_composition_positions(self):
        for matrix in ([[0, 0], [0, 0]], [[1, 2], [2, 4]], [[1]],
                       [[float("nan"), 0], [0, 1]], [[1, 0], [0, float("inf")]],
                       [["print('unsafe')", 0], [0, 1]]):
            with self.subTest(matrix=matrix):
                with self.assertRaises(ValueError):
                    is_q3_correct(matrix)
                with self.assertRaises(ValueError):
                    compose_corrections(matrix, np.eye(2))
                with self.assertRaises(ValueError):
                    compose_corrections(np.eye(2), matrix)
        with self.assertRaises(ValueError):
            compose_corrections(np.eye(2) * 1e200, np.eye(2) * 1e200)


if __name__ == "__main__":
    unittest.main()
