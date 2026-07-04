import sys
from pathlib import Path


# Permite que o script encontre a pasta services
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BASE_DIR)
    )


from services.api_copa import buscar_jogos_fase


def main():

    fase = "LAST_32"

    print(
        f"\nBuscando jogos da fase {fase}...\n"
    )

    df = buscar_jogos_fase(
        fase
    )

    if df.empty:

        print(
            "Nenhum jogo definido foi encontrado."
        )

        return

    print(
        "Colunas retornadas:"
    )

    print(
        df.columns.tolist()
    )

    print(
        "\nJogos encontrados:\n"
    )

    print(
        df.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()