import random
import math
import numpy as np

dimensao = 4
iteracoes = 100
tamanho_enxame = 100
w = 1  # inércia
c1 = 1  # aprendizado cognitivo
c2 = 1  # aprendizado social
limite_superior = 10
limite_inferior = -10
vizinhos = 4


class Particula:
    def __init__(self, dimensao, indice):
        self.indice = indice
        self.posicao = np.random.uniform(-10, 10, size=dimensao)
        self.velocidade = np.random.uniform(-1, 1, size=dimensao)
        self.melhor_posicao = self.posicao.copy()
        self.melhor_valor = float('inf')
        self.melhor_vizinha = np.random.uniform(-10, 10, size=dimensao)


def criar_enxame(tamanho_enxame, dimensao):
    return [Particula(dimensao, i) for i in range(tamanho_enxame)]


def atualizar_particula(particula, enxame, tamanho_enxame, w, c1, c2):
    vizinhos = []

    for offset in range(-2, 3):
        idx = (particula.indice + offset) % tamanho_enxame
        vizinhos.append(idx)

    melhor_vizinha_idx = min(
        vizinhos, key=lambda i: enxame[i].melhor_valor
    )
    particula.melhor_vizinha = enxame[melhor_vizinha_idx].melhor_posicao

    r1 = np.random.rand(len(particula.posicao))
    r2 = np.random.rand(len(particula.posicao))

    nova_velocidade = (
        w * particula.velocidade
        + c1 * r1 * (particula.melhor_posicao - particula.posicao)
        + c2 * r2 * (particula.melhor_vizinha - particula.posicao)
    )

    particula.velocidade = nova_velocidade
    nova_posicao = particula.posicao + nova_velocidade
    particula.posicao = np.clip(nova_posicao, limite_inferior, limite_superior)


def funcao_ackley(individuo):
    n = len(individuo)
    somatorio1 = sum(x ** 2 for x in individuo)
    somatorio2 = sum(math.cos(2 * math.pi * x) for x in individuo)
    termo1 = -20 * math.exp(-0.2 * math.sqrt(somatorio1 / n))
    termo2 = -math.exp(somatorio2 / n)
    return termo1 + termo2 + 20 + math.e


def pso():
    melhor_global = float('inf')
    melhor_vetor_global = None
    enxame = criar_enxame(tamanho_enxame, dimensao)

    for _ in range(iteracoes):
        for particula in enxame:
            valor_atual = funcao_ackley(particula.posicao)

            if valor_atual < particula.melhor_valor:
                particula.melhor_posicao = particula.posicao.copy()
                particula.melhor_valor = valor_atual

                if valor_atual < melhor_global:
                    melhor_global = valor_atual
                    melhor_vetor_global = particula.posicao.copy()

        for particula in enxame:
            atualizar_particula(particula, enxame, tamanho_enxame, w, c1, c2)

    print("Melhor valor encontrado:", melhor_global)
    print("Melhor vetor encontrado:", melhor_vetor_global)



pso()
