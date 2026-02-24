import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

# Configuración de rutas
root_dir = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means"
rfm_file = os.path.join(root_dir, "online_retail_rfm.csv")
output_dir = os.path.join(root_dir, "docs", "clustering_advanced")
os.makedirs(output_dir, exist_ok=True)

def advanced_kmeans():
    print("Cargando dataset RFM...")
    rfm = pd.read_csv(rfm_file, index_col='CustomerID')
    
    # 1. Preprocesamiento: Transformación Logarítmica para manejar el sesgo (skewness)
    print("Transformando y escalando datos...")
    rfm_log = np.log1p(rfm)
    
    # Escalado
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)
    rfm_scaled_df = pd.DataFrame(rfm_scaled, index=rfm.index, columns=rfm.columns)

    # 2. Método del Codo para encontrar K óptimo
    print("Calculando Método del Codo...")
    sse = {}
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(rfm_scaled)
        sse[k] = kmeans.inertia_

    plt.figure(figsize=(10, 6))
    plt.plot(list(sse.keys()), list(sse.values()), marker='o')
    plt.title('Método del Codo (Elbow Method)')
    plt.xlabel('Número de Clústeres (K)')
    plt.ylabel('SSE / Inercia')
    plt.savefig(os.path.join(output_dir, "elbow_method.png"))
    plt.close()

    # 3. Aplicación de K-Means (Elegiremos K=4 para este análisis avanzado)
    k_final = 4
    print(f"Aplicando K-Means con K={k_final}...")
    kmeans = KMeans(n_clusters=k_final, random_state=42, n_init=10)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

    # 4. PCA (Análisis de Componentes Principales) para visualización 2D
    print("Ejecutando PCA...")
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(rfm_scaled)
    rfm['PCA1'] = pca_result[:, 0]
    rfm['PCA2'] = pca_result[:, 1]

    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=rfm, palette='viridis', alpha=0.6)
    plt.title('Visualización de Clústeres con PCA (2D)')
    plt.savefig(os.path.join(output_dir, "pca_clusters.png"))
    plt.close()

    # 5. Snake Plot (Gráfico de Coordenadas Paralelas)
    print("Generando Snake Plot...")
    rfm_scaled_df['Cluster'] = rfm['Cluster']
    rfm_melted = pd.melt(rfm_scaled_df.reset_index(), 
                         id_vars=['CustomerID', 'Cluster'], 
                         value_vars=['Recency', 'Frequency', 'Monetary'], 
                         var_name='Metric', value_name='Value')

    plt.figure(figsize=(12, 8))
    sns.lineplot(x='Metric', y='Value', hue='Cluster', data=rfm_melted, palette='viridis')
    plt.title('Snake Plot: Características por Clúster (Normalizado)')
    plt.savefig(os.path.join(output_dir, "snake_plot.png"))
    plt.close()

    # 6. Mapa de Calor de Importancia de Atributos
    print("Generando Mapa de Calor de promedios...")
    cluster_avg = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean()
    population_avg = rfm[['Recency', 'Frequency', 'Monetary']].mean()
    relative_importance = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean() / rfm[['Recency', 'Frequency', 'Monetary']].mean() - 1

    plt.figure(figsize=(10, 6))
    sns.heatmap(relative_importance, annot=True, fmt='.2f', cmap='RdYlGn')
    plt.title('Importancia Relativa de Atributos por Clúster')
    plt.savefig(os.path.join(output_dir, "attribute_importance_heatmap.png"))
    plt.close()

    # Guardar resultados
    rfm.to_csv(os.path.join(root_dir, "online_retail_rfm_clusters.csv"))
    print(f"\nProceso completado. Archivos guardados en: {output_dir}")
    print("\nResumen Estadístico del Clustering:")
    print(cluster_avg)

if __name__ == "__main__":
    advanced_kmeans()
