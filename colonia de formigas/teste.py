import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools

# ============ Dados do TSP ============
distancias = []
solucao_otima = []

with open('distancias_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        distancias.append([int(num) for num in linha.strip().split()])

with open('resposta_caixeiro.txt', 'r') as arquivo:
    solucao_otima = [int(l.strip()) - 1 for l in arquivo]

num_cidades = len(solucao_otima)

# ============ Algoritmo ============
class Formiga:
    def __init__(self, cidade_inicial):
        self.inicio = cidade_inicial
        self.atual = cidade_inicial
        self.caminho = [cidade_inicial]
        self.visitados = set([cidade_inicial])
        self.distancia_total = 0.0

    def visitar_cidade(self, cidade, distancia):
        self.atual = cidade
        self.caminho.append(cidade)
        self.visitados.add(cidade)
        self.distancia_total += distancia

def calcular_probabilidade(formiga, distancias, feromonio, alpha, beta):
    probabilidades = [0.0] * num_cidades
    atual = formiga.atual

    for j in range(num_cidades):
        if j in formiga.visitados:
            continue
        tau = feromonio[atual][j]
        eta = 1 / distancias[atual][j] if distancias[atual][j] > 0 else 1e10
        probabilidades[j] = (tau ** alpha) * (eta ** beta)

    soma = sum(probabilidades)
    if soma == 0:
        return [1 if j not in formiga.visitados else 0 for j in range(num_cidades)]
    return [p / soma for p in probabilidades]

def escolher_cidade(probabilidades):
    return random.choices(range(num_cidades), weights=probabilidades, k=1)[0]

def jornada_formiga(formiga, distancias, feromonio, alpha, beta):
    while len(formiga.visitados) < num_cidades:
        prob = calcular_probabilidade(formiga, distancias, feromonio, alpha, beta)
        cidade = escolher_cidade(prob)
        formiga.visitar_cidade(cidade, distancias[formiga.atual][cidade])
    formiga.visitar_cidade(formiga.inicio, distancias[formiga.atual][formiga.inicio])

def atualizar_feromonio(feromonio, formigas, rho, Q):
    for i in range(num_cidades):
        for j in range(num_cidades):
            feromonio[i][j] *= (1 - rho)
    for f in formigas:
        contrib = Q / f.distancia_total
        for i in range(len(f.caminho) - 1):
            a, b = f.caminho[i], f.caminho[i + 1]
            feromonio[a][b] += contrib
            feromonio[b][a] += contrib

def ant_system_exec(alpha, beta, rho, Q, iteracoes):
    feromonio = [[1e-16 for _ in range(num_cidades)] for _ in range(num_cidades)]
    melhor_dist = float('inf')
    historico = []

    for _ in range(iteracoes):
        formigas = [Formiga(i) for i in range(num_cidades)]
        for f in formigas:
            jornada_formiga(f, distancias, feromonio, alpha, beta)
        atualizar_feromonio(feromonio, formigas, rho, Q)
        melhor_iteracao = min(f.distancia_total for f in formigas)
        historico.append(melhor_iteracao)
        if melhor_iteracao < melhor_dist:
            melhor_dist = melhor_iteracao

    return melhor_dist, historico

# ============ Experimento Fatorial ============
def experimento():
    iteracoes = 100
    execucoes_por_config = 10

    alpha_vals = [0.5, 1.0, 2.0]
    beta_vals = [1.0, 2.0, 5.0]
    rho_vals = [0.1, 0.3, 0.5]

    resultados = []

    for alpha, beta, rho in itertools.product(alpha_vals, beta_vals, rho_vals):
        fitness_execs = []
        historicos_execs = []

        for _ in range(execucoes_por_config):
            best, hist = ant_system_exec(alpha, beta, rho, Q=100, iteracoes=iteracoes)
            fitness_execs.append(best)
            historicos_execs.append(hist)

        melhor = np.min(fitness_execs)
        media = np.mean(fitness_execs)
        desvio = np.std(fitness_execs)

        resultados.append({
            'alpha': alpha, 'beta': beta, 'rho': rho,
            'melhor': melhor,
            'media': media,
            'desvio': desvio,
            'historico': historicos_execs
        })

    # Tabela PNG
    top30 = sorted(resultados, key=lambda x: x['melhor'])[:30]
    df = pd.DataFrame([{
        'alpha': r['alpha'], 'beta': r['beta'], 'rho': r['rho'],
        'Melhor': r['melhor'],
        'Média': r['media'],
        'Desvio': r['desvio']
    } for r in top30])

    fig, ax = plt.subplots(figsize=(10, len(df)*0.4))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    plt.title("Top 30 - ACO", fontweight="bold", pad=20)
    plt.savefig("tabela_top30_aco.png", bbox_inches='tight')
    plt.close()

    # Gráfico de evolução
    melhor_config = top30[0]
    historicos = melhor_config['historico']
    medias = [np.mean([h[i] for h in historicos]) for i in range(iteracoes)]

    plt.figure()
    plt.plot(medias, label='Média')
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.title("Evolução do Fitness - Melhor Config ACO")
    plt.grid()
    plt.legend()
    plt.savefig("grafico_melhor_configuracao_aco.png")
    plt.close()

    print("✅ ACO finalizado.")
    print("📊 Resultados salvos: tabela_top30_aco.png, grafico_melhor_configuracao_aco.png")

if __name__ == "__main__":
    experimento()
