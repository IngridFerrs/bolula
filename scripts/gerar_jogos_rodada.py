import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests

# ==========================================
# CONFIGURAÇÕES
# ==========================================

RODADA = int(input("Digite a rodada da Copa: "))

API_KEY = st.secrets["API_KEY"]
COMPETICAO = "WC"

headers = {
    "X-Auth-Token": API_KEY
}

url = (
    f"https://api.football-data.org/v4/"
    f"competitions/{COMPETICAO}/matches"
)

# ==========================================
# BUSCAR JOGOS NA API
# ==========================================

response = requests.get(url, headers=headers)

print("STATUS DA API:", response.status_code)

if response.status_code != 200:
    print("Erro ao consultar a API.")
    print(response.text)
    exit()

dados = response.json()
jogos_api = dados["matches"]

lista_jogos = []

for jogo in jogos_api:
    rodada = jogo["matchday"]

    if rodada != RODADA:
        continue

    lista_jogos.append(
        {
            "rodada": rodada,
            "jogo_id": jogo["id"],
            "time_casa": jogo["homeTeam"]["shortName"],
            "time_fora": jogo["awayTeam"]["shortName"],
        }
    )

df = pd.DataFrame(lista_jogos)

if df.empty:
    print(f"Nenhum jogo encontrado para a rodada {RODADA}.")
    exit()

# ==========================================
# SALVAR EXCEL
# ==========================================

arquivo_saida = f"dados/jogos_rodada_{RODADA}.xlsx"

df.to_excel(arquivo_saida, index=False)

print("\nPLANILHA DE JOGOS GERADA COM SUCESSO!")
print(f"Arquivo salvo em: {arquivo_saida}")
print("\nCopie essas colunas para a aba JOGOS:")
print(df)