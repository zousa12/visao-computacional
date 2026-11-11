from io import BytesIO

from PIL import Image, ImageDraw, ImageOps


def load_image(data: bytes) -> Image.Image:
    """Decode PNG or JPEG and return an oriented RGB image."""
    try:
        with Image.open(BytesIO(data), formats=["PNG", "JPEG"]) as source:
            if source.width < 2 or source.height < 2:
                raise ValueError("A imagem precisa ter pelo menos 2 × 2 pixels.")
            return ImageOps.exif_transpose(source).convert("RGB")
    except (OSError, Image.DecompressionBombError) as error:
        raise ValueError("Não foi possível abrir a imagem. Envie um PNG ou JPEG válido.") from error


def split_quadrants(
    image: Image.Image,
) -> tuple[Image.Image, Image.Image, Image.Image, Image.Image]:
    """Return the reference crops in reading order from an image at least 2 × 2."""
    width, height = image.size
    middle_x, middle_y = width // 2, height // 2

    # The right and bottom crops include the extra column or row for odd sizes.
    return (
        image.crop((0, 0, middle_x, middle_y)),
        image.crop((middle_x, 0, width, middle_y)),
        image.crop((0, middle_y, middle_x, height)),
        image.crop((middle_x, middle_y, width, height)),
    )


def example_image() -> Image.Image:
    image = Image.new("RGB", (480, 320), "#e0f2fe")
    drawing = ImageDraw.Draw(image)
    drawing.ellipse((344, 30, 419, 105), fill="#fbbf24")
    drawing.polygon([(0, 270), (148, 84), (300, 270)], fill="#475569")
    drawing.polygon([(86, 162), (148, 84), (212, 163), (153, 145)], fill="#f8fafc")
    drawing.polygon([(205, 269), (369, 139), (480, 251), (480, 320)], fill="#0f766e")
    drawing.rectangle((0, 270, 479, 319), fill="#15803d")
    return image
