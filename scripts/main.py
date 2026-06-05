import pandas as pd
import glob

# Leitura de Arquivos

#LOCALIZAR ARQUIVO DE PALPITES 

arquivos_palpites = glob.glob("dados/palpites_rodada_*.xlsx")

print("\nARQUIVOS DE PALPITES:\n")

#VALIDAR

if not arquivos_palpites:
    print("\nERRO : nenhum arquivo de palpite encontrado")
    exit()
lista_palpites = []

for arquivo in arquivos_palpites:

    df = pd.read_excel(arquivo)
    lista_palpites.append(df)
palpites = pd.concat(lista_palpites,ignore_index=True)
print(palpites.head())


arquivos_resultados = glob.glob("dados/resultados_rodada_*.xlsx")

print(arquivos_resultados)

print("\nARQUIVOS ENCONTRADOS\n")
print(arquivos_resultados)

#Lista de DATAFRAMES
lista_resultados = []


#LER CADA ARQUIVO

for arquivo in arquivos_resultados:
    df = pd.read_excel(arquivo)

    lista_resultados.append(df)

resultados = pd.concat(lista_resultados,ignore_index=True)

resultados = resultados.rename(
    columns={
        "gols_casa": "gols_a_real",
        "gols_fora": "gols_b_real",
        "time_casa": "time_a",
        "time_fora": "time_b"
    }
)

print(resultados.head())

#Juntar Tabelas

dados = palpites.merge(
    resultados,
    on =["rodada", "jogo_id"],
    how = "left"
)

dados = dados.dropna(
    subset=[
        "gols_a_real",
        "gols_b_real"
    ]
)

if dados.empty:

    print("\nNenhum jogo com resultado disponível ainda.")
    print("A classificação não será gerada neste momento.")

    exit()

#Função de pontuação

def calcular_pontos(linha):

    #palpites

    palpite_a = linha["palpite_a"]
    palpite_b = linha["palpite_b"]

    #resultados reais

    real_a = linha["gols_a_real"]
    real_b = linha["gols_b_real"]

    # REGRA 1 - PLACAR EXATO

    if palpite_a == real_a and palpite_b == real_b: 

        return pd.Series([5, "placar_exato"])
    
    # REGRA 2 - ACERTOU VENCEDOR

    #vencedor palpite

    vencedor_real = None
    vencedor_palpite = None

    if palpite_a > palpite_b:

        vencedor_palpite = "A"

    elif palpite_b > palpite_a:
        
        vencedor_palpite = "B"

    else:

        vencedor_palpite = "EMPATE"

    #vencedor real

    if real_a > real_b:

        vencedor_real = "A"

    elif real_b > real_a:

        vencedor_real = "B"

    else : 
        vencedor_real = "EMPATE"
    
    # Comparar Vencedor

    if vencedor_real == vencedor_palpite:

        return pd.Series([3, "vencedor"])
    
    # Regra 3 - TOTAL DE GOLS 

    total_palpite = palpite_a + palpite_b

    total_real = real_a + real_b

    if total_palpite == total_real:

        return pd.Series([1, "total_gols"])
    
    # REGRA 4 -ERROU TUDO

    return pd.Series([0, "erro"])

#Aplicar Função

dados[["pontos", "criterios"]] = dados.apply(calcular_pontos, axis=1)

#Mostrar Resultado

print( 
    dados [
              [
                  "participante",
                  "jogo_id",
                  "palpite_a",
                  "palpite_b",
                  "gols_a_real",
                  "gols_b_real",
                  "pontos",
                  "criterios"
                  
              ]
              
              ]
)


#Classificação Geral

classificacao = (dados.groupby("participante")["pontos"].sum().reset_index())

# Ordenar classificação

classificacao = classificacao.sort_values(by="pontos",ascending=False)


#Criar Posição

classificacao["posicao"]  = range(1,len(classificacao) + 1)

#Reorganizar Colunas

classificacao = classificacao [["posicao","participante","pontos"]]


# Mostrar Classificação Geral

print("\nCLASSIFICAÇÃO GERAL\n")

print(classificacao)

#Classsificação Por Rodada

classificacao_rodada = (dados.groupby(["rodada","participante"])["pontos"].sum().reset_index())


#Ordenar Classsificaçao Por Rodada

classificacao_rodada = classificacao_rodada.sort_values(by=["rodada","pontos"],ascending=[True,False])

#Criar Posição Por Rodada

classificacao_rodada["posicao"] = classificacao_rodada.groupby("rodada").cumcount() + 1

classificacao_rodada = classificacao_rodada[
    [
        "rodada",
        "posicao",
        "participante",
        "pontos"
    ]
]

#Mostrar

print("\nCLASSIFICAÇÃO POR RODADA\n")

print(classificacao_rodada)

#Criar Colunas

dados["jogo"] = ( dados["time_a"] + "x" + dados["time_b"])

dados["palpite"] = (dados["palpite_a"].astype(str) + "x" + dados["palpite_b"].astype(str))

dados["resultado"] = (dados["gols_a_real"].astype(str) + "x" + dados["gols_b_real"].astype(str))

#Extrato Final

extrato = dados [
    [
        "participante",
        "rodada",
        "jogo",
        "palpite",
        "resultado",
        "criterios",
        "pontos"
        
    ]
]

#Exportar para Excel

with pd.ExcelWriter(

    "saidas/resultado_final.xlsx",
    engine="openpyxl"
) as writer:
    
    #Aba 1

    classificacao.to_excel(
        writer,
        sheet_name="CLASSIFICACAO",
        index=False
    )

    #Aba 2

    extrato.to_excel(
        writer,
        sheet_name="EXTRATO",
        index=False
    )

print("\nARQUIVO EXCEL GERADO COM SUCESSO!")