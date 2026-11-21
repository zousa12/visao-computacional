from io import BytesIO
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from image_input import load_image


def image_bytes(image: Image.Image, format: str = "PNG", **options) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format=format, **options)
    return buffer.getvalue()


class ImageInputTests(unittest.TestCase):
    def test_png_and_jpeg_preserve_decoded_dimensions_and_return_rgb(self):
        for size in ((8, 6), (11, 7), (2, 2)):
            for format in ("PNG", "JPEG"):
                with self.subTest(size=size, format=format):
                    source = Image.new("RGB", size, (13, 57, 201))
                    loaded = load_image(image_bytes(source, format))
                    self.assertEqual(loaded.size, size)
                    self.assertEqual(loaded.mode, "RGB")
                    loaded.load()

    def test_exif_orientation_is_applied_before_quadrants(self):
        source = Image.fromarray(np.arange(7 * 11 * 3, dtype=np.uint8).reshape(7, 11, 3))
        exif = Image.Exif()
        exif[274] = 6
        data = image_bytes(source, "JPEG", exif=exif)
        result = load_image(data)
        with Image.open(BytesIO(data)) as decoded:
            expected = decoded.transpose(Image.Transpose.ROTATE_270).convert("RGB")
            self.assertEqual(result.size, (7, 11))
            np.testing.assert_array_equal(np.asarray(result), np.asarray(expected))

    def test_grayscale_and_rgba_png_are_normalized_to_three_channels(self):
        for mode, color in (("L", 75), ("RGBA", (10, 20, 30, 127))):
            with self.subTest(mode=mode):
                source = Image.new(mode, (11, 7), color)
                result = load_image(image_bytes(source))
                self.assertEqual(result.mode, "RGB")
                self.assertEqual(np.asarray(result).shape, (7, 11, 3))

    def test_invalid_truncated_and_unsupported_content_is_rejected(self):
        png = image_bytes(Image.new("RGB", (11, 7)))
        gif = image_bytes(Image.new("RGB", (11, 7)), "GIF")
        for data in (b"", b"not an image", png[:20], gif):
            with self.subTest(data=data[:10]), self.assertRaisesRegex(ValueError, "PNG ou JPEG"):
                load_image(data)

    def test_images_too_small_for_four_quadrants_are_rejected(self):
        for size in ((1, 1), (1, 2), (2, 1)):
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, "pelo menos"):
                load_image(image_bytes(Image.new("RGB", size)))

    def test_decoder_pixel_limit_becomes_a_clear_input_error(self):
        data = image_bytes(Image.new("RGB", (11, 7)))
        with patch.object(Image, "MAX_IMAGE_PIXELS", 1):
            with self.assertRaises(ValueError):
                load_image(data)


if __name__ == "__main__":
    unittest.main()
