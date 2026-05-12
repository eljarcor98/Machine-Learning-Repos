"""Genera reports/dashboard_wannacry.html — dashboard standalone sin dependencias de servidor."""
import json
import networkx as nx
from pathlib import Path

ROOT      = Path(__file__).parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT       = ROOT / "reports" / "dashboard_wannacry.html"

with open(PROCESSED / "wannacry_pcap_sir_metadata.json", encoding="utf-8") as f:
    meta = json.load(f)

# Load metrics
try:
    with open(PROCESSED / "ml_clinical_metrics.json", encoding="utf-8") as f:
        metrics_data = json.load(f)
except FileNotFoundError:
    metrics_data = []

PARAMS = {
    "beta_base":  meta["beta_from_pcap"],
    "gamma_base": meta["baseline_gamma"],
    "beta_ks":    meta["contained_beta"],
    "gamma_ks":   meta["contained_gamma"],
    "nodes":      320,
    "steps":      100,
}

# Load actual geographic graph
G_geo = nx.read_graphml(str(PROCESSED / "wannacry_realistic_geo_host_graph.graphml"))
node_mapping = {n: i for i, n in enumerate(G_geo.nodes())}
nodes_json = []
for n, d in G_geo.nodes(data=True):
    lon = d.get("longitude", 0.0)
    lat = d.get("latitude", 0.0)
    nodes_json.append({
        "id": node_mapping[n], 
        "label": d.get("label", n), 
        "country": d.get("country", "Unknown"),
        "x": lon * 8,
        "y": -lat * 8
    })
edges_json = [{"source": node_mapping[u], "target": node_mapping[v]} for u, v in G_geo.edges()]
real_graph_data = {"nodes": nodes_json, "edges": edges_json}

html = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏥 HealTech — Ciberseguridad Epidemiológica</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#050505; --bg-grad: radial-gradient(circle at top, #111424 0%, #050505 100%);
  --card:rgba(22, 27, 34, 0.6); --card-hover:rgba(30, 36, 46, 0.8);
  --border:rgba(255, 255, 255, 0.1); 
  --text:#E2E8F0; --muted:#94A3B8;
  --s:#38BDF8; --i:#F87171; --r:#34D399; --e:#FBBF24; --accent:#818CF8;
  --font-head: 'Outfit', sans-serif;
  --font-body: 'Inter', sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg); background-image:var(--bg-grad); color:var(--text); font-family:var(--font-body); height:100vh; overflow:hidden; display:flex; flex-direction:column;}

h1, h2, h3, h4, .hero-title { font-family: var(--font-head); }

/* HEADER GLOBAL */
#global-header {
  display:flex; 
  background:rgba(10, 12, 16, 0.8); 
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-bottom:1px solid var(--border);
  padding:15px 32px; align-items:center; justify-content:space-between; flex-shrink:0; z-index:50;
  transform: translateY(-100%); transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  position: absolute; width: 100%; top:0;
}
#global-header.show { transform: translateY(0); }

.btn-back {
  background:rgba(255,255,255,0.05); border:1px solid var(--border); color:var(--text); 
  padding:8px 16px; border-radius:8px; cursor:pointer; font-weight:600; font-family:var(--font-body);
  transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.btn-back:hover { background:rgba(129, 140, 248, 0.2); border-color:var(--accent); transform:translateX(-3px); }

/* TABS CONTENEDORES */
.tab-content {
  position: absolute; top:0; left:0; width:100%; height:100%;
  opacity: 0; pointer-events: none;
  transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  transform: scale(0.98); display:flex; flex-direction:column;
}
.tab-content.active {
  opacity: 1; pointer-events: all; transform: scale(1); z-index: 10;
}
/* Empujar el contenido hacia abajo cuando el header está visible (excepto en Simulación si queremos pantalla completa, pero lo haremos general) */
.tab-content.has-header { padding-top: 65px; }

/* LANDING PAGE (HOME) */
#tab-home { align-items:center; justify-content:center; }
#tab-home::before {
  content:""; position:absolute; width:600px; height:600px; 
  background: radial-gradient(circle, rgba(129,140,248,0.15) 0%, rgba(0,0,0,0) 70%);
  top:50%; left:50%; transform:translate(-50%, -50%); z-index:-1; pointer-events:none;
}
.hero-title {
  font-size:4.5rem; font-weight:800; letter-spacing:-1px;
  background:linear-gradient(135deg,#38BDF8,#818CF8,#F87171); -webkit-background-clip:text; -webkit-text-fill-color:transparent; 
  margin-bottom:15px; text-align:center; filter: drop-shadow(0 4px 10px rgba(129,140,248,0.3));
}
.hero-subtitle { color:var(--muted); font-size:1.25rem; font-weight:300; margin-bottom:60px; text-align:center; max-width:650px; line-height:1.6; }

.menu-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:35px; max-width:1150px; width:90%; z-index:10; }
.menu-card {
  background:var(--card); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  border:1px solid var(--border); border-radius:16px; padding:40px 30px; 
  cursor:pointer; transition:all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); text-align:center;
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.menu-card:hover { transform:translateY(-12px) scale(1.02); border-color:var(--accent); box-shadow:0 20px 40px rgba(129,140,248,0.15); background:var(--card-hover); }
.menu-card .icon { font-size:3.5rem; margin-bottom:25px; display:block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3)); }
.menu-card h3 { font-size:1.5rem; color:var(--text); margin-bottom:15px; font-weight:600; }
.menu-card p { color:var(--muted); font-size:0.95rem; line-height:1.6; font-weight:300; }

/* PROSE (Textos) */
.layout-scroll{padding:50px; max-width:900px; margin:0 auto; padding-bottom:120px; overflow-y:auto; width:100%;}
.prose h2 {color:var(--accent); margin-top:40px; margin-bottom:20px; font-size:2rem; font-weight:600;}
.prose p {line-height:1.8; color:var(--muted); margin-bottom:20px; font-size:1.1rem; font-weight:300;}
.prose ul {margin-left:25px; color:var(--muted); font-size:1.1rem; margin-bottom:20px; line-height:1.8; font-weight:300;}

