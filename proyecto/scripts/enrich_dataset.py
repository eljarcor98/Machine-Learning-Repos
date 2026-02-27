import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración
input_path = 'data/earthquakes_raw.csv'
output_path = 'data/earthquakes_enriched.csv'
viz_dir = 'documentacion/visualizaciones'
os.makedirs(viz_dir, exist_ok=True)

# Coordenadas aproximadas de fallas geológicas principales en Colombia
# Formato: (Nombre, Punto_Referencia_Lat, Punto_Referencia_Lon, Direccion_Aprox)
FALLAS_COLOMBIA = [
    {"nombre": "Falla de Romeral", "lat": 5.0, "lon": -75.5},
    {"nombre": "Falla de Bucaramanga-Santa Marta", "lat": 7.1, "lon": -73.1},
    {"nombre": "Falla Frontal Cordillera Oriental", "lat": 4.5, "lon": -73.7},
    {"nombre": "Falla de Algeciras", "lat": 2.3, "lon": -75.3},
    {"nombre": "Falla de Murindo", "lat": 6.8, "lon": -76.8}
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def get_municipality(place):
    if pd.isna(place): return "Desconocido"
    parts = place.split(', ')
    if len(parts) > 1:
        # Intenta obtener el municipio que suele estar antes de la coma final (región/país)
        sub_parts = parts[0].split(' of ')
        return sub_parts[-1]
    return place

def enrich_data():
    print("Cargando datos...")
    df = pd.read_csv(input_path)
    
    # 1. Extraer Municipio/Región
    print("Extrayendo municipios...")
    df['municipio_region'] = df['place'].apply(get_municipality)
    
    # 2. Magnitud vs Profundidad (Interacción)
    # Una métrica que combine ambos. Por ejemplo: mag / log1p(depth) 
    # Sismos superficiales con alta magnitud suelen tener mayor impacto.
    print("Calculando interacción Magnitud vs Profundidad...")
    df['mag_depth_ratio'] = df['mag'] / np.log1p(df['depth'])
    
    # 3. Sismos por Zona (Frecuencia en un radio de 0.5 grados ~55km)
    print("Calculando densidad de sismos por zona...")
    # Usamos un agrupamiento por grid simple para aproximar zonas
    df['grid_lat'] = df['latitude'].round(1)
    df['grid_lon'] = df['longitude'].round(1)
    zona_counts = df.groupby(['grid_lat', 'grid_lon']).size().reset_index(name='sismos_por_zona')
    df = df.merge(zona_counts, on=['grid_lat', 'grid_lon'], how='left')
    
    # 4. Proximidad a Fallas Geológicas
    print("Identificando proximidad a fallas...")
    def check_fault_proximity(row):
        for falla in FALLAS_COLOMBIA:
            dist = haversine(row['latitude'], row['longitude'], falla['lat'], falla['lon'])
            if dist < 100: # Umbral de 100km de influencia
                return f"Cerca de {falla['nombre']}"
        return "Sin falla principal cercana"
    
    df['proximidad_falla'] = df.apply(check_fault_proximity, axis=1)
    
    # 5. Generar Boxplots
    print("Generando visualizaciones comparativas...")
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    sns.boxplot(y=df['mag'], color='orange')
    plt.title('Distribución de Magnitudes')
    plt.ylabel('Magnitud (Richter)')
    
    plt.subplot(1, 2, 2)
    sns.boxplot(y=df['depth'], color='lightblue')
    plt.title('Distribución de Profundidades')
    plt.ylabel('Profundidad (km)')
    
    plt.tight_layout()
    plt.savefig(f"{viz_dir}/boxplots_escalas.png")
    plt.close()
    
    # Gráfico de comparación de escalas (Estandarizado para ver juntos)
    plt.figure(figsize=(10, 6))
    mag_scaled = (df['mag'] - df['mag'].mean()) / df['mag'].std()
    depth_scaled = (df['depth'] - df['depth'].mean()) / df['depth'].std()
    
    sns.kdeplot(mag_scaled, label='Magnitud (Std)', fill=True)
    sns.kdeplot(depth_scaled, label='Profundidad (Std)', fill=True)
    plt.title('Comparación de Escalas: Magnitud vs Profundidad (Estandarizadas)')
    plt.legend()
    plt.savefig(f"{viz_dir}/comparativa_escalas_kde.png")
    plt.close()

    # 6. Guardar Dataset
    df.to_csv(output_path, index=False)
    print(f"Dataset enriquecido guardado en: {output_path}")

if __name__ == "__main__":
    enrich_data()
