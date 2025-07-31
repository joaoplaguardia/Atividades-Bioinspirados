import random
import copy

distancias = []
solucao_otima = []
leitura = None


with open('datasets/distancias_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        linha = linha.strip()
        numeros = [int(num) for num in linha.split()]
        distancias.append(numeros)

with open('datasets/resposta_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        numero = int(linha.strip())
        solucao_otima.append(numero-1)


num_cidades = len(solucao_otima)
k = 2
npop = 100
nger = 100
n_elite = 2
Pc = 1.00
num_pontos = 2
Pm = 0.05

def criar_populacao(npop, num_cidades):
    return [random.sample(range(num_cidades), num_cidades) for _ in range(npop)]

def avaliar_individuo(individuo):
    distancia_individuo = 0
    for i in range(len(individuo)-1):
        distancia_individuo += distancias[individuo[i]][individuo[i+1]]

    distancia_individuo += distancias[individuo[-1]][individuo[0]]

    return distancia_individuo

        
def avaliar_população(pop):
    fitness = []
    for i in pop:
        fitness.append(avaliar_individuo(i))
    return fitness

def torneio(pop, fitness, k):
    pais = []
    for _ in range(len(pop)):
        selecionados = random.sample(range(len(pop)), k)
        melhor = min(selecionados, key=lambda i: fitness[i])
        pais.append(pop[melhor])
    return pais

def cruzamento_ox(pais, Pc, num_cidades, num_pontos):
    nova_pop = []
    ponto1, ponto2 = sorted(random.sample(range(num_cidades), num_pontos))

    for i in range(0, len(pais), 2):
        if len(nova_pop) >= npop - n_elite:
            break

        pai1 = pais[i]
        pai2 = pais[i + 1]

        filho1 = [None] * num_cidades
        filho2 = [None] * num_cidades

        if random.random() < Pc:

            filho1[ponto1:ponto2+1] = pai1[ponto1:ponto2+1]
            filho2[ponto1:ponto2+1] = pai2[ponto1:ponto2+1]

            def preencher(filho, pai):
                pos = (ponto2 + 1) % num_cidades
                for h in pai:
                    if h not in filho:
                        filho[pos] = h
                        pos = (pos + 1) % num_cidades

            preencher(filho1, pai2)
            preencher(filho2, pai1)

        else:
            filho1 = pai1[:]
            filho2 = pai2[:]

        nova_pop.append(filho1)
        nova_pop.append(filho2)

    return nova_pop

def mutacao(nova_pop, Pm):
    for individuo in nova_pop:
        for i in range(len(individuo)):
            if random.random() < Pm:
                aleatorio = random.randint(0, num_cidades - 1)
                individuo[i], individuo[aleatorio] = individuo[aleatorio], individuo[i]

def elitismo(fitness, nova_pop, n_elite, pop):
    melhores_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])
    for i in range(n_elite):
        nova_pop.append(pop[melhores_indices[i]])

def genetico_caixeiro():
    pop = criar_populacao(npop, num_cidades)
    fitness_otimo = avaliar_individuo(solucao_otima)
    melhor_fitness = float('inf')
    melhor_solucao = None
    for g in range(nger):
        fitness = avaliar_população(pop)

        if min(fitness) < melhor_fitness:
            melhor_fitness = min(fitness)
            melhor_solucao = pop[fitness.index(melhor_fitness)]

        pais = torneio(pop, fitness, k)
        nova_pop = cruzamento_ox(pais, Pc, num_cidades, num_pontos)
        mutacao(nova_pop, Pm)
        elitismo(fitness, nova_pop, n_elite, pop)
        pop = copy.deepcopy(nova_pop)

    print("\nMelhor solução encontrada:")
    print(melhor_solucao)
    print(f"Distância: {melhor_fitness}")
    print("\nSolução Ótima:")
    print(solucao_otima)
    print(f"Distância: {fitness_otimo}")
    


genetico_caixeiro()
    




