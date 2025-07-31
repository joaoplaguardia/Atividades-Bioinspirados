import numpy as np
import matplotlib.pyplot as plt
import statistics

def executar_algoritmo(npop, nger, Pc, Pm, k, n_elite):
    import random
    import copy

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

    def criar_populacao(npop, num_cidades):
        return [random.sample(range(num_cidades), num_cidades) for _ in range(npop)]

    def avaliar_individuo(individuo):
        distancia = sum(distancias[individuo[i]][individuo[i + 1]] for i in range(len(individuo) - 1))
        distancia += distancias[individuo[-1]][individuo[0]]
        return distancia

    def avaliar_populacao(pop):
        return [avaliar_individuo(ind) for ind in pop]

    def torneio(pop, fitness, k):
        pais = []
        for _ in range(len(pop)):
            selecionados = random.sample(range(len(pop)), k)
            melhor = min(selecionados, key=lambda i: fitness[i])
            pais.append(copy.deepcopy(pop[melhor]))
        return pais

    def cruzamento_pmx(pais, Pc, num_cidades):
        nova_pop = []
        for i in range(0, len(pais), 2):
            if i + 1 >= len(pais):
                break

            pai1 = pais[i]
            pai2 = pais[i + 1]

            filho1 = pai1[:]
            filho2 = pai2[:]

            if random.random() < Pc:
                p1, p2 = sorted(random.sample(range(num_cidades), 2))

                def pmx(f1, f2, start, end):
                    mapeamento = {}
                    for i in range(start, end + 1):
                        f1[i], f2[i] = f2[i], f1[i]
                        mapeamento[f2[i]] = f1[i]

                    def ajustar(filho, start, end):
                        for i in range(len(filho)):
                            if start <= i <= end:
                                continue
                            visitados = set()
                            while filho[i] in mapeamento:
                                if filho[i] in visitados:
                                    break
                                visitados.add(filho[i])
                                filho[i] = mapeamento[filho[i]]

                    ajustar(f1, start, end)
                    ajustar(f2, start, end)

                pmx(filho1, filho2, p1, p2)

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
            todos_fitness.append(fitness[:])

            pais = torneio(pop, fitness, k)
            nova_pop = cruzamento_pmx(pais, Pc, num_cidades)
            mutacao(nova_pop, Pm)
            elitismo(fitness, nova_pop, n_elite, pop)

            pop = nova_pop

        return melhor_por_geracao, media_por_geracao, todos_fitness

    return genetico_caixeiro()


def testar_algoritmo(n_execucoes, npop, nger, Pc, Pm, k, n_elite):
    todas_execucoes = []

    for i in range(n_execucoes):
        print(f"Execução {i + 1}/{n_execucoes}")
        melhor, media, todos = executar_algoritmo(npop, nger, Pc, Pm, k, n_elite)
        todas_execucoes.append(melhor)

    todas_execucoes = np.array(todas_execucoes)  # shape: (n_execucoes, nger)

    melhor = np.min(todas_execucoes, axis=0)
    pior = np.max(todas_execucoes, axis=0)
    media = np.mean(todas_execucoes, axis=0)
    mediana = np.median(todas_execucoes, axis=0)

    # Gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(melhor, label='Melhor')
    plt.plot(pior, label='Pior')
    plt.plot(media, label='Média')
    plt.plot(mediana, label='Mediana')
    plt.xlabel("Geração")
    plt.ylabel("Distância")
    plt.title("Evolução da aptidão - TSP com AG PMX")
    plt.legend(loc='right')
    plt.grid(True)
    plt.show()

# Exemplo de chamada:
# testar_algoritmo(n_execucoes=10, npop=100, nger=100, Pc=0.9, Pm=0.1, k=3, n_elite=2)
