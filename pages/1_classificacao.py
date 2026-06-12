import pandas as pd
import plotly.express as px
import streamlit as st
from services.google_sheets import (ler_classificacao,ler_extrato)
from utils.visual import aplicar_visual
from services.api_copa import buscar_rodada_atual

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================

st.set_page_config(
    page_title="BOLULA 3ª EDIÇÃO",
    page_icon="🏆",
    layout="wide"
)
aplicar_visual()

rodada_atual = buscar_rodada_atual()

st.markdown(
    "<div style='height: 24px;'></div>",
    unsafe_allow_html=True
)

if rodada_atual is not None:    
        
    st.info( f"🏆 Rodada atual: {rodada_atual}")

# ==================================================
# AJUSTES VISUAIS
# ==================================================

# ==================================================
# AJUSTES VISUAIS DA PÁGINA
# ==================================================

st.markdown(
    """
    <style>

    .metric-card {
        padding: 22px;
        color: #FAFAFA;
        border-radius: 16px;
        background: linear-gradient(135deg, #0B1F3A, #102A4C);
        border: 1px solid #1E3A5F;
        min-height: 185px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.25);
    }

    .metric-card h4 {
        color: #F4C542;
        font-size: 1.1rem;
        margin-bottom: 28px;
    }

    .metric-card h2 {
        color: #FFFFFF;
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .metric-card p {
        color: #D1D5DB;
        font-size: 1rem;
    }

    .stat-card {
        background: linear-gradient(135deg, #0B1F3A, #123B63);
        border: 1px solid #1E3A5F;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 18px;
        color: #FAFAFA;
        box-shadow: 0 8px 20px rgba(0,0,0,0.22);
    }

    .stat-card p {
        color: #D1D5DB;
        font-size: 1rem;
        margin: 0;
    }

    .stat-card strong {
        color: #00A651;
        font-size: 1.1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# LEITURA DE DADOS
# ==================================================

classificacao = ler_classificacao()

jogos = ler_extrato()

if classificacao.empty or jogos.empty:

    st.warning(
        "Ainda não há classificação disponível."
    )

    st.stop()
    
classificacao["posicao"] = classificacao["posicao"].astype(int)

classificacao["pontos"] = classificacao["pontos"].astype(int)

jogos["rodada"] = jogos["rodada"].astype(int)

jogos["pontos"] = jogos["pontos"].astype(int)


# ==================================================
# MÉTRICAS
# ==================================================

lider = classificacao.iloc[0]["participante"]

pontos_lider = classificacao.iloc[0]["pontos"]

qtd_participantes = classificacao["participante"].nunique()

qtd_jogos = jogos["jogo"].nunique()

placar_exatos = (
    jogos[jogos["criterios"] == "placar_exato"]
    .groupby("participante")
    .size()
    .reset_index(name="quantidade")
    .sort_values(by="quantidade", ascending=False)
)

melhor_rodada = (
    jogos
    .groupby(["rodada", "participante"])["pontos"]
    .sum()
    .reset_index()
    .sort_values(by="pontos", ascending=False)
)

media_acerto = jogos[jogos["criterios"] == "placar_exato"].shape[0]

total_jogos = jogos.shape[0]

percentual_acerto = round(
    (media_acerto / total_jogos) * 100,
    1
)

melhorRodada_participante = melhor_rodada.iloc[0]["participante"]

melhorRodada_pontos = melhor_rodada.iloc[0]["pontos"]

melhorRodada_numero = melhor_rodada.iloc[0]["rodada"]

if placar_exatos.empty:

    mais_placares = "-"

    qtd_placares = 0

else:

    mais_placares = placar_exatos.iloc[0]["participante"]

    qtd_placares = placar_exatos.iloc[0]["quantidade"]


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:


    st.markdown(
        """
<div class="sidebar-footer">
    <div class="sidebar-footer-title">
        🏆 BOLULA
    </div>
    <div class="sidebar-footer-subtitle">
        3ª Edição • Copa do Mundo 2026
    </div>
</div>
""",
        unsafe_allow_html=True
    )


# ==================================================
# DASHBOARD
# ==================================================

card1, card2, card3 = st.columns(3)

with card1:

    st.markdown(
        f"""
        <div class="metric-card">
            <h4>🥇 Líder Atual</h4>
            <h2>{lider}</h2>
            <p>{pontos_lider} pontos</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with card2:

    st.markdown(
        f"""
        <div class="metric-card">
            <h4>⚽ Jogos</h4>
            <h2>{qtd_jogos}</h2>
            <p>jogos disputados</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with card3:

    st.markdown(
        f"""
        <div class="metric-card">
            <h4>👥 Participantes</h4>
            <h2>{qtd_participantes}</h2>
            <p>no bolão</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")


# ==================================================
# LAYOUT PRINCIPAL
# ==================================================

df = (
    classificacao
    .sort_values(
        by="pontos",
        ascending=False
    )
    .head(10)
)

col_grafico, col_stats = st.columns([3, 1])


# ==================================================
# GRÁFICO
# ==================================================

with col_grafico:

    st.subheader("📊 Classificação Geral")

    fig = px.bar(
        df,
        x="pontos",
        y="participante",
        orientation="h",
        text="pontos"
    )

    fig.update_layout(
        height=420,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        plot_bgcolor="#081426",
        paper_bgcolor="#081426",
        font=dict(
            size=14,
            color="#FAFAFA"
        ),
        margin=dict(l=20, r=40, t=20, b=20)
    )

    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        color="#FAFAFA"
    )

    fig.update_yaxes(
        categoryorder="total ascending",
        tickfont=dict(
            size=15,
            color="#FAFAFA"
        ),
        showgrid=False
    )

    fig.update_traces(
        marker_color="#00A651",
        textposition="outside",
        textfont=dict(
            size=14,
            color="#F4C542"
        ),
        width=0.45
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ==================================================
# ESTATÍSTICAS
# ==================================================

with col_stats:

    st.subheader("📌 Estatísticas")

    st.markdown(
        f"""
        <div class="stat-card">
            <p>🔥 Mais placares exatos</p>
            <strong>{mais_placares} • {qtd_placares}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat-card">
            <p>⚽ Melhor rodada</p>
            <strong>{melhorRodada_participante} • {melhorRodada_pontos} pts na {melhorRodada_numero}ª rodada</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="stat-card">
            <p>📈 Média de acertos</p>
            <strong>{percentual_acerto}%</strong>
        </div>
        """,
        unsafe_allow_html=True
    )
st.subheader("Classificação Completa",divider="rainbow")

classificacao_exibicao = classificacao.rename(
    columns={
        "posicao":"Posição",
        "participante":"Participante",
        "pontos":"Pontos"
    }
)


st.dataframe(
    classificacao_exibicao,width="stretch",hide_index=True
)