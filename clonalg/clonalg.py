import random
import copy
import math

distancias = []
solucao_otima = []

with open('distancias_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        distancias.append([int(num) for num in linha.strip().split()])

with open('resposta_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        solucao_otima.append(int(linha.strip()) - 1)

num_cidades = len(solucao_otima)

# Parâmetros CLONALG
N = 20          # tamanho da população
nger = 100      # número de gerações
n = 20          # número de melhores selecionados
d = 5           # número de substituições (diversidade)
beta = 5        # fator de clonagem
rho = 2.5       # parâmetro da mutação adaptativa (hipermutação)
n_elite = 2     # número de elites mantidas

def criar_populacao(N, num_cidades):
    return [random.sample(range(num_cidades), num_cidades) for _ in range(N)]

def funcao_objetivo(individuo):
    distancia = sum(distancias[individuo[i]][individuo[i+1]] for i in range(len(individuo)-1))
    distancia += distancias[individuo[-1]][individuo[0]]
    return distancia

def avaliar_populacao(pop):
    return [funcao_objetivo(ind) for ind in pop]

def mutacao_adaptativa(ind, D, Dmax, rho):
    if Dmax == 0:
        alpha = 0
    else:
        D_norm = D / Dmax
        alpha = math.exp(-rho * D_norm)
    
    n_mutacoes = int(alpha * len(ind))
    novo = ind.copy()
    for _ in range(n_mutacoes):
        i, j = random.sample(range(len(ind)), 2)
        novo[i], novo[j] = novo[j], novo[i]
    return novo

def clonalg_caixeiro():
    pop = criar_populacao(N, num_cidades)
    fitness_otimo = funcao_objetivo(solucao_otima)
    melhor_fitness = float('inf')
    melhor_solucao = None

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
                clone_mutado = mutacao_adaptativa(ind, D, Dmax, rho)
                clones.append(clone_mutado)

        clones.sort(key=funcao_objetivo)
        nova_pop = clones[:N - d]

        nova_pop += criar_populacao(d, num_cidades)

        elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])[:n_elite]
        for i in elite_indices:
            nova_pop.append(pop[i])

        pop = nova_pop

        atual_fitness = avaliar_populacao(pop)
        if min(atual_fitness) < melhor_fitness:
            melhor_fitness = min(atual_fitness)
            melhor_solucao = pop[atual_fitness.index(melhor_fitness)]

    print("\nMelhor solução encontrada:")
    print(melhor_solucao)
    print(f"Distância: {melhor_fitness}")
    print("\nSolução Ótima:")
    print(solucao_otima)
    print(f"Distância: {fitness_otimo}")

clonalg_caixeiro()
