import random, copy, math
import itertools
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ===================== Dados =====================

distancias = []
solucao_otima = []

with open('distancias_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        distancias.append([int(num) for num in linha.strip().split()])

with open('resposta_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        solucao_otima.append(int(linha.strip()) - 1)

num_cidades = len(solucao_otima)
fitness_otimo = None

# ================ Funções do CLONALG ================

def criar_populacao(N, num_cidades):
    return [random.sample(range(num_cidades), num_cidades) for _ in range(N)]

def funcao_objetivo(individuo):
    return sum(distancias[individuo[i]][individuo[i+1]] for i in range(len(individuo)-1)) + distancias[individuo[-1]][individuo[0]]

def avaliar_populacao(pop):
    return [funcao_objetivo(ind) for ind in pop]

def mutacao_adaptativa(ind, D, Dmax, rho):
    alpha = 0 if Dmax == 0 else math.exp(-rho * (D / Dmax))
    n_mutacoes = int(alpha * len(ind))
    novo = ind.copy()
    for _ in range(n_mutacoes):
        i, j = random.sample(range(len(ind)), 2)
        novo[i], novo[j] = novo[j], novo[i]
    return novo

def clonalg(N, n, d, beta, rho, nger, n_elite):
    global fitness_otimo
    pop = criar_populacao(N, num_cidades)
    if fitness_otimo is None:
        fitness_otimo = funcao_objetivo(solucao_otima)

    melhor_global = float('inf')
    melhor_geracao = []
    media_geracao = []
    pior_geracao = []
    mediana_geracao = []

    for g in range(nger):
        fitness = avaliar_populacao(pop)
        pop_ordenada = [x for _, x in sorted(zip(fitness, pop), key=lambda pair: pair[0])]
        melhores = pop_ordenada[:n]
        fitness_melhores = sorted(fitness)[:n]
        Dmax = max(fitness_melhores)

        clones = []
        for i, (ind, D) in enumerate(zip(melhores, fitness_melhores)):
            n_clones = round(beta * N / (i + 1))
            for _ in range(n_clones):
                clones.append(mutacao_adaptativa(ind, D, Dmax, rho))

        clones.sort(key=funcao_objetivo)
        nova_pop = clones[:N - d] + criar_populacao(d, num_cidades)

        elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])[:n_elite]
        for i in elite_indices:
            nova_pop.append(pop[i])

        pop = nova_pop

        # Métricas por geração
        fitness_gen = avaliar_populacao(pop)
        melhor_geracao.append(min(fitness_gen))
        media_geracao.append(np.mean(fitness_gen))
        pior_geracao.append(max(fitness_gen))
        mediana_geracao.append(np.median(fitness_gen))

        if melhor_geracao[-1] < melhor_global:
            melhor_global = melhor_geracao[-1]

    return melhor_global, media_geracao[-1], np.std(avaliar_populacao(pop)), {
        'melhor': melhor_geracao,
        'media': media_geracao,
        'pior': pior_geracao,
        'mediana': mediana_geracao
    }

# ================ Experimento Fatorial ================

def experimento():
    N = 20
    n_elite = 2
    rho = 2.5
    nger = 100
    execucoes_por_config = 10

    n_vals = [10, 15, 20]
    d_vals = [2, 5, 8]
    beta_vals = [1, 3, 5]

    resultados = []
    historico_global = {}

    for n, d, beta in itertools.product(n_vals, d_vals, beta_vals):
        fitness_execs = []
        historico_execs = []

        for _ in range(execucoes_por_config):
            best, media, desvio, historico = clonalg(N=N, n=n, d=d, beta=beta, rho=rho, nger=nger, n_elite=n_elite)
            fitness_execs.append(best)
            historico_execs.append(historico)

        melhor = np.min(fitness_execs)
        media = np.mean(fitness_execs)
        desvio = np.std(fitness_execs)

        resultados.append({
            'n': n, 'd': d, 'beta': beta,
            'melhor': melhor,
            'media': media,
            'desvio': desvio,
            'fitness_execs': fitness_execs,
            'historico_execs': historico_execs
        })

    # Tabela Top 30
    top30 = sorted(resultados, key=lambda x: x['melhor'])[:30]
    df = pd.DataFrame([{
        'n': r['n'], 'd': r['d'], 'beta': r['beta'],
        'Melhor': r['melhor'],
        'Média': r['media'],
        'Desvio': r['desvio']
    } for r in top30])
    # Salvar tabela como imagem PNG
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.4))  # Altura adaptativa
    ax.axis('off')
    tabela = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1.2, 1.2)
    plt.title("Top 30 Configurações - CLONALG", fontweight="bold", pad=20)
    plt.savefig('tabela_top30.png', bbox_inches='tight')
    plt.close()


    # Gráfico 1: Evolução da média da população
    plt.figure()
    melhor_config = top30[0]
    historicos = melhor_config['historico_execs']
    medias = [np.mean([h['media'][g] for h in historicos]) for g in range(nger)]
    plt.plot(range(nger), medias, label='Média da População')
    plt.xlabel('Geração')
    plt.ylabel('Fitness Médio')
    plt.title('Evolução da Média da População')
    plt.legend()
    plt.grid()
    plt.savefig('grafico_media_populacao.png')
    plt.close()

    # Gráfico 2: Melhor configuração (menor fitness)
    melhor_config = top30[0]
    historicos = melhor_config['historico_execs']

    melhor = np.min(np.array([h['melhor'] for h in historicos]), axis=0)
    media = np.mean(np.array([h['media'] for h in historicos]), axis=0)
    pior = np.max(np.array([h['pior'] for h in historicos]), axis=0)
    mediana = np.median(np.array([h['mediana'] for h in historicos]), axis=0)


    plt.figure()
    plt.plot(melhor, label='Melhor')
    plt.plot(media, label='Média')
    plt.plot(pior, label='Pior')
    plt.plot(mediana, label='Mediana')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.title('Evolução do Fitness - Melhor Configuração')
    plt.legend()
    plt.grid()
    plt.savefig('grafico_melhor_configuracao.png')
    plt.close()

    print("✅ Experimento concluído.")
    print("📊 Resultados salvos: tabela_top30.csv, grafico_media_populacao.png, grafico_melhor_configuracao.png")

# ================ Executar ==================
if __name__ == "__main__":
    experimento()