/* CARDS INFO */
.card-grid {display:grid; grid-template-columns:repeat(auto-fit, minmax(350px, 1fr)); gap:25px; margin-top:30px;}
.info-card { background:rgba(255,255,255,0.03); border:1px solid var(--border); border-radius:12px; padding:30px; backdrop-filter:blur(5px); }
.info-card h4 {color:var(--text); margin-bottom:15px; font-size:1.2rem; font-weight:600;}

.metric-big {font-size:3rem; font-weight:800; color:var(--s); margin:15px 0; font-family:var(--font-head);}
.cm-grid {display:grid; grid-template-columns:1fr 1fr; gap:15px; text-align:center;}
.cm-box {padding:25px 15px; border-radius:12px; border:1px solid var(--border); transition:transform 0.2s;}
.cm-box:hover {transform:scale(1.02);}
.cm-box.tp {background:rgba(52, 211, 153,0.05); border-color:rgba(52, 211, 153, 0.3);}
.cm-box.tn {background:rgba(56, 189, 248,0.05); border-color:rgba(56, 189, 248, 0.3);}
.cm-box.fp {background:rgba(251, 191, 36,0.05); border-color:rgba(251, 191, 36, 0.3);}
.cm-box.fn {background:rgba(248, 113, 113,0.05); border-color:rgba(248, 113, 113, 0.3);}
.cm-box .val {font-size:2.5rem; font-weight:800; display:block; margin-bottom:8px; color:var(--text); font-family:var(--font-head);}
.cm-box .lbl {font-size:0.85rem; color:var(--muted); text-transform:uppercase; font-weight:500; letter-spacing:0.5px;}

.image-card {width:100%; max-width:850px; margin:40px auto; display:block; border-radius:16px; border:1px solid var(--border); box-shadow:0 10px 40px rgba(0,0,0,0.3);}

/* ---- LAYOUT SIMULACION ---- */
.layout-sim { position: relative; width: 100%; height: 100%; display: flex; flex-direction: row; }

/* SIDEBAR FLOTANTE (Overlay Vanish) */
.sidebar {
  position: absolute; left: 0; top: 0; bottom: 0; width: 340px;
  background: rgba(10, 12, 16, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255,255,255,0.15); padding: 25px; overflow-y: auto; 
  display: flex; flex-direction: column; gap: 25px;
  z-index: 100;
  transform: translateX(0); opacity: 1; pointer-events: all;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 10px 0 30px rgba(0,0,0,0.5);
}
.sidebar.collapsed {
  transform: translateX(-100%) scale(0.95);
  opacity: 0; pointer-events: none;
}

.sidebar h2 {font-size:0.85rem; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:10px;}
.scenario-btns {display:flex; flex-direction:column; gap:8px;}
.btn-scenario {
  padding:12px 16px; border:1px solid var(--border); background:rgba(255,255,255,0.02); color:var(--text); 
  border-radius:8px; cursor:pointer; font-size:0.9rem; text-align:left; font-family:var(--font-body);
  transition:all 0.2s; font-weight:500;
}
.btn-scenario:hover {border-color:var(--accent); background:rgba(129, 140, 248, 0.1);}
.btn-scenario.active {border-color:var(--accent); background:rgba(129, 140, 248, 0.2); color:#A5B4FC; font-weight:600; box-shadow: inset 4px 0 0 var(--accent);}

.slider-group{display:flex;flex-direction:column;gap:15px;}
.slider-item label{display:flex;justify-content:space-between;font-size:0.85rem;color:var(--muted);margin-bottom:8px; font-weight:500;}
.slider-item label span{color:var(--text);font-weight:600;}
input[type=range] {
  width:100%; accent-color:var(--accent); height:6px; cursor:pointer; 
  background:rgba(255,255,255,0.1); border-radius:3px; outline:none; -webkit-appearance:none;
}
input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:var(--accent); border-radius:50%; }

.metric-box{background:rgba(0,0,0,0.2);border:1px solid var(--border);border-radius:12px;padding:16px;}
.metric-box .metric-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.85rem;}
.metric-box .metric-row:last-child{border-bottom:none;}
.metric-box .metric-row .label{color:var(--muted);}
.metric-box .metric-row .val{font-weight:600;font-size:0.95rem;}
.val.red{color:var(--i);} .val.green{color:var(--r);} .val.blue{color:var(--s);} .val.yellow{color:var(--e);}

/* MAIN DASHBOARD FULL SCREEN */
.main { display:flex; flex-direction:row; width: 100%; height:100%; overflow:hidden; }

/* CHART CARD */
.chart-card {
  background:var(--bg); 
  padding:20px; 
  display:flex; flex-direction:column; gap:10px; 
  min-height:0; min-width:0; overflow:hidden; 
  position: relative;
}

.chart-card h3 {font-size:0.85rem;color:var(--text);text-transform:uppercase;letter-spacing:1px;flex-shrink:0; font-weight:600; z-index:2;}

.chart-container { position:relative; flex-grow:1; min-height:0; min-width:0; width:100%; height:100%; z-index:1;}
.chart-container canvas { position:absolute; left:0; top:0; width:100% !important; height:100% !important; }

.r0-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:700;}
.r0-badge.danger{background:rgba(248, 113, 113,0.15);color:var(--i);border:1px solid rgba(248, 113, 113,0.3);}
.r0-badge.safe{background:rgba(52, 211, 153,0.15);color:var(--r);border:1px solid rgba(52, 211, 153,0.3);}

.top-bar{display:flex;align-items:center;gap:15px; flex-shrink:0; z-index:10;}

