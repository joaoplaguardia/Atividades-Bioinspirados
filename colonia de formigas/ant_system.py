import random

distancias = []
solucao_otima = []

with open('distancias_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        numeros = [int(num) for num in linha.strip().split()]
        distancias.append(numeros)

with open('resposta_caixeiro.txt', 'r') as arquivo:
    for linha in arquivo:
        numero = int(linha.strip())
        solucao_otima.append(numero - 1)

num_cidades = len(solucao_otima)
feromonio = [[1e-16 for _ in range(num_cidades)] for _ in range(num_cidades)]
iteracoes = 100
alpha = 1.0
beta = 2.0
rho = 0.5
Q = 100

class Formiga:
    def __init__(self, cidade_inicial):
        self.inicio = cidade_inicial
        self.atual = cidade_inicial
        self.caminho = [cidade_inicial]
        self.visitados = set([cidade_inicial])
        self.distancia_total = 0.0

    def visitar_cidade(self, cidade, distancia):
        self.atual = cidade
        self.caminho.append(cidade)
        self.visitados.add(cidade)
        self.distancia_total += distancia

def calcular_probabilidade(formiga_atual, distancias, feromonio, alpha, beta):
    probabilidades = [0.0] * num_cidades
    atual = formiga_atual.atual

    for j in range(num_cidades):
        if j in formiga_atual.visitados:
            continue

        tau = feromonio[atual][j]
        d = distancias[atual][j]
        eta = 1 / d if d > 0 else 1e10

        valor = (tau ** alpha) * (eta ** beta)
        probabilidades[j] = valor

    soma = sum(probabilidades)
    if soma == 0:
        return [1 if j not in formiga_atual.visitados else 0 for j in range(num_cidades)]
    
    return [p / soma for p in probabilidades]

def escolher_cidade(probabilidades):
    cidades = list(range(num_cidades))
    return random.choices(cidades, weights=probabilidades, k=1)[0]

def jornada_formiga(formiga_atual, distancias, feromonio, alpha, beta, melhor_caminho, melhor_distancia):
    while len(formiga_atual.visitados) < num_cidades:
        probabilidades = calcular_probabilidade(formiga_atual, distancias, feromonio, alpha, beta)
        proxima_cidade = escolher_cidade(probabilidades)
        formiga_atual.visitar_cidade(proxima_cidade, distancias[formiga_atual.atual][proxima_cidade])

    formiga_atual.visitar_cidade(formiga_atual.inicio, distancias[formiga_atual.atual][formiga_atual.inicio])

    if formiga_atual.distancia_total < melhor_distancia:
        melhor_distancia = formiga_atual.distancia_total
        melhor_caminho = formiga_atual.caminho[:]

    return melhor_caminho, melhor_distancia

def atualizar_feromonio(feromonio, formigas, rho, Q):
    for i in range(num_cidades):
        for j in range(num_cidades):
            feromonio[i][j] *= (1 - rho)

    for formiga in formigas:
        contrib = Q / formiga.distancia_total
        for i in range(len(formiga.caminho) - 1):
            a = formiga.caminho[i]
            b = formiga.caminho[i + 1]
            feromonio[a][b] += contrib
            feromonio[b][a] += contrib

def ant_system():
    melhor_caminho = []
    melhor_distancia = float('inf')

    for _ in range(iteracoes):
        formigas = [Formiga(cidade_inicial=i) for i in range(num_cidades)]
        for formiga in formigas:
            melhor_caminho, melhor_distancia = jornada_formiga(formiga, distancias, feromonio, alpha, beta, melhor_caminho, melhor_distancia)

        atualizar_feromonio(feromonio, formigas, rho, Q)

    print("Melhor distância:", melhor_distancia)
    print("Melhor caminho:", melhor_caminho)

ant_system()
