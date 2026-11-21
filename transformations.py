"""Geometric operations independent of the Streamlit interface."""

import numpy as np
from PIL import Image


ROTATION_180 = -np.eye(2)


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
