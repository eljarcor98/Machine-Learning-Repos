# Proyecto de Análisis de Riesgo Sísmico (Colombia - USGS)

Este proyecto implementa un flujo de trabajo basado en la metodología **CRISP-DM** para analizar datos sísmicos obtenidos de la United States Geological Survey (USGS). El objetivo principal es identificar y segmentar zonas de riesgo sísmico en el territorio colombiano mediante técnicas de Aprendizaje No Supervisado.

## 🚀 Descripción General
El sistema descarga, limpia, enriquece y modela eventos sísmicos. Actualmente, el proyecto se centra en la identificación de **15 zonas de riesgo diferenciadas** utilizando el algoritmo **K-Means**, integrando variables de ubicación (Latitud, Longitud), Profundidad y Magnitud.

---

## 📂 Estructura del Proyecto

### 📊 Datos (`data/`)
- `earthquakes_raw.csv`: Datos originales descargados de la API de USGS.
- `earthquakes_cleaned.csv`: Datos tras el filtrado geográfico y eliminación de columnas técnicas con valores nulos.
- `earthquakes_enriched.csv`: Dataset con variables calculadas (municipios, proximidad a fallas, ratios de impacto).
- `earthquakes_kmeans.csv`: Resultados del clustering (asignación de zona y nivel de riesgo).
- `world.geojson`: Mapa base para visualizaciones geográficas.

### 📜 Scripts (`scripts/`)
- `load_data.py`: Descarga y carga inicial de datos.
- `data_cleaning.py`: Implementa el **Filtrado Territorial (Solo Colombia)** y limpieza de nulos.
- `enrich_dataset.py`: Georreferenciación oficial, cálculo de ratios y estandarización.
- `visualize_scaling.py`: Comparativa visual del impacto del escalado (Escala 0-200).
- `modeling_kmeans.py`: Experimentación con K (Método del Codo y Silhouette).
- `visualize_k_evolution.py`: Visualización evolutiva de clusters con mapa y fallas.
- `apply_k7_model.py`: Aplicación del modelo final seleccionado (K=7).
- `cluster_profiling.py`: Genera estadísticas y mapas de la Fase 5.
- `generate_html_report.py`: Genera el reporte interactivo premium en HTML.

### 📝 Documentación (`documentacion/`)
- `reporte_final/`: Contiene el `REPORTE_CRISP_DM.md` consolidado.
- `visualizaciones/`: Gráficos de análisis, mapas de calor y boxplots.
- `mapa_kmeans.html`: Dashboard interactivo de los clusters resultantes.

---

## 🛠️ Metodología CRISP-DM

1.  **Comprensión del Negocio**: Identificación de stakeholders y definición de hipótesis sobre las firmas sísmicas en Colombia.
2.  **Comprensión de los Datos**: Análisis exploratorio (EDA), nulos y correlaciones.
3.  **Preparación de los Datos**: 
    - Filtrado geográfico estricto (Reducción del ~50% del dataset original para eliminar ruido externo).
    - Escalado de características (`StandardScaler`) para evitar dominancia de la profundidad sobre la latitud.
4.  **Modelado**: Experimentación con K (2..10) y selección de K=7 basado en métricas y sentido geológico.
5.  **Evaluación**: Identificación de las 7 zonas sísmicas y perfilado de riesgo (Nariño, Santander, Chocó, etc).
6.  **Despliegue**: Reporte interactivo premium y Dashboard de clusters.

---

## 🏃 Cómo ejecutar

### 1. Requisitos previos
Se recomienda el uso de un entorno virtual:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install pandas numpy matplotlib seaborn plotly geopandas scikit-learn
```

### 2. Flujo de ejecución
Sigue este orden para procesar los datos desde cero:
1.  **Limpieza y Filtrado**: `python scripts/data_cleaning.py`
2.  **Enriquecimiento**: `python scripts/enrich_dataset.py`
3.  **Visualización de Impacto**: `python scripts/visualize_cleaning.py`
4.  **Modelado**: `python scripts/kmeans_analysis.py`

### 3. Visualizar el Reporte
El reporte principal se encuentra en `reporte_final/REPORTE_CRISP_DM.md`. Para una experiencia interactiva, abre `documentacion/mapa_kmeans.html` en tu navegador.

---
*Última actualización: Febrero 2026 - Enfoque en Optimización de Riesgo Territorial.*
