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
    
    final_shape = df_cleaned.shape
    
    print(f"Registros procesados: {initial_shape[0]}")
    print(f"Columnas eliminadas: {len(existing_drops)}")
    print(f"Columnas restantes: {final_shape[1]}")
    
    # Guardar dataset limpio
    df_cleaned.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"Dataset limpio guardado en: {CLEAN_DATA_PATH}")

if __name__ == "__main__":
    clean_data()
