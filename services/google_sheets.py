import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


NOME_PLANILHA = "BOLULA_2026"
ABA_RESULTADOS = "RESULTADOS"
ABA_PALPITES = "PALPITES"
ABA_EXTRATO = "EXTRATO"
ABA_CLASSIFICACAO = "CLASSIFICACAO"


@st.cache_resource
@st.cache_resource
def conectar_planilha():

    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credenciais = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=escopos
    )

    cliente = gspread.authorize(
        credenciais
    )

    planilha = cliente.open(
        NOME_PLANILHA
    )

    return planilha

def abrir_aba(nome_aba):

    planilha = conectar_planilha()

    return planilha.worksheet(
        nome_aba
    )


def ler_palpites():

    aba = abrir_aba(
        ABA_PALPITES
    )

    dados = aba.get_all_records()

    return pd.DataFrame(
        dados
    )


def salvar_palpites(df_envio):

    aba = abrir_aba(
        ABA_PALPITES
    )

    valores_existentes = aba.get_all_values()

    if not valores_existentes:

        aba.append_row(
            [
                "participante",
                "rodada",
                "jogo_id",
                "time_casa",
                "time_fora",
                "palpite_a",
                "palpite_b"
            ]
        )

    linhas = df_envio[
        [
            "participante",
            "rodada",
            "jogo_id",
            "time_casa",
            "time_fora",
            "palpite_a",
            "palpite_b"
        ]
    ].values.tolist()

    aba.append_rows(
        linhas
    )


def participante_ja_enviou(participante, rodada):

    df = ler_palpites()

    if df.empty:

        return False

    return (
        df["participante"]
        .astype(str)
        .str.strip()
        .eq(participante)
        &
        df["rodada"]
        .astype(int)
        .eq(int(rodada))
    ).any()

def ler_resultados():

    aba = abrir_aba(
        ABA_RESULTADOS
    )

    valores = aba.get_all_values()

    colunas = [
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora",
        "gols_casa",
        "gols_fora"
    ]

    if not valores:

        return pd.DataFrame(
            columns=colunas
        )

    if len(valores) == 1:

        return pd.DataFrame(
            columns=valores[0]
        )

    return pd.DataFrame(
        valores[1:],
        columns=valores[0]
    )


def salvar_resultados(df_resultados):

    aba = abrir_aba(
        ABA_RESULTADOS
    )

    valores_existentes = aba.get_all_values()

    if not valores_existentes:

        aba.append_row(
            [
                "rodada",
                "jogo_id",
                "time_casa",
                "time_fora",
                "gols_casa",
                "gols_fora"
            ]
        )

    linhas = df_resultados[
        [
            "rodada",
            "jogo_id",
            "time_casa",
            "time_fora",
            "gols_casa",
            "gols_fora"
        ]
    ].values.tolist()

    aba.append_rows(
        linhas
    )
def limpar_e_salvar_dataframe(nome_aba, df):

    aba = abrir_aba(
        nome_aba
    )

    aba.clear()

    if df.empty:

        return

    valores = [
        df.columns.tolist()
    ] + df.values.tolist()

    aba.update(
        valores
    )


def ler_extrato():

    aba = abrir_aba(
        ABA_EXTRATO
    )

    valores = aba.get_all_values()

    colunas = [
        "participante",
        "rodada",
        "jogo",
        "palpite",
        "resultado",
        "criterios",
        "pontos"
    ]

    if not valores:

        return pd.DataFrame(
            columns=colunas
        )

    if len(valores) == 1:

        return pd.DataFrame(
            columns=valores[0]
        )

    return pd.DataFrame(
        valores[1:],
        columns=valores[0]
    )


def ler_classificacao():

    aba = abrir_aba(
        ABA_CLASSIFICACAO
    )

    valores = aba.get_all_values()

    colunas = [
        "posicao",
        "participante",
        "pontos"
    ]

    if not valores:

        return pd.DataFrame(
            columns=colunas
        )

    if len(valores) == 1:

        return pd.DataFrame(
            columns=valores[0]
        )

    return pd.DataFrame(
        valores[1:],
        columns=valores[0]
    )


def salvar_extrato(df_extrato):

    limpar_e_salvar_dataframe(
        ABA_EXTRATO,
        df_extrato
    )


def salvar_classificacao(df_classificacao):

    limpar_e_salvar_dataframe(
        ABA_CLASSIFICACAO,
        df_classificacao
    )

def salvar_ou_atualizar_palpites(df_envio, participante, rodada):

    aba = abrir_aba(
        ABA_PALPITES
    )

    valores = aba.get_all_values()

    if not valores:

        aba.append_row(
            [
                "participante",
                "rodada",
                "jogo_id",
                "time_casa",
                "time_fora",
                "palpite_a",
                "palpite_b"
            ]
        )

        valores = aba.get_all_values()

    cabecalho = valores[0]

    linhas_para_manter = [
        cabecalho
    ]

    for linha in valores[1:]:

        registro = dict(
            zip(
                cabecalho,
                linha
            )
        )

        mesmo_participante = (
            str(registro.get("participante", "")).strip()
            == str(participante).strip()
        )

        mesma_rodada = (
            str(registro.get("rodada", "")).strip()
            == str(rodada).strip()
        )

        if not (
            mesmo_participante
            and mesma_rodada
        ):

            linhas_para_manter.append(
                linha
            )

    novas_linhas = df_envio[
        [
            "participante",
            "rodada",
            "jogo_id",
            "time_casa",
            "time_fora",
            "palpite_a",
            "palpite_b"
        ]
    ].values.tolist()

    linhas_finais = (
        linhas_para_manter
        + novas_linhas
    )

    aba.clear()

    aba.update(
        linhas_finais
    )