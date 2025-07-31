import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product
import importlib

# Algoritmos e caminhos
algoritmos_para_testar = {
    "PMX": "algoritmos_teste.caixeiro_pmx_teste",

}

# Indicar se é maximizador ou minimizador
modo_otimizacao = {
    "Mochila": "max",
    "Binario": "min",
    "Real": "min",
    "OX": "min",
    "CX": "min",
    "PMX": "min"
}

# Parâmetros
parametros = {
    "npop": [100, 200, 500],
    "nger": [100, 200, 500],
    "Pc": [1.0, 0.8],
    "Pm": [0.05, 0.1],
    "k": [2],
    "n_elite": [2, 0]
}

n_execucoes = 10
param_nomes = list(parametros.keys())
combinacoes = list(product(*parametros.values()))
os.makedirs("resultados", exist_ok=True)

# Função para formatar valores de forma consistente
def formatar_chave(param_dict):
    parts = []
    for k, v in param_dict.items():
        # Formata floats para evitar .0 quando é inteiro
        if isinstance(v, float) and v.is_integer():
            parts.append(f"{k}={int(v)}")
        else:
            parts.append(f"{k}={v}")
    return "_".join(parts)

for nome_algoritmo, caminho in algoritmos_para_testar.items():
    try:
        modulo = importlib.import_module(caminho)
    except ImportError as e:
        print(f"Erro ao importar módulo {caminho}: {e}")
        continue

    pasta_alg = os.path.join("resultados", nome_algoritmo)
    os.makedirs(pasta_alg, exist_ok=True)

    resultados_gerais = []
    media_geracao_por_param = {}
    media_populacao_por_param = {}
    historicos_por_combinacao = {}

    for comb in combinacoes:
        param_dict = dict(zip(param_nomes, comb))
        nome_combinacao = formatar_chave(param_dict)
        pasta_comb = os.path.join(pasta_alg, nome_combinacao)
        os.makedirs(pasta_comb, exist_ok=True)

        melhores_exec = []
        medias_exec = []

        for execucao in range(1, n_execucoes + 1):
            print(f"{nome_algoritmo} - {nome_combinacao} - Execução {execucao}")
            try:
                melhor_hist, media_hist, todos_fitness = modulo.executar_algoritmo(**param_dict)
            except Exception as e:
                print(f"Erro na execução do algoritmo: {e}")
                continue

            df_execucao = pd.DataFrame({
                "geracao": list(range(1, len(melhor_hist) + 1)),
                "melhor": melhor_hist,
                "media": media_hist
            })
            df_execucao.to_csv(os.path.join(pasta_comb, f"execucao_{execucao}.csv"), index=False)

            melhores_exec.append(melhor_hist)
            medias_exec.append(media_hist)

        if not melhores_exec:  # Se todas as execuções falharam
            continue

        melhores_exec = np.array(melhores_exec)
        medias_exec = np.array(medias_exec)
        media_melhor_geracao = np.mean(melhores_exec, axis=0)
        media_media_geracao = np.mean(medias_exec, axis=0)

        media_geracao_por_param[nome_combinacao] = media_melhor_geracao
        media_populacao_por_param[nome_combinacao] = media_media_geracao
        historicos_por_combinacao[nome_combinacao] = melhores_exec

        resultados_gerais.append({
            **param_dict,
            "Melhor μ": np.mean([hist[-1] for hist in melhores_exec]),
            "Melhor σ": np.std([hist[-1] for hist in melhores_exec]),
            "Média μ": np.mean([hist[-1] for hist in medias_exec]),
            "Média σ": np.std([hist[-1] for hist in medias_exec])
        })

        def salvar_grafico(y_values, ylabel, filename):
            plt.figure(figsize=(10, 6))
            plt.plot(range(1, len(y_values) + 1), y_values, label=nome_combinacao)
            plt.title(f"{ylabel} - {nome_algoritmo}\n{nome_combinacao}")
            plt.xlabel("Geração")
            plt.ylabel(ylabel)
            plt.grid()
            plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
            plt.tight_layout()
            plt.savefig(os.path.join(pasta_comb, filename))
            plt.close()

        salvar_grafico(media_melhor_geracao, "Melhor Fitness Médio", "grafico_melhor_fitness.png")
        salvar_grafico(media_media_geracao, "Média da População", "grafico_media_populacao.png")

    if not resultados_gerais:  # Se nenhuma combinação foi executada com sucesso
        continue

    # Determinar melhor combinação
    def obter_melhor_comb():
        chave = "Melhor μ"
        melhores = pd.DataFrame(resultados_gerais)
        if modo_otimizacao[nome_algoritmo] == "max":
            melhor_idx = melhores[chave].idxmax()
        else:
            melhor_idx = melhores[chave].idxmin()
        
        melhor_comb = melhores.loc[melhor_idx]
        # Usamos a mesma função de formatação para garantir consistência
        nome_melhor_comb = formatar_chave({k: melhor_comb[k] for k in param_nomes})
        return nome_melhor_comb, melhor_comb

    nome_melhor_comb, melhor_comb = obter_melhor_comb()
    
    if nome_melhor_comb not in historicos_por_combinacao:
        print(f"Combinação ótima não encontrada no histórico: {nome_melhor_comb}")
        continue
        
    historicos_melhor = historicos_por_combinacao[nome_melhor_comb]

    # Gráfico: evolução da melhor, pior, média e mediana
    if modo_otimizacao[nome_algoritmo] == "min":
        melhor = np.min(historicos_melhor, axis=0)
        pior = np.max(historicos_melhor, axis=0)
    else:
        melhor = np.max(historicos_melhor, axis=0)
        pior = np.min(historicos_melhor, axis=0)
    
    media = np.mean(historicos_melhor, axis=0)
    mediana = np.median(historicos_melhor, axis=0)

    plt.figure(figsize=(12, 8))
    plt.plot(melhor, label="Melhor Execução")
    plt.plot(pior, label="Pior Execução")
    plt.plot(media, label="Média")
    plt.plot(mediana, label="Mediana")
    plt.title(f"Evolução do Fitness - {nome_algoritmo} - {nome_melhor_comb}")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_alg, "grafico_evolucao_geracoes_melhor_comb.png"))
    plt.close()

    # Gráfico: evolução do melhor fitness entre TODAS execuções da melhor combinação
    melhores_geracoes = historicos_melhor[:, -1]
    if modo_otimizacao[nome_algoritmo] == "min":
        idx_escolhida = np.argmin(melhores_geracoes)
    else:
        idx_escolhida = np.argmax(melhores_geracoes)
    
    melhor_execucao = historicos_melhor[idx_escolhida]

    plt.figure(figsize=(12, 6))
    plt.plot(melhor_execucao, label="Melhor Execução (completa)")
    plt.title(f"Evolução do Melhor Fitness - {nome_algoritmo} - {nome_melhor_comb}")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_alg, "grafico_melhor_execucao_individual.png"))
    plt.close()

    def salvar_grafico_agregado(dados_dict, ylabel, filename):
        plt.figure(figsize=(12, 8))
        for nome_comb, valores in dados_dict.items():
            plt.plot(range(1, len(valores) + 1), valores, label=nome_comb)
        plt.title(f"{ylabel} - {nome_algoritmo} (Média das execuções)")
        plt.xlabel("Geração")
        plt.ylabel(ylabel)
        plt.grid()
        plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        plt.tight_layout()
        plt.savefig(os.path.join(pasta_alg, filename))
        plt.close()

    salvar_grafico_agregado(media_geracao_por_param, "Melhor Fitness Médio", "todas_combinacoes_melhor_fitness.png")
    salvar_grafico_agregado(media_populacao_por_param, "Média da População", "todas_combinacoes_media_populacao.png")

    df_resultado = pd.DataFrame(resultados_gerais)
    df_resultado.to_csv(os.path.join(pasta_alg, "tabela_resumo.csv"), index=False)

print("Todas execuções finalizadas com sucesso.")