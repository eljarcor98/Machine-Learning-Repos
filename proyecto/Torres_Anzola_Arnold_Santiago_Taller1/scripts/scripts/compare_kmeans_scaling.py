import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Configuración
DATA_PATH = 'data/earthquakes_enriched.csv'
OUTPUT_DIR = 'documentacion/visualizaciones'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_experiment():
    print("Cargando datos...")
    df = pd.read_csv(DATA_PATH)
    
    # Seleccionamos las features para el modelo
    features = ['latitude', 'longitude', 'depth', 'mag']
    X = df[features]
    
    print(f"Dataset: {len(df)} registros.")
    print("\nScales:")
    print(X.describe().loc[['min', 'max']])
    
    # 1. K-Means SIN ESCALAR
    print("\nEjecutando K-Means SIN ESCALAR...")
    kmeans_no_scale = KMeans(n_clusters=15, random_state=42, n_init=10)
    df['cluster_no_scale'] = kmeans_no_scale.fit_predict(X)
    
    # 2. K-Means CON ESCALAR
    print("Ejecutando K-Means CON ESCALAR...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans_scale = KMeans(n_clusters=15, random_state=42, n_init=10)
    df['cluster_scale'] = kmeans_scale.fit_predict(X_scaled)
    
    # Visualización comparativa: Longitud vs Profundidad (donde la disparidad es mayor)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Gráfico sin escalar
    sns.scatterplot(data=df, x='longitude', y='depth', hue='cluster_no_scale', 
                    palette='tab20', ax=ax1, s=40, alpha=0.7, legend=None)
    ax1.set_title('K-Means SIN ESCALAR\n(Dominio de Profundidad 0-200)', fontsize=14)
    ax1.invert_yaxis() # Profundidad hacia abajo
    
    # Gráfico con escalar
    sns.scatterplot(data=df, x='longitude', y='depth', hue='cluster_scale', 
                    palette='tab20', ax=ax2, s=40, alpha=0.7, legend=None)
    ax2.set_title('K-Means CON ESCALAR\n(Balance Geografía/Profundidad)', fontsize=14)
    ax2.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/comparativa_clusters_scaling.png")
    print(f"\nGráfico comparativo guardado en: {OUTPUT_DIR}/comparativa_clusters_scaling.png")
    
    # Análisis de dominancia
    print("\n--- ANALISIS DE CLUSTERS ---")
    print("\nSin Escalar (Promedio de Profundidad por Cluster):")
    print(df.groupby('cluster_no_scale')['depth'].mean().sort_values())
    
    print("\nCon Escalar (Promedio de Profundidad por Cluster):")
    print(df.groupby('cluster_scale')['depth'].mean().sort_values())

if __name__ == "__main__":
    run_experiment()
