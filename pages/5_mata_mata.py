import streamlit as st
import pandas as pd

from utils.visual import (
    aplicar_visual,
    exibir_rodape_sidebar
)

from services.api_copa import (
    traduzir_stage
)

from services.google_sheets import (
    ler_jogos_fase,
    salvar_ou_atualizar_palpites_mata_mata,
    buscar_palpites_mata_mata_participante_fase
)


# ==========================================
# USUÁRIOS
# ==========================================

USUARIOS = dict(
    st.secrets["usuarios"]
)


# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Palpites Mata-mata",
    page_icon="🥅",
    layout="wide"
)

aplicar_visual()
exibir_rodape_sidebar()


# ==========================================
# ESTADO DA SESSÃO
# ==========================================

# Reaproveitamos as mesmas chaves da página
# atual de envio de palpites.
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "mensagem_sucesso_mata_mata" not in st.session_state:
    st.session_state.mensagem_sucesso_mata_mata = None


# ==========================================
# TÍTULO
# ==========================================

st.title(
    "🥅 Envio de Palpites — Mata-mata"
)

st.divider()


# ==========================================
# LOGIN
# ==========================================

if not st.session_state.autenticado:

    st.subheader(
        "🔐 Login"
    )

    participante = st.selectbox(
        "Participante",
        list(USUARIOS.keys()),
        key="login_participante_mata_mata"
    )

    senha = st.text_input(
        "Senha",
        type="password",
        key="login_senha_mata_mata"
    )

    if st.button(
        "Entrar",
        key="entrar_mata_mata"
    ):

        if USUARIOS[participante] == senha:

            st.session_state.autenticado = True
            st.session_state.usuario = participante

            st.success(
                "Login realizado com sucesso!"
            )

            st.rerun()

        else:

            st.error(
                "Senha inválida."
            )


# ==========================================
# CONTEÚDO AUTENTICADO
# ==========================================

