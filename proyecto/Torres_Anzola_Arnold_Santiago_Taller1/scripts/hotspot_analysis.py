import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go
import plotly.express as px

# ----------------------------------------
# CONFIGURACIÓN
# ----------------------------------------
RADIO_KM = 50
MIN_SISMOS = 15
RADIO_RAD = RADIO_KM / 6371.0

path = 'data/earthquakes_raw.csv'

def clasificar_por_densidad(count):
    if count >= 500:
        return 'Muy alto riesgo'
    elif count >= 200:
        return 'Alto riesgo'
    elif count >= 80:
        return 'Riesgo moderado'
    elif count >= 15:
        return 'Riesgo bajo'
    else:
        return 'Zona relativamente segura'

def run_analysis():
    print("Cargando datos...")
    df = pd.read_csv(path)
    df['time'] = pd.to_datetime(df['time'])

    # ----------------------------------------
    # DBSCAN GRANULAR (50 km)
    # ----------------------------------------
    print(f"Aplicando DBSCAN (radio={RADIO_KM} km, min_sismos={MIN_SISMOS})...")
    coords_rad = np.radians(df[['latitude', 'longitude']].values)
    db = DBSCAN(eps=RADIO_RAD, min_samples=MIN_SISMOS, algorithm='ball_tree', metric='haversine')
    df['cluster'] = db.fit_predict(coords_rad)

    n_clusters = len(set(df['cluster'])) - (1 if -1 in df['cluster'] else 0)
    n_noise = (df['cluster'] == -1).sum()
    print(f"Hotspots detectados: {n_clusters}")
    print(f"Eventos aislados: {n_noise}")

    # ----------------------------------------
    # ESTADÍSTICAS POR CLUSTER
    # ----------------------------------------
    cluster_stats = df[df['cluster'] != -1].groupby('cluster').agg(
        count=('mag', 'count'),
        mag_promedio=('mag', 'mean'),
        mag_max=('mag', 'max'),
        lat_centroid=('latitude', 'mean'),
        lon_centroid=('longitude', 'mean'),
        lugar_referencia=('place', lambda x: x.mode()[0])
    ).reset_index()

    cluster_stats['nivel_riesgo'] = cluster_stats['count'].apply(clasificar_por_densidad)
    cluster_stats['id_zona'] = ['Zona ' + str(i+1) for i in range(len(cluster_stats))]

    # ----------------------------------------
    # ASIGNAR RIESGO Y ETIQUETA DE ZONA A CADA FILA
    # ----------------------------------------
    riesgo_map = cluster_stats.set_index('cluster')['nivel_riesgo'].to_dict()
    id_zona_map = cluster_stats.set_index('cluster')['id_zona'].to_dict()
    
    df['nivel_riesgo'] = df['cluster'].map(riesgo_map)
    df['zona_asignada'] = df['cluster'].map(id_zona_map)
    
    df.loc[df['cluster'] == -1, 'nivel_riesgo'] = 'Zona relativamente segura'
    df.loc[df['cluster'] == -1, 'zona_asignada'] = 'Sin zona específica (Aislado)'

    zonas_peligrosas = ['Muy alto riesgo', 'Alto riesgo', 'Riesgo moderado', 'Riesgo bajo']
    df['es_zona_segura'] = df['nivel_riesgo'].apply(
        lambda x: 'Segura' if x not in zonas_peligrosas else 'Peligrosa'
    )

    # ----------------------------------------
    # GUARDAR DATASET ENRIQUECIDO
    # ----------------------------------------
    df.to_csv('data/earthquakes_classified.csv', index=False)
    print("Archivo guardado: data/earthquakes_classified.csv")

    # ----------------------------------------
    # MAPA INTERACTIVO (ENRIQUECIDO)
    # ----------------------------------------
    print("\nGenerando mapa de hotspots enriquecido...")
    
    unique_clusters = sorted(df['cluster'].unique())
    cluster_colors = px.colors.qualitative.Dark24
    color_map_cluster = {c: cluster_colors[i % len(cluster_colors)] for i, c in enumerate(unique_clusters) if c != -1}
    color_map_cluster[-1] = '#bdc3c7' # Gris para ruido

    fig = go.Figure()

    # Capa 1: puntos individuales de sismos coloreados por CLUSTER
    for cluster_id in unique_clusters:
        subset = df[df['cluster'] == cluster_id]
        if len(subset) == 0:
            continue
            
        color = color_map_cluster[cluster_id]
        name = df[df['cluster'] == cluster_id]['zona_asignada'].iloc[0]
        
        # Preparar datos técnicos (manejando nulos)
        nst_clean = subset['nst'].fillna(0)
        rms_clean = subset['rms'].fillna(0)
        
        fig.add_trace(go.Scattermap(
            lat=subset['latitude'],
            lon=subset['longitude'],
            mode='markers',
            marker=dict(size=subset['mag'] * 2.2, color=color, opacity=0.7),
            name=name,
            text=subset['place'],
            customdata=np.stack([
                subset['mag'], 
                subset['depth'], 
                subset['nivel_riesgo'], 
                subset['es_zona_segura'],
                subset['time'].dt.strftime('%Y-%m-%d %H:%M'),
                subset['zona_asignada'],
                nst_clean,
                rms_clean
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br><br>"
                "<b>DATOS TÉCNICOS:</b><br>"
                "• Magnitud: %{customdata[0]:.1f}<br>"
                "• Profundidad: %{customdata[1]:.1f} km<br>"
                "• Fecha/Hora: %{customdata[4]}<br>"
                "• Estaciones (NST): %{customdata[6]:.0f}<br>"
                "• Calidad (RMS): %{customdata[7]:.2f}<br><br>"
                "<b>ANÁLISIS DE ZONA:</b><br>"
                "• Pertenece a: <b>%{customdata[5]}</b><br>"
                "• Tipo de zona: %{customdata[2]}<br>"
                "• Clasificación: <b>%{customdata[3]}</b><extra></extra>"
            )
        ))

    # Capa 2: centroides de cada hotspot (con información resumida)
    for _, row in cluster_stats.iterrows():
        color = color_map_cluster[row['cluster']]
        fig.add_trace(go.Scattermap(
            lat=[row['lat_centroid']],
            lon=[row['lon_centroid']],
            mode='markers+text',
            marker=dict(size=15, color='black', opacity=0.8),
            text=[row['id_zona']],
            textposition='top center',
            textfont=dict(size=10, color='black', family="Arial Black"),
            showlegend=False,
            customdata=[[row['count'], round(row['mag_promedio'], 2), round(row['mag_max'], 1), row['nivel_riesgo'], row['lugar_referencia']]],
            hovertemplate=(
                "<b>ZONA: %{text} (%{customdata[4]})</b><br>"
                "Sismos detectados: %{customdata[0]}<br>"
                "Magnitud Promedio: %{customdata[1]}<br>"
                "Magnitud Máxima: %{customdata[2]}<br>"
                "Nivel de Riesgo Global: <b>%{customdata[3]}</b><extra></extra>"
            )
        ))

    fig.update_layout(
        map=dict(
            style="carto-positron",
            center=dict(lat=4.57, lon=-74.30),
            zoom=4.8
        ),
        title=dict(
            text="Análisis de Riesgo y Hotspots Sísmicos (Detallado por Zonas)",
            font=dict(size=20)
        ),
        legend_title="Zonas Identificadas",
        margin={"r": 0, "t": 60, "l": 0, "b": 0}
    )

    output_file = 'documentacion/mapa_hotspots.html'
    fig.write_html(output_file)
    print(f"Mapa actualizado: {output_file}")

    return df, cluster_stats

if __name__ == "__main__":
    run_analysis()
