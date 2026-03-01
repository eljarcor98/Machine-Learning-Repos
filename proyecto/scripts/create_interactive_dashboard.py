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

                # Criterios de Agrupación y Nombres de Grupo
                if avg_depth < 70:
                    group_name = "Grupo Superficial (Más Percibidos)"
                    criteria = "Sismos cercanos a la superficie. Se agrupan aquí porque su impacto se siente con fuerza y ruido."
                    citizen_name = f"🔴 Zona de Riesgo {risk} (Superficial)"
                    impact_text = (f"Estos sismos ocurren a solo {avg_depth:.0f} km de profundidad. "
                                   f"Se agrupan en esta zona porque son los que más 'sacuden' las casas. "
                                   f"Con magnitudes de hasta {max_mag} ML, pueden dañar paredes y techos sin refuerzo.")
                elif avg_depth < 150:
                    group_name = "Grupo Intermedio (Moderados)"
                    criteria = "Sismos a profundidad media. Se agrupan aquí porque su energía se dispersa antes de llegar arriba."
                    citizen_name = f"🟡 Zona de Profundidad Moderada"
                    impact_text = (f"Ocurren a unos {avg_depth:.0f} km de profundidad. "
                                   f"Se agrupan aquí porque se sienten más como un balanceo que como un golpe seco. "
                                   f"Tienen un impacto moderado en las estructuras.")
                else:
                    group_name = "Grupo Profundo (Nidos Sísmicos)"
                    criteria = "Sismos a gran profundidad. Se agrupan aquí por su origen profundo, usualmente en nidos sísmicos."
                    citizen_name = f"🟢 Zona Profunda (Menor Riesgo)"
                    impact_text = (f"Son sismos muy profundos (a más de {avg_depth:.0f} km). "
                                   f"Se agrupan aquí porque rara vez causan daños, aunque se registren magnitudes de {max_mag} ML. "
                                   f"Se sienten como vibraciones largas y suaves.")

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
                    "impact_text": impact_text,
                    "group_name": group_name,
                    "grouping_criteria": criteria
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
        header {{ background: #2f3640; color: white; padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 15px rgba(0,0,0,0.2); flex-shrink: 0; z-index: 2000; }}
        .btn-reset {{ background: var(--primary); color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-family: inherit; font-weight: 700; font-size: 0.8rem; transition: 0.3s; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .btn-reset:hover {{ background: #5649c1; transform: translateY(-1px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }}
        .btn-reset:active {{ transform: translateY(0); }}
        .main-container {{ display: grid; grid-template-columns: minmax(0, 1fr) 400px; gap: 1.2rem; padding: 1rem; flex-grow: 1; overflow: hidden; }}
        #map-container {{ background: var(--card); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); position: relative; display: flex; flex-direction: column; }}
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

        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-top: 0.5rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.6rem; text-align: center; }}
        .stat-item {{ background: #f9f9fb; padding: 0.7rem; border-radius: 10px; border: 1px solid #edf2f7; }}
        .stat-num {{ font-size: 1.2rem; font-weight: 800; color: var(--primary); display: block; }}
        .stat-label {{ font-size: 0.68rem; opacity: 0.75; }}
        
        .legend-grid {{ display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.8rem; }}
        .legend-item {{ display: flex; align-items: center; background: #ffffff; padding: 10px 14px; border-radius: 10px; gap: 12px; border: 1px solid #edf2f7; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
        .legend-item .meta {{ display: flex; flex-direction: column; flex: 1; min-width: 0; }}
        .legend-item .meta .name {{ font-weight: 700; font-size: 0.82rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .legend-item .meta .sub  {{ font-size: 0.7rem; opacity: 0.6; margin-top: 2px; }}
        .dot {{ height: 12px; width: 12px; border-radius: 50%; flex-shrink: 0; }}
        
        .profile-panel {{ border-left: 5px solid #dfe6e9; background: #fff; display: flex; flex-direction: column; min-height: 280px; flex-shrink: 0; overflow: hidden; }}
        .profile-content {{ padding: 1.2rem; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; max-height: 100%; }}
        .instruction-box {{ text-align: center; padding: 30px 15px; opacity: 0.6; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }}
        .muni-list {{ max-height: 180px; overflow-y: auto; font-size: 0.78rem; padding: 6px; }}
        .muni-tag {{ display: inline-block; background: #edf2f7; color: #4a5568; padding: 3px 10px; border-radius: 15px; margin: 3px; font-weight: 500; border: 1px solid #e2e8f0; font-size: 0.72rem; }}
        
        .story-card {{ background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); color: white; padding: 1.2rem; border-radius: 12px; margin-top: 5px; }}
        .story-card h3 {{ margin: 0 0 8px 0; font-size: 0.95rem; display: flex; align-items: center; gap: 8px; }}
        .story-text {{ font-size: 0.78rem; line-height: 1.5; opacity: 0.95; }}
        
        .references {{ font-size: 0.65rem; opacity: 0.5; margin-top: 15px; padding: 10px; border-top: 1px solid #eee; line-height: 1.4; }}
        .references a {{ color: var(--primary); text-decoration: none; font-weight: 700; }}
    </style>
</head>
<body>

<header>
    <div>
        <h1 style="margin:0; font-size:1.2rem">Colombia Sísmica 2.0</h1>
        <span style="font-size:0.75rem; opacity:0.8">Explorador Dinámico de Provincias Tectónicas</span>
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <button class="btn-reset" onclick="resetFilters()">🔄 Reiniciar Todo</button>
        <div style="text-align:right">
            <span style="font-size:0.8rem; opacity: 0.8; display: block;">Versión 3.10</span>
            <span style="font-size:0.65rem; opacity: 0.6;">Feb 2026</span>
        </div>
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

        <!-- Panel de Perfil de Zona (Ocupa el espacio en blanco) -->
        <div class="card profile-panel" id="profile-panel">
            <div id="profile-content" class="profile-content">
                <div class="instruction-box">
                    <span style="font-size:3.5rem; display:block; margin-bottom:15px">🔍</span>
                    <p style="font-size:0.9rem; line-height: 1.6;">Selecciona una <b>zona en la leyenda</b> o un <b>punto en el mapa</b> para ver el criterio de riesgo y los municipios que se agrupan en esa categoría.</p>
                </div>
            </div>
        </div>
        <div class="card" style="flex-grow:1">
            <h2>Tendencia Anual</h2>
            <div style="height: 160px;"><canvas id="yearChart"></canvas></div>
        </div>

        <!-- Nueva Sección de Narrativa -->
        <div class="story-card">
            <h3>📖 Historia de Nuestra Tierra</h3>
            <div class="story-text">
                Colombia está en la intersección de las placas de <b>Nazca y Suramérica</b>. 
                Los sismos <b>superficiales (rojos)</b> suelen ocurrir en las fallas que rompen la corteza terrestre, 
                mientras que los <b>profundos (verdes)</b> son el eco de la placa que se hunde bajo nosotros. 
                Cada color en este mapa cuenta el viaje de milenios de nuestra geografía dinámica.
            </div>
        </div>

        <div class="references">
            <b>Fuentes Oficiales:</b><br>
            • <a href="https://www.sgc.gov.co/" target="_blank">Servicio Geológico Colombiano (SGC)</a>: Atlas de Fallas Cuaternarias 2020.<br>
            • <a href="https://earthquake.usgs.gov/" target="_blank">USGS (United States Geological Survey)</a>: Catálogo de Sismicidad Global.<br>
            • Metodología: Clustering Dinámico K-Means para Riesgo Sísmico.
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
        currentClusterFilter = null; // Reset filter on K change
        renderMarkers();
        updateLegend();
        updateProfilePanel();
    }}

    function resetFilters() {{
        currentK = 7;
        yearFrom = {min(years)};
        yearTo = {max(years)};
        currentClusterFilter = null;

        document.getElementById('k-slider').value = 7;
        document.getElementById('k-val-display').innerText = 7;
        document.getElementById('active-k').innerText = 7;
        
        document.getElementById('year-from').value = yearFrom;
        document.getElementById('year-to').value = yearTo;
        document.getElementById('year-from-label').innerText = yearFrom;
        document.getElementById('year-to-label').innerText = yearTo;

        renderMarkers();
        updateLegend();
        updateProfilePanel();
        map.setView([4.57, -74.3], 6);
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
        updateProfilePanel();
    }}

    function updateLegend() {{
        const grid = document.getElementById('legend-grid');
        const profiles = allProfiles[currentK] || {{}};
        grid.innerHTML = '';
        for(let i=0; i < currentK; i++) {{
            const isSelected = (currentClusterFilter === i);
            const opacity = (currentClusterFilter !== null && !isSelected) ? 'opacity: 0.3;' : 'opacity: 1;';
            const border = isSelected ? `border: 2px solid ${{colors[i]}}; background: #fdfdff;` : 'border: 1px solid #eee;';
            const prof = profiles[i] || {{}};
            const gname = prof.group_name || `Zona ${{i+1}}`;
            const sub   = prof.top_depto ? `📍 ${{prof.top_depto}} · hasta ${{prof.max_mag}} ML` : '';
            
            grid.innerHTML += `
                <div class="legend-item" onclick="toggleClusterFilter(${{i}})" 
                     style="cursor:pointer; transition:0.2s; ${{opacity}} ${{border}}">
                    <span class="dot" style="background-color:${{colors[i]}}"></span>
                    <div class="meta">
                        <span class="name">Zona ${{i+1}} · ${{gname}}</span>
                        <span class="sub">${{sub}}</span>
                    </div>
                </div>
            `;
        }}
    }}

    function updateProfilePanel() {{
        const content = document.getElementById('profile-content');
        const panel = document.getElementById('profile-panel');

        if (currentClusterFilter === null) {{
            panel.style.borderLeftColor = '#dfe6e9';
            content.innerHTML = `
                <div class="instruction-box">
                    <span style="font-size:3.5rem; display:block; margin-bottom:15px">🔍</span>
                    <p style="font-size:0.9rem; line-height: 1.6;">Selecciona una <b>zona en la leyenda</b> o un <b>punto en el mapa</b> para ver el criterio de riesgo y los municipios que se agrupan en esa categoría.</p>
                </div>
            `;
            return;
        }}

        const clusterKey = `cluster_k${{currentK}}`;
        const colorHex = colors[currentClusterFilter];
        const prof = (allProfiles[currentK] || {{}})[currentClusterFilter] || {{}};

        const munis = new Set();
        seismicPoints.forEach(p => {{
            if (p[clusterKey] === currentClusterFilter && p.year >= yearFrom && p.year <= yearTo) munis.add(p.municipio_region);
        }});

        panel.style.borderLeftColor = colorHex;
        content.innerHTML = `
            <div style="padding:15px">
                <div style="display:flex; align-items:center; margin-bottom:10px">
                    <span style="width:12px; height:12px; border-radius:50%; background:${{colorHex}}; margin-right:8px"></span>
                    <h2 style="margin:0; font-size:1.1rem">Zona ${{currentClusterFilter + 1}}: ${{prof.group_name}}</h2>
                </div>
                
                <div style="font-size:0.75rem; color:#636e72; font-style:italic; margin-bottom:15px">
                    <b>Criterio de Agrupación:</b> ${{prof.grouping_criteria}}
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:15px">
                    <div class="stat-item"><span class="stat-num">${{prof.count}}</span><span class="stat-label">Sismos</span></div>
                    <div class="stat-item"><span class="stat-num">${{prof.max_mag}}</span><span class="stat-label">Mag. Máx</span></div>
                </div>

                <div style="background:#f8f9fa; border-top: 3px solid ${{colorHex}}; padding:12px; border-radius:4px; font-size:0.82rem; line-height:1.5; color:#2d3436; margin-bottom:15px">
                    💡 ${{prof.impact_text}}
                </div>

                <div style="font-size:0.75rem; font-weight:700; margin-bottom:8px; opacity:0.6; text-transform:uppercase; letter-spacing:0.5px">Municipios en esta Zona (${{munis.size}})</div>
                <div class="muni-list">
                    ${{[...munis].sort().map(m => `<span class="muni-tag">${{m}}</span>`).join('')}}
                </div>
            </div>
        `;
    }}

    function showDetails(p) {{
        const clusterIdx = p[`cluster_k${{currentK}}`];
        currentClusterFilter = clusterIdx; // Sincronizar filtro al tocar punto
        renderMarkers();
        updateLegend();
        
        const content = document.getElementById('profile-content');
        const panel = document.getElementById('profile-panel');
        const prof = (allProfiles[currentK] || {{}})[clusterIdx] || {{}};
        const colorHex = colors[clusterIdx];

        let depthDesc = '';
        if (p.depth < 30) depthDesc = `Sismo **muy superficial** (${{p.depth}} km). Sacudida fuerte en superficie.`;
        else if (p.depth < 70) depthDesc = `Sismo **superficial** (${{p.depth}} km). Impacto directo local.`;
        else if (p.depth < 150) depthDesc = `Profundidad **moderada** (${{p.depth}} km). Energía dispersa.`;
        else depthDesc = `**Gran profundidad** (${{p.depth}} km). Vibración suave y balanceo.`;

        panel.style.borderLeftColor = colorHex;
        content.innerHTML = `
            <div style="padding:15px; background: #fdfdfd">
                <div style="border-bottom: 1px solid #eee; padding-bottom:10px; margin-bottom:10px">
                    <h2 style="margin:0; font-size:1.1rem; color:var(--primary)">${{p.municipio_region}}</h2>
                    <span style="font-size:0.8rem; opacity:0.7">${{p.departamento}}</span>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:0.85rem; margin-bottom:12px">
                    <div>💥 Mag: <b>${{p.mag}} ML</b></div>
                    <div>📉 Prof: <b>${{p.depth}} km</b></div>
                    <div>📅 Año: <b>${{p.year}}</b></div>
                    <div>${{prof.risk_icon}} <b>Zona ${{clusterIdx + 1}}</b></div>
                </div>

                <div style="background:${{colorHex}}15; border-left: 3px solid ${{colorHex}}; padding:10px; border-radius:4px; font-size:0.8rem; line-height:1.4; margin-bottom:15px">
                    ${{depthDesc}}
                </div>

                <div style="font-size:0.75rem; border-top: 1px dashed #ccc; padding-top:10px; margin-top:10px">
                    <b style="color:${{colorHex}}">Agrupado en:</b> ${{prof.group_name}}<br>
                    <span style="opacity:0.8">${{prof.grouping_criteria}}</span>
                </div>
                
                <button onclick="updateProfilePanel()" style="width:100%; margin-top:15px; padding:8px; background:#eee; border:none; border-radius:6px; cursor:pointer; font-size:0.75rem">
                    ← Ver todos los municipios de la Zona ${{clusterIdx + 1}}
                </button>
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
        // Actualizar Gráfico de Años (Línea de Tiempo)
        try {{
            const sortedYears = Object.keys(yearData).sort();
            yearChart.data.labels = sortedYears;
            yearChart.data.datasets[0].data = sortedYears.map(y => yearData[y]);
            yearChart.update('none');
        }} catch(e) {{ console.error("Error al actualizar gráfico anual:", e); }}
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
