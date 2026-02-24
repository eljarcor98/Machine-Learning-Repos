import pandas as pd
import os

# Configuración de rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(os.path.dirname(current_dir), 'KNN', 'dataset', 'iris.csv')

def calcular_medidas_dispersion(df):
    # Seleccionar solo columnas numéricas
    numeric_df = df.select_dtypes(include=['number'])
    
    # Calcular medidas
    resultados = {}
    for col in numeric_df.columns:
        # Rango
        rango = numeric_df[col].max() - numeric_df[col].min()
        # Varianza
        varianza = numeric_df[col].var()
        # Desviación Estándar
        desviacion_std = numeric_df[col].std()
        # Rango Intercuartílico (IQR)
        q1 = numeric_df[col].quantile(0.25)
        q3 = numeric_df[col].quantile(0.75)
        iqr = q3 - q1
        
        resultados[col] = {
            'Rango': round(rango, 4),
            'Varianza': round(varianza, 4),
            'Desv. Estándar': round(desviacion_std, 4),
            'IQR': round(iqr, 4)
        }
    
    return pd.DataFrame(resultados).T

def calcular_medidas_tendencia_central(df):
    # Seleccionar solo columnas numéricas
    numeric_df = df.select_dtypes(include=['number'])
    
    # Calcular medidas
    resultados = {}
    for col in numeric_df.columns:
        # Media
        media = numeric_df[col].mean()
        # Mediana
        mediana = numeric_df[col].median()
        # Moda (puede haber múltiples, tomamos la primera)
        moda = numeric_df[col].mode()[0]
        
        resultados[col] = {
            'Media': round(media, 4),
            'Mediana': round(mediana, 4),
            'Moda': round(moda, 4)
        }
    
    return pd.DataFrame(resultados).T

def main():
    if not os.path.exists(dataset_path):
        print(f"Error: No se encontró el archivo en {dataset_path}")
        return

    # Cargar el dataset
    df = pd.read_csv(dataset_path)
    
    print("--- Medidas de Tendencia Central del Dataset IRIS ---")
    tendencia_central_df = calcular_medidas_tendencia_central(df)
    print(tendencia_central_df)
    print("\n")
    
    print("--- Medidas de Dispersión del Dataset IRIS ---")
    dispersion_df = calcular_medidas_dispersion(df)
    print(dispersion_df)
    print("\n-------------------------------------------")

if __name__ == "__main__":
    main()
