# Registro de Cambios y Avances del Proyecto (Changelog)

Este documento contiene un registro cronológico y detallado de todas las actividades, modificaciones y hallazgos realizados durante el desarrollo del proyecto de análisis sísmico.

## [2026-02-24] - Sesión de Inicialización y Análisis Exploratorio

### 1. Configuración del Entorno y Estructura
- **Creación del Proyecto:** Se inicializó el directorio raíz `proyecto/`.
- **Entorno Virtual:** Se configuró `.venv` y se instalaron las dependencias base (`pandas`, `plotly`, `nbformat`).
- **Estructura de Carpetas:**
    - `data/`: Almacenamiento de datasets.
    - `scripts/`: Almacenamiento de lógica ejecutable.
    - `documentacion/`: Reportes y diccionarios en Markdown.

### 2. Adquisición de Datos
- **Automatización:** Se creó `scripts/load_data.py` para consultar la API de USGS.
- **Filtros de Consulta:**
    - Área: Colombia y alrededores (Lat: -4.5 a 13.5, Lon: -82 a -66.5).
    - Tiempo: 2010-01-01 a 2026-02-20.
    - Magnitud Mínima: 1.5.
- **Resultado:** Descarga exitosa de **2,792 registros** en `data/earthquakes_raw.csv`.

### 3. Análisis Exploratorio (EDA)
- **Variables:** Se identificaron 22 columnas técnicas. Se documentaron en `documentacion/diccionario_datos.md`.
- **Estadísticas Técnicas:**
    - Magnitud promedio: 4.48 (Máxima: 7.8).
    - Profundidad promedio: 74.47 km.
- **Análisis Temporal:** 
    - Se identificó un pico de actividad en el año 2016 (304 sismos).
    - Meses con más registros: Abril y Noviembre.
    - Se creó `documentacion/analisis_temporal.md`.

### 4. Visualización Avanzada
- **Mapa Interactivo:** Se desarrolló `scripts/create_map.py` utilizando Plotly.
- **Línea de Tiempo:** El mapa incluye una animación mensual que permite ver la evolución histórica de los sismos.
- **Producto:** `documentacion/mapa_sismos.html`.
- **Hallazgos:** Confirmación visual de la alta densidad en el Nido Sísmico de Bucaramanga y la costa pacífica.

### 5. Documentación
- Se creó `documentacion/analisis_geografico.md` detallando las zonas de mayor riesgo detectadas visualmente.
- Se actualizó el `README.md` principal para reflejar el estado actual del proyecto.

### 6. Análisis de Hotspots con DBSCAN
- **Librería instalada:** `scikit-learn` (incluye `scipy`, `joblib`, `threadpoolctl`).
- **Script creado:** `scripts/hotspot_analysis.py`.
- **Algoritmo:** DBSCAN con métrica haversine. Radio: **50 km**, Mínimo: **15 sismos**.
- **Resultados:** 21 hotspots detectados, 409 eventos aislados.
  - 🔴 **Zona 1 (986 sismos):** Costa de Ecuador — subducción de Placa de Nazca.
  - 🔴 **Zona 2 (682 sismos):** Norte de Colombia — Nido Sísmico de Bucaramanga.
- **Dataset enriquecido:** `data/earthquakes_classified.csv` con columnas:
  - `cluster`, `nivel_riesgo`, `es_zona_segura`.
- **Visualización:** `documentacion/mapa_hotspots.html`.
- **Documentación:** `documentacion/analisis_zonas_criticas.md`.

### 7. Reporte Final (Metodología CRISP-DM)
- **Carpeta creada:** `reporte_final/`.
- **Documento inicial:** `REPORTE_CRISP_DM.md`.
- **Mejora de Visualización:** El mapa de hotspots ahora cuenta con coloreado por cluster individual y tooltips técnicos detallados.
- **Estado:** Fases de Planning, Adquisición, Exploración y Modelado (Clustering) completadas e integradas bajo el estándar CRISP-DM.

### 8. Transición a K-Means Clustering
- **Justificación:** Se decidió cambiar de DBSCAN a K-Means para lograr una partición geográfica más equilibrada y una clasificación de riesgo gradual.
- **Implementación:** `scripts/kmeans_analysis.py`.
- **Configuración:** $k=15$ clusters geográficos.
- **Resultado:** 15 zonas identificadas con niveles de riesgo que van desde "Muy alto" (Nido de Bucaramanga) hasta "Bajo".
- **Nuevos Entregables:**
  - `data/earthquakes_kmeans.csv`: Dataset con etiquetas K-Means.
  - `documentacion/mapa_kmeans.html`: Nuevo mapa de calor por zonas.
  - `documentacion/analisis_kmeans.md`: Explicación técnica del modelo.
- **Actualización de Reporte:** El reporte final CRISP-DM ha sido actualizado para priorizar K-Means como modelo de clasificación principal.

---
*Este registro se actualizará conforme se realicen nuevos avances en la limpieza, modelado o reportes finales.*
