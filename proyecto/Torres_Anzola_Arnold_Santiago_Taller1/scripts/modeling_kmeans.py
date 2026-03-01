import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import os

# Configuración
DATA_PATH = 'data/earthquakes_enriched.csv'
OUTPUT_DIR = 'documentacion/visualizaciones'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def perform_modeling():
    print("Cargando datos enriquecidos...")
    df = pd.read_csv(DATA_PATH)
    
    # Seleccionamos las features para el modelo según el consenso previo
    # Usaremos las 3 dimensiones espaciales y la magnitud
    features = ['latitude', 'longitude', 'depth', 'mag']
    X = df[features]
    
    # Escalado obligatorio
    print("Estandarizando datos...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Rangos de K a probar
    ks = range(2, 11)
    inertias = []
    silhouettes = []
    
    print("\nIniciando experimentación con K = 2..10...")
    for k in ks:
        print(f"Procesando k={k}...")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        inertias.append(kmeans.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels))
    
    # 4.2 Gráfico del Método del Codo
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(ks, inertias, 'go-', linewidth=2)
    plt.title('Método del Codo (Inercia vs K)', fontsize=14, fontweight='bold')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Inercia (SSE)')
    plt.grid(True, alpha=0.3)
    
    # 4.3 Gráfico de Silhouette Score
    plt.subplot(1, 2, 2)
    plt.plot(ks, silhouettes, 'bo-', linewidth=2)
    plt.title('Silhouette Score vs K', fontsize=14, fontweight='bold')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Coeficiente de Silhouette')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/elbow_silhouette_analysis.png", dpi=120)
    print(f"\nAnálisis de métricas guardado en: {OUTPUT_DIR}/elbow_silhouette_analysis.png")
    
    # Mostrar resultados en consola para el análisis
    results_df = pd.DataFrame({'k': ks, 'Inertia': inertias, 'Silhouette': silhouettes})
    print("\nRESULTADOS DE LAS MÉTRICAS:")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    perform_modeling()
