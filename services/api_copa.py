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

def buscar_periodo_jogos_por_rodada():

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

    rodadas = {}

    for jogo in dados["matches"]:

        rodada = jogo["matchday"]

        if rodada is None:
            continue

        data_jogo = datetime.fromisoformat(
            jogo["utcDate"].replace(
                "Z",
                "+00:00"
            )
        )

        if rodada not in rodadas:

            rodadas[rodada] = {
                "primeiro_jogo": data_jogo,
                "ultimo_jogo": data_jogo
            }

        else:

            if data_jogo < rodadas[rodada]["primeiro_jogo"]:

                rodadas[rodada]["primeiro_jogo"] = data_jogo

            if data_jogo > rodadas[rodada]["ultimo_jogo"]:

                rodadas[rodada]["ultimo_jogo"] = data_jogo

    return rodadas

def buscar_periodo_jogos_por_rodada():

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

    rodadas = {}

    for jogo in dados["matches"]:

        rodada = jogo["matchday"]

        if rodada is None:
            continue

        data_jogo = datetime.fromisoformat(
            jogo["utcDate"].replace(
                "Z",
                "+00:00"
            )
        )

        if rodada not in rodadas:

            rodadas[rodada] = {
                "primeiro_jogo": data_jogo,
                "ultimo_jogo": data_jogo
            }

        else:

            if data_jogo < rodadas[rodada]["primeiro_jogo"]:

                rodadas[rodada]["primeiro_jogo"] = data_jogo

            if data_jogo > rodadas[rodada]["ultimo_jogo"]:

                rodadas[rodada]["ultimo_jogo"] = data_jogo

    return rodadas

def buscar_rodada_aberta():

    rodadas = buscar_periodo_jogos_por_rodada()

    agora = datetime.now(timezone.utc)

    for rodada, periodo in rodadas.items():

        primeiro_jogo = periodo["primeiro_jogo"]

        fechamento = primeiro_jogo - timedelta(
            minutes=30
        )

        if rodada == 1:

            abertura = primeiro_jogo - timedelta(
                hours=5
            )

        else:

            rodada_anterior = rodada - 1

            if rodada_anterior not in rodadas:

                continue

            ultimo_jogo_anterior = rodadas[
                rodada_anterior
            ]["ultimo_jogo"]

            abertura = (
                ultimo_jogo_anterior
                + timedelta(
                    hours=2,
                    minutes=40
                )
            )

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

    rodadas = buscar_periodo_jogos_por_rodada()

    if rodada not in rodadas:

        return False

    agora = datetime.now(timezone.utc)

    primeiro_jogo = rodadas[
        rodada
    ]["primeiro_jogo"]

    fechamento = primeiro_jogo - timedelta(
        minutes=30
    )

    return agora < fechamento

def buscar_rodada_atual():

    rodadas = buscar_primeiro_jogo_por_rodada()

    agora = datetime.now(timezone.utc)

    rodada_atual = None

    for rodada, primeiro_jogo in rodadas.items():

        if agora >= primeiro_jogo:

            rodada_atual = rodada

    return rodada_atual

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

def traduzir_stage(stage):

    mapa = {
        "LAST_32": "16-avos de final",
        "LAST_16": "Oitavas de final",
        "QUARTER_FINALS": "Quartas de final",
        "SEMI_FINALS": "Semifinais",
        "THIRD_PLACE": "Disputa do 3º lugar",
        "FINAL": "Final"
    }

    return mapa.get(stage, stage)
