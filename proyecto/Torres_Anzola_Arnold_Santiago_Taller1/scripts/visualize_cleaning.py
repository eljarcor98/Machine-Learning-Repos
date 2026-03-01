import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os

# Configuración de rutas
RAW_DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_raw.csv"
CLEAN_DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_cleaned.csv"
WORLD_GEOJSON = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\world.geojson"
OUTPUT_FIG = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones\comparativa_limpieza_geografica.png"

def plot_comparison():
    print("Cargando datos y mapa...")
    df_raw = pd.read_csv(RAW_DATA_PATH)
    df_clean = pd.read_csv(CLEAN_DATA_PATH)
    
    # Intentar cargar el mapa
    try:
        world = gpd.read_file(WORLD_GEOJSON)
        # Filtrar solo la zona de interés para acelerar el dibujo si es necesario, 
        # o simplemente usarlo de fondo.
    except Exception as e:
        print(f"Error cargando mapa: {e}")
        world = None

    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), sharex=True, sharey=True)
    
    # Límites de la visualización (para que ambos se vean igual)
    lon_lims = [-95, -60]
    lat_lims = [-15, 25]

    for ax, data, title in zip([ax1, ax2], [df_raw, df_clean], ["Antes de la Limpieza", "Después (Solo Colombia)"]):
        # Dibujar mapa de fondo
        if world is not None:
            world.plot(ax=ax, color='lightgrey', edgecolor='white', alpha=0.5)
        
        # Dibujar sismos
        sns.scatterplot(
            data=data, x='longitude', y='latitude', 
            hue='mag', palette='Reds', alpha=0.5, 
            ax=ax, size='mag', sizes=(5, 150),
            legend='brief' if ax == ax2 else False
        )
        
        ax.set_title(f'{title}\n({len(data)} sismos)', fontsize=14)
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud' if ax == ax1 else '')
        ax.set_xlim(lon_lims)
        ax.set_ylim(lat_lims)
        ax.grid(True, linestyle='--', alpha=0.3)

    plt.suptitle('Impacto del Filtrado Geográfico en el Territorio Colombiano', fontsize=18, y=1.02)
    plt.tight_layout()
    
    # Guardar
    os.makedirs(os.path.dirname(OUTPUT_FIG), exist_ok=True)
    plt.savefig(OUTPUT_FIG, bbox_inches='tight', dpi=300)
    print(f"Gráfico comparativo con mapa guardado en: {OUTPUT_FIG}")

if __name__ == "__main__":
    plot_comparison()
