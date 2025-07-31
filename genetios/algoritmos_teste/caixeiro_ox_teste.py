def executar_algoritmo(npop, nger, Pc, Pm, k, n_elite):
    import random
    import copy
    import numpy as np

    distancias = []
    solucao_otima = []

    with open('datasets/distancias_caixeiro.txt', 'r') as arquivo:
        for linha in arquivo:
            numeros = [int(num) for num in linha.strip().split()]
            distancias.append(numeros)

    with open('datasets/resposta_caixeiro.txt', 'r') as arquivo:
        for linha in arquivo:
            numero = int(linha.strip())
            solucao_otima.append(numero - 1)

    num_cidades = len(solucao_otima)
    num_pontos = 2  # Para OX

    def criar_populacao(npop, num_cidades):
        return [random.sample(range(num_cidades), num_cidades) for _ in range(npop)]

    def avaliar_individuo(individuo):
        distancia = 0
        for i in range(len(individuo) - 1):
            distancia += distancias[individuo[i]][individuo[i + 1]]
        distancia += distancias[individuo[-1]][individuo[0]]
        return distancia

    def avaliar_populacao(pop):
        return [avaliar_individuo(ind) for ind in pop]

    def torneio(pop, fitness, k):
        pais = []
        for _ in range(len(pop)):
            selecionados = random.sample(range(len(pop)), k)
            melhor = min(selecionados, key=lambda i: fitness[i])
            pais.append(pop[melhor])
        return pais

    def cruzamento_ox(pais, Pc, num_cidades, num_pontos):
        nova_pop = []
        for i in range(0, len(pais), 2):
            if len(nova_pop) >= npop - n_elite:
                break

            pai1 = pais[i]
            pai2 = pais[i + 1]

            filho1 = [None] * num_cidades
            filho2 = [None] * num_cidades

            if random.random() < Pc:
                ponto1, ponto2 = sorted(random.sample(range(num_cidades), num_pontos))

                filho1[ponto1:ponto2 + 1] = pai1[ponto1:ponto2 + 1]
                filho2[ponto1:ponto2 + 1] = pai2[ponto1:ponto2 + 1]

                def preencher(filho, pai):
                    pos = (ponto2 + 1) % num_cidades
                    for gene in pai:
                        if gene not in filho:
                            while filho[pos] is not None:
                                pos = (pos + 1) % num_cidades
                            filho[pos] = gene

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
            if random.random() < Pm:
                i, j = random.sample(range(num_cidades), 2)
                individuo[i], individuo[j] = individuo[j], individuo[i]

    def elitismo(fitness, nova_pop, n_elite, pop):
        melhores_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])
        for i in range(n_elite):
            nova_pop.append(copy.deepcopy(pop[melhores_indices[i]]))

    def genetico_caixeiro():
        pop = criar_populacao(npop, num_cidades)

        melhor_por_geracao = []
        media_por_geracao = []
        todos_fitness = []

        for g in range(nger):
            fitness = avaliar_populacao(pop)

            melhor_por_geracao.append(min(fitness))
            media_por_geracao.append(np.mean(fitness))
            todos_fitness.append(fitness[:])  # cópia

            pais = torneio(pop, fitness, k)
            nova_pop = cruzamento_ox(pais, Pc, num_cidades, num_pontos)
            mutacao(nova_pop, Pm)
            elitismo(fitness, nova_pop, n_elite, pop)

            pop = copy.deepcopy(nova_pop)

        return melhor_por_geracao, media_por_geracao, todos_fitness

    return genetico_caixeiro()
