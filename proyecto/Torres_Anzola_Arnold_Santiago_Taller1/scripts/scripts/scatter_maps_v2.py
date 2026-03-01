import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os

# Configuración de rutas
DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_enriched.csv"
GEO_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\world.geojson"
OUTPUT_DIR = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def refine_visualizations():
    print("--- Cargando datos y mapa base ---")
    df = pd.read_csv(DATA_PATH)
    
    # Cargar mapa base (silueta del mundo)
    try:
        world = gpd.read_file(GEO_PATH)
    except Exception as e:
        print(f"Error cargando geojson: {e}. Se usará un fondo simple.")
        world = None

    # Filtrar área de interés para el gráfico de dispersión (Colombia y alrededores)
    # Limites aproximados: Lon -85 a -65, Lat -5 a 15
    
    # 1. Mapa de Dispersión: Profundidad (Alarmista)
    plt.figure(figsize=(12, 10))
    if world is not None:
        world.plot(ax=plt.gca(), color='#f0f0f0', edgecolor='#d0d0d0')
    
    sns.scatterplot(data=df, x='longitude', y='latitude', hue='depth', 
                    palette='YlOrRd', size='depth', sizes=(20, 300), 
                    alpha=0.7, edgecolor='black', linewidth=0.5)
    
    plt.title('Mapa de Riesgo Sísmico: Profundidad (km)', fontsize=15, fontweight='bold', color='#8B0000')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.xlim(-85, -65)
    plt.ylim(-5, 15)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(title='Profundidad (km)', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_map_depth_red.png'), dpi=300)
    plt.close()

    # 2. Mapa de Dispersión: Magnitud (Alarmista)
    plt.figure(figsize=(12, 10))
    if world is not None:
        world.plot(ax=plt.gca(), color='#f0f0f0', edgecolor='#d0d0d0')
    
    sns.scatterplot(data=df, x='longitude', y='latitude', hue='mag', 
                    palette='Reds', size='mag', sizes=(20, 300), 
                    alpha=0.8, edgecolor='black', linewidth=0.5)
    
    plt.title('Mapa de Alerta Sísmica: Magnitud', fontsize=15, fontweight='bold', color='#8B0000')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.xlim(-85, -65)
    plt.ylim(-5, 15)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(title='Magnitud', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_map_mag_red.png'), dpi=300)
    plt.close()

    # 3. Recuperar/Generar Scatter de Magnitud vs Profundidad
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='depth', y='mag', hue='mag', palette='YlOrRd', alpha=0.5)
    plt.title('Relación Magnitud vs Profundidad', fontsize=12, fontweight='bold')
    plt.xlabel('Profundidad (km)')
    plt.ylabel('Magnitud')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_mag_depth_refined.png'), dpi=300)
    plt.close()

    print(f"\nVisualizaciones refinadas guardadas en {OUTPUT_DIR}")

if __name__ == "__main__":
    refine_visualizations()
