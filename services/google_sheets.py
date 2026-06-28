import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


NOME_PLANILHA = "BOLULA_2026"
ABA_RESULTADOS = "RESULTADOS"
ABA_PALPITES = "PALPITES"
ABA_EXTRATO = "EXTRATO"
ABA_CLASSIFICACAO = "CLASSIFICACAO"
ABA_PALPITES_MATA_MATA = "PALPITES_MATA_MATA"
ABA_RESULTADOS_MATA_MATA = "RESULTADOS_MATA_MATA"
ABA_EXTRATO_MATA_MATA = "EXTRATO_MATA_MATA"


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

    aba = abrir_aba(
        "JOGOS"
    )

    valores = aba.get_all_records()

    df = pd.DataFrame(
        valores
    )

    if df.empty:
        return df

    colunas_obrigatorias = [
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora"
    ]

    if not all(
        coluna in df.columns
        for coluna in colunas_obrigatorias
    ):
        return pd.DataFrame(
            columns=colunas_obrigatorias
        )

    # Converte valores inválidos ou vazios para NaN.
    df["rodada"] = pd.to_numeric(
        df["rodada"],
        errors="coerce"
    )

    df["jogo_id"] = pd.to_numeric(
        df["jogo_id"],
        errors="coerce"
    )

    # Primeiro filtra apenas a rodada solicitada.
    # Assim, linhas do mata-mata com rodada vazia não causam erro.
    df = df[
        df["rodada"].eq(
            int(rodada)
        )
    ].copy()

    df = df.dropna(
        subset=[
            "jogo_id"
        ]
    )

    df["rodada"] = (
        df["rodada"]
        .astype(int)
    )

    df["jogo_id"] = (
        df["jogo_id"]
        .astype(int)
    )

    if "data" in df.columns:

        df = df.sort_values(
            by="data"
        )

    return df.reset_index(
        drop=True
    )


