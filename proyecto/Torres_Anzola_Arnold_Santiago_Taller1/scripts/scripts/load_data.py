import pandas as pd
import os

# URL del dataset de terremotos (USGS)
url = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query"
    "?format=csv&starttime=2010-01-01&endtime=2026-02-20"
    "&minlatitude=-4.5&maxlatitude=13.5"
    "&minlongitude=-82&maxlongitude=-66.5"
    "&minmagnitude=1.5&orderby=time&limit=20000"
)

def load_data():
    print("Cargando datos desde USGS...")
    try:
        df = pd.read_csv(url)
        
        # Crear carpeta data si no existe
        os.makedirs('data', exist_ok=True)
        
        # Guardar una copia local
        output_path = 'data/earthquakes_raw.csv'
        df.to_csv(output_path, index=False)
        
        print(f"Datos cargados exitosamente. Total de registros: {len(df)}")
        print(f"Archivo guardado en: {output_path}")
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None

if __name__ == "__main__":
    load_data()