.btn-toggle-sidebar {
  background:rgba(129, 140, 248, 0.15); border:1px solid var(--accent); color:var(--text); 
  padding:8px 16px; border-radius:8px; cursor:pointer; font-size:0.85rem; font-weight:600;
  transition:all 0.3s cubic-bezier(0.16, 1, 0.3, 1); display:flex; align-items:center; gap:8px; margin-right:10px;
  box-shadow: 0 4px 12px rgba(129, 140, 248, 0.2);
}
.btn-toggle-sidebar:hover { background:var(--accent); color:#fff; transform:translateY(-2px); box-shadow: 0 6px 16px rgba(129, 140, 248, 0.4); }

.event-log{
  position:absolute; bottom:30px; right:30px; background:rgba(15, 23, 42, 0.95); backdrop-filter:blur(8px);
  border:1px solid var(--border); border-left:4px solid var(--accent); color:var(--text); 
  padding:15px 20px; border-radius:8px; font-size:0.9rem; max-width:350px; z-index:10; 
  display:flex; flex-direction:column; gap:8px; opacity:0; transition:all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
  pointer-events:none; box-shadow:0 10px 25px rgba(0,0,0,0.5); transform:translateY(10px);
}
.event-log.show{opacity:1; transform:translateY(0);}
.event-time{font-weight:700;color:var(--accent);font-size:0.8rem;letter-spacing:0.5px;}

.timeline-ctrl {display:flex; align-items:center; gap:15px; flex:1; margin:0 15px;}
.timeline-ctrl input {flex:1;}
.step-badge {background:rgba(0,0,0,0.4); padding:6px 12px; border-radius:6px; border:1px solid var(--border); font-size:0.85rem; font-family:monospace; min-width:90px; text-align:center; color:var(--accent);}

/* Estilos de botones control simulación */
.ctrl-btn { background:var(--accent); color:#fff; border:none; padding:8px 18px; border-radius:6px; cursor:pointer; font-size:0.9rem; font-weight:600; font-family:var(--font-body); transition:all 0.2s;}
.ctrl-btn:hover { background:#6366F1; transform:scale(1.05); }
.ctrl-select { background:rgba(255,255,255,0.05); color:var(--text); border:1px solid var(--border); border-radius:6px; padding:7px 12px; font-size:0.85rem; outline:none; }
</style>
</head>
<body>

<!-- HEADER GLOBAL -->
<header id="global-header">
  <div style="display:flex; align-items:center; gap:15px;">
    <button class="btn-back" onclick="openHome()">⬅ Volver al Menú Principal</button>
  </div>
  <h1 style="font-size:1.2rem; color:var(--text); margin:0; font-weight:600;" id="header-title">Título</h1>
</header>

<!-- HOME LANDING PAGE -->
<section id="tab-home" class="tab-content active">
  <h1 class="hero-title">🏥 HealTech</h1>
  <p class="hero-subtitle">Plataforma de Ciberseguridad Epidemiológica.<br>Simulando amenazas reales como epidemias biológicas para predecir y contener brotes de malware.</p>
  
  <div class="menu-grid">
    <div class="menu-card" onclick="openSection('tab-context', 'Contexto y Teoría')">
      <span class="icon">📖</span>
      <h3>1. Contexto</h3>
      <p>Aprende la teoría detrás de la analogía médica, los estados Susceptible e Infectado en redes, y los datasets.</p>
    </div>
    <div class="menu-card" onclick="openSection('tab-metrics', 'Análisis de Machine Learning')">
      <span class="icon">📊</span>
      <h3>2. Análisis ML</h3>
      <p>Explora cómo el desempeño clínico de los modelos impacta directamente en el contagio del malware.</p>
    </div>
    <div class="menu-card" onclick="openSection('tab-sim', 'Simulación de Brote Epidemiológico')">
      <span class="icon">🦠</span>
      <h3>3. Simulación</h3>
      <p>Visualiza el brote en tiempo real sobre el mapa de la red. Modifica parámetros e interactúa con el tiempo.</p>
    </div>
  </div>
</section>

<!-- PESTAÑA CONTEXTO -->
<section id="tab-context" class="tab-content has-header">
  <div class="layout-scroll prose">
    <h2>1. Objetivo del Proyecto</h2>
    <p>El proyecto <b>HealTech</b> explora la intersección entre la ciberseguridad y la epidemiología. Tratamos las redes informáticas como poblaciones de pacientes y las amenazas (ransomware, gusanos, botnets) como virus patógenos.</p>
    <p>Al igual que en la medicina, detectar un paciente infectado a tiempo y aislarlo (cuarentena) previene una pandemia. En redes, usar modelos de <i>Machine Learning</i> para detectar anomalías en los flujos de datos nos permite aislar equipos comprometidos antes de que propaguen la amenaza.</p>
    
    <h2>2. Datasets Utilizados</h2>
    <div class="card-grid">
      <div class="info-card">
        <h4>UNSW-NB15 / CIC-IDS2017</h4>
        <p>Datasets masivos de tráfico de red utilizados para entrenar nuestros modelos predictivos. Contienen flujos benignos y cientos de miles de ataques reales etiquetados. Estos datos permiten calcular las tasas de detección reales.</p>
      </div>
      <div class="info-card">
        <h4>WannaCry (PCAP Real - 15/05/2017)</h4>
        <p>Captura de paquetes histórica del ataque masivo de Ransomware WannaCry. De aquí hemos extraído las IPs reales contactadas y calculado empíricamente la agresiva <b>tasa de transmisión (β)</b> del gusano autónomo EternalBlue.</p>
      </div>
    </div>
    
    <h2>3. La Analogía Médica</h2>
    <ul>
      <li><b>Paciente Sano (Susceptible - S):</b> Equipo vulnerable en la red.</li>
      <li><b>Enfermedad Latente (Expuesto - E):</b> Equipo que ha recibido el malware (ej. SMB explotado) pero el payload aún no se ejecuta. Fase de incubación.</li>
      <li><b>Paciente Contagioso (Infectado - I):</b> El malware está activo. Cifra archivos y escanea la red velozmente.</li>
      <li><b>Cuarentena / Curado (Recuperado - R):</b> Equipo parcheado (MS17-010) o aislado por el firewall. Inmune.</li>
    </ul>

    <h2>4. Parámetros del Modelo SEIR</h2>
    <div class="card-grid">
      <div class="info-card">
        <h4>Tasa de Transmisión (β - Beta)</h4>
        <p>Mide qué tan contagioso es el malware. Es la probabilidad de que un equipo infectado logre vulnerar a un equipo susceptible al contactarlo. En WannaCry, su naturaleza autónoma hace que este valor sea extremadamente alto.</p>
      </div>
      <div class="info-card">
        <h4>Tasa de Recuperación (γ - Gamma)</h4>
        <p>Representa la velocidad a la que los equipos infectados son aislados (firewall) o curados (parcheados). A mayor Gamma, más rápido se contiene la amenaza. Está directamente ligada a la velocidad de respuesta del equipo de SOC.</p>
      </div>
      <div class="info-card">
        <h4>Tasa de Incubación (σ - Sigma / Alfa)</h4>
        <p>Mide el tiempo que pasa desde que un equipo es vulnerado hasta que empieza a escanear a otros (pasa de Expuesto a Infectado). En el caso del malware, puede ser el tiempo de descarga del payload y ejecución de rutinas criptográficas.</p>
      </div>
    </div>
  </div>
</section>

<!-- PESTAÑA METRICAS -->
<section id="tab-metrics" class="tab-content has-header">
  <div class="layout-scroll prose">
    <h2>Análisis Clínico de Detección de Amenazas</h2>
    <p>Evaluar un modelo de ciberseguridad como si fuera una prueba de detección de enfermedades nos da una visión cruda del impacto de sus errores. Un falso negativo en un gusano no es solo un error, es un paciente cero en potencia.</p>

    <div id="metrics-container"></div>
    
    <div class="card-grid" style="margin-top: 10px;">
      <div class="info-card">
        <h4>Sensibilidad (Tasa de Verdaderos Positivos)</h4>
        <p>Porcentaje de ataques reales que el modelo logró detectar. En epidemiología, si tu sensibilidad es baja, estás dejando caminar a personas infectadas (falsos negativos) libres por el hospital. En redes, es el parámetro más crítico para evitar pandemias digitales.</p>
      </div>
      <div class="info-card">
        <h4>Especificidad (Tasa de Verdaderos Negativos)</h4>
        <p>Porcentaje de tráfico benigno correctamente identificado. Si es baja, generas muchas Falsas Alarmas (falsos positivos), lo que en nuestra analogía significa poner en cuarentena a equipos sanos y detener las operaciones del negocio innecesariamente.</p>
      </div>
      <div class="info-card">
        <h4>Número Reproductivo Básico (R₀)</h4>
        <p>Promedio de equipos que un solo equipo infectado logrará contagiar en una red virgen. Si <b>R₀ > 1</b>, el brote crecerá exponencialmente. Si logramos reducirlo a <b>R₀ < 1</b> (mejorando la detección o aislando rápido), la epidemia morirá sola.</p>
      </div>
    </div>

    <div class="card-grid">
      <div class="info-card">
        <h4>El Índice de Youden (J)</h4>
        <p>En epidemiología, el <i>Índice de Youden</i> (Sensibilidad + Especificidad - 1) busca el umbral perfecto de decisión. Maximiza la detección de enfermos reales y minimiza las cuarentenas innecesarias a sanos. Es la métrica ideal para configurar reglas de cortafuegos.</p>
        <div class="metric-big" id="val-youden">--</div>
      </div>
      <div class="info-card">
        <h4>Falso Negativo (Peligro Crítico)</h4>
        <p>Un equipo infectado clasificado como benigno. En el modelo SIR, esto incrementa drásticamente la tasa efectiva de transmisión (<b>β efectiva</b>) ya que el equipo sigue activo en la red local buscando vulnerabilidades por el puerto 445.</p>
      </div>
    </div>

    <h2>Gráficos de Desempeño</h2>
    <p>Distribución clínica e impacto en los parámetros de propagación.</p>
    <img src="figures/07_sir_panel_clinico.png" alt="Panel clínico" class="image-card" onerror="this.style.display='none'">
    <img src="figures/06_ml_clinical_sir_panel.png" alt="ROC" class="image-card" onerror="this.style.display='none'">
  </div>
</section>

<!-- PESTAÑA SIMULACIÓN -->
<section id="tab-sim" class="tab-content has-header layout-sim">
  
  <!-- MAIN FULL SCREEN CON MAPA GIGANTE -->
  <main class="main" style="flex-direction:row;">
    
    <!-- COLUMNA IZQUIERDA (GRÁFICOS) -->
    <div class="charts-left" style="display:flex; flex-direction:column; width:450px; flex-shrink:0; gap:1px; background:var(--border); border-right:1px solid var(--border); z-index:2;">
      
      <!-- SIR Principal -->
      <div class="chart-card" style="flex:1.5;">
        <div class="top-bar" style="margin-bottom:10px;">
          <button class="btn-toggle-sidebar" onclick="toggleSidebar()" id="btn-toggle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            ⚙️ Panel
          </button>
          <h3 id="sir-title" style="margin:0;">Curva SIR</h3>
        </div>
        <span class="r0-badge danger" id="r0-badge" style="position:absolute; top:20px; right:20px; z-index:10;">R₀ = 23.1</span>
        <div class="chart-container"><canvas id="cSIR"></canvas></div>
      </div>
      
      <!-- Fila Intermedia: R(t) y Velocidad -->
      <div style="display:flex; flex:1; gap:1px; background:var(--border);">
        <div class="chart-card" style="flex:1; padding:15px;">
          <h3 style="font-size:0.75rem; margin-bottom:5px;">R(t) — N. Reproductivo</h3>
          <div class="chart-container"><canvas id="cRt"></canvas></div>
        </div>
        <div class="chart-card" style="flex:1; padding:15px;">
          <h3 style="font-size:0.75rem; margin-bottom:5px;">Velocidad (Nuevos/h)</h3>
          <div class="chart-container"><canvas id="cSpeed"></canvas></div>
        </div>
      </div>

      <!-- Fila Inferior: Pie Chart -->
      <div class="chart-card" style="flex:0.8; padding:15px;">
        <h3 style="font-size:0.75rem; margin-bottom:5px;">Distribución Final</h3>
        <div class="chart-container"><canvas id="cPie"></canvas></div>
      </div>
      
    </div>

    <!-- COLUMNA DERECHA (MAPA GIGANTE) -->
    <div class="map-right" style="flex:1; position:relative; background:var(--bg); display:flex; flex-direction:column;">
      <div class="top-bar" style="position:absolute; top:20px; left:20px; right:20px; z-index:10; background:rgba(10,12,16,0.7); padding:15px 25px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(10px); display:flex; justify-content:space-between; align-items:center; box-shadow:0 8px 32px rgba(0,0,0,0.4);">
        <h3 style="margin:0; color:var(--text); font-family:var(--font-head); font-size:1.2rem; text-shadow:0 2px 4px rgba(0,0,0,0.5);">Mapa de Infección Geo-Localizada</h3>
        <div style="display:flex; align-items:center; gap:20px; flex:1; max-width:650px;">
          <div class="timeline-ctrl" style="flex:1; margin:0;">
            <input type="range" id="timeline-slider" min="0" max="100" value="0">
            <span class="step-badge" id="step-badge">Paso: 0</span>
          </div>
          <select id="sel-speed" class="ctrl-select">
            <option value="300">Lento</option>
            <option value="100" selected>Normal</option>
            <option value="30">Rápido</option>
          </select>
          <button id="btn-play" class="ctrl-btn">▶ Play</button>
        </div>
      </div>
      
      <div class="chart-container" id="networkGraph" style="width:100%; height:100%; flex-grow:1;"></div>
      
      <div id="event-log" class="event-log" style="bottom:30px; right:30px; left:auto; max-width:400px; padding:20px;">
        <div class="event-time" id="ev-time"></div>
        <div class="event-msg" id="ev-msg"></div>
      </div>
    </div>
  </main>

  <!-- OVERLAY SIDEBAR -->
  <aside class="sidebar collapsed" id="sidebar">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h2 style="margin:0; font-size:1rem; color:var(--text); font-weight:800;">Panel de Control</h2>
      <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.5rem; cursor:pointer;">&times;</button>
    </div>
    
    <div>
      <h2>Escenario</h2>
      <div class="scenario-btns">
        <button class="btn-scenario" data-sc="libre" onclick="closeSidebarAfterSelect()">🔴 Sin Contención (Original)</button>
        <button class="btn-scenario" data-sc="ks" onclick="closeSidebarAfterSelect()">🟢 Kill-Switch Activado</button>
        <button class="btn-scenario active" data-sc="seir" onclick="closeSidebarAfterSelect()">🟣 SEIR (Periodo Latencia)</button>
        <button class="btn-scenario" data-sc="manual" onclick="closeSidebarAfterSelect()">⚙️ Parámetros Manuales</button>
      </div>
    </div>
    <div>
      <h2>Parámetros Clínicos</h2>
      <div class="slider-group">
        <div class="slider-item">
          <label>β transmisión <span id="vb">0.92</span></label>
          <input type="range" id="sb" min="0.01" max="1" step="0.01" value="0.9223">
        </div>
        <div class="slider-item">
          <label>γ recuperación <span id="vg">0.04</span></label>
          <input type="range" id="sg" min="0.01" max="0.5" step="0.01" value="0.04">
        </div>
        <div class="slider-item">
          <label>σ incubación (SEIR) <span id="vs">0.50</span></label>
          <input type="range" id="ss" min="0.05" max="1" step="0.05" value="0.5">
        </div>
        <div class="slider-item">
          <label>Pasos Temporales <span id="vsteps">100</span></label>
          <input type="range" id="ssteps" min="20" max="200" step="5" value="100">
        </div>
        <div class="slider-item">
          <label>Inmunidad Inicial (R) <span id="vvax">0%</span></label>
          <input type="range" id="svax" min="0" max="100" step="5" value="0">
        </div>
        <div class="slider-item" style="display:none;">
          <label>Nodos red <span id="vn">320</span></label>
          <input type="range" id="sn" min="50" max="600" step="50" value="320">
        </div>
      </div>
    </div>
    <div>
      <h2>Indicadores Epidémicos</h2>
      <div class="metric-box" id="metrics"></div>
    </div>
  </aside>

</section>

<script>
// ── UI Toggles y Animaciones ──────────────────────────────────────────────────
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  sb.classList.toggle('collapsed');
}
function closeSidebarAfterSelect() {
  document.getElementById('sidebar').classList.add('collapsed');
}

// ── Navegación Home -> Secciones (Efecto Vanish) ──────────────────────────────
function openHome() {
  // Ocultar header
  document.getElementById('global-header').classList.remove('show');
  
  // Ocultar todas las secciones
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  
  // Mostrar home
  document.getElementById('tab-home').classList.add('active');
}

function openSection(tabId, title) {
  // Desaparecer home y otras secciones suavemente
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  
  // Mostrar header animado
  document.getElementById('global-header').classList.add('show');
  document.getElementById('header-title').textContent = title;
  
  // Mostrar la nueva sección
  const target = document.getElementById(tabId);
  target.classList.add('active');
  
  // Si es simulación, forzar reflow para Canvas y esconder sidebar
  if(tabId === 'tab-sim') {
      document.getElementById('sidebar').classList.add('collapsed');
      window.dispatchEvent(new Event('resize'));
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        if(charts['cSIR']) charts['cSIR'].update();
      }, 300);
  }
}

