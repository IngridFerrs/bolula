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


from services.api_copa import (
    buscar_resultados_fase,
    traduzir_stage
)

from services.google_sheets import (
    salvar_ou_atualizar_resultados_mata_mata,
    ler_resultados_mata_mata
)


FASE = "LAST_32"


def main():

    nome_fase = traduzir_stage(
        FASE
    )

    print(
        f"\nBuscando resultados da fase: "
        f"{nome_fase} ({FASE})\n"
    )

    df_resultados = buscar_resultados_fase(
        FASE
    )

    if df_resultados.empty:

        print(
            "\nNenhum resultado finalizado foi "
            "encontrado para esta fase."
        )

        print(
            "A aba RESULTADOS_MATA_MATA "
            "não foi alterada."
        )

        return

    print(
        "\nResultados encontrados:\n"
    )

    print(
        df_resultados.to_string(
            index=False
        )
    )

    print(
        f"\nTotal de resultados: "
        f"{len(df_resultados)}"
    )

    confirmacao = input(
        "\nDigite SIM para atualizar "
        "RESULTADOS_MATA_MATA: "
    )

    if confirmacao.strip().upper() != "SIM":

        print(
            "\nOperação cancelada. "
            "Nenhuma alteração foi realizada."
        )

        return

    resultado_gravacao = (
        salvar_ou_atualizar_resultados_mata_mata(
            df_resultados
        )
    )

    print(
        "\nAtualização concluída:"
    )

    print(
        f"- Resultados inseridos: "
        f"{resultado_gravacao['inseridos']}"
    )

    print(
        f"- Resultados atualizados: "
        f"{resultado_gravacao['atualizados']}"
    )

    print(
        "\nConferindo RESULTADOS_MATA_MATA...\n"
    )

    df_salvo = ler_resultados_mata_mata()

    if df_salvo.empty:

        print(
            "A aba ainda está vazia."
        )

        return

    df_fase = df_salvo[
        df_salvo["fase"]
        .astype(str)
        .str.strip()
        .eq(FASE)
    ].copy()

    print(
        df_fase.to_string(
            index=False
        )
    )


if __name__ == "__main__":

    main()