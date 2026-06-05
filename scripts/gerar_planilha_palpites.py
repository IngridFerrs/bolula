import pandas as pd

#LER RODADA

rodada = int(input("Digite o número da rodada: "))

#LER RESULTADOS DA RODADA

arquivo = (f"dados/resultados_rodada_{rodada}.xlsx")

df = pd.read_excel(arquivo)

#CRIAR PLANILHA DE PALPITES

palpites = df[
    [
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora"
    ]
].copy()

palpites["participante"] = " "
palpites["palpite_a"] = " "
palpites["palpite_b"] = " "

palpites = palpites[
    [
        "participante",
        "rodada",
        "jogo_id",
        "time_casa",
        "time_fora",
        "palpite_a",
        "palpite_b"
    ]
]

arquivo_saida = (f"dados/palpites_rodada_{rodada}.xlsx")

palpites.to_excel(arquivo_saida,index=False)

print("\nPLANILHA GERADA COM SUCESSO\n")

print(f"\nArquivo salvo em : {arquivo_saida}")