// ── Configuracion global ──────────────────────────────────────────────────────
const PARAMS = """ + json.dumps(PARAMS) + r""";
const REAL_GRAPH = """ + json.dumps(real_graph_data) + r""";
const ML_METRICS = """ + json.dumps(metrics_data) + r""";

if(ML_METRICS && ML_METRICS.length > 0) {
  const m = ML_METRICS[0];
  document.getElementById('val-youden').textContent = (m.youden_index * 100).toFixed(1) + '%';
  document.getElementById('metrics-container').innerHTML = `
    <div class="card-grid" style="margin-bottom:30px;">
      <div class="info-card">
        <h4 style="border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px; margin-bottom:15px;">Modelo: ${m.model_name}</h4>
        <div class="cm-grid">
          <div class="cm-box tp"><span class="val">${m.TP}</span><span class="lbl">Verd. Positivo<br>(Ataque detenido)</span></div>
          <div class="cm-box fn"><span class="val">${m.FN}</span><span class="lbl">Falso Negativo<br>(Infectado Oculto)</span></div>
          <div class="cm-box fp"><span class="val">${m.FP}</span><span class="lbl">Falso Positivo<br>(Falsa Alarma)</span></div>
          <div class="cm-box tn"><span class="val">${m.TN}</span><span class="lbl">Verd. Negativo<br>(Tráfico Sano)</span></div>
        </div>
      </div>
      <div class="info-card">
        <h4>Efecto en los Parámetros Epidémicos</h4>
        <p>Sensibilidad: <b style="color:var(--text);">${(m.sensitivity*100).toFixed(2)}%</b></p>
        <p>Especificidad: <b style="color:var(--text);">${(m.specificity*100).toFixed(2)}%</b></p>
        <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:20px 0;">
        <p style="color:var(--r); font-size:1.15rem; margin-bottom:8px;"><b>γ efectiva (Recuperación):</b> ${m.gamma_effective.toFixed(4)}</p>
        <p style="color:var(--i); font-size:1.15rem; margin-bottom:20px;"><b>β efectiva (Transmisión):</b> ${m.beta_effective.toFixed(4)}</p>
        <p style="color:var(--s); font-size:1.6rem; font-weight:800; font-family:var(--font-head);">R₀ efectivo: ${m.r0_effective.toFixed(2)}</p>
        <p style="color:var(--muted); font-size:0.85rem; margin-top:8px;">(Un R0 menor a 1 previene la epidemia).</p>
      </div>
    </div>
  `;
}

