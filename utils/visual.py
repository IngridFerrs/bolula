import base64
from pathlib import Path

import streamlit as st


def aplicar_visual():

    caminho_imagem = Path("assets/copa_fundo_1.png")

    background_css = ""

    if caminho_imagem.exists():

        imagem_base64 = base64.b64encode(
            caminho_imagem.read_bytes()
        ).decode()

        background_css = f"""
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(
                    rgba(8, 20, 38, 0.95),
                    rgba(8, 20, 38, 0.95)
                ),
                url("data:image/png;base64,{imagem_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 1;
            z-index: 0;
            pointer-events: none;
        }}
        """

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: #081426;
            color: #FAFAFA;
        }}

        {background_css}

        section[data-testid="stSidebar"] {{
            background-color: #05101D;
            position: relative;
        }}

        section[data-testid="stSidebar"] * {{
            color: #FAFAFA;
        }}

        div.block-container {{
            padding-top: 1.5rem;
            position: relative;
            z-index: 1;
        }}

        h1, h2, h3, h4, h5, h6,
        p, label, span {{
            color: #FAFAFA;
        }}

        .stDeployButton {{
            display: none;
        }}

        .sidebar-footer {{

            
            margin-top:150px;
            padding-top= 18px;
            text-align: left;
            opacity:0.95;
        }}

        .sidebar-footer-title {{

            color: white;

            font-size: 24px;

            font-weight: 800;

            margin-bottom: 4px;

        }}

        .sidebar-footer-subtitle {{

            color: #9CA3AF;

            font-size: 14px;

        }}

        </style>
        """,
        unsafe_allow_html=True
    )


def exibir_rodape_sidebar():

    with st.sidebar:

        st.html(
            """
<div class="sidebar-footer">

    <div class="sidebar-footer-title">
        🏆 BOLULA
    </div>

    <div class="sidebar-footer-subtitle">
        3ª Edição • Copa do Mundo 2026
    </div>

</div>
"""
        )