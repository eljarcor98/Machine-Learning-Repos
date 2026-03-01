import pandas as pd
import json
import os
import geopandas as gpd
import markdown2

# Configuración de rutas
DATA_DIR = 'data'
VIS_DIR = 'documentacion/visualizaciones'
REPORT_DIR = 'reporte_final'
RAW_DATA = os.path.join(DATA_DIR, 'earthquakes_raw.csv')
GEOJSON_FAULT_PATH = os.path.join(DATA_DIR, "Atlas_Geol%C3%B3gico_de_Colombia_2020%3A_Fallas_Geol%C3%B3gicas.geojson")
INPUT_MD = os.path.join(REPORT_DIR, 'REPORTE_CRISP_DM.md')
OUTPUT_HTML = os.path.join(REPORT_DIR, 'REPORTE_FINAL_INTERACTIVO.html')

def generate_interactive_report():
    print("Iniciando generación de Reporte Final Interactivo (HTML)...")
    
    try:
        # 1. Cargar Datos Sísmicos y Geográficos
        df = pd.read_csv(RAW_DATA)
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        
        seismic_data = df[['latitude', 'longitude', 'mag', 'depth', 'year', 'place']].to_dict(orient='records')
        yearly_counts = df['year'].value_counts().sort_index().to_dict()
        years = list(yearly_counts.keys())
        counts = list(yearly_counts.values())

        print("Procesando fallas geológicas...")
        gdf_fallas = gpd.read_file(GEOJSON_FAULT_PATH)
        gdf_fallas['geometry'] = gdf_fallas['geometry'].simplify(0.01, preserve_topology=True)
        faults_json = gdf_fallas.to_json()

        # 2. Leer y Procesar Markdown
        print(f"Leyendo contenido desde: {INPUT_MD}")
        with open(INPUT_MD, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Limpiar etiquetas específicas de Markdown que no se ven bien en HTML puro o que queremos reemplazar
        # Eliminamos el bloque tip y el iframe anterior (si existe)
        import re
        md_content = re.sub(r'> \[!IMPORTANT\].*?\*.*?\*', '', md_content, flags=re.DOTALL)
        md_content = re.sub(r'!\[Análisis Temporal.*?\]\(.*?\)', '', md_content) # Quitamos la imagen estática

        # Convertir MD a HTML
        html_body = markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks", "alerts"])

        # 3. Construir el HTML Final con el Template Premium
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Final: Riesgo Sísmico en Colombia (Interactivo)</title>
    
    <!-- Librerías Externas -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --primary: #2563eb;
            --secondary: #64748b;
            --accent: #ef4444;
            --bg: #f1f5f9;
            --card: #ffffff;
            --text: #1e293b;
        }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            margin: 0;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            overflow-x: hidden;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: white;
            padding: 3rem 1rem;
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 5px solid var(--accent);
        }}

        h1 {{ margin: 0; font-size: 2.5rem; letter-spacing: -1px; }}
        
        .report-section {{
            background: var(--card);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }}

        h2, h3 {{ color: var(--primary); border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-top: 1.5rem; }}

        /* Dashboard Styles */
        .dashboard-container {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
            margin: 2rem 0;
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }}

        #map-area {{
            height: 600px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
        }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .viz-card {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .chart-wrapper {{ position: relative; height: 300px; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        th, td {{ padding: 0.75rem; border: 1px solid #e2e8f0; text-align: left; }}
        th {{ background: #f8fafc; color: var(--primary); }}

        .stats-box {{
            text-align: center;
            padding: 1rem;
            background: var(--bg);
            border-radius: 8px;
        }}

        #year-display {{ font-size: 2.5rem; font-weight: 700; color: var(--primary); display: block; }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--secondary);
            font-size: 0.9rem;
        }}

        @media (max-width: 900px) {{
            .dashboard-container {{ grid-template-columns: 1fr; }}
            #map-area {{ height: 400px; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="container">
        <h1>Análisis de Riesgo Sísmico en Colombia</h1>
        <p>REPORTE FINAL INTERACTIVO (CRISP-DM)</p>
    </div>
</header>

<div class="container">
    <div class="report-section">
        {html_body}
    </div>

    <!-- El Dashboard se inyectará después de la sección 1.1 -->
</div>

<footer>
    <p>&copy; 2026 - Análisis Tectónico Basado en Datos de la USGS. Visualizaciones desarrolladas con Leaflet.js y Chart.js.</p>
</footer>

<script>
    // 1. Datos
    const seismicPoints = {json.dumps(seismic_data)};
    const faultsGeoJSON = {faults_json};
    const chartLabels = {json.dumps(years)};
    const chartData = {json.dumps(counts)};

    // 2. Inyección Dinámica del Dashboard
    // Buscamos dónde termina la sección 1.1 para insertar el dashboard
    const reportBody = document.querySelector('.report-section');
    const sections = reportBody.querySelectorAll('h3');
    let targetSection = null;
    
    sections.forEach(s => {{
        if (s.innerText.includes('1.1')) targetSection = s;
    }});

    if (targetSection) {{
        const dashboardHTML = `
            <div class="dashboard-container">
                <div id="map-area"></div>
                <div class="sidebar">
                    <div class="viz-card">
                        <h3>Línea de Tiempo</h3>
                        <div class="chart-wrapper">
                            <canvas id="timelineChart"></canvas>
                        </div>
                        <button onclick="resetFilter()" style="margin-top:10px; cursor:pointer;">Reiniciar Filtro</button>
                    </div>
                    <div class="viz-card stats-box">
                        <h3>Año Seleccionado</h3>
                        <span id="year-display">TODOS</span>
                        <p>Total Sismos: <span id="event-count" style="font-weight:bold;">${{seismicPoints.length}}</span></p>
                    </div>
                </div>
            </div>
        `;
        // Insertar después de la descripción tectónica
        targetSection.nextElementSibling.insertAdjacentHTML('afterend', dashboardHTML);
    }}

    // 3. Lógica del Mapa
    const map = L.map('map-area').setView([4.5, -74.0], 6);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; CARTO'
    }}).addTo(map);

    L.geoJSON(faultsGeoJSON, {{
        style: {{ color: "#ff0000", weight: 1.5, opacity: 0.6 }}
    }}).addTo(map);

    const markerLayer = L.layerGroup().addTo(map);

    function getMarkerColor(mag) {{
        return mag > 6 ? '#7f1d1d' : mag > 5 ? '#b91c1c' : mag > 4 ? '#ef4444' : '#f87171';
    }}

    function filterData(year = null) {{
        markerLayer.clearLayers();
        let count = 0;
        seismicPoints.forEach(p => {{
            if (year === null || p.year === year) {{
                const marker = L.circleMarker([p.latitude, p.longitude], {{
                    radius: p.mag * 2,
                    fillColor: getMarkerColor(p.mag),
                    color: "white", weight: 0.5, opacity: 1, fillOpacity: 0.8
                }});
                marker.bindPopup(`<b>${{p.place}}</b><br>Mag: ${{p.mag}} | Prof: ${{p.depth}}km`);
                markerLayer.addLayer(marker);
                count++;
            }}
        }});
        document.getElementById('year-display').innerText = year || "TODOS";
        document.getElementById('event-count').innerText = count;
    }}

    // 4. Lógica del Chart
    const ctx = document.getElementById('timelineChart').getContext('2d');
    const chart = new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: chartLabels,
            datasets: [{{
                data: chartData,
                backgroundColor: '#2563eb',
            }}]
        }},
        options: {{
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            onClick: (e, items) => {{
                if (items.length > 0) filterData(chartLabels[items[0].index]);
            }}
        }}
    }});

    function resetFilter() {{ filterData(null); }}
    filterData(null);
</script>
</body>
</html>
"""
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"SUCCESS: Reporte Final Interactivo generado exitosamente en: {OUTPUT_HTML}")

    except Exception as e:
        print(f"ERROR: Error critico en la generacion del reporte HTML: {e}")

if __name__ == "__main__":
    generate_interactive_report()
