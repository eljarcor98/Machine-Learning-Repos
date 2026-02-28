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

        # 5. Generar perfiles automáticos por cluster para cada K
        print("Generando perfiles automáticos de clusters...")
        all_profiles = {}
        for k in range(2, 11):
            col = f'cluster_k{k}'
            profiles = {}
            for cid in range(k):
                sub = df[df[col] == cid]
                avg_depth = round(sub['depth'].mean(), 1)
                avg_mag   = round(sub['mag'].mean(), 2)
                max_mag   = round(sub['mag'].max(), 1)
                count     = len(sub)
                top_depto = sub['departamento'].value_counts().index[0] if len(sub) else "N/A"

                # Clasificación por profundidad
                if avg_depth < 70:
                    seis_type = "Cortical Superficial"
                    depth_icon = "⬆️"
                elif avg_depth < 150:
                    seis_type = "Intermedia"
                    depth_icon = "↕️"
                else:
                    seis_type = "Profunda (Nido)"
                    depth_icon = "⬇️"

                # Nivel de riesgo basado en mag y densidad
                risk_score = (avg_mag * 0.6) + (min(count / 200, 1) * 0.4 * 7)
                if risk_score >= 4.5 or max_mag >= 6.5:
                    risk = "Alto"
                    risk_icon = "🔴"
                elif risk_score >= 3.5:
                    risk = "Moderado"
                    risk_icon = "🟡"
                else:
                    risk = "Bajo"
                    risk_icon = "🟢"

                # Texto accesible para el ciudadano
                if avg_depth < 70:
                    citizen_name = f"🔴 Zona de Riesgo {risk} (Superficial)"
                    impact_text = (f"Sismos a {avg_depth:.0f} km de profundidad se sienten con fuerza en superficie. "
                                   f"Con magnitudes de hasta {max_mag} ML, son capaces de dañar edificaciones "
                                   f"sin refuerzo sísmico, cortar agua y gas, y activar deslizamientos.")
                elif avg_depth < 150:
                    citizen_name = f"🟡 Zona Intermedia (Profundidad Moderada)"
                    impact_text = (f"A {avg_depth:.0f} km de profundidad, la energía se amortigua parcialmente. "
                                   f"Aun así, con magnitudes promedio de {avg_mag} ML pueden sentirse en "
                                   f"grandes áreas y afectar estructuras antiguas o en mal estado.")
                else:
                    citizen_name = f"🟢 Zona Profunda (Bajo Impacto Superficial)"
                    impact_text = (f"Con focos a {avg_depth:.0f} km, la energía se disipa antes de llegar a "
                                   f"la superficie. Aunque se registran magnitudes de hasta {max_mag} ML, "
                                   f"el impacto estructural es menor. Se perciben como vibraciones largas y suaves.")

                profiles[cid] = {
                    "count": int(count),
                    "avg_depth": float(avg_depth),
                    "avg_mag": float(avg_mag),
                    "max_mag": float(max_mag),
                    "top_depto": top_depto,
                    "seis_type": seis_type,
                    "depth_icon": depth_icon,
                    "risk": risk,
                    "risk_icon": risk_icon,
                    "name": f"{risk_icon} {seis_type} — {risk} Riesgo",
                    "citizen_name": citizen_name,
                    "impact_text": impact_text
                }
            all_profiles[k] = profiles

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
        
        .k-selector {{ background: var(--primary); color: white; padding: 1rem; border-radius: 12px; }}
        .dark-panel {{ background: var(--text); color: white; padding: 1rem; border-radius: 12px; }}
        input[type=range] {{ width: 100%; cursor: pointer; accent-color: var(--primary); margin: 4px 0; }}
        .k-value {{ font-size: 1.3rem; font-weight: 800; float: right; }}
        .range-row {{ display: flex; justify-content: space-between; font-size: 0.75rem; opacity: 0.9; margin-bottom: 4px; }}
        .year-labels {{ display: flex; justify-content: space-between; font-size: 0.7rem; margin-top: 2px; opacity: 0.7; }}

        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem; }}
        .stat-item {{ background: var(--bg); padding: 0.8rem; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 1.2rem; font-weight: 800; color: var(--primary); display: block; }}
        .stat-label {{ font-size: 0.7rem; opacity: 0.7; }}
        
        .legend-grid {{ display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.78rem; }}
        .legend-item {{ display: flex; align-items: center; background: #fafafa; padding: 8px; border-radius: 6px; gap: 8px; }}
        .legend-item .meta {{ display: flex; flex-direction: column; flex: 1; }}
        .legend-item .meta .name {{ font-weight: 700; font-size: 0.8rem; }}
        .legend-item .meta .sub  {{ font-size: 0.68rem; opacity: 0.65; margin-top: 2px; }}
        .dot {{ height: 12px; width: 12px; border-radius: 50%; flex-shrink: 0; }}
        
        .muni-list {{ max-height: 130px; overflow-y: auto; font-size: 0.78rem; }}
        .muni-tag {{ display: inline-block; background: rgba(255,255,255,0.15); padding: 2px 7px; border-radius: 10px; margin: 2px; }}
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
        <!-- Rango de Tiempo -->
        <div class="dark-panel">
            <div style="font-weight:700; margin-bottom:8px">📅 Rango de Tiempo</div>
            <div class="range-row">
                <span>Desde: <b id="year-from-label">{min(years)}</b></span>
                <span>Hasta: <b id="year-to-label">{max(years)}</b></span>
            </div>
            <input type="range" id="year-from" min="{min(years)}" max="{max(years)}" value="{min(years)}" oninput="updateRange()">
            <input type="range" id="year-to" min="{min(years)}" max="{max(years)}" value="{max(years)}" oninput="updateRange()">
            <div class="year-labels"><span>{min(years)}</span><span>{max(years)}</span></div>
        </div>

        <!-- Detail Panel -->
        <div class="card" id="detail-panel" style="background: var(--primary); color: white; display: none; transition: 0.3s;">
            <h2 style="color: white; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 10px;">Detalle de Selección</h2>
            <div id="detail-content" style="font-size: 0.85rem;"></div>
        </div>

        <div class="card">
            <h2>Zonas Geográficas (K)</h2>
            <span class="k-value" id="k-val-display" style="color: var(--primary); font-size: 1.2rem; font-weight:800">7</span>
            <input type="range" id="k-slider" min="2" max="10" value="7" oninput="updateK(this.value)">
            <p style="font-size:0.7rem; margin-top:5px; opacity:0.6">Variación de segmentación sismotectónica</p>
        </div>

        <div class="card">
            <h2>Estado y Filtro</h2>
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
            <div id="legend-grid" class="legend-grid"></div>
        </div>

        <!-- Panel de Municipios por Cluster -->
        <div class="card" id="muni-panel" style="display:none; border-left: 4px solid var(--primary);">
            <h2 id="muni-panel-title">Municipios de la Zona</h2>
            <div id="muni-list" class="muni-list"></div>
        </div>
        <div class="card" style="flex-grow:1">
            <h2>Tendencia Anual</h2>
            <div style="height: 160px;"><canvas id="yearChart"></canvas></div>
        </div>
    </div>
</div>

<script>
    const seismicPoints = {json.dumps(seismic_data)};
    const faultsGeoJSON = {faults_json};
    const colors = {json.dumps(colors)};
    const allProfiles = {json.dumps(all_profiles)};
    let currentK = 7;
    let yearFrom = {min(years)};
    let yearTo = {max(years)};
    let currentClusterFilter = null;

    // Configuración del Mapa
    const map = L.map('map').setView([4.57, -74.3], 6);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }}).addTo(map);

    // Capa de Fallas (Más visibles)
    L.geoJSON(faultsGeoJSON, {{
        style: {{ color: "#d63031", weight: 1.5, opacity: 0.45 }},
        onEachFeature: (f, l) => {{ if(f.properties.NombreFall) l.bindPopup(`<b>FALLA GEOLÓGICA:</b> ${{f.properties.NombreFall}}`); }}
    }}).addTo(map);

    let markerLayer = L.layerGroup().addTo(map);
    let yearChart;

    function updateK(val) {{
        currentK = parseInt(val);
        document.getElementById('k-val-display').innerText = currentK;
        document.getElementById('active-k').innerText = currentK;
        renderMarkers();
        updateLegend();
    }}

    function updateRange() {{
        let from = parseInt(document.getElementById('year-from').value);
        let to = parseInt(document.getElementById('year-to').value);
        if (from > to) {{ let tmp = from; from = to; to = tmp; }}
        yearFrom = from; yearTo = to;
        document.getElementById('year-from-label').innerText = from;
        document.getElementById('year-to-label').innerText = to;
        renderMarkers();
    }}

    function toggleClusterFilter(idx) {{
        currentClusterFilter = (currentClusterFilter === idx) ? null : idx;
        renderMarkers();
        updateLegend();
        updateMuniPanel();
    }}

    function updateLegend() {{
        const grid = document.getElementById('legend-grid');
        const profiles = allProfiles[currentK] || {{}};
        grid.innerHTML = '';
        for(let i=0; i < currentK; i++) {{
            const isSelected = (currentClusterFilter === i);
            const opacity = (currentClusterFilter !== null && !isSelected) ? 'opacity: 0.3;' : 'opacity: 1;';
            const border = isSelected ? `border: 2px solid ${{colors[i]}}; background: #f4f4ff;` : 'border: 1px solid #eee;';
            const prof = profiles[i] || {{}};
            const cname = prof.citizen_name || `Zona ${{i+1}}`;
            const sub   = prof.top_depto ? `📍 ${{prof.top_depto}} · hasta ${{prof.max_mag}} ML` : '';
            
            grid.innerHTML += `
                <div class="legend-item" onclick="toggleClusterFilter(${{i}})" 
                     style="cursor:pointer; transition:0.2s; ${{opacity}} ${{border}}">
                    <span class="dot" style="background-color:${{colors[i]}}"></span>
                    <div class="meta">
                        <span class="name">Zona ${{i+1}} · ${{cname}}</span>
                        <span class="sub">${{sub}}</span>
                    </div>
                </div>
            `;
        }}
    }}

    function updateMuniPanel() {{
        const panel = document.getElementById('muni-panel');
        const list = document.getElementById('muni-list');
        const title = document.getElementById('muni-panel-title');

        if (currentClusterFilter === null) {{
            panel.style.display = 'none';
            return;
        }}

        const clusterKey = `cluster_k${{currentK}}`;
        const colorHex = colors[currentClusterFilter];
        const prof = (allProfiles[currentK] || {{}})[currentClusterFilter] || {{}};

        // Recolectar municipios únicos
        const munis = new Set();
        seismicPoints.forEach(p => {{
            if (p[clusterKey] === currentClusterFilter && p.year >= yearFrom && p.year <= yearTo) {{
                munis.add(p.municipio_region);
            }}
        }});

        title.innerHTML = `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${{colorHex}};margin-right:6px"></span><b>Zona ${{currentClusterFilter + 1}}</b> — ${{munis.size}} municipios`;
        
        const impactText = prof.impact_text || '';
        list.innerHTML = `
            <div style="background:rgba(0,0,0,0.04); border-radius:8px; padding:10px; margin-bottom:10px; font-size:0.82rem">
                <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px">${{prof.citizen_name || 'Zona ' + (currentClusterFilter+1)}}</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:10px">
                    <div>📊 <b>${{prof.count || 0}}</b> sismos</div>
                    <div>📍 <b>${{prof.top_depto || '—'}}</b></div>
                    <div>📉 <b>${{prof.avg_depth || 0}} km</b> prof. media</div>
                    <div>💥 hasta <b>${{prof.max_mag || 0}} ML</b></div>
                </div>
                <div style="background:rgba(0,0,0,0.06); border-radius:6px; padding:8px; font-size:0.76rem; line-height:1.6; color:#2f3640">
                    💬 ${{impactText}}
                </div>
            </div>
            <div style="font-size:0.7rem; font-weight:700; margin-bottom:5px; opacity:0.5; letter-spacing:0.5px">MUNICIPIOS AFECTADOS:</div>
            ${{[...munis].sort().map(m => `<span class="muni-tag">${{m}}</span>`).join('')}}
        `;
        panel.style.borderColor = colorHex;
        panel.style.display = 'block';
    }}

    function showDetails(p) {{
        const panel = document.getElementById('detail-panel');
        const content = document.getElementById('detail-content');
        panel.style.display = 'block';
        const clusterIdx = p[`cluster_k${{currentK}}`];
        const prof = (allProfiles[currentK] || {{}})[clusterIdx] || {{}};
        const colorHex = colors[clusterIdx];

        // Explicación sencilla sobre la profundidad e impacto
        let depthDesc = '';
        if (p.depth < 30) depthDesc = `Este sismo fue **muy superficial** (${{p.depth}} km), lo que suele causar sacudidas más fuertes y ruidosas en la superficie.`;
        else if (p.depth < 70) depthDesc = `Ocurrió a una profundidad **superficial** (${{p.depth}} km), donde la energía se siente directamente en los municipios cercanos.`;
        else if (p.depth < 150) depthDesc = `Fue un sismo de **profundidad moderada** (${{p.depth}} km). La sacudida se dispersa un poco más antes de llegar arriba.`;
        else depthDesc = `Ocurrió a **gran profundidad** (${{p.depth}} km), por lo que se siente como un balanceo suave pero largo en áreas muy extensas.`;

        const groupReason = `Se agrupa en esta zona porque su comportamiento y ubicación coinciden con el patrón histórico de **${{prof.top_depto}}**.`;
        
        content.innerHTML = `
            <b style="font-size:1.1rem; display:block; margin-bottom:5px">${{p.municipio_region}}</b>
            <span style="opacity:0.9">${{p.departamento}}</span>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.2); margin:10px 0">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:0.83rem">
                <div>💥 Mag: <b>${{p.mag}} ML</b></div>
                <div>📉 Prof: <b>${{p.depth}} km</b></div>
                <div>📅 Año: <b>${{p.year}}</b></div>
                <div>${{prof.risk_icon || ''}} <b>${{prof.risk || ''}} Riesgo</b></div>
            </div>
            <div style="margin-top:10px; padding:10px; background:rgba(255,255,255,0.12); border-radius:8px; font-size:0.78rem; line-height:1.5">
                <div style="margin-bottom:8px">${{depthDesc}}</div>
                <div style="opacity:0.8; font-style:italic; font-size:0.72rem">${{groupReason}}</div>
            </div>
        `;
    }}

    function renderMarkers() {{
        markerLayer.clearLayers();
        const clusterKey = `cluster_k${{currentK}}`;
        let count = 0;
        let statsDepto = {{}};
        let statsYear = {{}};
        
        seismicPoints.forEach(p => {{
            const clusterIdx = p[clusterKey];
            const yearMatch = p.year >= yearFrom && p.year <= yearTo;
            const clusterMatch = (currentClusterFilter === null) || (clusterIdx === currentClusterFilter);

            if (yearMatch && clusterMatch) {{
                // Acumular estadísticas dinámicas
                statsDepto[p.departamento] = (statsDepto[p.departamento] || 0) + 1;
                statsYear[p.year] = (statsYear[p.year] || 0) + 1;

                const marker = L.circleMarker([p.latitude, p.longitude], {{
                    radius: p.mag * 1.4,
                    fillColor: colors[clusterIdx],
                    color: "#fff",
                    weight: 0.4,
                    opacity: 0.8,
                    fillOpacity: 0.9
                }});
                
                marker.on('click', () => showDetails(p));
                markerLayer.addLayer(marker);
                count++;
            }}
        }});

        updateCharts(statsYear, statsDepto);
        document.getElementById('total-count').innerText = count;
    }}

    function updateCharts(yearData, deptoData) {{
        // Actualizar Gráfico de Años
        const sortedYears = Object.keys(yearData).sort();
        yearChart.data.labels = sortedYears;
        yearChart.data.datasets[0].data = sortedYears.map(y => yearData[y]);
        yearChart.update('none');

        // Actualizar Gráfico de Departamentos (Top 7 dinámico)
        const sortedDeptos = Object.keys(deptoData).sort((a,b) => deptoData[b] - deptoData[a]).slice(0, 7);
        deptoChart.data.labels = sortedDeptos;
        deptoChart.data.datasets[0].data = sortedDeptos.map(d => deptoData[d]);
        deptoChart.update('none');
    }}

    // Inicialización de Gráficos
    const chartOpts = {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ display: false }}, x: {{ display: false }} }} }};
    
    yearChart = new Chart(document.getElementById('yearChart'), {{
        type: 'line', 
        data: {{ labels: [], datasets: [{{ data: [], borderColor: '#6c5ce7', tension: 0.4, fill: true, backgroundColor: 'rgba(108, 92, 231, 0.05)' }}] }}, 
        options: chartOpts
    }});

    // Inicio
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
