import streamlit as st

from image_input import example_image, load_image, split_quadrants
from transformations import apply_centered_matrix, is_q1_correct, rotated_q1


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
    displayed_quadrants = (rotated_q1(quadrants[0]), *quadrants[1:])
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

st.header("Os quatro desafios")
st.markdown(
    """
1. **Frente Esquerdo** — Corrija uma rotação de 180°.
2. **Frente Direito** — Recupere o tamanho original com a escala inversa.
3. **Trás Esquerdo** — Desfaça um espelhamento horizontal.
4. **Trás Direito** — Recupere as cores com a matriz inversa de um filtro RGB.
"""
)