function loadRealGraph(){
  let adj = Array.from({length: PARAMS.nodes}, ()=>new Set());
  REAL_GRAPH.edges.forEach(e=>{
    adj[e.source].add(e.target);
    adj[e.target].add(e.source);
  });
  return adj;
}

function runSIR(adj, n, beta, gamma, steps, vax=0, initInfected=[4]){
  let state = Array(n).fill('S');
  initInfected.forEach(i=>state[i]='I');
  let cands = [];
  for(let i=0; i<n; i++) if(state[i]==='S') cands.push(i);
  cands.sort(()=>Math.random()-0.5);
  for(let i=0; i<Math.floor(vax*n); i++) state[cands[i]] = 'R';
  let history = [];
  for(let step=0;step<=steps;step++){
    let S=0,I=0,R=0;
    state.forEach(s=>{if(s==='S')S++;else if(s==='I')I++;else R++;});
    history.push({step,S,I,R,E:0, states: [...state]});
    if(step===steps) break;
    let next = [...state];
    for(let node=0;node<n;node++){
      if(state[node]==='I'){
        adj[node].forEach(nb=>{if(state[nb]==='S'&&Math.random()<beta) next[nb]='I';});
        if(Math.random()<gamma) next[node]='R';
      }
    }
    state = next;
  }
  return {history, finalState: state};
}

