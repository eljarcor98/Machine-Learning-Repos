import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuración de rutas
DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_enriched.csv"
OUTPUT_IMG = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones\frecuencia_municipios.png"

def analyze_regions():
    print("--- Cargando datos enriquecidos ---")
    if not os.path.exists(DATA_PATH):
        print(f"Error: No se encuentra el archivo {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    
    # 1. Gráfico por Municipio
    region_counts = df['municipio_region'].value_counts().head(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=region_counts.values, y=region_counts.index, palette='magma')
    plt.title('Top 20 Municipios de Colombia con Mayor Actividad Sísmica (2010-2026)')
    plt.xlabel('Cantidad de Eventos')
    plt.ylabel('Municipio')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"Gráfico de municipios guardado en: {OUTPUT_IMG}")

    # 2. Gráfico por Departamento
    depto_counts = df['departamento'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=depto_counts.values, y=depto_counts.index, palette='viridis')
    plt.title('Actividad Sísmica por Departamento en Colombia (2010-2026)')
    plt.xlabel('Cantidad de Eventos')
    plt.ylabel('Departamento')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    DEPTO_IMG = OUTPUT_IMG.replace('municipios.png', 'departamentos.png')
    plt.savefig(DEPTO_IMG)
    print(f"Gráfico de departamentos guardado en: {DEPTO_IMG}")
    
    # Mostrar el top para la consola
    print("\nTop 10 Departamentos:")
    print(depto_counts.head(10))

if __name__ == "__main__":
    analyze_regions()
