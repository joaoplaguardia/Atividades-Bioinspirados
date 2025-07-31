import numpy as np
import random

# Função de leitura com o caminho correto
def ler_dados_arquivo(caminho='datasets/dados_mochila.txt'):
    capacidade = 0
    valores = []
    pesos = []
    solucao_otima = []
    leitura = ''

    with open(caminho, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha == '':
                continue

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

    return capacidade, valores, pesos, solucao_otima


def executar_algoritmo(npop, nger, Pc, Pm, k, n_elite):
    # Usa o caminho correto por padrão
    capacidade, valores, pesos, _ = ler_dados_arquivo('datasets/dados_mochila.txt')
    n = len(pesos)

    def fitness(ind):
        total_peso = sum(p * i for p, i in zip(pesos, ind))
        total_valor = sum(v * i for v, i in zip(valores, ind))
        if total_peso <= capacidade:
            return total_valor
        else:
            excesso = total_peso - capacidade
            return total_valor - excesso * 10

    def selecao_torneio(pop, k):
        return max(random.sample(pop, k), key=lambda x: x[1])

    def cruzamento(pai1, pai2):
        if random.random() > Pc:
            return pai1[0][:], pai2[0][:]
        ponto = random.randint(1, n - 1)
        filho1 = pai1[0][:ponto] + pai2[0][ponto:]
        filho2 = pai2[0][:ponto] + pai1[0][ponto:]
        return filho1, filho2

    def mutacao(ind):
        for i in range(n):
            if random.random() < Pm:
                ind[i] = 1 - ind[i]
        return ind

    pop = [[[random.randint(0, 1) for _ in range(n)], 0] for _ in range(npop)]
    for ind in pop:
        ind[1] = fitness(ind[0])

    melhor_por_geracao = []
    media_por_geracao = []

    for _ in range(nger):
        nova_pop = []

        pop.sort(key=lambda x: x[1], reverse=True)
        elite = pop[:n_elite]
        nova_pop.extend([[e[0][:], e[1]] for e in elite])

        while len(nova_pop) < npop:
            pai1 = selecao_torneio(pop, k)
            pai2 = selecao_torneio(pop, k)
            filho1, filho2 = cruzamento(pai1, pai2)
            filho1 = mutacao(filho1)
            filho2 = mutacao(filho2)
            nova_pop.append([filho1, fitness(filho1)])
            if len(nova_pop) < npop:
                nova_pop.append([filho2, fitness(filho2)])

        pop = nova_pop
        fitness_geracao = [ind[1] for ind in pop]
        melhor_por_geracao.append(max(fitness_geracao))
        media_por_geracao.append(np.mean(fitness_geracao))

    return melhor_por_geracao, media_por_geracao, None
