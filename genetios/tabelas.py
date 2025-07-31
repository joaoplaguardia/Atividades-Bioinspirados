import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def gerar_top30_tabela(caminho_csv, saida_csv="top30.csv", saida_img="top30.png", maximizacao=True):
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(caminho_csv)

    # Ordenação baseada no objetivo
    if maximizacao:
        df_ordenado = df.sort_values(by=["Melhor μ", "Média μ"], ascending=[False, False])
    else:
        df_ordenado = df.sort_values(by=["Melhor μ", "Média μ"], ascending=[True, True])

    top30 = df_ordenado.head(30)
    top30.to_csv(saida_csv, index=False)

    # Plot da tabela
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.axis("off")
    tabela = ax.table(
        cellText=top30.values,
        colLabels=top30.columns,
        cellLoc="center",
        loc="center"
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1.2, 1.2)
    plt.savefig(saida_img, bbox_inches="tight")
    plt.close()
    print(f"Tabela salva como: {saida_csv}")
    print(f"Imagem salva como: {saida_img}")

# Exemplo de uso:
gerar_top30_tabela("resultados/Mochila/tabela_resumo.csv")
