import random, math, copy
import matplotlib.pyplot as plt
import numpy as np

# === CONFIG GERAL ===
npop = 100
nger = 100
n_elite = 2
Pc = 1.0
Pm_bin = 0.01
Pm_real = 0.01
Pm_mochila = 0.05
num_execucoes = 10

# === MOCHILA ===
def carregar_mochila(path):
    capacidade = None
    valores, pesos, solucao_otima = [], [], []
    leitura = None
    with open(path, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha: continue
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

# === AG BINÁRIO - ACKLEY ===
def ackley(x):
    n = len(x)
    s1 = sum(i**2 for i in x)
    s2 = sum(math.cos(2*math.pi*i) for i in x)
    return -20 * math.exp(-0.2 * math.sqrt(s1/n)) - math.exp(s2/n) + 20 + math.e

def bin_to_real(bits, bits_por_var, lim_inf, lim_sup):
    inteiro = int("".join(str(b) for b in bits), 2)
    max_int = 2**len(bits) - 1
    return lim_inf + (lim_sup - lim_inf) * inteiro / max_int

def decode_individual(ind, n_vars, bits_por_var, lim_inf, lim_sup):
    return [bin_to_real(ind[i:i+bits_por_var], bits_por_var, lim_inf, lim_sup)
            for i in range(0, len(ind), bits_por_var)]

def executar_ag_binario():
    n_vars, bits_por_var = 2, 16
    total_bits = n_vars * bits_por_var
    lim_inf, lim_sup = -2, 2
    k = 3
    resultados = []

    for _ in range(num_execucoes):
        pop = [[random.randint(0,1) for _ in range(total_bits)] for _ in range(npop)]
        historico = []
        for _ in range(nger):
            fitness = [ackley(decode_individual(ind, n_vars, bits_por_var, lim_inf, lim_sup)) for ind in pop]
            historico.append(fitness)
            paises = [min(random.sample(range(npop), k), key=lambda i: fitness[i]) for _ in range(npop)]
            nova = []
            for i in range(0, npop, 2):
                p1 = pop[paises[i]]
                p2 = pop[paises[(i+1)%npop]]
                if random.random() < Pc:
                    pt = random.randint(1, total_bits-1)
                    f1 = p1[:pt]+p2[pt:]
                    f2 = p2[:pt]+p1[pt:]
                else:
                    f1, f2 = p1[:], p2[:]
                nova.extend([f1,f2])
            for ind in nova:
                for i in range(total_bits):
                    if random.random() < Pm_bin:
                        ind[i] ^= 1
            elites = sorted(range(npop), key=lambda i: fitness[i])[:n_elite]
            for i in range(n_elite):
                nova[i] = copy.deepcopy(pop[elites[i]])
            pop = copy.deepcopy(nova)
        resultados.append(historico)
    return resultados, "AG Binário - Ackley"

# === AG REAL - BLX ===
def executar_ag_blx():
    n_vars = 2
    lim_inf, lim_sup = -2, 2
    alpha, beta = 0.75, 0.25
    resultados = []

    for _ in range(num_execucoes):
        pop = [[random.uniform(lim_inf, lim_sup) for _ in range(n_vars)] for _ in range(npop)]
        historico = []
        for _ in range(nger):
            fit = [ackley(ind) for ind in pop]
            historico.append(fit)
            inv = [1/(f+1e-9) for f in fit]
            total = sum(inv)
            probs = [v/total for v in inv]
            paises = [np.random.choice(range(npop), p=probs) for _ in range(npop)]
            nova = []
            for i in range(0, npop, 2):
                p1 = pop[paises[i]]
                p2 = pop[paises[(i+1)%npop]]
                if random.random() < Pc:
                    f1, f2 = [], []
                    for x1, x2 in zip(p1, p2):
                        d = abs(x1 - x2)
                        min_v = min(x1, x2) - alpha * d
                        max_v = max(x1, x2) + beta * d
                        f1.append(random.uniform(min_v, max_v))
                        f2.append(random.uniform(min_v, max_v))
                else:
                    f1, f2 = p1[:], p2[:]
                nova.extend([f1, f2])
            for ind in nova:
                for i in range(len(ind)):
                    if random.random() < Pm_real:
                        ind[i] = random.uniform(lim_inf, lim_sup)
            elites = sorted(range(npop), key=lambda i: fit[i])[:n_elite]
            for i in range(n_elite):
                nova[i] = copy.deepcopy(pop[elites[i]])
            pop = copy.deepcopy(nova)
        resultados.append(historico)
    return resultados, "AG Real - BLX - Ackley"

# === AG MOCHILA ===
def executar_ag_mochila(cap, val, pes, otima):
    num_itens = len(val)
    pontos = num_itens // 2
    resultados = []

    def avaliar(ind):
        peso, valor = 0, 0
        for i, bit in enumerate(ind):
            if bit:
                peso += pes[i]
                valor += val[i]
        return 0 if peso > cap else valor

    for _ in range(num_execucoes):
        pop = [[random.randint(0, 1) for _ in range(num_itens)] for _ in range(npop)]
        historico = []
        for _ in range(nger):
            fit = [avaliar(ind) for ind in pop]
            historico.append(fit)
            pais = [max(random.sample(range(npop), 2), key=lambda i: fit[i]) for _ in range(npop)]
            nova = []
            for i in range(0, npop, 2):
                p1 = pop[pais[i]]
                p2 = pop[pais[(i+1)%npop]]
                if random.random() < Pc:
                    f1 = p1[:pontos] + p2[pontos:]
                    f2 = p2[:pontos] + p1[pontos:]
                else:
                    f1, f2 = p1[:], p2[:]
                nova.extend([f1,f2])
            for ind in nova:
                for i in range(num_itens):
                    if random.random() < Pm_mochila:
                        ind[i] = 1 - ind[i]
            elites = sorted(range(npop), key=lambda i: fit[i], reverse=True)[:n_elite]
            for i in range(n_elite):
                nova.append(pop[elites[i]])
            pop = copy.deepcopy(nova[:npop])
        resultados.append(historico)
    return resultados, "AG Mochila"

# === PLOT RESULTADOS ===
def plot_resultados(resultados, titulo):
    melhor_execucao = min(resultados, key=lambda r: min(r[-1]))
    stats = {'melhor': [], 'pior': [], 'media': [], 'mediana': []}
    for g in range(nger):
        todos = [fit[g] for fit in resultados]
        flat = [f for sub in todos for f in sub]
        stats['melhor'].append(max(flat))
        stats['pior'].append(min(flat))
        stats['media'].append(np.mean(flat))
        stats['mediana'].append(np.median(flat))

    plt.figure(figsize=(12, 6))
    for chave, val in stats.items():
        plt.plot(val, label=chave.capitalize())
    plt.title(f"Estatísticas - {titulo}")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot([max(f) for f in melhor_execucao], label="Melhor Execução")
    plt.title(f"Melhor Execução - {titulo}")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

# === EXECUTAR TUDO ===
if __name__ == "__main__":
    mochila_path = "dados_mochila.txt"
    capacidade, valores, pesos, solucao_otima = carregar_mochila(mochila_path)

    for exec_fn in [executar_ag_binario, executar_ag_blx]:
        resultados, titulo = exec_fn()
        plot_resultados(resultados, titulo)

    resultados, titulo = executar_ag_mochila(capacidade, valores, pesos, solucao_otima)
    plot_resultados(resultados, titulo)
