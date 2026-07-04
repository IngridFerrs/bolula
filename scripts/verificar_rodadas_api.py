import requests
import streamlit as st
import pandas as pd

API_KEY = st.secrets["API_KEY"]
COMPETICAO = "WC"

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

lista = []

for jogo in dados["matches"]:

    lista.append(
        {
            "matchday": jogo.get("matchday"),
            "stage": jogo.get("stage"),
            "jogo_id": jogo.get("id"),
            "time_casa": jogo["homeTeam"].get("shortName"),
            "time_fora": jogo["awayTeam"].get("shortName"),
            "data": jogo.get("utcDate"),
            "status": jogo.get("status")
        }
    )

df = pd.DataFrame(lista)

print(
    df[
        [
            "matchday",
            "stage",
            "jogo_id",
            "time_casa",
            "time_fora",
            "data",
            "status"
        ]
    ].sort_values(
        by=[
            "matchday",
            "data"
        ],
        na_position="last"
    ).to_string()
)