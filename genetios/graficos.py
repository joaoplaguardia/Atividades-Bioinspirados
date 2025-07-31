import pandas as pd
import matplotlib.pyplot as plt

# Caminho do arquivo CSV
file_path = "/mnt/data/estatisticas_caixeiro.csv"

# Leitura do arquivo CSV
data = pd.read_csv(file_path)

# Verificação das colunas disponíveis
columns = data.columns.tolist()

# Exibir as primeiras linhas para entender o formato
print(columns)
print(data.head())
