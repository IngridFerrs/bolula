import pandas as pd
import streamlit as st
from services.api_copa import rodada_ja_comecou,traduzir_stage
from services.google_sheets import (
    ler_palpites,
    ler_extrato,
    ler_palpites_mata_mata,
    ler_extrato_mata_mata
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
LIBERAR_PALPITES_MATA_MATA = True
FASES_MATA_MATA_VISIVEIS = [
    "LAST_32",
    "LAST_16"
    
]

st.title("📊 Palpites dos Participantes")

st.divider()

# ==========================================
# SELEÇÃO DA ETAPA
# ==========================================

etapa_selecionada = st.radio(
    "Selecione a etapa",
    [
        "Fase de grupos",
        "Mata-mata"
    ],
    horizontal=True,
    key="etapa_pagina_palpites"
)


# ==========================================
# PALPITES DO MATA-MATA
# ==========================================

if etapa_selecionada == "Mata-mata":

    if not LIBERAR_PALPITES_MATA_MATA:

        st.warning(
            "Os palpites do mata-mata ainda estão ocultos. "
            "Eles serão liberados após o encerramento dos envios."
        )

        st.stop()

    palpites_mata = ler_palpites_mata_mata()

    if palpites_mata.empty:

        st.warning(
            "Nenhum palpite do mata-mata foi enviado até o momento."
        )

        st.stop()

    palpites_mata = palpites_mata.copy()

    # Campos internos usados para cruzar os dados
    palpites_mata["FaseCodigo"] = (
        palpites_mata["fase"]
        .astype(str)
        .str.strip()
    )

    palpites_mata["JogoId"] = (
        palpites_mata["jogo_id"]
        .astype(str)
        .str.strip()
    )
    palpites_mata = palpites_mata[
    palpites_mata["FaseCodigo"].isin(
        FASES_MATA_MATA_VISIVEIS
    )
    ].copy()

    if palpites_mata.empty:

        st.warning(
            "Os palpites desta fase do mata-mata ainda estão ocultos. "
            "Eles serão liberados após o encerramento dos envios."
        )

        st.stop()

    # Campos para exibição
    palpites_mata["Fase"] = (
        palpites_mata["FaseCodigo"]
        .apply(traduzir_stage)
    )

    palpites_mata["Participante"] = (
        palpites_mata["participante"]
        .astype(str)
        .str.strip()
    )

    palpites_mata["Jogo"] = (
        palpites_mata["time_casa"].astype(str).str.strip()
        + " x "
        + palpites_mata["time_fora"].astype(str).str.strip()
    )

    gols_casa = (
        pd.to_numeric(
            palpites_mata["palpite_a"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
        .astype(str)
    )

    gols_fora = (
        pd.to_numeric(
            palpites_mata["palpite_b"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
        .astype(str)
    )

    palpites_mata["Palpite — 90 min"] = (
        gols_casa
        + " x "
        + gols_fora
    )

    palpites_mata["Vencedor nos pênaltis"] = (
        palpites_mata["vencedor_penaltis"]
        .fillna("-")
        .astype(str)
        .str.strip()
        .replace("", "-")
    )


    # ======================================
    # RESULTADOS E PONTUAÇÃO DO MATA-MATA
    # ======================================

    extrato_mata = ler_extrato_mata_mata()

    if not extrato_mata.empty:

        extrato_mata = extrato_mata.copy()

        extrato_mata["Participante"] = (
            extrato_mata["participante"]
            .astype(str)
            .str.strip()
        )

        extrato_mata["FaseCodigo"] = (
            extrato_mata["fase"]
            .astype(str)
            .str.strip()
        )

        extrato_mata["JogoId"] = (
            extrato_mata["jogo_id"]
            .astype(str)
            .str.strip()
        )

        extrato_mata = extrato_mata.rename(
            columns={
                "resultado_90": "Resultado — 90 min",
                "vencedor_penaltis_real": "Vencedor real nos pênaltis",
                "pontos_base": "Pontos base",
                "bonus_penaltis": "Bônus pênaltis",
                "pontos": "Pontos"
            }
        )

        extrato_mata = extrato_mata[
            [
                "Participante",
                "FaseCodigo",
                "JogoId",
                "Resultado — 90 min",
                "Vencedor real nos pênaltis",
                "Pontos base",
                "Bônus pênaltis",
                "Pontos"
            ]
        ].copy()

        palpites_mata = palpites_mata.merge(
            extrato_mata,
            on=[
                "Participante",
                "FaseCodigo",
                "JogoId"
            ],
            how="left"
        )

    else:

        palpites_mata["Resultado — 90 min"] = "-"
        palpites_mata["Vencedor real nos pênaltis"] = "-"
        palpites_mata["Pontos base"] = "-"
        palpites_mata["Bônus pênaltis"] = "-"
        palpites_mata["Pontos"] = "-"


    # Preencher campos ainda sem resultado
    colunas_sem_resultado = [
        "Resultado — 90 min",
        "Vencedor real nos pênaltis",
        "Pontos base",
        "Bônus pênaltis",
        "Pontos"
    ]

    for coluna in colunas_sem_resultado:

        palpites_mata[coluna] = (
            palpites_mata[coluna]
            .fillna("-")
            .replace("", "-")
        )


    # ======================================
    # FILTROS
    # ======================================

    fases = sorted(
        palpites_mata["Fase"].dropna().unique()
    )

    col_fase, col_jogo, col_participante = st.columns(3)

    with col_fase:

        fase_selecionada = st.selectbox(
            "Selecione a fase",
            ["Todas"] + fases,
            key="filtro_fase_mata_mata"
        )

    base_jogos = palpites_mata.copy()

    if fase_selecionada != "Todas":

        base_jogos = base_jogos[
            base_jogos["Fase"] == fase_selecionada
        ]

    with col_jogo:

        jogos = sorted(
            base_jogos["Jogo"].dropna().unique()
        )

        jogo_selecionado = st.selectbox(
            "Selecione o jogo",
            ["Todos"] + jogos,
            key="filtro_jogo_mata_mata"
        )

    with col_participante:

        participantes = sorted(
            palpites_mata["Participante"]
            .dropna()
            .unique()
        )

        participante_selecionado = st.selectbox(
            "Selecione o participante",
            ["Todos"] + participantes,
            key="filtro_participante_mata_mata"
        )


    # ======================================
    # APLICAR FILTROS
    # ======================================

    df_mata_filtrado = palpites_mata.copy()

    if fase_selecionada != "Todas":

        df_mata_filtrado = df_mata_filtrado[
            df_mata_filtrado["Fase"]
            == fase_selecionada
        ]

    if jogo_selecionado != "Todos":

        df_mata_filtrado = df_mata_filtrado[
            df_mata_filtrado["Jogo"]
            == jogo_selecionado
        ]

    if participante_selecionado != "Todos":

        df_mata_filtrado = df_mata_filtrado[
            df_mata_filtrado["Participante"]
            == participante_selecionado
        ]


    # ======================================
    # TABELA DO MATA-MATA
    # ======================================

    df_mata_exibicao = df_mata_filtrado[
        [
            "Fase",
            "Participante",
            "Jogo",
            "Palpite — 90 min",
            "Vencedor nos pênaltis",
            "Resultado — 90 min",
            "Vencedor real nos pênaltis",
            "Pontos base",
            "Bônus pênaltis",
            "Pontos"
        ]
    ].copy()

    df_mata_exibicao = df_mata_exibicao.sort_values(
        by=[
            "Fase",
            "Jogo",
            "Participante"
        ]
    )

    st.dataframe(
        df_mata_exibicao,
        width="stretch",
        hide_index=True
    )

    # Impede a execução da lógica antiga da fase de grupos
    st.stop()
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

# # ==========================================
# # BLOQUEIO TEMPORÁRIO DA RODADA 3
# # Remover este bloco quando a Rodada 3 começar
# # ==========================================

# palpites = palpites[
#     palpites["Rodada"] != 3
# ].copy()




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