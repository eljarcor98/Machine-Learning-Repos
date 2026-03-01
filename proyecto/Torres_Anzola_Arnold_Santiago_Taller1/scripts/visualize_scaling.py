import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import os

# Configuración básica
DATA_PATH = 'data/earthquakes_enriched.csv'
OUTPUT_IMG = 'documentacion/visualizaciones/comparativa_estandarizacion.png'
os.makedirs('documentacion/visualizaciones', exist_ok=True)

def generate_scaling_comparison():
    print("Iniciando análisis de estandarización...")
    df = pd.read_csv(DATA_PATH)
    # Seleccionamos variables críticas para la comparativa (MAGNITUD VS PROFUNDIDAD)
    features = ['mag', 'depth'] 
    data = df[features] # Usamos TODO el dataset de Colombia (1,412 registros)
    
    # Estandarización
    scaler = StandardScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data), columns=features)
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    sns.set_theme(style="whitegrid")
    
    # Gráfico 1: Sin Estandarizar
    sns.scatterplot(data=data, x='mag', y='depth', ax=ax1, color='#d63031', s=30, alpha=0.5)
    ax1.set_title('DATOS SIN ESTANDARIZAR\n(Escala Global 0-200)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Magnitud (Escala Real 1-8)', fontsize=12)
    ax1.set_ylabel('Profundidad (Escala Real 0-200)', fontsize=12)
    
    # FORZAR DISPARIDAD VISUAL: Usar el mismo rango para ambos ejes
    ax1.set_xlim(1, 8) 
    ax1.set_ylim(0, 200)
    import numpy as np
    ax1.set_yticks(np.arange(0, 201, 5))
    ax1.set_xticks(np.arange(1, 9, 1))
    ax1.tick_params(axis='y', labelsize=8) # Reducir fuente para evitar amontonamiento
    
    ax1.text(0.05, 0.95, 'Dataset Completo (1,412 sismos)\nLa disparidad X-Y es masiva.', transform=ax1.transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
    
    # Gráfico 2: Con Estandarizar
    sns.scatterplot(data=data_scaled, x='mag', y='depth', ax=ax2, color='#6c5ce7', s=30, alpha=0.5)
    ax2.set_title('DATOS ESTANDARIZADOS\n(Zoom y Balance Estadístico)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Magnitud (Escala Z: -3 a 3)', fontsize=12)
    ax2.set_ylabel('Profundidad (Escala Z: -3 a 3)', fontsize=12)
    ax2.text(0.05, 0.95, 'Distribución equilibrada\nLista para K-Means.', transform=ax2.transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=120)
    print(f"Gráfico comparativo guardado en: {OUTPUT_IMG}")
    
    # Mostrar ejemplos numéricos
    print("\nEJEMPLO DE TRANSFORMACIÓN (Top 3):")
    print("-" * 50)
    print("ORIGINAL:")
    print(data.head(3))
    print("\nESTANDARIZADO (StandardScaler):")
    print(data_scaled.head(3))

if __name__ == "__main__":
    generate_scaling_comparison()
