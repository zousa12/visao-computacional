import streamlit as st


st.set_page_config(page_title="Visão Computacional")
st.title("Software Educacional de Transformações de Imagens")
st.write(
    "Pratique vetores e matrizes corrigindo as transformações aplicadas "
    "aos quatro quadrantes de uma imagem."
)

st.header("Os quatro desafios")
st.markdown(
    """
1. **Frente Esquerdo** — Corrija uma rotação de 180°.
2. **Frente Direito** — Recupere o tamanho original com a escala inversa.
3. **Trás Esquerdo** — Desfaça um espelhamento horizontal.
4. **Trás Direito** — Recupere as cores com a matriz inversa de um filtro RGB.
"""
)
