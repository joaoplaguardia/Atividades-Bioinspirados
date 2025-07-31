
import itertools
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

# Função de avaliação (Ackley)
def funcao_ackley(individuo):
    n = len(individuo)
    somatorio1 = sum(x ** 2 for x in individuo)
    somatorio2 = sum(math.cos(2 * math.pi * x) for x in individuo)
    termo1 = -20 * math.exp(-0.2 * math.sqrt(somatorio1 / n))
    termo2 = -math.exp(somatorio2 / n)
    return termo1 + termo2 + 20 + math.e

# Partícula
class Particula:
    def __init__(self, dimensao, indice):
        self.indice = indice
        self.posicao = np.random.uniform(-10, 10, size=dimensao)
        self.velocidade = np.random.uniform(-1, 1, size=dimensao)
        self.melhor_posicao = self.posicao.copy()
        self.melhor_valor = float('inf')
        self.melhor_vizinha = np.random.uniform(-10, 10, size=dimensao)

# PSO
def pso(dimensao, iteracoes, tamanho_enxame, w, c1, c2):
    limite_superior = 10
    limite_inferior = -10
    enxame = [Particula(dimensao, i) for i in range(tamanho_enxame)]
    melhor_global = float('inf')
    melhor_vetor_global = None

    historico_melhor = []

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
            vizinhos = [(particula.indice + i) % tamanho_enxame for i in range(-2, 3)]
            melhor_vizinha_idx = min(vizinhos, key=lambda i: enxame[i].melhor_valor)
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

        historico_melhor.append(melhor_global)

    return melhor_global, historico_melhor

# Execução dos testes fatoriais
def main():
    dimensao = 4
    iteracoes = 100
    tamanho_enxame = 30
    valores_w = [0.5, 1.0, 1.5]
    valores_c1 = [1.0, 1.5, 2.0]
    valores_c2 = [1.0, 1.5, 2.0]
    repeticoes = 10

    historicos_todos = []
    registros = []

    for w, c1, c2 in itertools.product(valores_w, valores_c1, valores_c2):
        for rep in range(repeticoes):
            _, historico = pso(dimensao, iteracoes, tamanho_enxame, w, c1, c2)
            historicos_todos.append(historico)
            registros.append({
                'w': w, 'c1': c1, 'c2': c2,
                'melhor_valor': historico[-1],
                'media': np.mean(historico),
                'desvio': np.std(historico),
                'historico': historico
            })

    # Ordenar pelas melhores soluções finais
    registros_ordenados = sorted(registros, key=lambda x: x['melhor_valor'])[:30]
    df_top30 = pd.DataFrame([{
        'w': r['w'],
        'c1': r['c1'],
        'c2': r['c2'],
        'Melhor Aptidão Final': r['melhor_valor'],
        'Média das Aptidões': r['media'],
        'Desvio Padrão': r['desvio']
    } for r in registros_ordenados])

    # Salvar tabela como imagem
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    tabela = ax.table(cellText=df_top30.values,
                      colLabels=df_top30.columns,
                      loc='center',
                      cellLoc='center')
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1.2, 1.5)
    plt.savefig("tabela_top30_pso.png", bbox_inches='tight', dpi=300)
    plt.close()

    # Gerar gráfico global com melhor, pior, média e mediana
    finais = [h[-1] for h in historicos_todos]
    melhor_idx = np.argmin(finais)
    pior_idx = np.argmax(finais)
    mediana_idx = np.argsort(finais)[len(finais)//2]
    media_historico = np.mean(historicos_todos, axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(historicos_todos[melhor_idx], label="Melhor execução", color="blue")
    plt.plot(historicos_todos[pior_idx], label="Pior execução", color="red")
    plt.plot(historicos_todos[mediana_idx], label="Execução mediana", color="green")
    plt.plot(media_historico, label="Média de todas execuções", color="orange")
    plt.xlabel("Geração")
    plt.ylabel("Aptidão")
    plt.title("Evolução global das execuções do PSO")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafico_global_pso.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
