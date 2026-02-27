import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de rutas
DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_enriched.csv"
OUTPUT_DIR = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def perform_restructure_analysis():
    print("--- Cargando datos enriquecidos ---")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Análisis Cuantitativo
    total_records = len(df)
    # Colombia records: check if 'municipio_region' doesn't contain Ecuador etc.
    # Note: enrich_dataset logic marked common places. Let's assume Colombia if not in excluded list
    # or just filter by coordinates if we want to be very precise, but let's use the place names.
    # Actually, let's just count how many have 'Colombia' in the original 'place' or are recognized municipios.
    colombia_records = df[df['place'].str.contains('Colombia', case=False, na=False)].shape[0]
    
    print(f"Registros Totales: {total_records}")
    print(f"Registros de Colombia: {colombia_records}")
    
    # 2. Análisis de Nulos
    null_stats = df.isnull().sum()
    null_percent = (null_stats / total_records) * 100
    print("\n--- Estadísticas de Nulos ---")
    print(null_percent[null_percent > 0])
    
    # 3. Generación de Mapas Scatter
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x='longitude', y='latitude', hue='depth', palette='viridis', size='depth', sizes=(10, 200), alpha=0.6)
    plt.title('Mapa de Dispersión: Latitud vs Longitud (Color por Profundidad)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_map_depth.png'))
    plt.close()
    
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x='longitude', y='latitude', hue='mag', palette='magma', size='mag', sizes=(10, 200), alpha=0.6)
    plt.title('Mapa de Dispersión: Latitud vs Longitud (Color por Magnitud)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_map_mag.png'))
    plt.close()
    
    print(f"\nVisualizaciones guardadas en {OUTPUT_DIR}")

if __name__ == "__main__":
    perform_restructure_analysis()