function runSEIR(adj, n, beta, sigma, gamma, steps, vax=0, initInfected=[4]){
  let state = Array(n).fill('S');
  initInfected.forEach(i=>state[i]='I');
  let cands = [];
  for(let i=0; i<n; i++) if(state[i]==='S') cands.push(i);
  cands.sort(()=>Math.random()-0.5);
  for(let i=0; i<Math.floor(vax*n); i++) state[cands[i]] = 'R';
  let history = [];
  for(let step=0;step<=steps;step++){
    let S=0,I=0,R=0,E=0;
    state.forEach(s=>{if(s==='S')S++;else if(s==='I')I++;else if(s==='R')R++;else E++;});
    history.push({step,S,I,R,E, states: [...state]});
    if(step===steps) break;
    let next=[...state];
    for(let node=0;node<n;node++){
      if(state[node]==='I'){
        adj[node].forEach(nb=>{if(state[nb]==='S'&&Math.random()<beta) next[nb]='E';});
        if(Math.random()<gamma) next[node]='R';
      } else if(state[node]==='E'){
        if(Math.random()<sigma) next[node]='I';
      }
    }
    state=next;
  }
  return {history, finalState: state};
}

let adj = loadRealGraph();
let scenario = 'seir';
let charts   = {};
let currentHist = [];
let networkNodes = new vis.DataSet();
let networkEdges = new vis.DataSet();
let network = null;
let currentN = 0;
let playInterval = null;
let currentGlobalStep = 0;

function initNetwork() {
  const container = document.getElementById('networkGraph');
  const data = { nodes: networkNodes, edges: networkEdges };
  const options = {
    nodes: { shape: 'dot', size: 6, borderWidth: 1, borderColor: '#000' },
    edges: { color: 'rgba(255,255,255,0.08)', width: 1 },
    physics: { enabled: false }, 
    interaction: { dragNodes: false, zoomView: true, dragView: true }
  };
  network = new vis.Network(container, data, options);
  const mapImg = new Image();
  mapImg.src = 'https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg';
  network.on("beforeDrawing", function(ctx) {
    if (mapImg.complete) {
      ctx.globalAlpha = 0.1;
      ctx.drawImage(mapImg, -1440, -680, 2880, 1400);
      ctx.globalAlpha = 1.0;
    }
  });
}

function getParams(){
  return {
    beta:  parseFloat(document.getElementById('sb').value),
    gamma: parseFloat(document.getElementById('sg').value),
    sigma: parseFloat(document.getElementById('ss').value),
    steps: parseInt(document.getElementById('ssteps').value),
    n:     parseInt(document.getElementById('sn').value),
  };
}

function simulate(){
  const p = getParams();
  const n = p.n;
  let beta=p.beta, gamma=p.gamma;
  if(scenario==='libre'){beta=PARAMS.beta_base; gamma=PARAMS.gamma_base;}
  else if(scenario==='ks'){beta=PARAMS.beta_ks; gamma=PARAMS.gamma_ks;}
  if(scenario!=='manual'&&scenario!=='seir'){
    document.getElementById('sb').value=beta;
    document.getElementById('sg').value=gamma;
    document.getElementById('vb').textContent=beta.toFixed(2);
    document.getElementById('vg').textContent=gamma.toFixed(2);
  }
  
  let res;
  if(scenario==='seir') res = runSEIR(adj,n,beta,p.sigma,gamma,p.steps);
  else res = runSIR(adj,n,beta,gamma,p.steps);
  
  currentHist = res.history;
  document.getElementById('timeline-slider').max = p.steps;
  
  return {hist: res.history, finalState: res.finalState, beta, gamma, n, p};
}

const CGRID  = 'rgba(255,255,255,0.05)';
const CTEXT  = '#94A3B8';
const commonOpts = {
  responsive:true, maintainAspectRatio:false, animation:{duration:0}, 
  plugins:{legend:{labels:{color:CTEXT,boxWidth:12,font:{family:'Inter',size:11}}}},
  scales:{
    x:{grid:{color:CGRID},ticks:{color:CTEXT,maxTicksLimit:10,font:{family:'Inter',size:10}}},
    y:{grid:{color:CGRID},ticks:{color:CTEXT,font:{family:'Inter',size:10}}}
  }
};
function mkLine(id, datasets, labels, extraOpts={}){
  const ctx = document.getElementById(id).getContext('2d');
  if(charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx,{
    type:'line',
    data:{labels, datasets},
    options:{...commonOpts,...extraOpts, plugins:{...commonOpts.plugins,...(extraOpts.plugins||{})}}
  });
}
function mkBar(id, data, labels, colors, extraOpts={}){
  const ctx = document.getElementById(id).getContext('2d');
  if(charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx,{
    type:'bar',
    data:{labels, datasets:[{data, backgroundColor:colors, borderWidth:0}]},
    options:{...commonOpts,...extraOpts,plugins:{legend:{display:false}}}
  });
}
function mkDoughnut(id, data, labels, colors){
  const ctx = document.getElementById(id).getContext('2d');
  if(charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx,{
    type:'doughnut',
    data:{labels, datasets:[{data, backgroundColor:colors, borderWidth:0}]},
    options:{responsive:true,maintainAspectRatio:false,animation:{duration:0},
      cutout:'70%',
      plugins:{legend:{labels:{color:CTEXT,font:{family:'Inter',size:11}}}}}
  });
}

