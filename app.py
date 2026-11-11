import streamlit as st

from image_input import example_image, load_image


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

st.header("Os quatro desafios")
st.markdown(
    """
1. **Frente Esquerdo** — Corrija uma rotação de 180°.
2. **Frente Direito** — Recupere o tamanho original com a escala inversa.
3. **Trás Esquerdo** — Desfaça um espelhamento horizontal.
4. **Trás Direito** — Recupere as cores com a matriz inversa de um filtro RGB.
"""
)
