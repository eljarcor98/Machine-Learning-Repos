import pandas as pd

# Cargar el dataset guardado anteriormente
path = 'data/earthquakes_raw.csv'

def explore_time():
    try:
        df = pd.read_csv(path)
        
        # Convertir la columna time a datetime
        df['time'] = pd.to_datetime(df['time'])
        
        print("--- Análisis de la Dimensión Temporal ---")
        print(f"Fecha del primer sismo registrado: {df['time'].min()}")
        print(f"Fecha del último sismo registrado: {df['time'].max()}")
        print(f"Rango de tiempo total: {df['time'].max() - df['time'].min()}")
        
        # Extraer componentes de tiempo para análisis
        df['year'] = df['time'].dt.year
        df['month'] = df['time'].dt.month
        df['day_name'] = df['time'].dt.day_name()
        df['hour'] = df['time'].dt.hour
        
        print("\n--- Sismos por Año ---")
        print(df['year'].value_counts().sort_index())
        
        print("\n--- Sismos por Mes (Distribución Estacional) ---")
        meses = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
                 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
        dist_mes = df['month'].value_counts().sort_index()
        dist_mes.index = dist_mes.index.map(meses)
        print(dist_mes)
        
        print("\n--- Horas con más actividad (Top 5) ---")
        print(df['hour'].value_counts().head(5).sort_index())
        
    except Exception as e:
        print(f"Error al analizar el tiempo: {e}")

if __name__ == "__main__":
    explore_time()
