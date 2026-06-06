import pandas as pd
import sys
from pathlib import Path
import glob

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from services.google_sheets import (ler_palpites,ler_resultados,salvar_classificacao,salvar_extrato)

# Leitura de Arquivos

#LOCALIZAR ARQUIVO DE PALPITES 

# ==========================================
# LER PALPITES DO GOOGLE SHEETS
# ==========================================

palpites = ler_palpites()

if palpites.empty:

    print("\nERRO: nenhum palpite encontrado.")
    exit()

print("\nPALPITES:\n")
print(palpites.head())


# ==========================================
# LER RESULTADOS DO GOOGLE SHEETS
# ==========================================

resultados = ler_resultados()

if resultados.empty:

    print("\nERRO: nenhum resultado encontrado.")
    exit()

print("\nRESULTADOS:\n")
print(resultados.head())

resultados = resultados.rename(
    columns={
        "gols_casa": "gols_a_real",
        "gols_fora": "gols_b_real",
        "time_casa": "time_a",
        "time_fora": "time_b"
    }
)

# ==========================================
# AJUSTAR TIPOS
# ==========================================

palpites["rodada"] = palpites["rodada"].astype(int)
palpites["jogo_id"] = palpites["jogo_id"].astype(int)
palpites["palpite_a"] = palpites["palpite_a"].astype(int)
palpites["palpite_b"] = palpites["palpite_b"].astype(int)

resultados["rodada"] = resultados["rodada"].astype(int)
resultados["jogo_id"] = resultados["jogo_id"].astype(int)

resultados["gols_a_real"] = pd.to_numeric(
    resultados["gols_a_real"],
    errors="coerce"
)

resultados["gols_b_real"] = pd.to_numeric(
    resultados["gols_b_real"],
    errors="coerce"
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

# ==========================================
# SALVAR NO GOOGLE SHEETS
# ==========================================

salvar_classificacao(
    classificacao
)

salvar_extrato(
    extrato
)

print("\nCLASSIFICAÇÃO E EXTRATO SALVOS NO GOOGLE SHEETS COM SUCESSO!")