"""Educational feedback built on the same numerical checks as the operations."""

from dataclasses import dataclass

import numpy as np
from PIL import Image

from transformations import (
    HORIZONTAL_REFLECTION, MATRIX_ATOL, RGB_ATOL, ROTATION_180,
    is_q1_correct, is_q2_correct, is_q3_correct, is_q4_correct,
    rgb_values, scaled_size, validate_matrix,
)


@dataclass(frozen=True)
class AnswerFeedback:
    correct: bool
    message: str


def geometry_feedback(matrix: object, applied: np.ndarray, quadrant: str) -> AnswerFeedback:
    correct = is_q1_correct(matrix) if quadrant == "Q1" else is_q3_correct(matrix)
    if correct:
        return AnswerFeedback(True, f"Correto! A transformação recuperou a orientação original do {quadrant}.")
    composition = validate_matrix(matrix) @ applied
    axes = [axis for row, axis in enumerate(("X", "Y"))
            if not np.allclose(composition[row], np.eye(2)[row], rtol=0, atol=MATRIX_ATOL)]
    return AnswerFeedback(
        False,
        f"{quadrant}: a transformação final ainda altera o eixo {' e '.join(axes)}. "
        "Revise os sinais e os termos fora da diagonal; a correção deve desfazer a alteração inicial.",
    )


def q1_feedback(matrix: object) -> AnswerFeedback:
    return geometry_feedback(matrix, ROTATION_180, "Q1")


def q2_feedback(original_size: tuple[int, int], enlarged_size: tuple[int, int],
                sx: float, sy: float) -> AnswerFeedback:
    if is_q2_correct(original_size, enlarged_size, sx, sy):
        return AnswerFeedback(True, "Correto! A escala inversa recuperou a largura e a altura originais do Q2.")
    actual = scaled_size(enlarged_size, sx, sy)
    if actual != original_size:
        axes = [axis for i, axis in enumerate(("X", "Y")) if actual[i] != original_size[i]]
        return AnswerFeedback(
            False,
            f"Q2: resultado de {actual[0]} × {actual[1]} px; esperado {original_size[0]} × {original_size[1]} px. "
            f"Revise a escala inversa em {' e '.join(axes)}.",
        )
    return AnswerFeedback(
        False,
        "Q2: o arredondamento produziu o tamanho esperado, mas os fatores ainda não são os inversos. "
        "Divida a dimensão original pela ampliada em cada eixo e use seis casas decimais.",
    )


def q3_feedback(matrix: object) -> AnswerFeedback:
    if np.allclose(validate_matrix(matrix), ROTATION_180, rtol=0, atol=MATRIX_ATOL):
        return AnswerFeedback(
            False,
            "Q3: a rotação de 180° isolada não desfaz o espelhamento horizontal. "
            "Inclua a reflexão vertical na composição ou use a reflexão horizontal direta.",
        )
    return geometry_feedback(matrix, HORIZONTAL_REFLECTION, "Q3")


def q4_feedback(reference: Image.Image, corrected: object, matrix: object) -> AnswerFeedback:
    if is_q4_correct(reference, corrected, matrix):
        return AnswerFeedback(True, "Correto! A matriz inversa recuperou os valores RGB originais do Q4.")
    result = rgb_values(corrected)
    original = np.asarray(reference.convert("RGB"), dtype=np.float64)
    if result.shape != original.shape:
        return AnswerFeedback(False, "Q4: a correção deve preservar a largura, a altura e os três canais RGB.")
    difference = float(np.max(np.abs(result - original)))
    if difference <= RGB_ATOL:
        return AnswerFeedback(
            False,
            "Q4: os pixels coincidem nesta imagem, mas a matriz ainda não desfaz o filtro RGB. "
            "Confira se a matriz de correção multiplicada pelo filtro produz a identidade.",
        )
    return AnswerFeedback(
        False,
        f"Q4: diferença máxima nos canais de {difference:.6g}; tolerância {RGB_ATOL:g}. "
        "Revise a matriz inversa e a ordem dos canais R, G e B.",
    )
