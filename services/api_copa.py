import requests
import pandas as pd
from datetime import datetime,timedelta,timezone
import streamlit as st

API_KEY = st.secrets["API_KEY"]

COMPETICAO = "WC"


def buscar_jogos_rodada(rodada_desejada):


    headers = {
        "X-Auth-Token": API_KEY
    }

    url = (
        f"https://api.football-data.org/v4/"
        f"competitions/{COMPETICAO}/matches"
    )

    response = requests.get(
        url,
        headers=headers
    )

    dados = response.json()

    # --------------------------------------
    # VALIDAR RESPOSTA
    # --------------------------------------

    if "matches" not in dados:

        print("\nERRO NA API:\n")
        print(dados)

        return pd.DataFrame()

    jogos = dados["matches"]

    lista_jogos = []

    for jogo in jogos:

        rodada = jogo["matchday"]

        if rodada != rodada_desejada:
            continue

        lista_jogos.append({

            "rodada": rodada,

            "jogo_id": jogo["id"],

            "time_casa": jogo["homeTeam"]["shortName"],

            "time_fora": jogo["awayTeam"]["shortName"],

            "data": jogo["utcDate"]

        })

    return pd.DataFrame(lista_jogos)

def buscar_primeiro_jogo_por_rodada():

    headers = {
        "X-Auth-Token": API_KEY
    }

    url = (
        f"https://api.football-data.org/v4/"
        f"competitions/{COMPETICAO}/matches"
    )

    response = requests.get(
        url,
        headers=headers
    )

    dados = response.json()

    if "matches" not in dados:

        print("\nERRO NA API:\n")
        print(dados)

        return {}

    jogos = dados["matches"]

    rodadas = {}

    for jogo in jogos:

        rodada = jogo["matchday"]

        # Ignora jogos sem rodada
        if rodada is None:
            continue

        data_jogo = datetime.fromisoformat(
            jogo["utcDate"].replace(
                "Z",
                "+00:00"
            )
        )

        if rodada not in rodadas:

            rodadas[rodada] = data_jogo

        elif data_jogo < rodadas[rodada]:

            rodadas[rodada] = data_jogo

    return rodadas

def buscar_rodada_aberta():

    rodadas = buscar_primeiro_jogo_por_rodada()

    agora = datetime.now(timezone.utc)

    for rodada, primeiro_jogo in rodadas.items():

        abertura = primeiro_jogo - timedelta(hours=5)

        fechamento = primeiro_jogo - timedelta(minutes=30)

        if abertura <= agora <= fechamento:

            return rodada

    return None


def buscar_resultados_rodada(rodada_desejada):

    headers = {
        "X-Auth-Token": API_KEY
    }

    url = (
        f"https://api.football-data.org/v4/"
        f"competitions/{COMPETICAO}/matches"
    )

    response = requests.get(
        url,
        headers=headers
    )

    dados = response.json()

    if "matches" not in dados:

        print("\nERRO NA API:\n")
        print(dados)

        return pd.DataFrame()

    jogos = dados["matches"]

    lista_resultados = []

    for jogo in jogos:

        rodada = jogo["matchday"]

        if rodada != rodada_desejada:
            continue

        gols_casa = jogo["score"]["fullTime"]["home"]
        gols_fora = jogo["score"]["fullTime"]["away"]

        if gols_casa is None or gols_fora is None:
            continue

        lista_resultados.append({

            "rodada": rodada,
            "jogo_id": jogo["id"],
            "time_casa": jogo["homeTeam"]["shortName"],
            "time_fora": jogo["awayTeam"]["shortName"],
            "gols_casa": gols_casa,
            "gols_fora": gols_fora

        })

    return pd.DataFrame(lista_resultados)

def rodada_ja_comecou(rodada):

    rodadas = buscar_primeiro_jogo_por_rodada()

    if rodada not in rodadas:

        return False

    primeiro_jogo = rodadas[rodada]

    agora = datetime.now(timezone.utc)

    return agora >= primeiro_jogo

def rodada_ainda_aberta(rodada):

    rodadas = buscar_primeiro_jogo_por_rodada()

    if rodada not in rodadas:

        return False

    agora = datetime.now(timezone.utc)

    primeiro_jogo = rodadas[rodada]

    fechamento = primeiro_jogo - timedelta(minutes=30)

    return agora < fechamento