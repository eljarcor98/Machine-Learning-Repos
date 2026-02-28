import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Configuración
DATA_PATH = 'data/earthquakes_enriched.csv'
WORLD_GEOJSON = 'data/world.geojson'
FAULTS_GEOJSON = 'data/Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson'
OUTPUT_IMG = 'documentacion/visualizaciones/evolucion_clusters_geo.png'
os.makedirs('documentacion/visualizaciones', exist_ok=True)

def generate_evolution_geo_grid():
    print("Cargando datos sísmicos...")
    df = pd.read_csv(DATA_PATH)
    features = ['latitude', 'longitude', 'depth', 'mag']
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("Cargando mapas base...")
    world = gpd.read_file(WORLD_GEOJSON)
    colombia = world[world['name'] == 'Colombia']
    
    # Cargar fallas
    try:
        faults = gpd.read_file(FAULTS_GEOJSON)
        print("Fallas cargadas con éxito.")
    except Exception as e:
        print(f"Error cargando fallas: {e}")
        faults = None

    ks = range(2, 11)
    fig, axes = plt.subplots(3, 3, figsize=(20, 20))
    axes = axes.flatten()
    
    for i, k in enumerate(ks):
        print(f"Procesando K={k}...")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # 1. Dibujar croquis de Colombia
        colombia.plot(ax=axes[i], color='#f5f6fa', edgecolor='#7f8c8d', linewidth=0.8)
        
        # 2. Dibujar fallas geológicas
        if faults is not None:
            faults.plot(ax=axes[i], color='#e17055', alpha=0.3, linewidth=0.5, label='Fallas')
        
        # 3. Dibujar sismos agrupados
        scatter = axes[i].scatter(df['longitude'], df['latitude'], c=labels, 
                                  cmap='viridis', s=10, alpha=0.7, edgecolors='none')
        
        axes[i].set_title(f'K = {k}', fontsize=16, fontweight='bold')
        axes[i].set_xlim(-82, -66) # Límites geográficos de Colombia
        axes[i].set_ylim(-4, 14)
        axes[i].set_axis_off() # Limpiar para que parezca mapa
        
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=120)
    print(f"Cuadrícula evolutiva geográfica guardada en: {OUTPUT_IMG}")

if __name__ == "__main__":
    generate_evolution_geo_grid()
