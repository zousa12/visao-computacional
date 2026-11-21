import hashlib

import streamlit as st

from challenge_ui import render_challenges
from image_input import example_image, load_image
from session_progress import clear_progress, PROGRESS_KEY
from history_ui import render_history


st.set_page_config(page_title="Visão Computacional", layout="wide")
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
image_token = source
if source == "Imagem de exemplo":
    image = example_image()
else:
    uploaded_image = st.file_uploader("Selecione um arquivo", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        try:
            data = uploaded_image.getvalue()
            image = load_image(data)
            image_token = f"{source}|{uploaded_image.name}|{hashlib.sha256(data).hexdigest()}"
        except ValueError as error:
            st.error(str(error))

if image is not None:
    st.image(image, caption=f"Prévia - {image.width} x {image.height} px", width=480)
    render_challenges(image, image_token)
else:
    clear_progress(st.session_state)

render_history(st.session_state.get(PROGRESS_KEY))
