import random
import copy

capacidade = None
valores = []
pesos = []
solucao_otima = []
leitura = None


with open('datasets/dados_mochila.txt', 'r') as arquivo:
    for linha in arquivo:
        linha = linha.strip()

        if linha == '': continue

        if linha.endswith(':'): 
            leitura = linha[:-1]
            continue

        if leitura == 'capacidade':
            capacidade = int(linha)
        elif leitura == 'valores':
            valores.append(int(linha))
        elif leitura == 'pesos':
            pesos.append(int(linha))
        elif leitura == 'solucao':
            solucao_otima.append(int(linha))

num_itens = len(solucao_otima)
k = 2
npop = 100
nger = 100
n_elite = 2
Pc = 1.00
pontos = num_itens//2
Pm = 0.05

def criar_populacao(npop, num_itens):
    return [[random.randint(0, 1) for _ in range(num_itens)] for _ in range(npop)]

def avaliar_individuo(individuo):
    valor_individuo = 0
    peso_individuo = 0
    for idx, i in enumerate(individuo):
        if i == 1:
            valor_individuo += valores[idx]
            peso_individuo += pesos[idx]
    if peso_individuo > capacidade:
        return 0
    return valor_individuo

        
def avaliar_população(pop):
    fitness = []
    for i in pop:
        fitness.append(avaliar_individuo(i))
    return fitness

def torneio(pop, fitness, k):
    pais = []
    for _ in range(len(pop)):
        selecionados = random.sample(range(len(pop)), k)
        melhor = max(selecionados, key=lambda i: fitness[i])
        pais.append(pop[melhor])
    return pais

def cruzamento(pais, Pc, pontos):
    nova_pop = []
    for i in range (0, len(pais), 2):
        pai1 = pais[i]
        pai2 = pais[i+1]

        if random.random() < Pc:
            filho1 = pai1[:pontos] + pai2[pontos:]
            filho2 = pai2[:pontos] + pai1[pontos:]
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
                individuo[i] =  1 - individuo[i]

def elitismo(fitness, nova_pop, n_elite, pop):
    melhores_indices = sorted(range(len(fitness)), key=lambda i: fitness[i], reverse=True)
    for i in range(n_elite):
        nova_pop.append(pop[melhores_indices[i]])

def genetico_mochila():
    pop = criar_populacao(npop, num_itens)
    for g in range(nger):
        fitness = avaliar_população(pop)
        pais = torneio(pop, fitness, k)
        nova_pop = cruzamento(pais, Pc, pontos)
        mutacao(nova_pop, Pm)
        elitismo(fitness, nova_pop, n_elite, pop)
        pop = copy.deepcopy(nova_pop)

    valor_otimo = sum(val for val, escolhido in zip(valores, solucao_otima) if escolhido == 1)
    fitness_final = avaliar_população(pop)
    melhor_idx = max(range(len(fitness_final)), key=lambda i: fitness_final[i])
    melhor_individuo = pop[melhor_idx]
    valor_total = sum(val for val, escolhido in zip(valores, melhor_individuo) if escolhido == 1)

    print("Melhor solução:", pop[melhor_idx])
    print("valor:", valor_total)
    print("Solução Ótima:", solucao_otima)
    print("valor:", valor_otimo)

    

genetico_mochila()
    




