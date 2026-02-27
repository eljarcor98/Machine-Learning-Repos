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
    
    # Análisis de Frecuencia por Región/Municipio
    print("\n--- Analizando Frecuencia por Municipio/Región ---")
    region_counts = df['municipio_region'].value_counts().head(20)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=region_counts.values, y=region_counts.index, palette='magma')
    plt.title('Top 20 Lugares con Mayor Actividad Sísmica (2010-2026)')
    plt.xlabel('Cantidad de Eventos')
    plt.ylabel('Municipio / Región')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig(OUTPUT_IMG)
    print(f"Gráfico de frecuencia guardado en: {OUTPUT_IMG}")
    
    # Mostrar el top para la consola
    print("\nTop 10 Regiones:")
    print(region_counts.head(10))

if __name__ == "__main__":
    analyze_regions()
