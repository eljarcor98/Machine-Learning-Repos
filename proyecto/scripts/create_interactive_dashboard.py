import pandas as pd
import json
import os
import geopandas as gpd

# Configuración de rutas
DATA_DIR = 'data'
VIS_DIR = 'documentacion/visualizaciones'
LOCAL_DATA = os.path.join(DATA_DIR, 'earthquakes_enriched.csv')
GEOJSON_FAULT_PATH = os.path.join(DATA_DIR, "Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson")
OUTPUT_HTML = os.path.join(VIS_DIR, 'dashboard_interactivo.html')

def create_dashboard():
    print("Iniciando creación de dashboard interactivo para Colombia...")
    os.makedirs(VIS_DIR, exist_ok=True)

    try:
        # 1. Cargar y procesar sismos (Solo Colombia)
        if not os.path.exists(LOCAL_DATA):
            print(f"Error: No se encuentra {LOCAL_DATA}. Ejecuta enrich_dataset.py primero.")
            return

        df = pd.read_csv(LOCAL_DATA)
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        # Mapeo de interpretaciones de clusters (basado en Fase 5)
        cluster_info = {
            0: {"name": "Subducción Pacífico Sur (Nariño)", "color": "#1abc9c"},
            1: {"name": "Nido de Bucaramanga (Santander)", "color": "#e67e22"},
            2: {"name": "Fallas del Caribe (Norte)", "color": "#3498db"},
            3: {"name": "Pacífico Norte (Chocó - RIESGO MÁXIMO)", "color": "#e74c3c"},
            4: {"name": "Andes Occidentales (Chocó/Antioquia)", "color": "#9b59b6"},
            5: {"name": "Límite Placa Caribe (Guajira)", "color": "#f1c40f"},
            6: {"name": "Piedemonte Llanero (Meta)", "color": "#2ecc71"}
        }

        # Preparar datos para JS (incluyendo cluster)
        seismic_data = df[['latitude', 'longitude', 'mag', 'depth', 'year', 'municipio_region', 'departamento', 'cluster']].to_dict(orient='records')
        
        # Calcular conteos por año
        yearly_counts = df['year'].value_counts().sort_index().to_dict()
        years = list(yearly_counts.keys())
        years_counts = list(yearly_counts.values())

        # Calcular conteos por departamento (Top 10)
        depto_counts_df = df['departamento'].value_counts().head(10)
        deptos = depto_counts_df.index.tolist()
        deptos_counts = depto_counts_df.values.tolist()

        # 2. Cargar y simplificar fallas
        print("Procesando fallas geológicas y sus nombres...")
        gdf_fallas = gpd.read_file(GEOJSON_FAULT_PATH)
        gdf_fallas = gdf_fallas[['NombreFall', 'geometry']].copy()
        gdf_fallas['geometry'] = gdf_fallas['geometry'].simplify(0.01, preserve_topology=True)
        faults_json = gdf_fallas.to_json()

        # 3. Generar el HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sismicidad Colombia - Dashboard de Riesgo (K=7)</title>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --primary: #6c5ce7;
            --secondary: #a29bfe;
            --bg: #f8f9fa;
            --card: #ffffff;
            --text: #2d3436;
            --fault: #ff7675;
        }}
        
        body {{ font-family: 'Outfit', sans-serif; margin: 0; background-color: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; }}
        header {{ background: linear-gradient(135deg, #1e272e 0%, #000000 100%); color: white; padding: 0.8rem 2rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
        .main-container {{ display: grid; grid-template-columns: 2.5fr 1fr; gap: 1rem; padding: 1rem; flex-grow: 1; overflow: hidden; }}
        #map-container {{ background: var(--card); border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.1); position: relative; }}
        #map {{ height: 100%; width: 100%; }}
        .sidebar {{ display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; padding-right: 5px; }}
        .card {{ background: var(--card); padding: 1.2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        h2 {{ margin-top: 0; font-size: 0.9rem; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid var(--bg); padding-bottom: 0.5rem; margin-bottom: 0.8rem; }}
        .btn-reset {{ background: #2d3436; color: white; border: none; padding: 0.6rem; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.3s; }}
        .btn-reset:hover {{ background: #000; }}
        .stat-box {{ background: var(--bg); padding: 0.8rem; border-radius: 8px; text-align: center; margin-top: 0.5rem; border: 1px solid #eee; }}
        #selection-label {{ font-size: 1.2rem; font-weight: 800; color: var(--primary); margin: 0.2rem 0; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; font-size: 0.85rem; }}
        .dot {{ height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
        .popup-title {{ color: var(--primary); font-size: 1.1rem; border-bottom: 1px solid #eee; margin-bottom: 5px; display: block; }}
        .risk-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.75rem; margin-top: 5px; }}
    </style>
</head>
<body>

<header>
    <h1>Dashboard de Riesgo Sísmico Colombia (K=7)</h1>
    <p>Segmentación por Provincias Sismotectónicas - Fase de Despliegue</p>
</header>

<div class="main-container">
    <div id="map-container">
        <div id="map"></div>
    </div>

    <div class="sidebar">
        <div class="card">
            <h2>Leyenda de Provincias (Clusters)</h2>
            <div id="legend-content"></div>
        </div>

        <div class="card">
            <h2>Filtros y Estadísticas</h2>
            <button class="btn-reset" onclick="resetFilter()">🔄 REINICIAR MAPA</button>
            <div class="stat-box">
                <div id="filter-type">MOSTRANDO</div>
                <div id="selection-label">TODOS LOS EVENTOS</div>
                <p>Total sismos: <span id="total-count" style="font-weight: 800; color: var(--primary); font-size: 1.3rem;">{len(df)}</span></p>
            </div>
        </div>

        <div class="card" style="flex-grow:1">
            <h2>Sismicidad por Año</h2>
            <div style="height: 150px;"><canvas id="yearChart"></canvas></div>
            <h2 style="margin-top:15px">Top Departamentos</h2>
            <div style="height: 180px;"><canvas id="deptoChart"></canvas></div>
        </div>
    </div>
</div>

<script>
    const seismicPoints = {json.dumps(seismic_data)};
    const faultsGeoJSON = {faults_json};
    const clusterMeta = {json.dumps(cluster_info)};
    
    // Generar Leyenda dinámica
    const legendDiv = document.getElementById('legend-content');
    Object.keys(clusterMeta).forEach(key => {{
        const item = clusterMeta[key];
        legendDiv.innerHTML += `
            <div class="legend-item">
                <span class="dot" style="background-color: ${{item.color}}"></span>
                <span>${{item.name}}</span>
            </div>
        `;
    }});

    const map = L.map('map').setView([4.57, -74.3], 6);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

    // Fallas en Rojo Suave
    L.geoJSON(faultsGeoJSON, {{
        style: {{ color: "var(--fault)", weight: 1.2, opacity: 0.3 }},
        onEachFeature: (f, l) => {{ if(f.properties.NombreFall) l.bindPopup(`<b>FALLA:</b> ${{f.properties.NombreFall}}`); }}
    }}).addTo(map);

    let markerLayer = L.layerGroup().addTo(map);

    function renderMarkers(filter = null, type = 'year') {{
        markerLayer.clearLayers();
        let count = 0;
        
        seismicPoints.forEach(p => {{
            let show = (filter === null) || (type === 'year' && p.year == filter) || (type === 'depto' && p.departamento == filter);

            if (show) {{
                const info = clusterMeta[p.cluster];
                const marker = L.circleMarker([p.latitude, p.longitude], {{
                    radius: p.mag * 1.8,
                    fillColor: info.color,
                    color: "#fff",
                    weight: 0.8,
                    opacity: 1,
                    fillOpacity: 0.8
                }});
                
                marker.bindPopup(`
                    <div style="font-family: 'Outfit', sans-serif;">
                        <span class="popup-title">${{p.municipio_region}}</span>
                        <b>Depto:</b> ${{p.departamento}}<br>
                        <b>Magnitud:</b> ${{p.mag}} ML<br>
                        <b>Profundidad:</b> ${{p.depth}} km<br>
                        <div class="risk-tag" style="background-color: ${{info.color}}">
                            PROVINCIA: ${{info.name}}
                        </div>
                    </div>
                `);
                markerLayer.addLayer(marker);
                count++;
            }}
        }});

        document.getElementById('selection-label').innerText = filter || "COBERTURA NACIONAL";
        document.getElementById('total-count').innerText = count;
    }}

    // Gráficos (Reducidos para Sidebar)
    const commonOpts = {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ display: false }}, x: {{ grid: {{ display: false }} }} }} }};
    
    new Chart(document.getElementById('yearChart'), {{
        type: 'line',
        data: {{ labels: {json.dumps(years)}, datasets: [{{ data: {json.dumps(years_counts)}, borderColor: 'var(--primary)', tension: 0.3, fill: true, backgroundColor: 'rgba(108, 92, 231, 0.1)' }}] }},
        options: {{ ...commonOpts, onClick: (e, i) => {{ if(i.length) renderMarkers({json.dumps(years)}[i[0].index], 'year'); }} }}
    }});

    new Chart(document.getElementById('deptoChart'), {{
        type: 'bar',
        data: {{ labels: {json.dumps(deptos)}, datasets: [{{ data: {json.dumps(deptos_counts)}, backgroundColor: 'rgba(162, 155, 254, 0.6)' }}] }},
        options: {{ ...commonOpts, indexAxis: 'y', onClick: (e, i) => {{ if(i.length) renderMarkers({json.dumps(deptos)}[i[0].index], 'depto'); }} }}
    }});

    function resetFilter() {{ renderMarkers(null); }}
    renderMarkers(null);
</script>
</body>
</html>
"""
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"Dashboard con 7 Clusters guardado exitosamente en: {OUTPUT_HTML}")

    except Exception as e:
        print(f"Error al crear el dashboard: {e}")

if __name__ == "__main__":
    create_dashboard()

if __name__ == "__main__":
    create_dashboard()
