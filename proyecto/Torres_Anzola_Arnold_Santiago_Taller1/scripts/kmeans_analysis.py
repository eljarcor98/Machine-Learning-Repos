import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px

# ----------------------------------------
# CONFIGURACIÓN
# ----------------------------------------
N_CLUSTERS = 15  # Número de zonas a identificar
path = 'data/earthquakes_raw.csv'

def clasificar_riesgo_kmeans(count):
    if count >= 400:
        return 'Muy alto riesgo'
    elif count >= 150:
        return 'Alto riesgo'
    elif count >= 50:
        return 'Riesgo moderado'
    elif count >= 20:
        return 'Riesgo bajo'
    else:
        return 'Zona relativamente segura'

def run_kmeans_analysis():
    print("Cargando datos para K-Means...")
    df = pd.read_csv(path)
    df['time'] = pd.to_datetime(df['time'])

    # 1. Preparar datos para clustering (Coordenadas)
    X = df[['latitude', 'longitude']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Aplicar K-Means
    print(f"Agrupando datos en {N_CLUSTERS} zonas usando K-Means...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    df['cluster_kmeans'] = kmeans.fit_predict(X_scaled)

    # 3. Calcular estadísticas por cluster
    cluster_stats = df.groupby('cluster_kmeans').agg(
        count=('mag', 'count'),
        mag_promedio=('mag', 'mean'),
        mag_max=('mag', 'max'),
        lat_centroid=('latitude', 'mean'),
        lon_centroid=('longitude', 'mean'),
        lugar_referencia=('place', lambda x: x.mode()[0])
    ).reset_index()

    cluster_stats['nivel_riesgo'] = cluster_stats['count'].apply(clasificar_riesgo_kmeans)
    cluster_stats['id_zona'] = ['Zona ' + str(i+1) for i in range(len(cluster_stats))]

    # 4. Mapear riesgos
    riesgo_map = cluster_stats.set_index('cluster_kmeans')['nivel_riesgo'].to_dict()
    id_zona_map = cluster_stats.set_index('cluster_kmeans')['id_zona'].to_dict()
    
    df['nivel_riesgo'] = df['cluster_kmeans'].map(riesgo_map)
    df['zona_asignada'] = df['cluster_kmeans'].map(id_zona_map)

    # Variable binaria de seguridad
    df['es_zona_segura'] = df['nivel_riesgo'].apply(
        lambda x: 'Segura' if x == 'Zona relativamente segura' or x == 'Riesgo bajo' else 'Peligrosa'
    )

    # 5. Guardar resultados
    df.to_csv('data/earthquakes_kmeans.csv', index=False)
    print("Archivo guardado: data/earthquakes_kmeans.csv")

    # 6. Tabla Resumen consolidada
    print("\n--- RESUMEN DE ZONAS (K-Means) ---")
    resumen = cluster_stats.sort_values('count', ascending=False)
    print(resumen[['id_zona', 'lugar_referencia', 'count', 'nivel_riesgo']].to_string(index=False))

    # 7. Visualización
    print("\nGenerando mapa interactivo K-Means...")
    color_map_riesgo = {
        'Muy alto riesgo': '#c0392b',
        'Alto riesgo': '#e67e22',
        'Riesgo moderado': '#f1c40f',
        'Riesgo bajo': '#27ae60',
        'Zona relativamente segura': '#2980b9'
    }

    fig = go.Figure()

    # Capa de sismos individuales
    for nivel, color in color_map_riesgo.items():
        subset = df[df['nivel_riesgo'] == nivel]
        if len(subset) == 0: continue
        
        fig.add_trace(go.Scattermap(
            lat=subset['latitude'],
            lon=subset['longitude'],
            mode='markers',
            marker=dict(size=subset['mag'] * 1.8, color=color, opacity=0.4),
            name=nivel,
            text=subset['place'],
            customdata=np.stack([
                subset['mag'], 
                subset['depth'], 
                subset['zona_asignada'],
                subset['nivel_riesgo']
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Zona: %{customdata[2]}<br>"
                "Magnitud: %{customdata[0]:.1f}<br>"
                "Nivel Riesgo: <b>%{customdata[3]}</b><extra></extra>"
            )
        ))

    # Centros de los clusters (sin la propiedad 'line' que falló)
    fig.add_trace(go.Scattermap(
        lat=cluster_stats['lat_centroid'],
        lon=cluster_stats['lon_centroid'],
        mode='markers+text',
        marker=dict(size=14, color='black', opacity=0.8),
        text=cluster_stats['id_zona'],
        textposition='top center',
        name='Centro de Zona',
        hovertemplate="Centroide de %{text}<extra></extra>"
    ))

    fig.update_layout(
        map=dict(style="carto-positron", center=dict(lat=4.57, lon=-74.30), zoom=4.5),
        title="Agrupación Geográfica de Riesgo Sísmico (K-Means Clustering)",
        legend_title="Niveles de Riesgo",
        margin={"r":0,"t":50,"l":0,"b":0}
    )

    output_file = 'documentacion/mapa_kmeans.html'
    fig.write_html(output_file)
    print(f"Mapa K-Means guardado: {output_file}")

    return df, cluster_stats

if __name__ == "__main__":
    run_kmeans_analysis()
