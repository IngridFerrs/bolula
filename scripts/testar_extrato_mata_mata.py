import sys
from pathlib import Path

import pandas as pd


BASE_DIR = Path(
    __file__
).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BASE_DIR)
    )


from services.pontuacao_mata_mata import (
    calcular_extrato_mata_mata
)


def main():

    # ------------------------------------------
    # PALPITES FICTÍCIOS
    # ------------------------------------------

    df_palpites = pd.DataFrame(
        [
            {
                "participante": "Ingrid",
                "fase": "LAST_32",
                "jogo_id": 1001,
                "time_casa": "Brazil",
                "time_fora": "Japan",
                "palpite_a": 1,
                "palpite_b": 1,
                "vencedor_penaltis": "Brazil"
            },
            {
                "participante": "Maria",
                "fase": "LAST_32",
                "jogo_id": 1001,
                "time_casa": "Brazil",
                "time_fora": "Japan",
                "palpite_a": 0,
                "palpite_b": 0,
                "vencedor_penaltis": "Japan"
            },
            {
                "participante": "Ingrid",
                "fase": "LAST_32",
                "jogo_id": 1002,
                "time_casa": "Canada",
                "time_fora": "Mexico",
                "palpite_a": 2,
                "palpite_b": 0,
                "vencedor_penaltis": "Canada"
            }
        ]
    )

    # ------------------------------------------
    # RESULTADOS FICTÍCIOS
    # ------------------------------------------

    df_resultados = pd.DataFrame(
        [
            {
                "fase": "LAST_32",
                "jogo_id": 1001,
                "time_casa": "Brazil",
                "time_fora": "Japan",
                "gols_casa_90": 1,
                "gols_fora_90": 1,
                "duracao": "PENALTY_SHOOTOUT",
                "vencedor_penaltis": "Brazil"
            },
            {
                "fase": "LAST_32",
                "jogo_id": 1002,
                "time_casa": "Canada",
                "time_fora": "Mexico",
                "gols_casa_90": 1,
                "gols_fora_90": 0,
                "duracao": "REGULAR",
                "vencedor_penaltis": ""
            }
        ]
    )

    # ------------------------------------------
    # CALCULAR
    # ------------------------------------------

    df_extrato = calcular_extrato_mata_mata(
        df_palpites,
        df_resultados
    )

    print(
        "\nExtrato calculado:\n"
    )

    print(
        df_extrato.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # CONFERÊNCIAS
    # ------------------------------------------

    ingrid_jogo_1001 = df_extrato[
        (
            df_extrato["participante"] == "Ingrid"
        )
        &
        (
            df_extrato["jogo_id"] == 1001
        )
    ].iloc[0]

    # Placar exato: 5
    # Acertou pênaltis: +1
    assert ingrid_jogo_1001["pontos_base"] == 5
    assert ingrid_jogo_1001["bonus_penaltis"] == 1
    assert ingrid_jogo_1001["pontos"] == 6

    maria_jogo_1001 = df_extrato[
        (
            df_extrato["participante"] == "Maria"
        )
        &
        (
            df_extrato["jogo_id"] == 1001
        )
    ].iloc[0]

    # Acertou o empate: 3
    # Errou os pênaltis: 0
    assert maria_jogo_1001["pontos_base"] == 3
    assert maria_jogo_1001["bonus_penaltis"] == 0
    assert maria_jogo_1001["pontos"] == 3

    ingrid_jogo_1002 = df_extrato[
        (
            df_extrato["participante"] == "Ingrid"
        )
        &
        (
            df_extrato["jogo_id"] == 1002
        )
    ].iloc[0]

    # Acertou o vencedor: 3
    # Não houve pênaltis: 0
    assert ingrid_jogo_1002["pontos_base"] == 3
    assert ingrid_jogo_1002["bonus_penaltis"] == 0
    assert ingrid_jogo_1002["pontos"] == 3

    assert len(df_extrato) == 3

    print(
        "\n✅ TESTE COMPLETO DO EXTRATO PASSOU."
    )


if __name__ == "__main__":

    main()