import sys
from pathlib import Path


BASE_DIR = Path(
    __file__
).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BASE_DIR)
    )


from services.google_sheets import (
    ler_palpites_mata_mata,
    ler_resultados_mata_mata,
    salvar_extrato_mata_mata
)

from services.pontuacao_mata_mata import (
    calcular_extrato_mata_mata
)


def main():

    print(
        "\n========================================"
    )

    print(
        "CÁLCULO DOS PONTOS DO MATA-MATA"
    )

    print(
        "========================================\n"
    )

    # ------------------------------------------
    # CARREGAR PALPITES
    # ------------------------------------------

    print(
        "Carregando PALPITES_MATA_MATA..."
    )

    df_palpites = ler_palpites_mata_mata()

    if df_palpites.empty:

        print(
            "\nPALPITES_MATA_MATA está vazia."
        )

        print(
            "Nenhum cálculo foi realizado."
        )

        return

    print(
        f"Palpites encontrados: {len(df_palpites)}"
    )

    # ------------------------------------------
    # CARREGAR RESULTADOS
    # ------------------------------------------

    print(
        "\nCarregando RESULTADOS_MATA_MATA..."
    )

    df_resultados = ler_resultados_mata_mata()

    if df_resultados.empty:

        print(
            "\nRESULTADOS_MATA_MATA está vazia."
        )

        print(
            "Nenhum cálculo foi realizado."
        )

        return

    print(
        f"Resultados encontrados: {len(df_resultados)}"
    )

    # ------------------------------------------
    # CALCULAR EXTRATO
    # ------------------------------------------

    df_extrato = calcular_extrato_mata_mata(
        df_palpites,
        df_resultados
    )

    if df_extrato.empty:

        print(
            "\nNenhum palpite corresponde aos "
            "resultados cadastrados."
        )

        print(
            "Confira fase e jogo_id nas duas abas."
        )

        return

    print(
        "\nExtrato calculado:\n"
    )

    print(
        df_extrato.to_string(
            index=False
        )
    )

    print(
        f"\nRegistros calculados: {len(df_extrato)}"
    )

    # ------------------------------------------
    # RESUMO ANTES DE GRAVAR
    # ------------------------------------------

    resumo = (
        df_extrato
        .groupby(
            "participante",
            as_index=False
        )
        .agg(
            pontos_base=(
                "pontos_base",
                "sum"
            ),
            bonus_penaltis=(
                "bonus_penaltis",
                "sum"
            ),
            pontos=(
                "pontos",
                "sum"
            )
        )
        .sort_values(
            by=[
                "pontos",
                "participante"
            ],
            ascending=[
                False,
                True
            ]
        )
    )

    print(
        "\nResumo da pontuação do mata-mata:\n"
    )

    print(
        resumo.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # CONFIRMAÇÃO
    # ------------------------------------------

    confirmacao = input(
        "\nDigite SIM para substituir o conteúdo "
        "de EXTRATO_MATA_MATA pelos dados acima: "
    )

    if confirmacao.strip().upper() != "SIM":

        print(
            "\nOperação cancelada."
        )

        print(
            "EXTRATO_MATA_MATA não foi alterada."
        )

        return

    # ------------------------------------------
    # GRAVAR EXTRATO
    # ------------------------------------------

    salvar_extrato_mata_mata(
        df_extrato
    )

    print(
        "\n✅ EXTRATO_MATA_MATA atualizado com sucesso."
    )


if __name__ == "__main__":

    main()