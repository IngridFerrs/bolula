import pandas as pd
from services.google_sheets import salvar_palpites

df = pd.DataFrame(
    [
        {
            "participante": "TESTE",
            "rodada": 1,
            "jogo_id": 999,
            "time_casa": "Brasil",
            "time_fora": "Japão",
            "palpite_a": 2,
            "palpite_b": 0
        }
    ]
)

salvar_palpites(df)

print("OK")