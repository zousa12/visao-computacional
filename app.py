import streamlit as st

from image_input import example_image, load_image, split_quadrants
from transformations import apply_centered_matrix, is_q1_correct, rotated_q1
from transformations import Q2_SCALE_X, Q2_SCALE_Y, enlarged_q2, is_q2_correct, scale_image
from transformations import compose_corrections, is_q3_correct, mirrored_q3


def matrix_inputs(label: str, key: str) -> list[list[float]]:
    """Read numeric matrix entries without evaluating student-supplied code."""
    st.write(label)
    matrix = []
    for row in range(2):
        columns = st.columns(2)
        matrix.append([
            columns[column].number_input(
                f"{label} — linha {row + 1}, coluna {column + 1}",
                value=float(row == column), step=0.1, format="%.6f",
                key=f"{key}_{row}{column}",
            )
            for column in range(2)
        ])
    return matrix


st.set_page_config(page_title="Visão Computacional")
st.title("Software Educacional de Transformações de Imagens")
st.write(
    "Pratique vetores e matrizes corrigindo as transformações aplicadas "
    "aos quatro quadrantes de uma imagem."
)

st.header("Escolha uma imagem")
source = st.radio(
    "Origem da imagem",
    ("Imagem de exemplo", "Enviar PNG ou JPEG"),
    horizontal=True,
)

image = None
if source == "Imagem de exemplo":
    image = example_image()
else:
    uploaded_image = st.file_uploader("Selecione um arquivo", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        try:
            image = load_image(uploaded_image.getvalue())
        except ValueError as error:
            st.error(str(error))

if image is not None:
    st.image(image, caption=f"Prévia · {image.width} × {image.height} px", width=480)

    st.subheader("Quadrantes da imagem")
    quadrants = split_quadrants(image)
    labels = ("1. Frente Esquerdo", "2. Frente Direito", "3. Trás Esquerdo", "4. Trás Direito")
    columns = st.columns(2) + st.columns(2)
    q2_image = None
    q2_error = None
    try:
        q2_image = enlarged_q2(quadrants[1])
    except ValueError as error:
        q2_error = str(error)
    displayed_quadrants = (
        rotated_q1(quadrants[0]),
        q2_image if q2_image is not None else quadrants[1],
        mirrored_q3(quadrants[2]),
        quadrants[3],
    )
    for column, label, quadrant in zip(columns, labels, displayed_quadrants, strict=True):
        width, height = quadrant.size
        column.image(quadrant, caption=f"{label} · {width} × {height} px")

    st.subheader("Q1 — Corrija a rotação de 180°")
    st.write(
        "O primeiro quadrante foi girado em torno do centro. Insira uma matriz "
        "2 x 2 que recupere sua orientação original. As coordenadas são relativas "
        "ao centro, com X para a direita e Y para cima."
    )
    st.caption("A prévia mantém o tamanho do quadrante; áreas fora dele são recortadas.")
    with st.form("q1_matrix"):
        first_row = st.columns(2)
        a = first_row[0].number_input("a₁₁", value=1.0, step=0.1, format="%.6f")
        b = first_row[1].number_input("a₁₂", value=0.0, step=0.1, format="%.6f")
        second_row = st.columns(2)
        c = second_row[0].number_input("a₂₁", value=0.0, step=0.1, format="%.6f")
        d = second_row[1].number_input("a₂₂", value=1.0, step=0.1, format="%.6f")
        submitted = st.form_submit_button("Aplicar matriz ao Q1")
    if submitted:
        try:
            matrix = [[a, b], [c, d]]
            result = apply_centered_matrix(displayed_quadrants[0], matrix)
            st.image(result, caption="Resultado da sua tentativa — Q1")
            if is_q1_correct(matrix):
                st.success("Correto! A matriz restaurou a orientação original do Q1.")
            else:
                st.warning("A orientação ainda não foi restaurada. Revise os sinais e tente novamente.")
        except ValueError as error:
            st.error(str(error))

    st.subheader("Q2 — Recupere o tamanho com a escala inversa")
    if q2_image is None:
        st.error(f"Não foi possível ampliar o Q2: {q2_error}")
    else:
        reference_width, reference_height = quadrants[1].size
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
                st.image(result, caption=f"Resultado Q2 — {result.width} × {result.height} px")
                if is_q2_correct(quadrants[1].size, q2_image.size, sx, sy):
                    st.success("Correto! A escala inversa recuperou a largura e a altura originais do Q2.")
                else:
                    st.warning("O tamanho ou os fatores ainda estão incorretos. Calcule a escala inversa de cada eixo.")
            except ValueError as error:
                st.error(str(error))

    st.subheader("Q3 — Desfaça o espelhamento horizontal")
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
        try:
            q3_matrix = (
                compose_corrections(q3_first, q3_second)
                if q3_second is not None else q3_first
            )
            result = apply_centered_matrix(displayed_quadrants[2], q3_matrix)
            st.image(result, caption=f"Resultado Q3 — {result.width} × {result.height} px")
            if is_q3_correct(q3_matrix):
                st.success("Correto! A transformação recuperou a orientação original do Q3.")
            else:
                st.warning("O Q3 ainda está invertido. Revise os sinais e a composição das matrizes.")
        except ValueError as error:
            st.error(str(error))

st.header("Os quatro desafios")
st.markdown(
    """
1. **Frente Esquerdo** — Corrija uma rotação de 180°.
2. **Frente Direito** — Recupere o tamanho original com a escala inversa.
3. **Trás Esquerdo** — Desfaça um espelhamento horizontal.
4. **Trás Direito** — Recupere as cores com a matriz inversa de um filtro RGB.
"""
)
