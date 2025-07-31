import random
import math
import copy

npop = 100
nger = 100
n_elite = 2
Pc = 1.0
Pm = 0.01
n_vars = 2
limite_inferior = -2
limite_superior = 2
alpha = 0.75
beta = 0.25

def cria_populacao_inicial(npop, n_vars):
    return [[random.uniform(limite_inferior, limite_superior) for _ in range(n_vars)] for _ in range(npop)]

def funcao_ackley(individuo):
    n = len(individuo)
    somatorio1 = sum(x ** 2 for x in individuo)
    somatorio2 = sum(math.cos(2 * math.pi * x) for x in individuo)
    termo1 = -20 * math.exp(-0.2 * math.sqrt(somatorio1 / n))
    termo2 = -math.exp(somatorio2 / n)
    return termo1 + termo2 + 20 + math.e

def avalia_populacao(pop):
    return [funcao_ackley(ind) for ind in pop]

def calcula_probabilidades(fit):
    inversos = [1.0 / (f + 1e-10) for f in fit] 
    soma_inversos = sum(inversos)
    probabilidades = [f / soma_inversos for f in inversos]
    return probabilidades

def roleta(probabilidades):
    r = random.random()
    acum = 0.0
    for i, p in enumerate(probabilidades):
        acum += p
        if r <= acum:
            return i
    return len(probabilidades) - 1

def selecao_roleta(pop, fit):
    probabilidades = calcula_probabilidades(fit)
    paises = []
    for _ in range(len(pop)):
        pais = roleta(probabilidades)
        paises.append(pais)
    return paises

def cruzamento_blx(pop, paises, Pc, alpha=0.5, beta=0.5):
    nova_pop = []
    for i in range(0, len(paises), 2):
        pai1 = pop[paises[i]]
        pai2 = pop[paises[(i + 1) % len(paises)]]

        if random.random() < Pc:
            filho1 = []
            filho2 = []
            for x1, x2 in zip(pai1, pai2):
                d = abs(x1 - x2)
                min_val = min(x1, x2) - alpha * d
                max_val = max(x1, x2) + beta * d
                filho1.append(random.uniform(min_val, max_val))
                filho2.append(random.uniform(min_val, max_val))
        else:
            filho1 = pai1[:]
            filho2 = pai2[:]

        nova_pop.append(filho1)
        nova_pop.append(filho2)

    return nova_pop[:len(pop)]

def mutacao(pop, Pm):
    for individuo in pop:
        for i in range(len(individuo)):
            if random.random() < Pm:
                individuo[i] = random.uniform(limite_inferior, limite_superior)

def elitismo(pop, fit, pop_intermediaria, n_elite):
    elite_idx = sorted(range(len(fit)), key=lambda i: fit[i])[:n_elite]
    for i in range(n_elite):
        pop_intermediaria[i] = copy.deepcopy(pop[elite_idx[i]])

def imprime_populacao_final(pop):
    print("\nPopulação Final:")
    melhores = sorted(pop, key=lambda ind: funcao_ackley(ind))[:10]
    for i, individuo in enumerate(melhores):
        fx = funcao_ackley(individuo)
        print(f"{i:3}: f(x) = {fx:.6f}, x = {individuo}")

def genericAG():
    pop = cria_populacao_inicial(npop, n_vars)
    for g in range(nger):
        fit = avalia_populacao(pop)
        paises = selecao_roleta(pop, fit)
        pop_intermediaria = cruzamento_blx(pop, paises, Pc, alpha, beta)
        mutacao(pop_intermediaria, Pm)
        elitismo(pop, fit, pop_intermediaria, n_elite)
        pop = copy.deepcopy(pop_intermediaria)

    imprime_populacao_final(pop)

genericAG()
