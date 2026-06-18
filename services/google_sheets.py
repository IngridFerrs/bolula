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

@st.cache_data(ttl=30)
def ler_palpites():

    colunas = [
        "participante",
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b"
    ]

    aba = abrir_aba(
        ABA_PALPITES
    )

    valores = aba.get_all_values()

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

    cabecalho_padrao = [
        "participante",
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b"
    ]

    valores = aba.get_all_values()

    if not valores:

        aba.append_row(
            cabecalho_padrao
        )

        valores = aba.get_all_values()

    cabecalho = valores[0]

    linhas_existentes = {}

    for numero_linha, linha in enumerate(valores[1:], start=2):

        registro = dict(
            zip(
                cabecalho,
                linha
            )
        )

        chave = (
            str(registro.get("participante", "")).strip(),
            str(registro.get("rodada", "")).strip(),
            str(registro.get("jogo_id", "")).strip()
        )

        linhas_existentes[chave] = numero_linha

    atualizacoes = []
    novas_linhas = []

    for _, linha in df_envio.iterrows():

        chave = (
            str(participante).strip(),
            str(rodada).strip(),
            str(linha["jogo_id"]).strip()
        )

        nova_linha = [
            linha["participante"],
            linha["rodada"],
            linha["jogo_id"],
            linha["time_casa"],
            linha["time_fora"],
            linha["palpite_a"],
            linha["palpite_b"]
        ]

        if chave in linhas_existentes:

            numero_linha = linhas_existentes[chave]

            atualizacoes.append(
                {
                    "range": f"A{numero_linha}:G{numero_linha}",
                    "values": [
                        nova_linha
                    ]
                }
            )

        else:

            novas_linhas.append(
                nova_linha
            )

    if atualizacoes:

        aba.batch_update(
            atualizacoes
        )

    if novas_linhas:

        aba.append_rows(
            novas_linhas
        )
    st.cache_data.clear()
def buscar_palpites_participante_rodada(participante, rodada):

    df = ler_palpites()

    if df.empty:

        return {}

    df_filtrado = df[
        (
            df["participante"].astype(str).str.strip()
            == str(participante).strip()
        )
        &
        (
            df["rodada"].astype(str).str.strip()
            == str(rodada).strip()
        )
    ]

    palpites_existentes = {}

    for _, linha in df_filtrado.iterrows():

        jogo_id = int(linha["jogo_id"])

        palpites_existentes[jogo_id] = {
            "palpite_a": int(linha["palpite_a"]),
            "palpite_b": int(linha["palpite_b"])
        }

    return palpites_existentes

@st.cache_data(ttl=300)
def ler_jogos_rodada(rodada):
    aba = abrir_aba("JOGOS")

    valores = aba.get_all_records()

    df = pd.DataFrame(valores)

    if df.empty:
        return df

    df["rodada"] = df["rodada"].astype(int)
    df["jogo_id"] = df["jogo_id"].astype(int)

    df = df[df["rodada"] == int(rodada)].copy()

    return df