function render(forceRecalc=true){
  if(forceRecalc) {
    let result = simulate();
    currentGlobalStep = result.p.steps; 
    document.getElementById('timeline-slider').value = currentGlobalStep;
  }
  
  const hist = currentHist;
  const n = currentN || getParams().n;
  const beta = parseFloat(document.getElementById('sb').value);
  const gamma = parseFloat(document.getElementById('sg').value);
  
  const startDate = new Date("2017-05-12T08:00:00Z");
  const steps_labels = hist.map(h => {
    let d = new Date(startDate.getTime() + h.step * 60 * 60 * 1000); 
    return d.toLocaleString('es-ES', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
  });
  
  const r0 = beta/gamma;
  const peakRow = hist.reduce((a,b)=>b.I>a.I?b:a);
  const last = hist[hist.length-1];
  const Rt = hist.map(h=>(beta/gamma)*(h.S/n));
  const dI = hist.map((h,i)=>i===0?0:h.I-hist[i-1].I);
  
  window.fullRt = Rt;
  window.fullSpeed = dI;
  window.fullLabels = steps_labels;
  const rtCross = hist.findIndex(h=>(beta/gamma)*(h.S/n)<1);

  if(forceRecalc) {
    const titles = {libre:'SIR — Sin Contención',ks:'SIR — Kill-Switch',seir:'SEIR — Con Latencia',manual:'SIR — Personalizado'};
    document.getElementById('sir-title').textContent = titles[scenario];
    const badge = document.getElementById('r0-badge');
    badge.textContent = 'R₀ = '+r0.toFixed(2);
    badge.className = 'r0-badge '+(r0>1?'danger':'safe');

    const savedPct = ((last.S/n)*100).toFixed(1);
    const finalR   = ((last.R/n)*100).toFixed(1);
    const peakPct  = ((peakRow.I/n)*100).toFixed(1);
    const contThr  = (r0/(1+r0)*100).toFixed(1);
    document.getElementById('metrics').innerHTML = [
      ['R₀ base', r0.toFixed(2), r0>1?'red':'green'],
      ['Pico infección', peakPct+'% · '+steps_labels[peakRow.step], 'red'],
      ['Tasa ataque final', finalR+'%', 'yellow'],
      ['No infectados', savedPct+'%', 'green'],
      ['R(t)<1 desde', rtCross>=0?steps_labels[rtCross]:'nunca', 'blue'],
      ['β / γ', beta.toFixed(3)+' / '+gamma.toFixed(3), ''],
    ].map(([l,v,c])=>`<div class="metric-row"><span class="label">${l}</span><span class="val ${c}">${v}</span></div>`).join('');

    const sirDs = [
      {label:'Susceptibles (S)',data:hist.map(h=>+(h.S/n*100).toFixed(1)),borderColor:'#38BDF8',backgroundColor:'rgba(56, 189, 248, 0.1)',fill:true,tension:0.4,pointRadius:0,borderWidth:2},
      {label:'Infectados (I)',  data:hist.map(h=>+(h.I/n*100).toFixed(1)),borderColor:'#F87171',backgroundColor:'rgba(248, 113, 113, 0.15)', fill:true,tension:0.4,pointRadius:0,borderWidth:2.5},
      {label:'Recuperados (R)', data:hist.map(h=>+(h.R/n*100).toFixed(1)),borderColor:'#34D399',backgroundColor:'rgba(52, 211, 153, 0.1)',fill:true,tension:0.4,pointRadius:0,borderWidth:2},
    ];
    if(scenario==='seir')
      sirDs.push({label:'Expuestos (E)',data:hist.map(h=>+(h.E/n*100).toFixed(1)),borderColor:'#FBBF24',backgroundColor:'transparent',fill:false,tension:0.4,pointRadius:0,borderWidth:2,borderDash:[4,4]});
    mkLine('cSIR', sirDs, steps_labels, {
      scales:{
        x:{...commonOpts.scales.x,title:{display:false}},
        y:{...commonOpts.scales.y,min:0,max:100,ticks:{...commonOpts.scales.y.ticks,callback:v=>v+'%'}}
      },
      plugins:{
        legend:{labels:{color:CTEXT,boxWidth:12,font:{family:'Inter',size:11}}},
        annotation:{annotations:{peak:{type:'line',xMin:steps_labels[peakRow.step],xMax:steps_labels[peakRow.step],borderColor:'rgba(248, 113, 113, 0.5)',borderWidth:1,borderDash:[4,4]}}}
      }
    });

    mkLine('cRt',[
      {label:'R(t)',data:Rt.map(v=>+v.toFixed(3)),borderColor:'#FBBF24',backgroundColor:'rgba(251, 191, 36, 0.1)',fill:true,tension:0.4,pointRadius:0,borderWidth:2},
      {label:'R=1',data:steps_labels.map(()=>1),borderColor:'#94A3B8',borderWidth:1.5,borderDash:[6,4],pointRadius:0},
    ], steps_labels, {scales:{x:{...commonOpts.scales.x},y:{...commonOpts.scales.y,title:{display:false}}}});

    mkBar('cSpeed', dI, steps_labels, dI.map(v=>v>=0?'rgba(248, 113, 113, 0.8)':'rgba(52, 211, 153, 0.8)'), {
      scales:{x:{...commonOpts.scales.x},y:{...commonOpts.scales.y,title:{display:false}}}
    });

    mkDoughnut('cPie',[last.S,last.I,last.R],['S','I','R'],['#38BDF8','#F87171','#34D399']);

    if(n !== currentN) {
      currentN = n;
      networkNodes.clear();
      networkEdges.clear();
      let nodesArr = [];
      for(let i=0; i<n; i++) {
         let d = REAL_GRAPH.nodes[i];
         nodesArr.push({ id: i, title: '<b>'+d.label+'</b><br>'+d.country, color:'#38BDF8', x: d.x, y: d.y, fixed: true });
      }
      let edgesArr = [];
      REAL_GRAPH.edges.forEach(e => { edgesArr.push({from: e.source, to: e.target}); });
      networkNodes.add(nodesArr);
      networkEdges.add(edgesArr);
    }
  }

  updateToStep(currentGlobalStep);
}

function updateToStep(step) {
  document.getElementById('step-badge').textContent = 'Paso: ' + step;
  if(!currentHist || !currentHist[step]) return;
  const n = currentN;
  let state = currentHist[step].states;
  
  let updates = [];
  for(let i=0; i<n; i++) {
    let s = state[i];
    let c = s==='S' ? '#38BDF8' : s==='I' ? '#F87171' : s==='R' ? '#34D399' : '#FBBF24';
    updates.push({id: i, color: c});
  }
  networkNodes.update(updates);
  
  let curr = currentHist[step];
  if(charts['cPie']){
    charts['cPie'].data.datasets[0].data = [curr.S, curr.I, curr.R];
    charts['cPie'].update();
  }

  let pHist = currentHist.slice(0, step + 1);
  if(charts['cSIR']){
    charts['cSIR'].data.labels = window.fullLabels.slice(0, step + 1);
    charts['cSIR'].data.datasets[0].data = pHist.map(h=>+(h.S/n*100).toFixed(1));
    charts['cSIR'].data.datasets[1].data = pHist.map(h=>+(h.I/n*100).toFixed(1));
    charts['cSIR'].data.datasets[2].data = pHist.map(h=>+(h.R/n*100).toFixed(1));
    if(charts['cSIR'].data.datasets[3]) charts['cSIR'].data.datasets[3].data = pHist.map(h=>+(h.E/n*100).toFixed(1));
    charts['cSIR'].update('none');
  }
  if(charts['cRt'] && window.fullRt){
    charts['cRt'].data.labels = window.fullLabels.slice(0, step + 1);
    charts['cRt'].data.datasets[0].data = window.fullRt.slice(0, step + 1).map(v=>+v.toFixed(3));
    charts['cRt'].data.datasets[1].data = window.fullLabels.slice(0, step + 1).map(()=>1);
    charts['cRt'].update('none');
  }
  if(charts['cSpeed'] && window.fullSpeed){
    let pSpeed = window.fullSpeed.slice(0, step + 1);
    charts['cSpeed'].data.labels = window.fullLabels.slice(0, step + 1);
    charts['cSpeed'].data.datasets[0].data = pSpeed;
    charts['cSpeed'].data.datasets[0].backgroundColor = pSpeed.map(v=>v>=0?'rgba(248, 113, 113, 0.8)':'rgba(52, 211, 153, 0.8)');
    charts['cSpeed'].update('none');
  }
  
  const HISTORICAL_EVENTS = [
    { step: 0, msg: "Brote inicial detectado (SMBv1)." },
    { step: 3, msg: "Propagación masiva y autónoma por la red." },
    { step: 7, msg: "Marcus Hutchins descubre el dominio Kill-Switch." },
    { step: 16, msg: "Colapso global reportado en sistemas hospitalarios." },
    { step: 24, msg: "Aplicación de parches de emergencia (MS17-010)." },
    { step: 40, msg: "Aislamiento a nivel de firewall completado." },
    { step: 72, msg: "Inicio de la fase de recuperación." }
  ];
  let currentEvent = [...HISTORICAL_EVENTS].reverse().find(e => step >= e.step);
  if(currentEvent) {
     document.getElementById('event-log').classList.add('show');
     document.getElementById('ev-time').textContent = "⏱ " + window.fullLabels[step];
     document.getElementById('ev-msg').textContent = currentEvent.msg;
  } else {
     document.getElementById('event-log').classList.remove('show');
  }
}

document.querySelectorAll('.btn-scenario').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.btn-scenario').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    scenario = btn.dataset.sc;
    render(true);
  });
});

