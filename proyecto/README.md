# Proyecto de Análisis de Terremotos (USGS)

Este proyecto tiene como objetivo analizar los datos sísmicos obtenidos de la USGS para un área geográfica específica (Colombia y alrededores), siguiendo la metodología CRISP-DM.

## Estructura del Proyecto

- `data/`: Datos crudos (`earthquakes_raw.csv`) y enriquecidos (`earthquakes_enriched.csv`).
- `documentacion/`: 
    - `visualizaciones/`: Gráficos de nulos, correlación, frecuencia regional y mapas.
    - `reporte_interactivo.html`: Versión premium e interactiva del informe final.
- `reporte_final/`: Informe consolidado `REPORTE_CRISP_DM.md`.
- `scripts/`: 
    - `load_data.py`: Descarga de datos.
    - `enrich_dataset.py`: Limpieza y extracción de municipios/región.
    - `phase2_analysis.py`: Análisis de nulos y correlación.
    - `region_analysis.py`: Análisis de frecuencia geográfica.
    - `generate_html_report.py`: Generador del reporte interactivo.
- `.venv/`: Entorno virtual.

## Hitos del Proyecto (CRISP-DM)

### Fase 1: Entendimiento del Negocio
- Definición de objetivos: Identificar patrones sísmicos y zonas de alto riesgo.
- Contextualización geológica (Mapas de fallas).

### Fase 2: Entendimiento de los Datos
- **Calidad de Datos:** Identificación de valores nulos ( NST y errores instrumentales).
- **Correlación:** Análisis de la relación Magnitud vs Profundidad (Pearson: -0.06).
- **Frecuencia Regional:** Identificación de Cepitá y Jordán como puntos calientes (Nido de Bucaramanga).

### Fase 3: Preparación de Datos
- Enriquecimiento del dataset con etiquetas geográficas claras.
- Limpieza de datos no representativos.

## Cómo empezar

1. Activa el entorno virtual:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. Instala las dependencias:
   ```powershell
   pip install pandas seaborn matplotlib folium jinja2
   ```
3. Genera el reporte interactivo:
   ```powershell
   python scripts/generate_html_report.py
   ```
