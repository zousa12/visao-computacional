import streamlit as st
from PIL import Image

from image_input import split_quadrants
from answer_validation import AnswerFeedback, q1_feedback, q2_feedback, q3_feedback, q4_feedback
from session_progress import SessionProgress, ensure_progress
from transformations import (
    Q2_SCALE_X, Q2_SCALE_Y, apply_centered_matrix, apply_rgb_matrix,
    compose_corrections, enlarged_q2, filtered_q4, mirrored_q3,
    rgb_preview, rotated_q1, scale_image,
)


def show_feedback(feedback: AnswerFeedback) -> None:
    if feedback.correct:
        st.success(feedback.message)
    else:
        st.warning(feedback.message)


def show_attempt(progress: SessionProgress, quadrant: int) -> None:
    attempt = progress.attempts.get(quadrant)
    if attempt is not None:
        if attempt.preview is not None:
            width, height = attempt.preview.size
            st.image(attempt.preview, caption=f"Resultado Q{quadrant} — {width} × {height} px")
        if attempt.error is not None:
            st.error(attempt.error)
        elif attempt.feedback is not None:
            show_feedback(attempt.feedback)
    if quadrant in progress.corrected:
        st.caption(f"Q{quadrant} concluído — correção salva nesta sessão.")


def matrix_inputs(label: str, key: str, size: int = 2) -> list[list[float]]:
    """Read numeric matrix entries without evaluating student-supplied code."""
    st.write(label)
    matrix = []
    for row in range(size):
        columns = st.columns(size)
        matrix.append([
            columns[column].number_input(
                f"{label} — linha {row + 1}, coluna {column + 1}",
                value=float(row == column), step=0.1, format="%.6f",
                key=f"{key}_{row}{column}",
            )
            for column in range(size)
        ])
    return matrix


def render_q1(reference: Image.Image, progress: SessionProgress) -> None:
    st.subheader("Q1 — Corrija a rotação de 180°")
    altered = rotated_q1(reference)
    st.image(altered, caption=f"1. Frente Esquerdo - {altered.width} x {altered.height} px", width="stretch")
    st.write(
        "O primeiro quadrante foi girado em torno do centro. Insira uma matriz "
        "2 x 2 que recupere sua orientação original. As coordenadas são relativas "
        "ao centro, com X para a direita e Y para cima."
    )
    st.caption("A prévia mantém o tamanho do quadrante; áreas fora dele são recortadas.")
    with st.form("q1_matrix"):
        first_row = st.columns(2)
        a = first_row[0].number_input("a₁₁", value=1.0, step=0.1, format="%.6f", key="q1_00")
        b = first_row[1].number_input("a₁₂", value=0.0, step=0.1, format="%.6f", key="q1_01")
        second_row = st.columns(2)
        c = second_row[0].number_input("a₂₁", value=0.0, step=0.1, format="%.6f", key="q1_10")
        d = second_row[1].number_input("a₂₂", value=1.0, step=0.1, format="%.6f", key="q1_11")
        submitted = st.form_submit_button("Aplicar matriz ao Q1")
    if submitted:
        try:
            matrix = [[a, b], [c, d]]
            result = apply_centered_matrix(altered, matrix)
            progress.record(1, result, q1_feedback(matrix), {"matrix": matrix})
        except ValueError as error:
            progress.record_error(1, f"Q1: {error}", {"matrix": matrix})
    show_attempt(progress, 1)


def render_q2(reference: Image.Image, progress: SessionProgress) -> None:
    st.subheader("Q2 — Recupere o tamanho com a escala inversa")
    q2_image = None
    q2_error = None
    try:
        q2_image = enlarged_q2(reference)
    except ValueError as error:
        q2_error = str(error)
    if q2_image is None:
        st.image(reference, caption="2. Frente Direito — referência sem ampliação", width="stretch")
        st.error(f"Não foi possível ampliar o Q2: {q2_error}")
    else:
        st.image(q2_image, caption=f"2. Frente Direito - {q2_image.width} x {q2_image.height} px", width="stretch")
        reference_width, reference_height = reference.size
        st.write(
            f"O Q2 foi ampliado {Q2_SCALE_X:g}× em X e {Q2_SCALE_Y:g}× em Y, "
            "sem recortar. Calcule os fatores inversos para recuperar o tamanho original."
        )
        st.write(
            f"Dimensões originais: {reference_width} × {reference_height} px. "
            f"Dimensões ampliadas: {q2_image.width} × {q2_image.height} px."
        )
        st.caption(
            "A imagem inteira é exibida ajustada ao espaço da tela; as dimensões em pixels "
            "estão na legenda. Use até seis casas decimais nos fatores. "
            "A correção é validada pela escala e pelo tamanho, independentemente da interpolação."
        )
        with st.form("q2_scale"):
            scale_columns = st.columns(2)
            sx = scale_columns[0].number_input(
                "Fator de correção em X", value=1.0, step=0.01, format="%.6f", key="q2_sx",
            )
            sy = scale_columns[1].number_input(
                "Fator de correção em Y", value=1.0, step=0.01, format="%.6f", key="q2_sy",
            )
            q2_submitted = st.form_submit_button("Aplicar escala ao Q2")
        if q2_submitted:
            try:
                result = scale_image(q2_image, sx, sy)
                progress.record(2, result, q2_feedback(reference.size, q2_image.size, sx, sy),
                                {"scale_x": sx, "scale_y": sy})
            except ValueError as error:
                progress.record_error(2, f"Q2: {error}", {"scale_x": sx, "scale_y": sy})
        show_attempt(progress, 2)


