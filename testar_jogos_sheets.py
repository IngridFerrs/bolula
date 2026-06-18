from services.google_sheets import ler_jogos_rodada

df = ler_jogos_rodada(2)

print(df)
print(df.dtypes)
print("Quantidade de jogos:", len(df))