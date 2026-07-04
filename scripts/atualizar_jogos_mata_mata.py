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
    buscar_jogos_fase,
    traduzir_stage
)

from services.google_sheets import (
    salvar_ou_atualizar_jogos_fase,
    ler_jogos_fase
)


FASE = "LAST_16"


def main():

    nome_fase = traduzir_stage(
        FASE
    )

    print(
        f"\nBuscando jogos da fase: "
        f"{nome_fase} ({FASE})\n"
    )

    df_jogos = buscar_jogos_fase(
        FASE
    )

    if df_jogos.empty:

        print(
            "Nenhum confronto completo foi encontrado."
        )

        return

    colunas_exibicao = [
        "fase",
        "jogo_id",
        "time_casa",
        "time_fora",
        "data"
    ]

    print(
        df_jogos[
            colunas_exibicao
        ].to_string(
            index=False
        )
    )

    print(
        f"\nTotal de confrontos definidos: "
        f"{len(df_jogos)}"
    )

    confirmacao = input(
        "\nDigite SIM para atualizar a aba JOGOS: "
    )

    if confirmacao.strip().upper() != "SIM":

        print(
            "\nOperação cancelada. "
            "Nenhuma alteração foi realizada."
        )

        return

    resultado = salvar_ou_atualizar_jogos_fase(
        df_jogos
    )

    print(
        "\nAtualização concluída:"
    )

    print(
        f"- Jogos inseridos: "
        f"{resultado['inseridos']}"
    )

    print(
        f"- Jogos atualizados: "
        f"{resultado['atualizados']}"
    )

    print(
        "\nConferindo a leitura da aba JOGOS...\n"
    )

    df_salvo = ler_jogos_fase(
        FASE
    )

    if df_salvo.empty:

        print(
            "A leitura retornou vazia. "
            "Confira a aba JOGOS."
        )

        return

    print(
        df_salvo.to_string(
            index=False
        )
    )


if __name__ == "__main__":

    main()