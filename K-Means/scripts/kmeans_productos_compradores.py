import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Configuración de rutas
root_dir = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means"
file_path = os.path.join(root_dir, "Online Retail.xlsx")
output_dir = os.path.join(root_dir, "docs", "clustering")
os.makedirs(output_dir, exist_ok=True)

def run_kmeans_step1():
    print("Cargando datos para K-Means...")
    df = pd.read_excel(file_path)
    
    # 1. Limpieza inicial (Crucial para K-Means)
    print("Limpiando datos (eliminando negativos y nulos)...")
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # 2. Agregación por Cliente (Compradores vs Productos)
    print("Creando matriz de características por cliente...")
    customer_data = df.groupby('CustomerID').agg({
        'Quantity': 'sum',           # Volumen total
        'TotalPrice': 'sum',         # Valor total (Monetario)
        'StockCode': 'nunique',     # Variedad de productos diferentes
        'InvoiceNo': 'nunique'      # Frecuencia de visitas
    }).rename(columns={
        'Quantity': 'TotalQuantity',
        'TotalPrice': 'TotalRevenue',
        'StockCode': 'ProductVariety',
        'InvoiceNo': 'Frequency'
    })
    
    # 3. Tratamiento de Outliers (Filtrado simple para el primer intento)
    # K-Means es muy sensible a valores extremos. 
    # Filtramos clientes que están por encima del percentil 95 para ver grupos base claros
    print("Filtrando outliers extremos para mejorar visualización del modelo...")
    q_low = customer_data.quantile(0.01)
    q_high = customer_data.quantile(0.95)
    customer_data_filtered = customer_data[
        (customer_data > q_low).all(axis=1) & 
        (customer_data < q_high).all(axis=1)
    ]
    
    # 4. Escalado de datos (Obligatorio para K-Means)
    print("Escalando datos...")
    scaler = StandardScaler()
    features = ['TotalQuantity', 'TotalRevenue', 'ProductVariety']
    scaled_data = scaler.fit_transform(customer_data_filtered[features])
    
    # 5. Aplicación de K-Means (Intento inicial con K=4)
    print("Entrenando modelo K-Means (K=4)...")
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    customer_data_filtered['Cluster'] = kmeans.fit_predict(scaled_data)
    
    # 6. Visualización de Resultados
    print("Generando visualizaciones del clustering...")
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=customer_data_filtered, 
        x='ProductVariety', 
        y='TotalRevenue', 
        hue='Cluster', 
        palette='viridis',
        style='Cluster',
        s=100, alpha=0.7
    )
    plt.title('Segmentación de Clientes: Variedad de Productos vs Gasto Total')
    plt.xlabel('Variedad de Productos (Diferentes SKUs)')
    plt.ylabel('Gasto Total (£)')
    
    plot_path = os.path.join(output_dir, "cluster_variedad_vs_gasto.png")
    plt.savefig(plot_path)
    print(f"Gráfico guardado en: {plot_path}")
    plt.close()
    
    # 7. Resumen de Clústeres
    cluster_summary = customer_data_filtered.groupby('Cluster').mean()
    print("\nResumen de los Grupos Encontrados (Promedios):")
    print(cluster_summary)
    
    return cluster_summary

if __name__ == "__main__":
    run_kmeans_step1()