def render_q3(reference: Image.Image, progress: SessionProgress) -> None:
    st.subheader("Q3 — Desfaça o espelhamento horizontal")
    altered = mirrored_q3(reference)
    st.image(altered, caption=f"3. Trás Esquerdo - {altered.width} x {altered.height} px", width="stretch")
    st.write(
        "O quadrante Trás Esquerdo foi espelhado da esquerda para a direita. "
        "Recupere a orientação original com uma reflexão direta ou com a composição "
        "de uma rotação de 180° em Z seguida de uma reflexão vertical. "
        "Use coordenadas relativas ao centro: X para a direita e Y para cima."
    )
    q3_mode = st.radio(
        "Método de correção do Q3",
        ("Reflexão direta", "Composição de duas matrizes"), key="q3_mode",
    )
    with st.form("q3_matrix"):
        if q3_mode == "Reflexão direta":
            q3_first = matrix_inputs("Matriz de correção", "q3_direct")
            q3_second = None
        else:
            st.caption("Primeiro aplica-se A e depois B: a matriz resultante é B × A.")
            q3_first = matrix_inputs("A — rotação de 180° em Z", "q3_first")
            q3_second = matrix_inputs("B — reflexão vertical", "q3_second")
        q3_submitted = st.form_submit_button("Aplicar correção ao Q3")
    if q3_submitted:
        answer = {"method": q3_mode, "first": q3_first, "second": q3_second}
        try:
            q3_matrix = (
                compose_corrections(q3_first, q3_second)
                if q3_second is not None else q3_first
            )
            result = apply_centered_matrix(altered, q3_matrix)
            progress.record(3, result, q3_feedback(q3_matrix), answer)
        except ValueError as error:
            progress.record_error(3, f"Q3: {error}", answer)
    show_attempt(progress, 3)


def render_q4(reference: Image.Image, progress: SessionProgress) -> None:
    st.subheader("Q4 — Recupere as cores com a matriz inversa")
    q4_pixels = filtered_q4(reference)
    st.image(rgb_preview(q4_pixels), caption=f"4. Trás Direito - {reference.width} x {reference.height} px", width="stretch")
    st.write(
        "O quadrante Trás Direito recebeu uma mistura reversível dos canais RGB. "
        "Cada pixel é um vetor coluna: RGB alterado = M × RGB original. "
        "Calcule e insira a inversa de M para recuperar as cores."
    )
    st.latex(r"M = \begin{bmatrix}0.75 & 0.25 & 0 \\ 0.25 & 0.75 & 0 \\ 0 & 0 & 1\end{bmatrix}")
    st.caption(
        "As linhas da matriz produzem R, G e B, nessa ordem. Os cálculos preservam "
        "as frações dos canais; apenas as prévias são arredondadas e limitadas a 0–255. "
        "A tolerância dos canais recuperados é 0.000001."
    )
    with st.form("q4_rgb"):
        q4_matrix = matrix_inputs("Matriz de correção RGB", "q4", size=3)
        q4_submitted = st.form_submit_button("Aplicar matriz ao Q4")
    if q4_submitted:
        try:
            result = apply_rgb_matrix(q4_pixels, q4_matrix)
            preview = rgb_preview(result)
            progress.record(4, preview, q4_feedback(reference, result, q4_matrix), {"matrix": q4_matrix})
        except ValueError as error:
            progress.record_error(4, f"Q4: {error}", {"matrix": q4_matrix})
    show_attempt(progress, 4)


def render_challenges(image: Image.Image, source_token: str = "") -> None:
    """Place each statement, numeric form and result in its own quadrant."""
    progress = ensure_progress(st.session_state, image, source_token)
    quadrants = split_quadrants(image)
    renderers = (render_q1, render_q2, render_q3, render_q4)
    st.header("Os quatro desafios")
    st.write("Escolha um quadrante, preencha os valores e aplique a correção. O resultado aparece no mesmo painel.")
    for row in range(2):
        columns = st.columns(2)
        for column_index, column in enumerate(columns):
            index = row * 2 + column_index
            with column:
                with st.container(border=True):
                    renderers[index](quadrants[index], progress)
    completed = len(progress.corrected)
    st.progress(completed / 4, text=f"{completed} de 4 quadrantes corrigidos")
    reconstructed = progress.reconstruct()
    if reconstructed is not None:
        st.subheader("Imagem recomposta")
        st.image(reconstructed, caption=f"Imagem recomposta — {reconstructed.width} × {reconstructed.height} px")
