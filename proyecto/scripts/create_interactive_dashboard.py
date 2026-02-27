import pandas as pd
import json
import os
import geopandas as gpd

# Configuración de rutas
DATA_DIR = 'data'
VIS_DIR = 'documentacion/visualizaciones'
RAW_DATA = os.path.join(DATA_DIR, 'earthquakes_raw.csv')
GEOJSON_FAULT_PATH = os.path.join(DATA_DIR, "Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson")
OUTPUT_HTML = os.path.join(VIS_DIR, 'dashboard_interactivo.html')

def create_dashboard():
    print("Iniciando creación de dashboard interactivo...")
    os.makedirs(VIS_DIR, exist_ok=True)

    try:
        # 1. Cargar y procesar sismos
        df = pd.read_csv(RAW_DATA)
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        # Preparar datos para JS (solo lo necesario para no sobrecargar el HTML)
        seismic_data = df[['latitude', 'longitude', 'mag', 'depth', 'year', 'place']].to_dict(orient='records')
        
        # Calcular conteos por año para el gráfico
        yearly_counts = df['year'].value_counts().sort_index().to_dict()
        years = list(yearly_counts.keys())
        counts = list(yearly_counts.values())

        # 2. Cargar y simplificar fallas (JSON nativo para Leaflet)
        print("Procesando fallas geológicas...")
        gdf_fallas = gpd.read_file(GEOJSON_FAULT_PATH)
        # Simplificamos la geometría para que el HTML no pese 10MB
        gdf_fallas['geometry'] = gdf_fallas['geometry'].simplify(0.01, preserve_topology=True)
        faults_json = gdf_fallas.to_json()

        # 3. Generar el HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Sísmico Interactivo - Colombia</title>
    
    <!-- Librerías Externas -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --primary: #007bff;
            --bg: #f8f9fa;
            --card: #ffffff;
            --text: #212529;
            --fault: #ff0000;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            margin: 0;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}

        header {{
            background: #212529;
            color: white;
            padding: 1rem 2rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .main-container {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1rem;
            padding: 1rem;
            flex-grow: 1;
        }}

        #map-container {{
            background: var(--card);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            position: relative;
        }}

        #map {{ height: 100%; width: 100%; }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
            padding-right: 5px;
        }}

        .chart-wrapper {{
            position: relative;
            height: 350px;
            width: 100%;
        }}

        .card {{
            background: var(--card);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}

        h2 {{ margin-top: 0; font-size: 1.2rem; border-bottom: 2px solid var(--bg); padding-bottom: 0.5rem; }}

        #controls {{ text-align: center; }}
        .btn-reset {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: opacity 0.2s;
        }}
        .btn-reset:hover {{ opacity: 0.8; }}

        .legend {{
            background: white;
            padding: 10px;
            line-height: 18px;
            color: #555;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }}
        .legend i {{
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>

<header>
    <h1>Explorador Sísmico Regional (2010-2026)</h1>
    <p>Haz clic en una barra del timeline para filtrar los sismos por año</p>
</header>

<div class="main-container">
    <div id="map-container">
        <div id="map"></div>
    </div>

    <div class="sidebar">
        <div class="card">
            <h2>Timeline de Actividad</h2>
            <div class="chart-wrapper">
                <canvas id="timelineChart"></canvas>
            </div>
            <div id="controls" style="margin-top: 1rem;">
                <button class="btn-reset" onclick="resetFilter()">Mostrar Todos los Años</button>
            </div>
        </div>
        
        <div class="card">
            <h2>Información de Selección</h2>
            <div id="stats">
                <p>Selecciona un año para ver estadísticas específicas.</p>
                <div id="year-label" style="font-size: 2rem; font-weight: bold; color: var(--primary);">TODOS</div>
                <p>Total sismos: <span id="total-count" style="font-weight: bold;">{len(df)}</span></p>
            </div>
        </div>
    </div>
</div>

<script>
    // 1. Datos del Backend
    const seismicPoints = {json.dumps(seismic_data)};
    const faultsGeoJSON = {faults_json};
    const chartLabels = {json.dumps(years)};
    const chartData = {json.dumps(counts)};

    // 2. Inicializar Mapa
    const map = L.map('map').setView([4.5709, -74.2973], 6);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }}).addTo(map);

    // Capa de Fallas (Siempre visible)
    L.geoJSON(faultsGeoJSON, {{
        style: {{ color: "var(--fault)", weight: 1.5, opacity: 0.6 }}
    }}).addTo(map);

    // Grupo de marcadores
    let markerLayer = L.layerGroup().addTo(map);

    function getMarkerColor(mag) {{
        return mag > 6 ? '#800026' :
               mag > 5 ? '#BD0026' :
               mag > 4 ? '#E31A1C' :
               mag > 3 ? '#FC4E2A' : '#FD8D3C';
    }}

    function renderMarkers(filteredYear = null) {{
        markerLayer.clearLayers();
        let count = 0;
        
        seismicPoints.forEach(p => {{
            if (filteredYear === null || p.year === filteredYear) {{
                const marker = L.circleMarker([p.latitude, p.longitude], {{
                    radius: p.mag * 1.5,
                    fillColor: getMarkerColor(p.mag),
                    color: "#fff",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.7
                }});
                marker.bindPopup(`<b>${{p.place}}</b><br>Magnitud: ${{p.mag}}<br>Profundidad: ${{p.depth}} km<br>Año: ${{p.year}}`);
                markerLayer.addLayer(marker);
                count++;
            }}
        }});

        // Actualizar UI
        document.getElementById('year-label').innerText = filteredYear || "TODOS";
        document.getElementById('total-count').innerText = count;
    }}

    // 3. Inicializar Timeline
    const ctx = document.getElementById('timelineChart').getContext('2d');
    const timelineChart = new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: chartLabels,
            datasets: [{{
                label: 'Sismos por Año',
                data: chartData,
                backgroundColor: 'rgba(0, 123, 255, 0.6)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(255, 0, 0, 0.8)'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            onClick: (evt, item) => {{
                if (item.length > 0) {{
                    const index = item[0].index;
                    const year = chartLabels[index];
                    renderMarkers(year);
                }}
            }},
            scales: {{
                y: {{ beginAtZero: true, display: true }}
            }},
            plugins: {{
                legend: {{ display: false }}
            }}
        }}
    }});

    function resetFilter() {{
        renderMarkers(null);
    }}

    // Renderizado Inicial
    renderMarkers(null);

</script>
</body>
</html>
"""
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"✅ Dashboard interactivo guardado exitosamente en: {OUTPUT_HTML}")

    except Exception as e:
        print(f"❌ Error al crear el dashboard: {e}")

if __name__ == "__main__":
    create_dashboard()
