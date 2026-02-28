import pandas as pd
import os

# Configuración de rutas
RAW_DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_raw.csv"
CLEAN_DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_cleaned.csv"

def clean_data():
    print("--- Iniciando Limpieza de Datos (Fase 3) ---")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Error: No se encuentra el archivo {RAW_DATA_PATH}")
        return

    df = pd.read_csv(RAW_DATA_PATH)
    initial_shape = df.shape
    
    # Columnas a eliminar (Métricas de error instrumental y baja completitud)
    columns_to_drop = [
        'nst',             # Number of seismic stations (60% nulos)
        'horizontalError', # Errores instrumentales
        'magError',        # Errores instrumentales
        'dmin',            # Distancia a la estación más cercana
        'magNst',          # Estaciones para magnitud
        'depthError',      # Errores instrumentales
        'gap',             # Gap azimutal
        'rms'              # Root Mean Square error
    ]
    
    # Eliminar solo las columnas que existan en el dataframe
    existing_drops = [col for col in columns_to_drop if col in df.columns]
    df_cleaned = df.drop(columns=existing_drops)
    
    # --- FILTRADO GEOGRÁFICO (SOLO COLOMBIA) ---
    print("Filtrando sismos fuera del territorio colombiano...")
    
    # Límites aproximados de Colombia
    lat_min, lat_max = -4.5, 13.5
    lon_min, lon_max = -82.0, -66.5
    
    # Filtro por coordenadas
    df_colombia = df_cleaned[
        (df_cleaned['latitude'] >= lat_min) & (df_cleaned['latitude'] <= lat_max) &
        (df_cleaned['longitude'] >= lon_min) & (df_cleaned['longitude'] <= lon_max)
    ].copy()
    
    # Filtro adicional por etiqueta de lugar (asegurar que mencione Colombia)
    df_colombia = df_colombia[df_colombia['place'].str.contains('Colombia', case=False, na=False)]
    
    final_shape = df_colombia.shape
    deleted_count = initial_shape[0] - final_shape[0]
    deleted_percent = (deleted_count / initial_shape[0]) * 100
    
    print(f"Registros iniciales: {initial_shape[0]}")
    print(f"Registros eliminados (fuera de Colombia): {deleted_count} ({deleted_percent:.2f}%)")
    print(f"Registros finales: {final_shape[0]}")
    print(f"Columnas eliminadas: {len(existing_drops)}")
    
    # Guardar dataset limpio
    df_colombia.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"Dataset filtrado y limpio guardado en: {CLEAN_DATA_PATH}")

if __name__ == "__main__":
    clean_data()
