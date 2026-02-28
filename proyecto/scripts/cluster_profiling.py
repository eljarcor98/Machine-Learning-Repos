import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os

# Configuración
DATA_PATH = 'data/earthquakes_enriched.csv'
WORLD_GEOJSON = 'data/world.geojson'
OUTPUT_DIR = 'documentacion/visualizaciones'
REPORT_STATS = 'documentacion/stats_clusters.csv'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def profile_clusters():
    print("Cargando datos con clusters...")
    df = pd.read_csv(DATA_PATH)
    
    if 'cluster' not in df.columns:
        print("Error: Columna 'cluster' no encontrada. Ejecute apply_k7_model.py primero.")
        return

    # 1. Estadísticas Descriptivas por Cluster
    stats = df.groupby('cluster').agg({
        'mag': ['count', 'mean', 'std', 'min', 'max'],
        'depth': ['mean', 'std', 'min', 'max'],
        'latitude': ['mean', 'min', 'max'],
        'longitude': ['mean', 'min', 'max'],
        'departamento': lambda x: x.mode().iloc[0] if not x.mode().empty else 'Desconocido'
    })
    
    # Guardar stats para referencia
    stats.to_csv(REPORT_STATS)
    print(f"Estadísticas guardadas en: {REPORT_STATS}")
    print("\n--- RESUMEN POR CLUSTER ---")
    print(stats[['mag', 'depth']].to_string())

    # 2. Visualización Geográfica (Latitud vs Longitud)
    print("\nGenerando mapa de clusters...")
    world = gpd.read_file(WORLD_GEOJSON)
    colombia = world[world['name'] == 'Colombia']
    
    plt.figure(figsize=(12, 10))
    ax = colombia.plot(color='#f5f6fa', edgecolor='#7f8c8d', linewidth=0.8)
    
    # Graficar sismos por cluster
    sns.scatterplot(data=df, x='longitude', y='latitude', hue='cluster', 
                    palette='tab10', s=25, alpha=0.8, ax=ax)
    
    plt.title('DISTRIBUCIÓN GEOGRÁFICA DE LOS 7 CLUSTERS SÍSMICOS', fontsize=16, fontweight='bold')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.xlim(-82, -66)
    plt.ylim(-4, 14)
    plt.grid(True, alpha=0.2)
    plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/mapa_clusters_fase5.png", dpi=120)
    print(f"Mapa guardado en: {OUTPUT_DIR}/mapa_clusters_fase5.png")

if __name__ == "__main__":
    profile_clusters()