else:

    usuario = st.session_state.usuario

    st.success(
        f"✅ Logada como: {usuario}"
    )

    if st.session_state.mensagem_sucesso_mata_mata:

        st.success(
            st.session_state.mensagem_sucesso_mata_mata,
            icon="✅"
        )

        st.session_state.mensagem_sucesso_mata_mata = None

    st.divider()

    # ==========================================
    # CONTROLE MANUAL
    # ==========================================

    # Durante os primeiros testes, manteremos
    # o controle manual da fase.
    FASE_ABERTA = "SEMI_FINALS"

    # Como essa alteração ainda está apenas
    # no ambiente local, deixaremos aberto
    # para os testes.
    ENVIO_ABERTO = False

    nome_fase = traduzir_stage(
        FASE_ABERTA
    )

    # ==========================================
    # CARREGAR JOGOS DA ABA JOGOS
    # ==========================================

    try:

        df_fase = ler_jogos_fase(
            FASE_ABERTA
        )

    except Exception as erro:

        st.error(
            "Não foi possível carregar os jogos do mata-mata. "
            "Verifique a aba JOGOS no Google Sheets."
        )

        st.exception(
            erro
        )

        st.stop()

    if df_fase.empty:

        st.warning(
            "Ainda não existem confrontos completos cadastrados "
            "para esta fase."
        )

        st.stop()

    st.subheader(
        f"Fase: {nome_fase}"
    )

    st.write(
        f"Quantidade de confrontos disponíveis: {len(df_fase)}"
    )

    TOTAL_JOGOS_FASE = 2

    if len(df_fase) < TOTAL_JOGOS_FASE:

        st.warning(
            f"⚠️ Neste momento, {len(df_fase)} dos "
            f"{TOTAL_JOGOS_FASE} confrontos desta fase "
            "já estão definidos. Os demais jogos serão "
            "adicionados conforme a classificação for confirmada. "
            "Será necessário retornar a esta página para "
            "preencher os novos confrontos."
        )


    # ==========================================
    # PALPITES EXISTENTES
    # ==========================================

    try:

        palpites_existentes = (
            buscar_palpites_mata_mata_participante_fase(
                usuario,
                FASE_ABERTA
            )
        )

    except Exception as erro:

        st.error(
            "Não foi possível carregar seus palpites no momento. "
            "Aguarde alguns segundos e tente novamente."
        )

        st.exception(
            erro
        )

        st.stop()

    ja_enviou = bool(
        palpites_existentes
    )

    # ==========================================
    # PRAZO ENCERRADO
    # ==========================================

    if not ENVIO_ABERTO:

        st.warning(
            "O prazo para envio ou edição dos palpites "
            "desta fase foi encerrado."
        )

        st.divider()

        if st.button(
            "Sair",
            key="sair_mata_mata_fechado"
        ):

            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.mensagem_sucesso_mata_mata = None

            st.rerun()

        st.stop()

    # ==========================================
    # INFORMAÇÕES
    # ==========================================

    if ja_enviou:

        st.info(
            "Você já enviou palpites para esta fase. "
            "É possível editar e reenviar enquanto "
            "o prazo estiver aberto."
        )

    else:

        st.success(
            "Você ainda não enviou seus palpites "
            "para esta fase."
        )

    st.warning(
        "⚠️ Informe o placar do tempo regulamentar, "
        "incluindo os acréscimos. Depois escolha quem "
        "vencerá caso a partida seja decidida nos pênaltis."
    )

    st.caption(
        "O placar dos pênaltis não deve ser informado. "
        "É necessário escolher apenas a seleção vencedora."
    )

    st.divider()

    # ==========================================
    # FORMULÁRIO DE PALPITES
    # ==========================================

    palpites_usuario = []

    with st.form(
        key=f"form_mata_mata_{usuario}_{FASE_ABERTA}"
    ):

        st.subheader(
            "Preencha seus palpites"
        )

        for _, linha in df_fase.iterrows():

            jogo_id = int(
                linha["jogo_id"]
            )

            time_casa = str(
                linha["time_casa"]
            ).strip()

            time_fora = str(
                linha["time_fora"]
            ).strip()

            palpite_existente = palpites_existentes.get(
                jogo_id,
                {
                    "palpite_a": 0,
                    "palpite_b": 0,
                    "vencedor_penaltis": ""
                }
            )

            st.markdown(
                f"### {time_casa} x {time_fora}"
            )

            col1, col2, col3 = st.columns(
                [1, 0.3, 1]
            )

            with col1:

                gols_casa = st.number_input(
                    time_casa,
                    min_value=0,
                    max_value=20,
                    value=int(
                        palpite_existente["palpite_a"]
                    ),
                    step=1,
                    key=(
                        f"mata_casa_"
                        f"{usuario}_{jogo_id}"
                    )
                )

            with col2:

                st.markdown(
                    "<h3 style='text-align:center;'>x</h3>",
                    unsafe_allow_html=True
                )

            with col3:

                gols_fora = st.number_input(
                    time_fora,
                    min_value=0,
                    max_value=20,
                    value=int(
                        palpite_existente["palpite_b"]
                    ),
                    step=1,
                    key=(
                        f"mata_fora_"
                        f"{usuario}_{jogo_id}"
                    )
                )

            opcoes_vencedor = [
                "Selecione uma seleção",
                time_casa,
                time_fora
            ]

            vencedor_existente = str(
                palpite_existente.get(
                    "vencedor_penaltis",
                    ""
                )
            ).strip()

            if vencedor_existente in opcoes_vencedor:

                indice_vencedor = opcoes_vencedor.index(
                    vencedor_existente
                )

            else:

                indice_vencedor = 0

            vencedor_penaltis = st.selectbox(
                "Se a partida for para os pênaltis, quem vence?",
                options=opcoes_vencedor,
                index=indice_vencedor,
                key=(
                    f"mata_vencedor_"
                    f"{usuario}_{jogo_id}"
                )
            )

            palpites_usuario.append(
                {
                    "participante": usuario,
                    "fase": FASE_ABERTA,
                    "jogo_id": jogo_id,
                    "time_casa": time_casa,
                    "time_fora": time_fora,
                    "palpite_a": int(gols_casa),
                    "palpite_b": int(gols_fora),
                    "vencedor_penaltis": (
                        ""
                        if vencedor_penaltis
                        == "Selecione uma seleção"
                        else vencedor_penaltis
                    )
                }
            )

            st.divider()

        enviar = st.form_submit_button(
            "📤 Enviar Palpites do Mata-mata",
            use_container_width=True
        )

    # ==========================================
    # SALVAR
    # ==========================================

    if enviar:

        palpites_sem_vencedor = [
            palpite
            for palpite in palpites_usuario
            if not palpite["vencedor_penaltis"]
        ]

        if palpites_sem_vencedor:

            st.error(
                "Selecione o possível vencedor dos pênaltis "
                "em todos os confrontos antes de enviar."
            )

            st.stop()

        df_envio = pd.DataFrame(
            palpites_usuario
        )

        try:

            salvar_ou_atualizar_palpites_mata_mata(
                df_envio,
                usuario,
                FASE_ABERTA
            )

        except Exception as erro:

            st.error(
                "Não foi possível salvar seus palpites agora. "
                "Aguarde alguns segundos e tente novamente."
            )

            st.exception(
                erro
            )

            st.stop()

        quantidade_palpites = len(df_envio)

        st.session_state.mensagem_sucesso_mata_mata = (
            f"Palpites enviados com sucesso! "
            f"Foram salvos {quantidade_palpites} confrontos. "
            "Você pode retornar e editar enquanto o prazo estiver aberto."
        )

        st.rerun()



    # ==========================================
    # LOGOUT
    # ==========================================

    st.divider()

    if st.button(
        "Sair",
        key="sair_mata_mata"
    ):

        st.session_state.autenticado = False
        st.session_state.usuario = None

        st.rerun()