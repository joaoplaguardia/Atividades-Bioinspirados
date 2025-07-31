import random
import math
import copy

npop = 100
nger = 100
n_elite = 2
Pc = 1.0
Pm = 0.01
n_vars = 2
bits_por_var = 16
total_bits = n_vars * bits_por_var
limite_inferior = -2
limite_superior = 2
k = 3

def cria_populacao_inicial(npop, total_bits):
    return [[random.randint(0, 1) for _ in range(total_bits)] for _ in range(npop)]

def binario_para_real(bits):
    inteiro = int("".join(str(b) for b in bits), 2)
    max_int = 2 ** len(bits) - 1
    real = limite_inferior + (limite_superior - limite_inferior) * inteiro / max_int
    return real

def decodifica_individuo(individuo):
    valores = []
    for i in range(0, total_bits, bits_por_var):
        bits = individuo[i:i+bits_por_var]
        valores.append(binario_para_real(bits))
    return valores

def funcao_ackley(individuo_real):
    n = len(individuo_real)
    somatorio1 = sum(x ** 2 for x in individuo_real)
    somatorio2 = sum(math.cos(2 * math.pi * x) for x in individuo_real)
    termo1 = -20 * math.exp(-0.2 * math.sqrt(somatorio1 / n))
    termo2 = -math.exp(somatorio2 / n)
    return termo1 + termo2 + 20 + math.e

def avalia_populacao(pop):
    return [funcao_ackley(decodifica_individuo(ind)) for ind in pop]

def torneio(pop, fit, k):
    paises = []
    for _ in range(len(pop)):
        competidores = random.sample(range(len(pop)), k)
        melhor = min(competidores, key=lambda i: fit[i])
        paises.append(melhor)
    return paises

def cruzamento(pop, paises, Pc):
    nova_pop = []
    for i in range(0, len(paises), 2):
        pai1 = pop[paises[i]]
        pai2 = pop[paises[(i + 1) % len(paises)]]

        if random.random() < Pc:
            ponto = random.randint(1, total_bits - 1)
            filho1 = pai1[:ponto] + pai2[ponto:]
            filho2 = pai2[:ponto] + pai1[ponto:]
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
                individuo[i] = 1 - individuo[i]

def elitismo(pop, fit, pop_intermediaria, n_elite):
    elite_idx = sorted(range(len(fit)), key=lambda i: fit[i])[:n_elite]
    for i in range(n_elite):
        pop_intermediaria[i] = copy.deepcopy(pop[elite_idx[i]])

def imprime_populacao_final(pop):
    print("\nPopulação Final:")
    for i, individuo in enumerate(pop[:10]):
        valores = decodifica_individuo(individuo)
        fx = funcao_ackley(valores)
        print(f"{i:3}: f(x) = {fx:.6f}, x = {valores}")

def genericAG():
    pop = cria_populacao_inicial(npop, total_bits)
    for g in range(nger):
        fit = avalia_populacao(pop)
        paises = torneio(pop, fit, k)
        pop_intermediaria = cruzamento(pop, paises, Pc)
        mutacao(pop_intermediaria, Pm)
        elitismo(pop, fit, pop_intermediaria, n_elite)
        pop = copy.deepcopy(pop_intermediaria)

    imprime_populacao_final(pop)

genericAG()
