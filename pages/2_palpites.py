import pandas as pd
import streamlit as st
from services.api_copa import rodada_ja_comecou
from services.google_sheets import (
    ler_palpites,
    ler_extrato
)
from utils.visual import (
    aplicar_visual,
    exibir_rodape_sidebar
)

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Palpites",
    page_icon="📊",
    layout="wide"
)

aplicar_visual()
exibir_rodape_sidebar()
st.title("📊 Palpites dos Participantes")

st.divider()


# ==========================================
# CONFIGURAÇÕES
# ==========================================




# ==========================================
# FUNÇÕES
# ==========================================

def colorir_regra(valor):

    if valor == "🎯 Placar Exato":
        return "background-color: #d4edda; color: #0F5132;"

    if valor == "🏆 Vencedor":
        return "background-color: #d1ecf1; color: #0C5460;"

    if valor == "⚽ Total de Gols":
        return "background-color: #fff3cd; color: #856404;"

    if valor == "❌ Erro":
        return "background-color: #f8d7da; color: #721C24;"

    return ""


# ==========================================
# CARREGAR DADOS
# ==========================================

extrato = ler_extrato()

if not extrato.empty:

    palpites = extrato.rename(
        columns={
            "participante": "Participante",
            "rodada": "Rodada",
            "jogo": "Jogo",
            "palpite": "Palpite",
            "resultado": "Resultado",
            "criterios": "Regra",
            "pontos": "Pontos"
        }
    )

    mapa_regras = {
        "placar_exato": "🎯 Placar Exato",
        "vencedor": "🏆 Vencedor",
        "total_gols": "⚽ Total de Gols",
        "erro": "❌ Erro"
    }

    palpites["Regra"] = (
        palpites["Regra"]
        .map(mapa_regras)
        .fillna(palpites["Regra"])
    )

    palpites["Rodada"] = palpites["Rodada"].astype(int)
    palpites["Pontos"] = palpites["Pontos"].astype(int)

    tem_resultado = True

else:

    st.warning(
        "Ainda não há pontuação calculada. Exibindo apenas os palpites enviados."
    )

    palpites = ler_palpites()

    if palpites.empty:

        st.warning(
            "Nenhum palpite enviado até o momento."
        )

        st.stop()

    palpites["Palpite"] = (
        palpites["palpite_a"].astype(str)
        + " x "
        + palpites["palpite_b"].astype(str)
    )

    palpites["Jogo"] = (
        palpites["time_casa"]
        + " x "
        + palpites["time_fora"]
    )

    palpites = palpites.rename(
        columns={
            "participante": "Participante",
            "rodada": "Rodada"
        }
    )

    palpites["Rodada"] = palpites["Rodada"].astype(int)

    tem_resultado = False


# ==========================================
# FILTROS
# ==========================================

rodadas = sorted(
    palpites["Rodada"].unique()
)

opcao_rodada = st.selectbox(
    "Selecione a rodada",
    ["Todas"] + rodadas
)

participantes = sorted(
    palpites["Participante"].unique()
)

opcao_participante = st.selectbox(
    "Selecione o participante",
    ["Todos"] + participantes
)


# ==========================================
# APLICAR FILTROS
# ==========================================

df_filtrado = palpites.copy()

if opcao_rodada != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Rodada"] == opcao_rodada
    ]

if opcao_participante != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Participante"] == opcao_participante
    ]


# ==========================================
# BLOQUEIO AUTOMÁTICO DE VISUALIZAÇÃO
# ==========================================
# MANTER COMENTADO DURANTE OS TESTES
# Quando for para produção, descomente este bloco.

# if opcao_rodada != "Todas":
#
#     if not rodada_ja_comecou(opcao_rodada):
#
#         st.warning(
#             "Os palpites desta rodada ainda não estão disponíveis. Eles serão liberados após o início do primeiro jogo da rodada."
#         )
#
#         st.stop()
#
# else:
#
#     rodadas_liberadas = [
#
#         rodada
#         for rodada in rodadas
#         if rodada_ja_comecou(rodada)
#
#     ]
#
#     if not rodadas_liberadas:
#
#         st.warning(
#             "Nenhuma rodada teve início ainda. Os palpites permanecem ocultos."
#         )
#
#         st.stop()
#
#     df_filtrado = df_filtrado[
#         df_filtrado["Rodada"].isin(rodadas_liberadas)
#     ]


# ==========================================
# TABELA DE EXIBIÇÃO
# ==========================================

if tem_resultado:

    df_exibicao = df_filtrado[
        [
            "Rodada",
            "Participante",
            "Jogo",
            "Palpite",
            "Resultado",
            "Regra",
            "Pontos"
        ]
    ].copy()

else:

    df_exibicao = df_filtrado[
        [
            "Rodada",
            "Participante",
            "Jogo",
            "Palpite"
        ]
    ].copy()


df_exibicao = df_exibicao.sort_values(
    by=[
        "Rodada",
        "Jogo",
        "Participante"
    ]
)


# ==========================================
# MOSTRAR TABELA
# ==========================================

if tem_resultado:

    st.dataframe(
        df_exibicao.style.map(
            colorir_regra,
            subset=["Regra"]
        ),
        width="stretch",
        hide_index=True,
       
    )

else:

    st.dataframe(
        df_exibicao,
        width="stretch",
        hide_index=True
    )