['sb','sg','ss','ssteps','svax','sn'].forEach(id=>{
  const el = document.getElementById(id);
  const labelId = id.replace('s','v');
  el.addEventListener('input',()=>{
    document.getElementById(labelId).textContent=(id==='svax') ? el.value+'%' : parseFloat(el.value).toFixed(id==='ss'?2:id==='ssteps'||id==='sn'?0:2);
    if(scenario!=='manual') {scenario='manual'; document.querySelectorAll('.btn-scenario').forEach(b=>{b.classList.remove('active');if(b.dataset.sc==='manual')b.classList.add('active');});}
    render(true);
  });
});

document.getElementById('timeline-slider').addEventListener('input', (e) => {
  if (playInterval) { clearInterval(playInterval); playInterval = null; document.getElementById('btn-play').textContent = '▶ Play'; }
  currentGlobalStep = parseInt(e.target.value);
  updateToStep(currentGlobalStep);
});

document.getElementById('btn-play').addEventListener('click', () => {
  if (playInterval) { 
    clearInterval(playInterval); 
    playInterval = null; 
    document.getElementById('btn-play').textContent = '▶ Play';
    return;
  }
  if (currentGlobalStep >= parseInt(document.getElementById('ssteps').value)) {
    currentGlobalStep = 0;
  }
  
  document.getElementById('btn-play').textContent = '⏹ Stop';
  playInterval = setInterval(() => {
    if (currentGlobalStep >= currentHist.length - 1) {
      clearInterval(playInterval);
      playInterval = null;
      document.getElementById('btn-play').textContent = '▶ Play';
      return;
    }
    currentGlobalStep++;
    document.getElementById('timeline-slider').value = currentGlobalStep;
    updateToStep(currentGlobalStep);
  }, parseInt(document.getElementById('sel-speed').value));
});

window.addEventListener('load', () => { initNetwork(); render(true); currentGlobalStep = 0; document.getElementById('timeline-slider').value = 0; updateToStep(0); });
window.addEventListener('resize', () => {
  Object.values(charts).forEach(c => c.resize());
});
</script>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print(f"[OK] Dashboard generado: {OUT}")
print(f"     Abre en browser: {OUT.resolve()}")
