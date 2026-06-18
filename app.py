import streamlit as st


# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="BOLULA",
    page_icon="🏆",
    layout="wide"
)


# ==========================================
# NAVEGAÇÃO
# ==========================================


MANUTENCAO = True

if MANUTENCAO:

    st.title("🚧 BOLULA em manutenção")

    st.warning(
        "Estamos ajustando o sistema para melhorar o envio dos palpites. "
        "Volte em alguns minutos."
    )

    st.stop()

pages = {

    "BOLULA": [

        st.Page(
            "pages/1_classificacao.py",
            title="🏆 Classificação"
        ),

        st.Page(
            "pages/2_palpites.py",
            title="📊 Palpites"
        ),

        st.Page(
            "pages/3_jogos.py",
            title="⚽ Jogos"
        ),

        st.Page(
            "pages/4_enviarPalpites.py",
            title="📤 Envio Palpites"
        )

    ]
}


pg = st.navigation(pages)

pg.run()