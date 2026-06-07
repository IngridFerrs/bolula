import streamlit as st
import pandas as pd
from utils.visual import aplicar_visual
USUARIOS = dict(st.secrets["usuarios"])
from services.api_copa import (buscar_jogos_rodada,buscar_rodada_aberta)
from utils.visual import (aplicar_visual,exibir_rodape_sidebar)
import os
from services.google_sheets import (salvar_ou_atualizar_palpites,participante_ja_enviou)


# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Envio de Palpites",
    page_icon="📤",
    layout="wide"
)

aplicar_visual()
exibir_rodape_sidebar()

# ==========================================
# SESSION STATE
# ==========================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "jogos_rodada" not in st.session_state:
    st.session_state.jogos_rodada = None

if "rodada_aberta" not in st.session_state:
    st.session_state.rodada_aberta = None
if "rodada_cache" not in st.session_state:
    st.session_state.rodada_cache = None

# ==========================================
# TÍTULO
# ==========================================

st.title("📤 Envio de Palpites")

st.divider()

# ==========================================
# LOGIN
# ==========================================

if not st.session_state.autenticado:

    st.subheader("🔐 Login")

    participante = st.selectbox(
        "Participante",
        list(USUARIOS.keys())
    )

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        if USUARIOS[participante] == senha:

            st.session_state.autenticado = True
            st.session_state.usuario = participante

            st.success(
                "Login realizado com sucesso!"
            )

            st.rerun()

        else:

            st.error(
                "Senha inválida."
            )

# ==========================================
# ÁREA LOGADA
# ==========================================

else:

    usuario = st.session_state.usuario

    st.success(
        f"✅ Logada como: {usuario}"
    )

    st.divider()

    # ==========================================
    # RODADA ABERTA
    # ==========================================

    # TEMPORÁRIO PARA TESTES

    rodada_aberta = 1

#     # FUTURO

#     if st.session_state.rodada_aberta is None:

#          st.session_state.rodada_aberta = (
#         buscar_rodada_aberta()
#     )

#     rodada_aberta = (
#        st.session_state.rodada_aberta
# )

#     if rodada_aberta is None:

#         st.warning(
#          """
#          Nenhuma rodada está aberta
#          para envio de palpites.
#          """
#      )
#         if st.button("Sair"):

#             st.session_state.autenticado = False
#             st.session_state.usuario = None
#             st.session_state.jogos_rodada = None
#             st.session_state.rodada_aberta = None
#             st.session_state.rodada_cache = None

#             st.rerun()
#         st.stop()

    # ==========================================
    # CARREGAR JOGOS DA API
    # ==========================================

   
    if (
        st.session_state.jogos_rodada is None
        or st.session_state.rodada_cache != rodada_aberta
    ):

        with st.spinner(
            "Carregando jogos da rodada..."
        ):

            st.session_state.jogos_rodada = (
                buscar_jogos_rodada(
                    rodada_aberta
                )
            )

        st.session_state.rodada_cache = rodada_aberta

    df_rodada = st.session_state.jogos_rodada

    # ==========================================
    # VALIDAR RETORNO DA API
    # ==========================================

    if df_rodada.empty:

        st.error(
            """
            Não foi possível carregar os jogos da rodada.

            Verifique a API ou tente novamente mais tarde.
            """
        )

        st.stop()

    st.subheader(
        f"Rodada {rodada_aberta}"
    )

    st.write(
        f"Quantidade de jogos: {len(df_rodada)}"
    )

    # ==========================================
    # ARQUIVO DE PALPITES
    # ==========================================

    arquivo_palpites = (
        f"dados/palpites_rodada_{rodada_aberta}.xlsx"
    )

    # ==========================================
    # VERIFICAR SE JÁ ENVIOU
    # ==========================================

    ja_enviou = participante_ja_enviou(
    usuario,
    rodada_aberta
    )
    # ==========================================
    # BLOQUEAR DUPLICIDADE
    # ==========================================

    if ja_enviou:

        st.warning(
            "Você já enviou seus palpites para esta rodada."
        )

    else:

        st.success(
            "Você ainda não enviou seus palpites."
        )

        st.divider()

        st.subheader(
            "Preencha seus palpites"
        )

        palpites_usuario = []

        for indice, linha in df_rodada.iterrows():

            st.markdown(
                f"### {linha['time_casa']} x {linha['time_fora']}"
            )

            col1, col2, col3 = st.columns(
                [1, 0.3, 1]
            )

            with col1:

                gols_casa = st.number_input(
                    linha["time_casa"],
                    min_value=0,
                    max_value=20,
                    value=0,
                    key=f"casa_{indice}"
                )

            with col2:

                st.markdown(
                    "<h3 style='text-align:center;'>x</h3>",
                    unsafe_allow_html=True
                )

            with col3:

                gols_fora = st.number_input(
                    linha["time_fora"],
                    min_value=0,
                    max_value=20,
                    value=0,
                    key=f"fora_{indice}"
                )

            palpites_usuario.append({

                "participante": usuario,

                "rodada": linha["rodada"],

                "jogo_id": linha["jogo_id"],

                "time_casa": linha["time_casa"],

                "time_fora": linha["time_fora"],

                "palpite_a": gols_casa,

                "palpite_b": gols_fora

            })

            st.divider()

        # ==========================================
        # ENVIAR PALPITES
        # ==========================================

        if st.button("📤 Enviar Palpites"):

            df_envio = pd.DataFrame(
                palpites_usuario
            )

            salvar_ou_atualizar_palpites(
                df_envio,
                usuario,
                rodada_aberta
            )

            st.success(
                "🎉 Palpites enviados com sucesso!"
            )

            st.rerun()

    # ==========================================
    # LOGOUT
    # ==========================================

    st.divider()

    if st.button("Sair"):

        st.session_state.autenticado = False

        st.session_state.usuario = None

        st.session_state.jogos_rodada = None

        st.session_state.rodada_aberta = None

        st.session_state.rodada_cache = None

        st.rerun()