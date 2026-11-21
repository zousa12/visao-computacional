"""Geometric operations independent of the Streamlit interface."""

import math

import numpy as np
from PIL import Image


ROTATION_180 = -np.eye(2)
HORIZONTAL_REFLECTION = np.diag([-1.0, 1.0])


def validate_matrix(matrix: object) -> np.ndarray:
    """Return a finite, invertible 2 x 2 matrix supplied by the student."""
    try:
        values = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError("Informe uma matriz 2 x 2 com valores numéricos.") from error
    if values.shape != (2, 2) or not np.isfinite(values).all():
        raise ValueError("Informe uma matriz 2 x 2 com valores numéricos finitos.")
    try:
        inverse = np.linalg.inv(values)
    except np.linalg.LinAlgError as error:
        raise ValueError("A matriz é singular. Use um determinante diferente de zero.") from error
    if not np.isfinite(inverse).all():
        raise ValueError("Os valores da matriz são pequenos demais para gerar uma prévia.")
    return values


def apply_centered_matrix(image: Image.Image, matrix: object) -> Image.Image:
    """Apply a forward matrix around the center on a fixed-size canvas.

    X points right and Y points upwards. Pillow maps destination coordinates
    back to the source, so it receives the inverse in screen coordinates.
    """
    values = validate_matrix(matrix)
    screen_axes = np.diag([1.0, -1.0])
    inverse = screen_axes @ np.linalg.inv(values) @ screen_axes
    center = np.array(image.size, dtype=float) / 2
    offset = center - inverse @ center
    coefficients = (*inverse[0], offset[0], *inverse[1], offset[1])
    return image.transform(
        image.size, Image.Transform.AFFINE, coefficients,
        resample=Image.Resampling.NEAREST,
    )


def rotated_q1(reference: Image.Image) -> Image.Image:
    """Create Q1 without modifying the reference or losing edge pixels."""
    return reference.transpose(Image.Transpose.ROTATE_180)


def is_q1_correct(matrix: object) -> bool:
    """Validate geometry even when the reference image is symmetric."""
    values = validate_matrix(matrix)
    return bool(np.allclose(values @ ROTATION_180, np.eye(2), rtol=0, atol=1e-8))


Q2_SCALE_X = 2.0
Q2_SCALE_Y = 3.0
MAX_SCALED_PIXELS = 16_000_000
MAX_SCALED_SIDE = 16_384


def scaled_size(size: tuple[int, int], sx: float, sy: float) -> tuple[int, int]:
    """Compute rounded pixel dimensions and reject invalid or excessive outputs."""
    try:
        factors = float(sx), float(sy)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Informe fatores de escala numéricos, finitos e maiores que zero.") from error
    if any(not math.isfinite(factor) or factor <= 0 for factor in factors):
        raise ValueError("Os fatores de escala devem ser finitos e maiores que zero.")
    dimensions = tuple(side * factor for side, factor in zip(size, factors, strict=True))
    if any(not math.isfinite(side) or side > MAX_SCALED_SIDE for side in dimensions):
        raise ValueError("A escala excede o limite de 16.384 pixels por lado.")
    result = tuple(round(side) for side in dimensions)
    if min(result) < 1:
        raise ValueError("A escala precisa produzir pelo menos 1 pixel em cada dimensão.")
    if result[0] * result[1] > MAX_SCALED_PIXELS:
        raise ValueError("A escala excede o limite de 16 milhões de pixels. Use uma imagem menor.")
    return result


def scale_image(image: Image.Image, sx: float, sy: float) -> Image.Image:
    """Resize the entire image without cropping; always return a new image."""
    return image.resize(scaled_size(image.size, sx, sy), Image.Resampling.BICUBIC)


def enlarged_q2(
    reference: Image.Image, sx: float = Q2_SCALE_X, sy: float = Q2_SCALE_Y,
) -> Image.Image:
    """Create a full Q2 enlargement; non-integer factors round to whole pixels."""
    size = scaled_size(reference.size, sx, sy)
    if float(sx) < 1 or float(sy) < 1:
        raise ValueError("A ampliação do desafio deve usar fatores maiores ou iguais a 1.")
    return reference.resize(size, Image.Resampling.BICUBIC)


def is_q2_correct(
    original_size: tuple[int, int], enlarged_size: tuple[int, int], sx: float, sy: float,
) -> bool:
    """Check inverse geometry and dimensions, independently of interpolation.

    Effective factors use actual pixel dimensions after rounding. A tolerance
    of 1e-6 accepts six decimal places for recurring fractions such as 1/3.
    """
    result_size = scaled_size(enlarged_size, sx, sy)
    expected = np.asarray(original_size, dtype=float) / enlarged_size
    return result_size == original_size and bool(
        np.allclose([float(sx), float(sy)], expected, rtol=0, atol=1e-6)
    )


def mirrored_q3(reference: Image.Image) -> Image.Image:
    """Mirror left/right without changing dimensions or the reference pixels."""
    return reference.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def compose_corrections(first: object, second: object) -> np.ndarray:
    """For column vectors, applying A then B produces B @ A."""
    a = validate_matrix(first)
    b = validate_matrix(second)
    with np.errstate(over="ignore", invalid="ignore"):
        result = b @ a
    return validate_matrix(result)


def is_q3_correct(matrix: object) -> bool:
    """Validate the equivalent reflection, even for symmetric reference images."""
    values = validate_matrix(matrix)
    return bool(np.allclose(values @ HORIZONTAL_REFLECTION, np.eye(2), rtol=0, atol=1e-8))
