import unittest

import numpy as np
from PIL import Image, ImageDraw

from image_input import split_quadrants
from transformations import enlarged_q2, is_q2_correct, scale_image, scaled_size


class ScalingTests(unittest.TestCase):
    def test_inverse_restores_dimensions_for_even_odd_and_minimum_quadrants(self):
        for size in ((8, 6), (11, 7), (2, 2), (3, 5)):
            for factors in ((2, 2), (2, 3), (3, 2)):
                with self.subTest(size=size, factors=factors):
                    reference = split_quadrants(Image.new("RGB", size))[1]
                    altered = enlarged_q2(reference, *factors)
                    self.assertEqual(altered.size, (reference.width * factors[0], reference.height * factors[1]))
                    inverse = (1 / factors[0], 1 / factors[1])
                    corrected = scale_image(altered, *inverse)
                    self.assertEqual(corrected.size, reference.size)
                    self.assertTrue(is_q2_correct(reference.size, altered.size, *inverse))

    def test_enlargement_keeps_all_corners_and_reference(self):
        reference = Image.new("RGB", (9, 9), "white")
        drawing = ImageDraw.Draw(reference)
        for box, color in (((0, 0, 2, 2), "red"), ((6, 0, 8, 2), "green"),
                           ((0, 6, 2, 8), "blue"), ((6, 6, 8, 8), "yellow")):
            drawing.rectangle(box, fill=color)
        before = np.asarray(reference).copy()
        altered = enlarged_q2(reference, 2, 3)
        for source, target in (((0, 0), (0, 0)), ((8, 0), (17, 0)),
                               ((0, 8), (0, 26)), ((8, 8), (17, 26))):
            self.assertEqual(altered.getpixel(target), reference.getpixel(source))
        np.testing.assert_array_equal(np.asarray(reference), before)

    def test_fractional_enlargement_uses_effective_pixel_factors(self):
        altered = enlarged_q2(Image.new("RGB", (5, 3)), 1.5, 2.5)
        self.assertEqual(altered.size, (8, 8))
        self.assertTrue(is_q2_correct((5, 3), altered.size, 5 / 8, 3 / 8))
        self.assertEqual(scale_image(altered, 5 / 8, 3 / 8).size, (5, 3))

    def test_six_decimal_inverse_is_accepted(self):
        self.assertTrue(is_q2_correct((240, 160), (480, 480), 0.5, 0.333333))
        self.assertFalse(is_q2_correct((240, 160), (480, 480), 0.333333, 0.5))
        self.assertFalse(is_q2_correct((240, 160), (480, 480), 1, 1))

    def test_rounding_alone_does_not_accept_wrong_scale(self):
        self.assertEqual(scaled_size((2, 3), 0.6, 0.4), (1, 1))
        self.assertFalse(is_q2_correct((1, 1), (2, 3), 0.6, 0.4))

    def test_invalid_and_excessive_factors_are_rejected_before_resizing(self):
        for value in (0, -1, float("nan"), float("inf"), "abc", None, 1e308, 1e-308):
            for factors in ((value, 1), (1, value)):
                with self.subTest(factors=factors), self.assertRaises(ValueError):
                    scale_image(Image.new("RGB", (10, 10)), *factors)
        with self.assertRaises(ValueError):
            scaled_size((4000, 4000), 2, 2)
        with self.assertRaises(ValueError):
            enlarged_q2(Image.new("RGB", (10, 10)), 0.5, 2)


if __name__ == "__main__":
    unittest.main()
