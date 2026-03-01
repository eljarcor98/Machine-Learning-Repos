import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuración
path_raw = 'data/earthquakes_raw.csv'
output_dir = 'documentacion/visualizaciones'
os.makedirs(output_dir, exist_ok=True)

def run_eda_phase2():
    print("Iniciando Análisis Exploratorio de Datos (Fase 2)...")
    df = pd.read_csv(path_raw)
    
    # 1. Conteo de registros
    total_registros = len(df)
    print(f"\n1. Conteo de registros: {total_registros}")
    
    # 2. Valores nulos
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / total_registros) * 100
    eda_nulls = pd.DataFrame({
        'Nulos': null_counts,
        'Porcentaje': null_percentages
    }).sort_values(by='Nulos', ascending=False)
    print("\n2. Análisis de valores nulos (Top 10):")
    print(eda_nulls.head(10))
    
    # 3. Métricas descriptivas detalladas
    print("\n3. Métricas descriptivas detalladas:")
    desc_stats = df[['mag', 'depth', 'latitude', 'longitude']].describe().T
    desc_stats['skew'] = df[['mag', 'depth', 'latitude', 'longitude']].skew()
    desc_stats['kurtosis'] = df[['mag', 'depth', 'latitude', 'longitude']].kurt()
    print(desc_stats)
    
    # 4. Correlaciones
    print("\n4. Correlaciones (Pearson):")
    corr_pearson = df[['mag', 'depth', 'latitude', 'longitude']].corr()
    print(corr_pearson)
    
    print("\n4. Correlaciones (Spearman):")
    corr_spearman = df[['mag', 'depth', 'latitude', 'longitude']].corr(method='spearman')
    print(corr_spearman)
    
    # 5. Visualizaciones
    
    # 5.1 Scatter Plot: Magnitud vs Profundidad
    print("\nGenerando Scatter Plot: Magnitud vs Profundidad...")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='mag', y='depth', alpha=0.5, color='teal')
    plt.title('Relación entre Magnitud y Profundidad')
    plt.xlabel('Magnitud (Richter)')
    plt.ylabel('Profundidad (km)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(f'{output_dir}/scatter_mag_depth.png')
    plt.close()
    
    # 5.2 Mapa Interactivo: Lat vs Lon (Color por Profundidad)
    print("Generando Mapa: Color por Profundidad...")
    fig_depth = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="depth",
                                size="mag", color_continuous_scale=px.colors.cyclical.IceFire, 
                                size_max=15, zoom=4, mapbox_style="carto-positron",
                                title="Distribución Sísmica por Profundidad")
    fig_depth.write_html(f'documentacion/mapa_profundidad.html')
    
    # 5.3 Mapa Interactivo: Lat vs Lon (Color por Magnitud)
    print("Generando Mapa: Color por Magnitud...")
    fig_mag = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="mag",
                                size="mag", color_continuous_scale=px.colors.sequential.YlOrRd, 
                                size_max=15, zoom=4, mapbox_style="carto-positron",
                                title="Distribución Sísmica por Magnitud")
    fig_mag.write_html(f'documentacion/mapa_magnitud.html')
    
    # Guardar resultados en CSV para el reporte
    desc_stats.to_csv('documentacion/metricas_descriptivas.csv')
    corr_pearson.to_csv('documentacion/correlacion_pearson.csv')
    
    print("\n--- Ejecución completada con éxito ---")
    print(f"Visualizaciones guardadas en: {output_dir}")
    print("Archivos HTML guardados en: documentacion/")

if __name__ == "__main__":
    run_eda_phase2()