@st.cache_data(ttl=30)
def ler_palpites_mata_mata():

    colunas = [
        "participante",
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b",
        "vencedor_penaltis"
    ]

    aba = abrir_aba(
        ABA_PALPITES_MATA_MATA
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


def buscar_palpites_mata_mata_participante_fase(participante, fase):

    df = ler_palpites_mata_mata()

    if df.empty:

        return {}

    df_filtrado = df[
        (
            df["participante"].astype(str).str.strip()
            == str(participante).strip()
        )
        &
        (
            df["fase"].astype(str).str.strip()
            == str(fase).strip()
        )
    ]

    palpites_existentes = {}

    for _, linha in df_filtrado.iterrows():

        jogo_id = int(linha["jogo_id"])

        palpites_existentes[jogo_id] = {
            "palpite_a": int(linha["palpite_a"])
            if str(linha["palpite_a"]).strip()
            else 0,
            "palpite_b": int(linha["palpite_b"])
            if str(linha["palpite_b"]).strip()
            else 0,
            "vencedor_penaltis": str(linha["vencedor_penaltis"]).strip()
        }

    return palpites_existentes


def salvar_ou_atualizar_palpites_mata_mata(df_envio, participante, fase):

    aba = abrir_aba(
        ABA_PALPITES_MATA_MATA
    )

    cabecalho_padrao = [
        "participante",
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b",
        "vencedor_penaltis"
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
            str(registro.get("fase", "")).strip(),
            str(registro.get("jogo_id", "")).strip()
        )

        linhas_existentes[chave] = numero_linha

    atualizacoes = []
    novas_linhas = []

    for _, linha in df_envio.iterrows():

        chave = (
            str(participante).strip(),
            str(fase).strip(),
            str(linha["jogo_id"]).strip()
        )

        nova_linha = [
            linha["participante"],
            linha["fase"],
            linha["jogo_id"],
            linha["time_casa"],
            linha["time_fora"],
            linha["palpite_a"],
            linha["palpite_b"],
            linha["vencedor_penaltis"]
        ]

        if chave in linhas_existentes:

            numero_linha = linhas_existentes[chave]

            atualizacoes.append(
                {
                    "range": f"A{numero_linha}:H{numero_linha}",
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

    ler_palpites_mata_mata.clear()

@st.cache_data(ttl=300)
def ler_jogos_fase(fase):

    aba = abrir_aba(
        "JOGOS"
    )

    valores = aba.get_all_records()

    df = pd.DataFrame(
        valores
    )

    if df.empty:
        return df

    colunas_obrigatorias = [
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora"
    ]

    if not all(
        coluna in df.columns
        for coluna in colunas_obrigatorias
    ):

        return pd.DataFrame(
            columns=colunas_obrigatorias
        )

    df["fase"] = (
        df["fase"]
        .astype(str)
        .str.strip()
    )

    df["time_casa"] = (
        df["time_casa"]
        .astype(str)
        .str.strip()
    )

    df["time_fora"] = (
        df["time_fora"]
        .astype(str)
        .str.strip()
    )

    df["jogo_id"] = pd.to_numeric(
        df["jogo_id"],
        errors="coerce"
    )

    df = df[
        df["fase"].eq(
            str(fase).strip()
        )
    ].copy()

    # Não exibe confrontos ainda indefinidos.
    df = df[
        df["time_casa"].ne("")
        &
        df["time_fora"].ne("")
    ].copy()

    df = df.dropna(
        subset=[
            "jogo_id"
        ]
    )

    df["jogo_id"] = (
        df["jogo_id"]
        .astype(int)
    )

    if "data" in df.columns:

        df = df.sort_values(
            by="data"
        )

    return df.reset_index(
        drop=True
    )

def salvar_ou_atualizar_jogos_fase(df_jogos):

    colunas_necessarias = {
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "data"
    }

    if df_jogos is None or df_jogos.empty:

        return {
            "inseridos": 0,
            "atualizados": 0
        }

    colunas_faltantes = (
        colunas_necessarias
        - set(df_jogos.columns)
    )

    if colunas_faltantes:

        raise ValueError(
            "O DataFrame dos jogos não possui as colunas necessárias: "
            + ", ".join(
                sorted(colunas_faltantes)
            )
        )

    aba = abrir_aba(
        "JOGOS"
    )

    cabecalho_esperado = [
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora",
        "data",
        "fase"
    ]

    valores = aba.get_all_values()

    # Caso a aba esteja totalmente vazia.
    if not valores:

        aba.append_row(
            cabecalho_esperado
        )

        valores = [
            cabecalho_esperado
        ]

    cabecalho_atual = [
        str(coluna).strip()
        for coluna in valores[0]
    ]

    if cabecalho_atual[:6] != cabecalho_esperado:

        raise ValueError(
            "O cabeçalho da aba JOGOS está diferente do esperado. "
            "A ordem correta é: "
            "rodada, jogo_id, time_casa, time_fora, data, fase."
        )

    # Mapeia jogo_id para o número da linha na planilha.
    linhas_existentes = {}

    for numero_linha, linha_planilha in enumerate(
        valores[1:],
        start=2
    ):

        # Completa linhas que eventualmente tenham menos colunas.
        linha_completa = (
            linha_planilha
            + [""] * (
                len(cabecalho_atual)
                - len(linha_planilha)
            )
        )

        registro = dict(
            zip(
                cabecalho_atual,
                linha_completa
            )
        )

        jogo_id_existente = str(
            registro.get(
                "jogo_id",
                ""
            )
        ).strip()

        if jogo_id_existente:

            linhas_existentes[
                jogo_id_existente
            ] = numero_linha

    atualizacoes = []
    novas_linhas = []

    for _, jogo in df_jogos.iterrows():

        jogo_id = int(
            pd.to_numeric(
                jogo["jogo_id"],
                errors="raise"
            )
        )

        fase = str(
            jogo["fase"]
        ).strip()

        time_casa = str(
            jogo["time_casa"]
        ).strip()

        time_fora = str(
            jogo["time_fora"]
        ).strip()

        data = str(
            jogo["data"]
        ).strip()

        # Ignora qualquer confronto incompleto.
        if not time_casa or not time_fora:
            continue

        nova_linha = [
            "",          # rodada vazia no mata-mata
            jogo_id,
            time_casa,
            time_fora,
            data,
            fase
        ]

        chave = str(
            jogo_id
        )

        if chave in linhas_existentes:

            numero_linha = linhas_existentes[
                chave
            ]

            atualizacoes.append(
                {
                    "range": (
                        f"A{numero_linha}:"
                        f"F{numero_linha}"
                    ),
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

    # Limpa somente os caches relacionados à aba JOGOS.
    ler_jogos_fase.clear()
    ler_jogos_rodada.clear()

    return {
        "inseridos": len(novas_linhas),
        "atualizados": len(atualizacoes)
    }

@st.cache_data(ttl=30)
def ler_resultados_mata_mata():

    colunas = [
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "gols_casa_90",
        "gols_fora_90",
        "duracao",
        "vencedor_penaltis"
    ]

    aba = abrir_aba(
        ABA_RESULTADOS_MATA_MATA
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
def salvar_ou_atualizar_resultados_mata_mata(
    df_resultados
):

    colunas_necessarias = {
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "gols_casa_90",
        "gols_fora_90",
        "duracao",
        "vencedor_penaltis"
    }

    if df_resultados is None or df_resultados.empty:

        return {
            "inseridos": 0,
            "atualizados": 0
        }

    colunas_faltantes = (
        colunas_necessarias
        - set(df_resultados.columns)
    )

    if colunas_faltantes:

        raise ValueError(
            "O DataFrame de resultados não possui "
            "as colunas necessárias: "
            + ", ".join(
                sorted(colunas_faltantes)
            )
        )

    aba = abrir_aba(
        ABA_RESULTADOS_MATA_MATA
    )

    cabecalho_esperado = [
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "gols_casa_90",
        "gols_fora_90",
        "duracao",
        "vencedor_penaltis"
    ]

    valores = aba.get_all_values()

    if not valores:

        aba.append_row(
            cabecalho_esperado
        )

        valores = [
            cabecalho_esperado
        ]

    cabecalho_atual = [
        str(coluna).strip()
        for coluna in valores[0]
    ]

    if cabecalho_atual[:8] != cabecalho_esperado:

        raise ValueError(
            "O cabeçalho da aba RESULTADOS_MATA_MATA "
            "está diferente do esperado. A ordem correta é: "
            "fase, jogo_id, time_casa, time_fora, "
            "gols_casa_90, gols_fora_90, duracao, "
            "vencedor_penaltis."
        )

    linhas_existentes = {}

    for numero_linha, linha_planilha in enumerate(
        valores[1:],
        start=2
    ):

        linha_completa = (
            linha_planilha
            + [""] * (
                len(cabecalho_atual)
                - len(linha_planilha)
            )
        )

        registro = dict(
            zip(
                cabecalho_atual,
                linha_completa
            )
        )

        jogo_id_existente = str(
            registro.get(
                "jogo_id",
                ""
            )
        ).strip()

        if jogo_id_existente:

            linhas_existentes[
                jogo_id_existente
            ] = numero_linha

    atualizacoes = []
    novas_linhas = []

    for _, resultado in df_resultados.iterrows():

        jogo_id = int(
            pd.to_numeric(
                resultado["jogo_id"],
                errors="raise"
            )
        )

        vencedor_penaltis = str(
            resultado.get(
                "vencedor_penaltis",
                ""
            )
        ).strip()

        nova_linha = [
            str(resultado["fase"]).strip(),
            jogo_id,
            str(resultado["time_casa"]).strip(),
            str(resultado["time_fora"]).strip(),
            int(resultado["gols_casa_90"]),
            int(resultado["gols_fora_90"]),
            str(resultado["duracao"]).strip(),
            vencedor_penaltis
        ]

        chave = str(
            jogo_id
        )

        if chave in linhas_existentes:

            numero_linha = linhas_existentes[
                chave
            ]

            atualizacoes.append(
                {
                    "range": (
                        f"A{numero_linha}:"
                        f"H{numero_linha}"
                    ),
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

    ler_resultados_mata_mata.clear()

    return {
        "inseridos": len(novas_linhas),
        "atualizados": len(atualizacoes)
    }

@st.cache_data(ttl=30)
def ler_extrato_mata_mata():

    colunas = [
        "participante",
        "fase",
        "jogo_id",
        "jogo",
        "palpite",
        "resultado_90",
        "vencedor_penaltis_palpite",
        "vencedor_penaltis_real",
        "pontos_base",
        "bonus_penaltis",
        "pontos"
    ]

    aba = abrir_aba(
        ABA_EXTRATO_MATA_MATA
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
def salvar_extrato_mata_mata(
    df_extrato
):

    colunas_esperadas = [
        "participante",
        "fase",
        "jogo_id",
        "jogo",
        "palpite",
        "resultado_90",
        "vencedor_penaltis_palpite",
        "vencedor_penaltis_real",
        "pontos_base",
        "bonus_penaltis",
        "pontos"
    ]

    if df_extrato is None:

        raise ValueError(
            "O DataFrame do extrato não pode ser None."
        )

    colunas_faltantes = [
        coluna
        for coluna in colunas_esperadas
        if coluna not in df_extrato.columns
    ]

    if colunas_faltantes:

        raise ValueError(
            "O DataFrame do extrato não possui "
            "as colunas necessárias: "
            + ", ".join(
                colunas_faltantes
            )
        )

    df_salvar = df_extrato[
        colunas_esperadas
    ].copy()

    limpar_e_salvar_dataframe(
        ABA_EXTRATO_MATA_MATA,
        df_salvar
    )

    ler_extrato_mata_mata.clear()