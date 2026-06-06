import pandas as pd
import streamlit as st
from utils.visual import aplicar_visual
from utils.visual import (aplicar_visual,exibir_rodape_sidebar)
from services.google_sheets import ler_resultados

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Jogoss",
    page_icon="⚽",
    layout="wide"
)
aplicar_visual() 
exibir_rodape_sidebar()

st.title("⚽ Jogos da Copa")

st.divider()

# ==========================================
# BANDEIRAS
# ==========================================

CODIGOS_BANDEIRAS = {
    "Algeria": "dz",
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Bosnia-H.": "ba",
    "Brazil": "br",
    "Canada": "ca",
    "Cape Verde": "cv",
    "Colombia": "co",
    "Croatia": "hr",
    "Czechia": "cz",
    "Ecuador": "ec",
    "Egypt": "eg",
    "England": "gb-eng",
    "France": "fr",
    "Germany": "de",
    "Ghana": "gh",
    "Haiti": "ht",
    "Iran": "ir",
    "Ivory Coast": "ci",
    "Japan": "jp",
    "Korea Republic": "kr",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Panama": "pa",
    "Paraguay": "py",
    "Portugal": "pt",
    "Qatar": "qa",
    "Saudi Arabia": "sa",
    "Scotland": "gb-sct",
    "Senegal": "sn",
    "South Africa": "za",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Tunisia": "tn",
    "Turkey": "tr",
    "Uruguay": "uy",
    "USA": "us",
}


def bandeira_img(time):

    codigo = CODIGOS_BANDEIRAS.get(
        str(time).strip()
    )

    if not codigo:
        return ""

    return (
        f"<img src='https://flagcdn.com/32x24/{codigo}.png' "
        f"style='vertical-align:middle; margin-right:8px; border-radius:3px;'>"
    )


# ==========================================
# LER RESULTADOS
# ==========================================

jogos = ler_resultados()

if jogos.empty:

    st.warning(
        "Nenhum jogo encontrado até o momento."
    )

    st.stop()
jogos["rodada"] = jogos["rodada"].astype(int)

jogos["gols_casa"] = pd.to_numeric(
    jogos["gols_casa"],
    errors="coerce"
)

jogos["gols_fora"] = pd.to_numeric(
    jogos["gols_fora"],
    errors="coerce"
)
# ==========================================
# FILTRO DE RODADA
# ==========================================

rodadas = sorted(
    jogos["rodada"].dropna().unique()
)

rodada_selecionada = st.selectbox(
    "Selecione a rodada",
    rodadas
)

jogos_rodada = jogos[
    jogos["rodada"] == rodada_selecionada
].copy()

# ==========================================
# ESTILO DOS CARDS
# ==========================================

st.markdown(
    """
    <style>
    .card-jogo {
        background-color: linear-gradient(135deg, #0B1F3A, #102A4C);
        border: 1px solid #e6e6e6;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }

    .linha-jogo {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .time {
        font-size: 20px;
        font-weight: 600;
        width: 35%;
    }

    .placar {
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        width: 20%;
    }

    .rodada {
        color: #666;
        font-size: 14px;
        margin-top: 8px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# EXIBIR JOGOS
# ==========================================

st.subheader(
    f"Rodada {rodada_selecionada}"
)

for _, jogo in jogos_rodada.iterrows():

    time_casa = jogo["time_casa"]
    time_fora = jogo["time_fora"]

    gols_casa = jogo["gols_casa"]
    gols_fora = jogo["gols_fora"]

    if pd.isna(gols_casa) or pd.isna(gols_fora):

        placar = "x"

    else:

        placar = f"{int(gols_casa)} x {int(gols_fora)}"

    st.markdown(
        f"""
        <div class="card-jogo">
            <div class="linha-jogo">
                <div class="time">{bandeira_img(time_casa)} {time_casa}</div>
                <div class="placar">{placar}</div>
                <div class="time" style="text-align:right;">{bandeira_img(time_fora)} {time_fora}</div>
            </div>
            <div class="rodada">Rodada {int(jogo["rodada"])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
