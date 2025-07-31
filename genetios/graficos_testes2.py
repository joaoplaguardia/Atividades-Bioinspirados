import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

# Caminho da pasta contendo os arquivos CSV
folder_path = "/home/joaop/Área de trabalho/faculdade/Bio/resultados/Real/npop=200_nger=500_Pc=0.8_Pm=0.1_k=2_n_elite=2"

# Busca todos os arquivos CSV na pasta
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Dicionário para acumular somas e contagens para cada geração
soma_por_geracao = {}
contagem_por_geracao = {}

for file in csv_files:
    data = pd.read_csv(file)
    
    # Verifica se as colunas existem
    if "geracao" in data.columns and "media" in data.columns:
        # Agrupa por geração e calcula a média da população
        media_por_geracao = data.groupby("geração")["média da população"].mean()
        
        # Acumula para cada geração
        for geracao, media in media_por_geracao.items():
            if geracao not in soma_por_geracao:
                soma_por_geracao[geracao] = 0
                contagem_por_geracao[geracao] = 0
            soma_por_geracao[geracao] += media
            contagem_por_geracao[geracao] += 1
    else:
        print(f"Colunas 'geração' ou 'média da população' não encontradas em {file}")

# Calcula a média das médias para cada geração
media_das_medias = {g: soma_por_geracao[g]/contagem_por_geracao[g] for g in soma_por_geracao}

# Ordena por geração
geracoes_ordenadas = sorted(media_das_medias.keys())
valores_ordenados = [media_das_medias[g] for g in geracoes_ordenadas]

# Plotar
plt.figure(figsize=(10,6))
plt.plot(geracoes_ordenadas, valores_ordenados, marker='o')
plt.xlabel("Geração")
plt.ylabel("Média das médias da população")
plt.title("Evolução da média das médias da população através das gerações")
plt.grid(True)
plt.show()
