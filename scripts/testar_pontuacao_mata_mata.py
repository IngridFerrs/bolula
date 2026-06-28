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


from services.pontuacao_mata_mata import (
    calcular_pontos_base,
    calcular_bonus_penaltis
)


def main():

    # Placar exato.
    assert calcular_pontos_base(
        1,
        1,
        1,
        1
    ) == 5

    # Acertou empate.
    assert calcular_pontos_base(
        0,
        0,
        1,
        1
    ) == 3

    # Acertou vencedor.
    assert calcular_pontos_base(
        2,
        1,
        1,
        0
    ) == 3

    # Acertou apenas total de gols.
    assert calcular_pontos_base(
        2,
        0,
        1,
        1
    ) == 1

    # Não pontuou.
    assert calcular_pontos_base(
        3,
        0,
        1,
        1
    ) == 0

    # Acertou vencedor dos pênaltis.
    assert calcular_bonus_penaltis(
        "PENALTY_SHOOTOUT",
        "Brazil",
        "Brazil"
    ) == 1

    # Errou vencedor dos pênaltis.
    assert calcular_bonus_penaltis(
        "PENALTY_SHOOTOUT",
        "Japan",
        "Brazil"
    ) == 0

    # Acertou time, mas não houve pênaltis.
    assert calcular_bonus_penaltis(
        "EXTRA_TIME",
        "Brazil",
        "Brazil"
    ) == 0

    print(
        "\n✅ TODOS OS TESTES DE PONTUAÇÃO PASSARAM."
    )


if __name__ == "__main__":

    main()