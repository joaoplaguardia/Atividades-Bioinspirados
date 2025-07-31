import matplotlib.pyplot as plt
import numpy as np
import random
import copy

# === CONFIGURAÇÕES ===
npop = 100
nger = 100
n_elite = 2
Pc = 1.00
Pm = 0.05
k = 2
num_execucoes = 10
num_pontos = 2  # para OX

# === LEITURA DOS DADOS ===
def carregar_dados():
    with open("distancias_caixeiro.txt", "r") as f:
        distancias = [list(map(int, linha.strip().split())) for linha in f]
    with open("resposta_caixeiro.txt", "r") as f:
        solucao_otima = [int(linha.strip()) - 1 for linha in f]
    return distancias, solucao_otima

# === FUNÇÕES BÁSICAS ===
def criar_populacao(npop, num_cidades):
    return [random.sample(range(num_cidades), num_cidades) for _ in range(npop)]

def avaliar_individuo(ind, distancias):
    return sum(distancias[ind[i]][ind[i + 1]] for i in range(len(ind) - 1)) + distancias[ind[-1]][ind[0]]

def avaliar_populacao(pop, distancias):
    return [avaliar_individuo(ind, distancias) for ind in pop]

def torneio(pop, fitness, k):
    return [pop[min(random.sample(range(len(pop)), k), key=lambda i: fitness[i])] for _ in range(len(pop))]

def mutacao(pop, Pm):
    for ind in pop:
        for i in range(len(ind)):
            if random.random() < Pm:
                j = random.randint(0, len(ind) - 1)
                ind[i], ind[j] = ind[j], ind[i]

def elitismo(fitness, nova_pop, n_elite, pop):
    melhores = sorted(range(len(fitness)), key=lambda i: fitness[i])[:n_elite]
    for i in melhores:
        nova_pop.append(pop[i])

# === CRUZAMENTOS ===
def cruzamento_ox(pais, Pc, num_cidades, num_pontos):
    nova_pop = []
    for i in range(0, len(pais), 2):
        pai1, pai2 = pais[i], pais[i + 1]
        filho1, filho2 = [None] * num_cidades, [None] * num_cidades
        if random.random() < Pc:
            p1, p2 = sorted(random.sample(range(num_cidades), num_pontos))
            filho1[p1:p2+1] = pai1[p1:p2+1]
            filho2[p1:p2+1] = pai2[p1:p2+1]
            def preencher(filho, pai):
                pos = (p2 + 1) % num_cidades
                for gene in pai:
                    if gene not in filho:
                        filho[pos] = gene
                        pos = (pos + 1) % num_cidades
            preencher(filho1, pai2)
            preencher(filho2, pai1)
        else:
            filho1, filho2 = pai1[:], pai2[:]
        nova_pop.extend([filho1, filho2])
    return nova_pop

def cruzamento_cx(pais, Pc, num_cidades):
    nova_pop = []
    for i in range(0, len(pais), 2):
        pai1, pai2 = pais[i], pais[i + 1]
        filho1, filho2 = [None] * num_cidades, [None] * num_cidades
        if random.random() < Pc:
            ciclo = 0
            indices_restantes = set(range(num_cidades))
            while indices_restantes:
                index = next(iter(indices_restantes))
                ciclo_indices = []
                while True:
                    ciclo_indices.append(index)
                    valor = pai2[index]
                    index = pai1.index(valor)
                    if index in ciclo_indices:
                        break
                if ciclo % 2 == 0:
                    for idx in ciclo_indices:
                        filho1[idx] = pai1[idx]
                        filho2[idx] = pai2[idx]
                else:
                    for idx in ciclo_indices:
                        filho1[idx] = pai2[idx]
                        filho2[idx] = pai1[idx]
                indices_restantes -= set(ciclo_indices)
                ciclo += 1
            for idx in range(num_cidades):
                if filho1[idx] is None: filho1[idx] = pai2[idx]
                if filho2[idx] is None: filho2[idx] = pai1[idx]
        else:
            filho1, filho2 = pai1[:], pai2[:]
        nova_pop.extend([filho1, filho2])
    return nova_pop

# === EXECUÇÃO GENÉRICA ===
def testar_algoritmo(nome, cruzamento_fn, distancias, extra_args=()):
    num_cidades = len(distancias)
    fitness_execucoes = []
    melhor_execucao = None
    melhor_fitness_global = float('inf')

    for _ in range(num_execucoes):
        pop = criar_populacao(npop, num_cidades)
        historico = []

        for _ in range(nger):
            fitness = avaliar_populacao(pop, distancias)
            historico.append(fitness)
            pais = torneio(pop, fitness, k)
            nova_pop = cruzamento_fn(pais, Pc, num_cidades, *extra_args)
            mutacao(nova_pop, Pm)
            elitismo(fitness, nova_pop, n_elite, pop)
            pop = copy.deepcopy(nova_pop)

        fitness_execucoes.append(historico)
        if min(historico[-1]) < melhor_fitness_global:
            melhor_fitness_global = min(historico[-1])
            melhor_execucao = historico

    # Estatísticas
    melhores, piores, medias, medianas = [], [], [], []
    for g in range(nger):
        geracao_fitness = [execucao[g] for execucao in fitness_execucoes]
        flat = [f for sub in geracao_fitness for f in sub]
        melhores.append(min(flat))
        piores.append(max(flat))
        medias.append(np.mean(flat))
        medianas.append(np.median(flat))

    # Plot estatísticas
    plt.figure(figsize=(12, 6))
    plt.plot(melhores, label='Melhor')
    plt.plot(piores, label='Pior')
    plt.plot(medias, label='Média')
    plt.plot(medianas, label='Mediana')
    plt.title(f'Estatísticas - {nome}')
    plt.xlabel('Geração')
    plt.ylabel('Distância')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot melhor execução
    plt.figure(figsize=(12, 6))
    plt.plot([min(f) for f in melhor_execucao], label='Melhor Execução')
    plt.title(f'Melhor Execução - {nome}')
    plt.xlabel('Geração')
    plt.ylabel('Distância')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === EXECUÇÃO FINAL ===
if __name__ == "__main__":
    distancias, solucao_otima = carregar_dados()
    testar_algoritmo("Cruzamento OX", cruzamento_ox, distancias, extra_args=(num_pontos,))
    testar_algoritmo("Cruzamento CX", cruzamento_cx, distancias)
