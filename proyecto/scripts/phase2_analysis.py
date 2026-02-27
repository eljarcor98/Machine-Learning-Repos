import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuración de rutas
DATA_PATH = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\data\earthquakes_raw.csv"
OUTPUT_IMG = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones\matriz_correlacion.png"
OS_DIR = os.path.dirname(OUTPUT_IMG)

if not os.path.exists(OS_DIR):
    os.makedirs(OS_DIR)

def analyze_phase2():
    print("--- Cargando datos ---")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Análisis de valores nulos
    print("\n--- Análisis de Valores Nulos ---")
    null_counts = df.isnull().sum()
    null_pct = (df.isnull().sum() / len(df)) * 100
    null_df = pd.DataFrame({'Nulos': null_counts, 'Porcentaje': null_pct})
    null_df = null_df[null_df['Nulos'] > 0].sort_values(by='Nulos', ascending=False)
    
    print(null_df)
    
    # Visualización de Valores Nulos
    plt.figure(figsize=(10, 6))
    sns.barplot(x=null_df.index, y=null_df['Porcentaje'], palette='viridis')
    plt.title('Porcentaje de Valores Nulos por Variable')
    plt.ylabel('Porcentaje (%)')
    plt.xlabel('Variable')
    plt.xticks(rotation=45)
    plt.tight_layout()
    NULL_IMG = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\proyecto\documentacion\visualizaciones\porcentaje_nulos.png"
    plt.savefig(NULL_IMG)
    print(f"Gráfico de nulos guardado en: {NULL_IMG}")
    
    # 2. Matriz de Correlación
    print("\n--- Generando Matriz de Correlación ---")
    # Seleccionar solo columnas numéricas
    df_numeric = df.select_dtypes(include=['float64', 'int64'])
    corr_matrix = df_numeric.corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Matriz de Correlación - Sismos Colombia')
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG)
    print(f"Heatmap guardado en: {OUTPUT_IMG}")

    
    # Retornar datos para documentación
    return null_df, corr_matrix

if __name__ == "__main__":
    analyze_phase2()