def buscar_fase_mata_mata_atual():

    headers = {
        "X-Auth-Token": API_KEY
    }

    url = (
        f"https://api.football-data.org/v4/"
        f"competitions/{COMPETICAO}/matches"
    )

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as erro:

        print(
            "\nERRO AO CONSULTAR FASE ATUAL DO MATA-MATA:\n"
        )

        print(erro)

        return None

    dados = response.json()

    if "matches" not in dados:

        print("\nERRO NA API:\n")
        print(dados)

        return None

    ordem_fases = {
        "LAST_32": 1,
        "LAST_16": 2,
        "QUARTER_FINALS": 3,
        "SEMI_FINALS": 4,
        "THIRD_PLACE": 5,
        "FINAL": 6
    }

    fases_encontradas = {}

    for jogo in dados["matches"]:

        stage = str(
            jogo.get("stage") or ""
        ).strip().upper()

        if stage not in ordem_fases:
            continue

        time_casa = (
            jogo.get("homeTeam", {}).get("shortName")
            or jogo.get("homeTeam", {}).get("name")
        )

        time_fora = (
            jogo.get("awayTeam", {}).get("shortName")
            or jogo.get("awayTeam", {}).get("name")
        )

        if not time_casa or not time_fora:
            continue

        status = str(
            jogo.get("status") or ""
        ).strip().upper()

        if stage not in fases_encontradas:

            fases_encontradas[stage] = {
                "total": 0,
                "finalizados": 0
            }

        fases_encontradas[stage]["total"] += 1

        if status == "FINISHED":

            fases_encontradas[stage]["finalizados"] += 1

    if not fases_encontradas:

        return None

    fases_nao_finalizadas = [
        fase
        for fase, dados_fase in fases_encontradas.items()
        if dados_fase["finalizados"] < dados_fase["total"]
    ]

    if fases_nao_finalizadas:

        return max(
            fases_nao_finalizadas,
            key=lambda fase: ordem_fases[fase]
        )

    return max(
        fases_encontradas.keys(),
        key=lambda fase: ordem_fases[fase]
    )


def buscar_texto_rodada_atual():

    fase_mata_mata = buscar_fase_mata_mata_atual()

    if fase_mata_mata:

        return traduzir_stage(
            fase_mata_mata
        )

    rodada = buscar_rodada_atual()

    if rodada is None:

        return "Aguardando início"

    return f"Rodada {rodada}"


def buscar_jogos_fase(stage_desejado):

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

    lista_jogos = []

    for jogo in dados["matches"]:

        stage = jogo["stage"]

        if stage != stage_desejado:
            continue

        time_casa = jogo["homeTeam"]["shortName"]
        time_fora = jogo["awayTeam"]["shortName"]

        if time_casa is None or time_fora is None:
            continue

        lista_jogos.append(
            {
                "fase": stage,
                "fase_nome": traduzir_stage(stage),
                "jogo_id": jogo["id"],
                "time_casa": time_casa,
                "time_fora": time_fora,
                "data": jogo["utcDate"]
            }
        )

    return pd.DataFrame(lista_jogos)

COLUNAS_RESULTADOS_MATA_MATA = [
    "fase",
    "jogo_id",
    "time_casa",
    "time_fora",
    "gols_casa_90",
    "gols_fora_90",
    "duracao",
    "vencedor_penaltis"
]


def dataframe_resultados_mata_mata_vazio():

    return pd.DataFrame(
        columns=COLUNAS_RESULTADOS_MATA_MATA
    )

def obter_nome_time(dados_time):

    if not dados_time:
        return None

    return (
        dados_time.get("shortName")
        or dados_time.get("name")
    )
def obter_gols_placar(placar, lado):

    if not placar:
        return None

    if lado == "casa":

        valor = placar.get("home")

        if valor is None:
            valor = placar.get("homeTeam")

        return valor

    if lado == "fora":

        valor = placar.get("away")

        if valor is None:
            valor = placar.get("awayTeam")

        return valor

    raise ValueError(
        "O lado deve ser 'casa' ou 'fora'."
    )
def obter_vencedor_penaltis(
    duracao,
    vencedor_api,
    time_casa,
    time_fora
):

    duracao = str(
        duracao or ""
    ).strip().upper()

    vencedor_api = str(
        vencedor_api or ""
    ).strip().upper()

    if duracao != "PENALTY_SHOOTOUT":
        return ""

    if vencedor_api == "HOME_TEAM":
        return time_casa

    if vencedor_api == "AWAY_TEAM":
        return time_fora

    return ""
