---
description: Proceso de Scraping Profundo y Visualización Táctica de WhoScored (/scraping-whoscored)
---

Este workflow automatiza la extracción de pases y posiciones de cualquier partido de WhoScored guardado localmente.

### Instrucciones de Uso
Para ejecutar este proceso en un nuevo partido, simplemente asegúrate de tener el HTML guardado y especifica las rutas cuando se te solicite, o sigue estos pasos:

### Paso 1: Localizar el HTML del Partido
Guarda el partido completo desde WhoScored en tu carpeta de datos.
Ruta recomendada: `data/raw/scraped_data/[Nombre_Partido].html`

### Paso 2: Procesamiento Automático
Este comando ejecutará la cadena completa de herramientas:
1. Extracción de `matchCentreData` desde el HTML.
2. Análisis de pases y receptores para ambos equipos.
3. Inyección de datos tácticos en el visor HTML.

// turbo
```powershell
# Define las rutas aquí para automatizar
$HTML_INPUT = "data/raw/scraped_data/Everton 2-0 Burnley - Premier League 2025_2026 Live.html"
$JSON_FULL = "data/raw/scraped_data/full_events.json"
$JSON_TACTIC = "data/raw/scraped_data/tactical_data.json"
$HTML_VIEWER = "reports/match_viewer_everton_burnley.html"

# Ejecución de la cadena genérica
python "src/extract_local_data.py" "$HTML_INPUT" "$JSON_FULL"
python "src/extract_both_teams.py" "$JSON_FULL" "$JSON_TACTIC"
python "src/inject_both_teams.py" "$JSON_TACTIC" "$HTML_VIEWER"
```

### Paso 3: Abrir Visor
Abre el archivo indicado en `$HTML_VIEWER` para ver la red de pases reales dinámica.

---
> [!IMPORTANT]
> Los scripts se encuentran en `src/` y están diseñados para ser agnósticos al partido. Puedes copiar este workflow y la carpeta `src/` a cualquier otro proyecto de Machine Learning para habilitar el comando `/scraping-whoscored` instantáneamente.
