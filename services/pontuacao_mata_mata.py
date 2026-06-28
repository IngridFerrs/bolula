import pandas as pd


COLUNAS_EXTRATO_MATA_MATA = [
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


def dataframe_extrato_vazio():

    return pd.DataFrame(
        columns=COLUNAS_EXTRATO_MATA_MATA
    )


def normalizar_texto(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    return str(
        valor
    ).strip().casefold()


def identificar_resultado(
    gols_casa,
    gols_fora
):

    if gols_casa > gols_fora:
        return "CASA"

    if gols_fora > gols_casa:
        return "FORA"

    return "EMPATE"


def calcular_pontos_base(
    palpite_a,
    palpite_b,
    gols_casa_90,
    gols_fora_90
):

    palpite_a = int(palpite_a)
    palpite_b = int(palpite_b)
    gols_casa_90 = int(gols_casa_90)
    gols_fora_90 = int(gols_fora_90)

    # 5 pontos: placar exato.
    if (
        palpite_a == gols_casa_90
        and palpite_b == gols_fora_90
    ):
        return 5

    resultado_palpite = identificar_resultado(
        palpite_a,
        palpite_b
    )

    resultado_real = identificar_resultado(
        gols_casa_90,
        gols_fora_90
    )

    # 3 pontos: vencedor ou empate correto.
    if resultado_palpite == resultado_real:
        return 3

    total_palpite = (
        palpite_a
        + palpite_b
    )

    total_real = (
        gols_casa_90
        + gols_fora_90
    )

    # 1 ponto: total de gols correto.
    if total_palpite == total_real:
        return 1

    return 0


def calcular_bonus_penaltis(
    duracao,
    vencedor_palpitado,
    vencedor_real
):

    duracao_normalizada = normalizar_texto(
        duracao
    )

    if duracao_normalizada != "penalty_shootout":
        return 0

    vencedor_palpitado = normalizar_texto(
        vencedor_palpitado
    )

    vencedor_real = normalizar_texto(
        vencedor_real
    )

    if not vencedor_palpitado:
        return 0

    if not vencedor_real:
        return 0

    if vencedor_palpitado == vencedor_real:
        return 1

    return 0


def calcular_extrato_mata_mata(
    df_palpites,
    df_resultados
):

    if df_palpites is None or df_palpites.empty:
        return dataframe_extrato_vazio()

    if df_resultados is None or df_resultados.empty:
        return dataframe_extrato_vazio()

    colunas_palpites = {
        "participante",
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b",
        "vencedor_penaltis"
    }

    colunas_resultados = {
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "gols_casa_90",
        "gols_fora_90",
        "duracao",
        "vencedor_penaltis"
    }

    faltantes_palpites = (
        colunas_palpites
        - set(df_palpites.columns)
    )

    if faltantes_palpites:

        raise ValueError(
            "Faltam colunas em PALPITES_MATA_MATA: "
            + ", ".join(
                sorted(faltantes_palpites)
            )
        )

    faltantes_resultados = (
        colunas_resultados
        - set(df_resultados.columns)
    )

    if faltantes_resultados:

        raise ValueError(
            "Faltam colunas em RESULTADOS_MATA_MATA: "
            + ", ".join(
                sorted(faltantes_resultados)
            )
        )

    palpites = df_palpites.copy()
    resultados = df_resultados.copy()

    palpites["fase"] = (
        palpites["fase"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    resultados["fase"] = (
        resultados["fase"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    palpites["jogo_id"] = pd.to_numeric(
        palpites["jogo_id"],
        errors="coerce"
    )

    resultados["jogo_id"] = pd.to_numeric(
        resultados["jogo_id"],
        errors="coerce"
    )

    palpites["palpite_a"] = pd.to_numeric(
        palpites["palpite_a"],
        errors="coerce"
    )

    palpites["palpite_b"] = pd.to_numeric(
        palpites["palpite_b"],
        errors="coerce"
    )

    resultados["gols_casa_90"] = pd.to_numeric(
        resultados["gols_casa_90"],
        errors="coerce"
    )

    resultados["gols_fora_90"] = pd.to_numeric(
        resultados["gols_fora_90"],
        errors="coerce"
    )

    palpites = palpites.dropna(
        subset=[
            "jogo_id",
            "palpite_a",
            "palpite_b"
        ]
    )

    resultados = resultados.dropna(
        subset=[
            "jogo_id",
            "gols_casa_90",
            "gols_fora_90"
        ]
    )

    palpites["jogo_id"] = (
        palpites["jogo_id"]
        .astype(int)
    )

    resultados["jogo_id"] = (
        resultados["jogo_id"]
        .astype(int)
    )

    palpites["palpite_a"] = (
        palpites["palpite_a"]
        .astype(int)
    )

    palpites["palpite_b"] = (
        palpites["palpite_b"]
        .astype(int)
    )

    resultados["gols_casa_90"] = (
        resultados["gols_casa_90"]
        .astype(int)
    )

    resultados["gols_fora_90"] = (
        resultados["gols_fora_90"]
        .astype(int)
    )

    # Proteção contra resultados duplicados.
    resultados = resultados.drop_duplicates(
        subset=[
            "fase",
            "jogo_id"
        ],
        keep="last"
    )

    dados = palpites.merge(
        resultados,
        on=[
            "fase",
            "jogo_id"
        ],
        how="inner",
        suffixes=(
            "_palpite",
            "_resultado"
        )
    )

    if dados.empty:
        return dataframe_extrato_vazio()

    linhas_extrato = []

    for _, linha in dados.iterrows():

        pontos_base = calcular_pontos_base(
            linha["palpite_a"],
            linha["palpite_b"],
            linha["gols_casa_90"],
            linha["gols_fora_90"]
        )

        bonus_penaltis = calcular_bonus_penaltis(
            linha["duracao"],
            linha["vencedor_penaltis_palpite"],
            linha["vencedor_penaltis_resultado"]
        )

        pontos_total = (
            pontos_base
            + bonus_penaltis
        )

        time_casa = str(
            linha["time_casa_resultado"]
        ).strip()

        time_fora = str(
            linha["time_fora_resultado"]
        ).strip()

        linhas_extrato.append(
            {
                "participante": linha["participante"],
                "fase": linha["fase"],
                "jogo_id": int(linha["jogo_id"]),
                "jogo": (
                    f"{time_casa} x {time_fora}"
                ),
                "palpite": (
                    f"{int(linha['palpite_a'])}"
                    f" x "
                    f"{int(linha['palpite_b'])}"
                ),
                "resultado_90": (
                    f"{int(linha['gols_casa_90'])}"
                    f" x "
                    f"{int(linha['gols_fora_90'])}"
                ),
                "vencedor_penaltis_palpite": str(
                    linha[
                        "vencedor_penaltis_palpite"
                    ]
                ).strip(),
                "vencedor_penaltis_real": str(
                    linha[
                        "vencedor_penaltis_resultado"
                    ]
                ).strip(),
                "pontos_base": pontos_base,
                "bonus_penaltis": bonus_penaltis,
                "pontos": pontos_total
            }
        )

    df_extrato = pd.DataFrame(
        linhas_extrato,
        columns=COLUNAS_EXTRATO_MATA_MATA
    )

    return df_extrato.sort_values(
        by=[
            "participante",
            "fase",
            "jogo_id"
        ]
    ).reset_index(
        drop=True
    )