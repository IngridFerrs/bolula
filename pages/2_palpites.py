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

LIBERAR_PALPITES = True

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

palpites_base = ler_palpites()

if palpites_base.empty:

    st.warning(
        "Nenhum palpite enviado até o momento."
    )

    st.stop()

palpites_base["Rodada"] = palpites_base["rodada"].astype(int)
palpites_base["Participante"] = palpites_base["participante"].astype(str)
palpites_base["Jogo"] = (
    palpites_base["time_casa"].astype(str)
    + "x"
    + palpites_base["time_fora"].astype(str)
)
palpites_base["Palpite"] = (
    palpites_base["palpite_a"].astype(str)
    + " x "
    + palpites_base["palpite_b"].astype(str)
)

palpites = palpites_base[
    [
        "Rodada",
        "Participante",
        "Jogo",
        "Palpite"
    ]
].copy()

extrato = ler_extrato()

if not extrato.empty:

    extrato = extrato.rename(
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

    extrato["Rodada"] = extrato["Rodada"].astype(int)

    mapa_regras = {
        "placar_exato": "🎯 Placar Exato",
        "vencedor": "🏆 Vencedor",
        "total_gols": "⚽ Total de Gols",
        "erro": "❌ Erro"
    }

    extrato["Regra"] = (
        extrato["Regra"]
        .map(mapa_regras)
        .fillna(extrato["Regra"])
    )

    extrato = extrato[
        [
            "Rodada",
            "Participante",
            "Jogo",
            "Resultado",
            "Regra",
            "Pontos"
        ]
    ].copy()

    palpites = palpites.merge(
        extrato,
        on=[
            "Rodada",
            "Participante",
            "Jogo"
        ],
        how="left"
    )

else:

    palpites["Resultado"] = "-"
    palpites["Regra"] = "-"
    palpites["Pontos"] = "-"

palpites["Resultado"] = palpites["Resultado"].fillna("-")
palpites["Regra"] = palpites["Regra"].fillna("-")
palpites["Pontos"] = palpites["Pontos"].fillna("-")

palpites["Jogo"] = palpites["Jogo"].str.replace(
    "x",
    " x ",
    regex=False
)

palpites["Palpite"] = palpites["Palpite"].str.replace(
    "x",
    " x ",
    regex=False
)

palpites["Resultado"] = palpites["Resultado"].astype(str).str.replace(
    "x",
    " x ",
    regex=False
)

# ==========================================
# BLOQUEIO TEMPORÁRIO DA RODADA 3
# Remover este bloco quando a Rodada 3 começar
# ==========================================

palpites = palpites[
    palpites["Rodada"] != 3
].copy()




# ==========================================
# FILTROS
# ==========================================

rodadas = sorted(
    palpites["Rodada"].unique()
)
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
with col_filtro1:
    opcao_rodada = st.selectbox(
        "Selecione a rodada",
        ["Todas"] + rodadas
    )
with col_filtro2:
    if opcao_rodada == "Todas":

        opcao_jogo = st.selectbox(
            "Selecione o jogo",
            ["Todas"]
        )

        st.caption(
            "Para filtrar por jogo, selecione primeiro uma rodada."
        )

    else:

        jogos_da_rodada = sorted(
            palpites[
                palpites["Rodada"] == opcao_rodada
            ]["Jogo"].unique()
        )

        opcao_jogo = st.selectbox(
            "Selecione o jogo",
            ["Todas"] + jogos_da_rodada
        )
with col_filtro3:
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

if opcao_jogo != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Jogo"] == opcao_jogo
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

#     if not rodada_ja_comecou(opcao_rodada):

#         st.warning(
#             "Os palpites desta rodada ainda não estão disponíveis. Eles serão liberados após o início do primeiro jogo da rodada."
#         )

#         st.stop()

# else:

#     rodadas_liberadas = [

#         rodada
#         for rodada in rodadas
#         if rodada_ja_comecou(rodada)

#     ]

#     if not rodadas_liberadas:

#         st.warning(
#             "Nenhuma rodada teve início ainda. Os palpites permanecem ocultos."
#         )

#         st.stop()

    




# ==========================================
# TABELA DE EXIBIÇÃO
# ==========================================

if not LIBERAR_PALPITES:

    st.warning(
        "Os palpites ainda estão ocultos. Eles serão liberados após o início da rodada."
    )

    st.stop()

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

st.dataframe(
    df_exibicao.style.map(
        colorir_regra,
        subset=["Regra"]
    ),
    width="stretch",
    hide_index=True
)