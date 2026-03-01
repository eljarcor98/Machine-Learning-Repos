import pandas as pd

# Cargar el dataset guardado anteriormente
path = 'data/earthquakes_raw.csv'

def explore_data():
    try:
        df = pd.read_csv(path)
        
        print("--- Información General del Dataset ---")
        print(f"Total de registros: {df.shape[0]}")
        print(f"Total de variables: {df.shape[1]}")
        
        print("\n--- Lista de Variables y Tipos de Datos ---")
        print(df.info())
        
        print("\n--- Primeras 5 Filas ---")
        print(df.head())
        
        print("\n--- Estadísticas Básicas de Magnitud y Profundidad ---")
        print(df[['mag', 'depth']].describe())
        
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

if __name__ == "__main__":
    explore_data()
