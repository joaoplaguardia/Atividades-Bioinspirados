import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import math

# ============ Parâmetros Gerais ============
dimensao = 4
limite_inferior = -10
limite_superior = 10
iteracoes = 100
execucoes_por_config = 10
tamanho_enxame = 30


class Particula:
    def __init__(self, indice):
        self.indice = indice
        self.posicao = np.random.uniform(limite_inferior, limite_superior, dimensao)
        self.velocidade = np.random.uniform(-1, 1, dimensao)
        self.melhor_posicao = self.posicao.copy()
        self.melhor_valor = float('inf')
        self.melhor_vizinha = self.posicao.copy()


def funcao_ackley(individuo):
    n = len(individuo)
    somatorio1 = sum(x ** 2 for x in individuo)
    somatorio2 = sum(math.cos(2 * math.pi * x) for x in individuo)
    termo1 = -20 * math.exp(-0.2 * math.sqrt(somatorio1 / n))
    termo2 = -math.exp(somatorio2 / n)
    return termo1 + termo2 + 20 + math.e


def criar_enxame():
    return [Particula(i) for i in range(tamanho_enxame)]


def atualizar_particula(p, enxame, w, c1, c2):
    vizinhos = [(p.indice + offset) % tamanho_enxame for offset in range(-2, 3)]
    melhor_vizinha_idx = min(vizinhos, key=lambda i: enxame[i].melhor_valor)
    p.melhor_vizinha = enxame[melhor_vizinha_idx].melhor_posicao

    r1 = np.random.rand(dimensao)
    r2 = np.random.rand(dimensao)

    p.velocidade = (
        w * p.velocidade
        + c1 * r1 * (p.melhor_posicao - p.posicao)
        + c2 * r2 * (p.melhor_vizinha - p.posicao)
    )
    p.posicao += p.velocidade
    p.posicao = np.clip(p.posicao, limite_inferior, limite_superior)


def pso_exec(w, c1, c2):
    enxame = criar_enxame()
    melhor_global = float('inf')
    historico = []

    for _ in range(iteracoes):
        for p in enxame:
            valor = funcao_ackley(p.posicao)
            if valor < p.melhor_valor:
                p.melhor_valor = valor
                p.melhor_posicao = p.posicao.copy()
                if valor < melhor_global:
                    melhor_global = valor
        historico.append(melhor_global)
        for p in enxame:
            atualizar_particula(p, enxame, w, c1, c2)

    return melhor_global, historico

# ============ Experimento Fatorial ============

def experimento():
    w_vals = [0.5, 1.0, 1.5]
    c1_vals = [0.5, 1.0, 2.0]
    c2_vals = [0.5, 1.0, 2.0]

    resultados = []

    for w, c1, c2 in itertools.product(w_vals, c1_vals, c2_vals):
        fitness_execs = []
        historicos_execs = []

        for _ in range(execucoes_por_config):
            best, hist = pso_exec(w, c1, c2)
            fitness_execs.append(best)
            historicos_execs.append(hist)

        melhor = np.min(fitness_execs)
        media = np.mean(fitness_execs)
        desvio = np.std(fitness_execs)

        resultados.append({
            'w': w, 'c1': c1, 'c2': c2,
            'melhor': melhor,
            'media': media,
            'desvio': desvio,
            'historico': historicos_execs
        })

    # Tabela PNG (com ajustes visuais)
    top30 = sorted(resultados, key=lambda x: x['melhor'])[:30]
    df = pd.DataFrame([{
        'w': r['w'], 'c1': r['c1'], 'c2': r['c2'],
        'Melhor': r['melhor'],
        'Média': r['media'],
        'Desvio': r['desvio']

    } for r in top30])

    fig, ax = plt.subplots(figsize=(14, len(df) * 0.5))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.4, 1.4)
    plt.title("Top 30 - PSO (Ackley)", fontweight="bold", pad=20)
    plt.savefig("tabela_top30_pso.png", bbox_inches='tight')
    plt.close()

    # Gráfico da melhor configuração
    melhor_config = top30[0]
    historicos = melhor_config['historico']
    medias = [np.mean([h[i] for h in historicos]) for i in range(iteracoes)]

    plt.figure()
    plt.plot(medias, label='Fitness Médio')
    plt.xlabel("Iteração")
    plt.ylabel("Fitness")
    plt.title("Evolução do Fitness - Melhor Config PSO")
    plt.grid()
    plt.legend()
    plt.savefig("grafico_melhor_configuracao_pso.png")
    plt.close()

    print("✅ PSO finalizado.")
    print("📊 Resultados salvos: tabela_top30_pso.png, grafico_melhor_configuracao_pso.png")

if __name__ == "__main__":
    experimento()
