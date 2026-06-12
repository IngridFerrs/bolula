import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import requests
import pandas as pd

from services.google_sheets import salvar_resultados


# ==========================================
# CONFIGURAÇÕES
# ==========================================

RODADA = int(input("Digite a rodada da Copa: "))

API_KEY = "6c4d31443b4d4348a2e53a6c48f786f6"

COMPETICAO = "WC"

STATUS = "SCHEDULED"

# ==========================================
# CABEÇALHO
# ==========================================

headers = {
    "X-Auth-Token": API_KEY
}

# ==========================================
# URL DA API
# ==========================================

url = (
    f"https://api.football-data.org/v4/"
    f"competitions/{COMPETICAO}/matches"
    #f"?status={STATUS}"
)

# ==========================================
# REQUISIÇÃO
# ==========================================

response = requests.get(
    url,
    headers=headers
)

# ==========================================
# VALIDAR RESPOSTA
# ==========================================

print("\nSTATUS DA API:\n")

print(response.status_code)

# ==========================================
# JSON
# ==========================================

dados = response.json()

# ==========================================
# PEGAR JOGOS
# ==========================================

jogos = dados["matches"]

print("\nQUANTIDADE DE JOGOS:\n")

print(len(jogos))

# ==========================================
# LISTA FINAL
# ==========================================

lista_jogos = []

# ==========================================
# LOOP DOS JOGOS
# ==========================================

for jogo in jogos:

    # --------------------------------------
    # TIMES
    # --------------------------------------

    time_casa = jogo["homeTeam"]["shortName"]

    time_fora = jogo["awayTeam"]["shortName"]

    # --------------------------------------
    # PLACAR
    # --------------------------------------

    gols_casa = jogo["score"]["fullTime"]["home"]

    gols_fora = jogo["score"]["fullTime"]["away"]

    # --------------------------------------
    # RODADA
    # --------------------------------------

    rodada = jogo["matchday"]

    if rodada != RODADA:
        continue

    # --------------------------------------
    # ID DO JOGO
    # --------------------------------------

    jogo_id = jogo["id"]

    # --------------------------------------
    # MOSTRAR NO TERMINAL
    # --------------------------------------

    print(
        rodada,
        "-",
        time_casa,
        gols_casa,
        "x",
        gols_fora,
        time_fora
    )

    # --------------------------------------
    # DICIONÁRIO
    # --------------------------------------

    dados_jogo = {

        "rodada": rodada,

        "jogo_id": jogo_id,

        "time_casa": time_casa,

        "time_fora": time_fora,

        "gols_casa": gols_casa,

        "gols_fora": gols_fora
    }

    # --------------------------------------
    # ADICIONAR NA LISTA
    # --------------------------------------

    lista_jogos.append(dados_jogo)

# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(lista_jogos)

# ==========================================
# MOSTRAR DATAFRAME
# ==========================================

print("\nDATAFRAME FINAL:\n")

print(df)

# ==========================================
# EXPORTAR EXCEL
# ==========================================

df = df.dropna(
    subset=[
        "gols_casa",
        "gols_fora"
    ]
)

salvar_resultados(df)

print("\nRESULTADOS SALVOS NO GOOGLE SHEETS COM SUCESSO!")