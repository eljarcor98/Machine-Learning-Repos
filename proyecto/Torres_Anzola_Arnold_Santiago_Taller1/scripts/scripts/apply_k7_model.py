import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Configuración
DATA_PATH = 'data/earthquakes_enriched.csv'
OUTPUT_PATH = 'data/earthquakes_enriched.csv' # Sobrescribimos con los clusters

def apply_final_model(k=7):
    print(f"Aplicando modelo final con K={k}...")
    df = pd.read_csv(DATA_PATH)
    
    # Features finales
    features = ['latitude', 'longitude', 'depth', 'mag']
    X = df[features]
    
    # Escalado
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means Final
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Renombrar clusters para que sean más legibles (opcional en esta fase, o dejar como 0-6)
    # Por ahora los dejaremos como números para la fase de perfilado
    
    # Guardar dataset con clusters
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset actualizado con clusters en: {OUTPUT_PATH}")
    
    # Mostrar distribución
    print("\nDistribución de sismos por cluster:")
    print(df['cluster'].value_counts().sort_index())

if __name__ == "__main__":
    apply_final_model(k=7)
