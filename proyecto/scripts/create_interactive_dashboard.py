import pandas as pd
import json
import os
import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configuración de rutas
DATA_DIR = 'data'
VIS_DIR = 'documentacion/visualizaciones'
LOCAL_DATA = os.path.join(DATA_DIR, 'earthquakes_enriched.csv')
GEOJSON_FAULT_PATH = os.path.join(DATA_DIR, "Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson")
OUTPUT_HTML = os.path.join(VIS_DIR, 'dashboard_interactivo.html')

def create_dashboard():
    print("Iniciando creación de dashboard dinámico (K=2 a 10)...")
    os.makedirs(VIS_DIR, exist_ok=True)

    try:
        # 1. Cargar y procesar sismos
        if not os.path.exists(LOCAL_DATA):
            print(f"Error: No se encuentra {LOCAL_DATA}. Ejecuta enrich_dataset.py primero.")
            return

        df = pd.read_csv(LOCAL_DATA)
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        # 2. Calcular Clusters Dinámicos (K=2 a 10)
        # Usamos las mismas features que en el modelado oficial
        features = ['latitude', 'longitude', 'depth', 'mag']
        X = df[features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        print("Pre-calculando segmentaciones sismotectónicas...")
        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            df[f'cluster_k{k}'] = kmeans.fit_predict(X_scaled)

        # Preparar datos para JS (incluyendo todos los clusters)
        cluster_cols = [f'cluster_k{k}' for k in range(2, 11)]
        seismic_data = df[['latitude', 'longitude', 'mag', 'depth', 'year', 'municipio_region', 'departamento'] + cluster_cols].to_dict(orient='records')
        
        # Estadísticas básicas
        yearly_counts = df['year'].value_counts().sort_index().to_dict()
        years = list(yearly_counts.keys())
        years_counts = list(yearly_counts.values())

        depto_counts_df = df['departamento'].value_counts().head(10)
        deptos = depto_counts_df.index.tolist()
        deptos_counts = depto_counts_df.values.tolist()

        # Fallas geológicas
        print("Cargando fallas geológicas...")
        gdf_fallas = gpd.read_file(GEOJSON_FAULT_PATH)
        gdf_fallas = gdf_fallas[['NombreFall', 'geometry']].copy()
        gdf_fallas['geometry'] = gdf_fallas['geometry'].simplify(0.01)
        faults_json = gdf_fallas.to_json()

        # 4. Paleta de colores Premium (10 colores)
        colors = [
            "#6c5ce7", "#e74c3c", "#2ecc71", "#f1c40f", "#3498db", 
            "#e67e22", "#9b59b6", "#16a085", "#d35400", "#c0392b"
        ]

        # 5. Generar el HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Sísmico Dinámico - Colombia</title>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --primary: #6c5ce7;
            --bg: #f5f6fa;
            --card: #ffffff;
            --text: #2f3640;
            --fault: #ff7675;
        }}
        
        body {{ font-family: 'Outfit', sans-serif; margin: 0; background-color: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        header {{ background: #2f3640; color: white; padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .main-container {{ display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; padding: 0.8rem; flex-grow: 1; overflow: hidden; }}
        #map-container {{ background: var(--card); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); position: relative; }}
        #map {{ height: 100%; width: 100%; filter: grayscale(0.2); }}
        .sidebar {{ display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; padding-right: 5px; }}
        .card {{ background: var(--card); padding: 1.2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
        h2 {{ margin: 0 0 0.8rem 0; font-size: 0.85rem; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; }}
        
        .k-selector {{ background: var(--primary); color: white; padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; }}
        input[type=range] {{ width: 100%; cursor: pointer; }}
        .k-value {{ font-size: 1.5rem; font-weight: 800; float: right; }}

        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem; }}
        .stat-item {{ background: var(--bg); padding: 0.8rem; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 1.2rem; font-weight: 800; color: var(--primary); display: block; }}
        .stat-label {{ font-size: 0.7rem; opacity: 0.7; }}
        
        .legend-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; font-size: 0.75rem; }}
        .legend-item {{ display: flex; align-items: center; background: #fafafa; padding: 4px; border-radius: 4px; }}
        .dot {{ height: 8px; width: 8px; border-radius: 50%; margin-right: 6px; }}
        
        .popup-card {{ min-width: 150px; font-size: 0.85rem; }}
        .popup-card b {{ color: var(--primary); }}
    </style>
</head>
<body>

<header>
    <div>
        <h1 style="margin:0; font-size:1.2rem">Colombia Sísmica 2.0</h1>
        <span style="font-size:0.75rem; opacity:0.8">Explorador Dinámico de Provincias Tectónicas</span>
    </div>
    <div style="text-align:right">
        <span style="font-size:0.8rem">Actualizado: Feb 2026</span>
    </div>
</header>

<div class="main-container">
    <div id="map-container">
        <div id="map"></div>
    </div>

    <div class="sidebar">
        <div class="k-selector">
            <span>Zonas Geográficas (K):</span>
            <span class="k-value" id="k-val-display">7</span>
            <input type="range" id="k-slider" min="2" max="10" value="7" oninput="updateK(this.value)">
            <p style="font-size:0.7rem; margin:10px 0 0 0; opacity:0.9">Desliza para ver la evolución de los clusters</p>
        </div>

        <div class="card">
            <h2>Estado de la Cobertura</h2>
            <div class="stat-grid">
                <div class="stat-item">
                    <span class="stat-num" id="total-count">1412</span>
                    <span class="stat-label">Sismos</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num" id="active-k">7</span>
                    <span class="stat-label">Provincias</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Leyenda de Clusters</h2>
            <div id="legend-grid" class="legend-grid"></div>
        </div>

        <div class="card" style="flex-grow:1">
            <h2 id="chart-title">Tendencia Anual</h2>
            <div style="height: 120px;"><canvas id="yearChart"></canvas></div>
            <h2 style="margin-top:15px">Departamentos</h2>
            <div style="height: 150px;"><canvas id="deptoChart"></canvas></div>
        </div>
    </div>
</div>

<script>
    const seismicPoints = {json.dumps(seismic_data)};
    const faultsGeoJSON = {faults_json};
    const colors = {json.dumps(colors)};
    let currentK = 7;

    // Configuración del Mapa (Mapa Plano Minimalista)
    const map = L.map('map').setView([4.57, -74.3], 6);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }}).addTo(map);

    // Capa de Fallas (Sutil)
    L.geoJSON(faultsGeoJSON, {{
        style: {{ color: "#ff7675", weight: 1, opacity: 0.25 }},
        onEachFeature: (f, l) => {{ if(f.properties.NombreFall) l.bindPopup(`<b>FALLA:</b> ${{f.properties.NombreFall}}`); }}
    }}).addTo(map);

    let markerLayer = L.layerGroup().addTo(map);

    function updateK(val) {{
        currentK = parseInt(val);
        document.getElementById('k-val-display').innerText = currentK;
        document.getElementById('active-k').innerText = currentK;
        renderMarkers();
        updateLegend();
    }}

    function updateLegend() {{
        const grid = document.getElementById('legend-grid');
        grid.innerHTML = '';
        for(let i=0; i < currentK; i++) {{
            grid.innerHTML += `
                <div class="legend-item">
                    <span class="dot" style="background-color: ${{colors[i]}}"></span>
                    <span>Zona ${{i+1}}</span>
                </div>
            `;
        }}
    }}

    function renderMarkers() {{
        markerLayer.clearLayers();
        const clusterKey = `cluster_k${{currentK}}`;
        
        seismicPoints.forEach(p => {{
            const clusterIdx = p[clusterKey];
            const marker = L.circleMarker([p.latitude, p.longitude], {{
                radius: p.mag * 1.5,
                fillColor: colors[clusterIdx],
                color: "#fff",
                weight: 0.5,
                opacity: 0.8,
                fillOpacity: 0.9
            }});
            
            marker.bindPopup(`
                <div class="popup-card">
                    <b>${{p.municipio_region}}</b><br>
                    ${{p.departamento}}<br>
                    <hr style="border:0; border-top:1px solid #eee; margin:5px 0">
                    Mag: ${{p.mag}} | Prof: ${{p.depth}} km<br>
                    Zona: ${{clusterIdx + 1}} (en K=${{currentK}})
                </div>
            `);
            markerLayer.addLayer(marker);
        }});
    }}

    // Gráficos Estáticos (Solo contexto)
    const chartOpts = {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ display: false }}, x: {{ display: false }} }} }};
    new Chart(document.getElementById('yearChart'), {{
        type: 'line', data: {{ labels: {json.dumps(years)}, datasets: [{{ data: {json.dumps(years_counts)}, borderColor: '#6c5ce7', tension: 0.4 }}] }}, options: chartOpts
    }});
    new Chart(document.getElementById('deptoChart'), {{
        type: 'bar', data: {{ labels: {json.dumps(deptos)}, datasets: [{{ data: {json.dumps(deptos_counts)}, backgroundColor: '#a29bfe' }}] }}, options: {{ ...chartOpts, indexAxis: 'y' }}
    }});

    // Inicialización
    updateK(7);
</script>
</body>
</html>
"""
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"Dashboard Dinámico (K=2-10) generado exitosamente en: {OUTPUT_HTML}")

    except Exception as e:
        print(f"Error al crear el dashboard: {e}")

if __name__ == "__main__":
    create_dashboard()