def buscar_resultados_fase(stage_desejado):

    headers = {
        "X-Auth-Token": API_KEY
    }

    url = (
        f"https://api.football-data.org/v4/"
        f"competitions/{COMPETICAO}/matches"
    )

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as erro:

        print(
            "\nERRO AO CONSULTAR RESULTADOS DA API:\n"
        )

        print(erro)

        return dataframe_resultados_mata_mata_vazio()

    try:

        dados = response.json()

    except ValueError:

        print(
            "\nA API retornou uma resposta inválida.\n"
        )

        return dataframe_resultados_mata_mata_vazio()

    if "matches" not in dados:

        print(
            "\nERRO NA RESPOSTA DA API:\n"
        )

        print(dados)

        return dataframe_resultados_mata_mata_vazio()

    stage_desejado = str(
        stage_desejado
    ).strip().upper()

    lista_resultados = []

    jogos_da_fase = 0
    jogos_finalizados = 0

    for jogo in dados["matches"]:

        fase = str(
            jogo.get("stage") or ""
        ).strip().upper()

        if fase != stage_desejado:
            continue

        jogos_da_fase += 1

        status = str(
            jogo.get("status") or ""
        ).strip().upper()

        if status != "FINISHED":
            continue

        jogos_finalizados += 1

        time_casa = obter_nome_time(
            jogo.get("homeTeam")
        )

        time_fora = obter_nome_time(
            jogo.get("awayTeam")
        )

        if not time_casa or not time_fora:

            print(
                "Jogo ignorado por não possuir "
                f"os dois times definidos: {jogo.get('id')}"
            )

            continue

        score = jogo.get("score") or {}

        duracao = str(
            score.get("duration") or ""
        ).strip().upper()

        vencedor_api = str(
            score.get("winner") or ""
        ).strip().upper()

        regular_time = (
            score.get("regularTime")
            or {}
        )

        full_time = (
            score.get("fullTime")
            or {}
        )

        # ------------------------------------------
        # PLACAR DOS 90 MINUTOS
        # ------------------------------------------

        if duracao == "REGULAR":

            # Em jogos encerrados nos 90 minutos,
            # tenta regularTime e usa fullTime
            # como alternativa.
            gols_casa_90 = obter_gols_placar(
                regular_time,
                "casa"
            )

            gols_fora_90 = obter_gols_placar(
                regular_time,
                "fora"
            )

            if (
                gols_casa_90 is None
                or gols_fora_90 is None
            ):

                gols_casa_90 = obter_gols_placar(
                    full_time,
                    "casa"
                )

                gols_fora_90 = obter_gols_placar(
                    full_time,
                    "fora"
                )

        elif duracao in {
            "EXTRA_TIME",
            "PENALTY_SHOOTOUT"
        }:

            # Quando houve prorrogação ou pênaltis,
            # não usamos fullTime.
            # Precisamos obrigatoriamente do placar
            # dos 90 minutos.
            gols_casa_90 = obter_gols_placar(
                regular_time,
                "casa"
            )

            gols_fora_90 = obter_gols_placar(
                regular_time,
                "fora"
            )

        else:

            print(
                "Jogo ignorado por apresentar "
                f"duração desconhecida: "
                f"{jogo.get('id')} - {duracao}"
            )

            continue

        if (
            gols_casa_90 is None
            or gols_fora_90 is None
        ):

            print(
                "Jogo ignorado porque o placar "
                f"dos 90 minutos não está disponível: "
                f"{jogo.get('id')}"
            )

            continue

        vencedor_penaltis = obter_vencedor_penaltis(
            duracao,
            vencedor_api,
            time_casa,
            time_fora
        )

        lista_resultados.append(
            {
                "fase": fase,
                "jogo_id": int(jogo["id"]),
                "time_casa": str(time_casa).strip(),
                "time_fora": str(time_fora).strip(),
                "gols_casa_90": int(gols_casa_90),
                "gols_fora_90": int(gols_fora_90),
                "duracao": duracao,
                "vencedor_penaltis": vencedor_penaltis
            }
        )

    print(
        f"\nJogos encontrados em {stage_desejado}: "
        f"{jogos_da_fase}"
    )

    print(
        f"Jogos finalizados: {jogos_finalizados}"
    )

    print(
        "Resultados válidos para o Bolula: "
        f"{len(lista_resultados)}"
    )

    return pd.DataFrame(
        lista_resultados,
        columns=COLUNAS_RESULTADOS_MATA_MATA
    )