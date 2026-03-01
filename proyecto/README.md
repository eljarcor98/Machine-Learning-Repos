# Proyecto de Análisis de Riesgo Sísmico (Colombia - USGS)

Este proyecto implementa un flujo de trabajo basado en la metodología **CRISP-DM** para analizar datos sísmicos obtenidos de la United States Geological Survey (USGS). El sistema identifica zonas de riesgo sismotectónico mediante clustering dinámico, proporcionando una interfaz intuitiva para ciudadanos y expertos.

## 🚀 Descripción General
El sistema permite explorar la sismicidad en Colombia mediante un **Dashboard Interactivo Pro (v3.4)**. A diferencia de modelos estáticos, este sistema permite:
- **Clustering Dinámico**: Variar el número de zonas (K) de 2 a 10 en tiempo real.
- **Justificación de Agrupación (v3.6+)**: Perfiles dicientes que explican *por qué* un sismo pertenece a un grupo (ej. superficial, intermedio, profundo).
- **Panel Lateral Unificado (v3.7+)**: Toda la información de zonas, municipios y detalles de sismos se concentra en un solo lugar permanente.
- **Botón de Reinicio Maestro (v3.10)**: Restauración instantánea de todos los filtros, zoom y segmentación K.
- **Narrativa Sismológica (v3.11)**: Sección "La Historia de nuestra Tierra" que explica la interacción de las placas de Nazca y Suramérica.
- **Referencias Oficiales**: Citas integradas al Servicio Geológico Colombiano (SGC) y al USGS.
- **Layout Optimizada**: Interfaz adaptable que evita solapamientos y maximiza la legibilidad del texto de impacto.
- **Perfiles Ciudadanos**: Clasificación automática de clusters en lenguaje sencillo (Riesgo Alto/Medio/Bajo e impacto esperado).
- **Control Temporal**: Rango de años seleccionable (Desde/Hasta) para observar la evolución sísmica.
- **Contexto Geológico**: Visualización de fallas geológicas oficiales (Atlas 2020) sobre un mapa minimalista.

---

## 📂 Estructura del Proyecto

### 📊 Datos (`data/`)
- `earthquakes_raw.csv`: Datos originales descargados de la API de USGS.
- `earthquakes_enriched.csv`: Dataset enriquecido con georreferenciación (municipios) y métricas sismológicas.
- `Atlas_Geológico...geojson`: Capa oficial de fallas geológicas de Colombia.

### 📜 Scripts Principales (`scripts/`)
- `enrich_dataset.py`: Limpieza profunda y georreferenciación de sismos.
- `create_interactive_dashboard.py`: **Motor principal.** Genera el dashboard dinámico con perfiles de riesgo y timeline doble.

### 📝 Documentación y Salidas (`documentacion/`)
- `visualizaciones/dashboard_interactivo.html`: El explorador interactivo final.
- `reporte_final/REPORTE_CRISP_DM.md`: Documentación técnica detallada de todas las fases.

---

## 🏃 Cómo ejecutar

### 1. Requisitos previos
Recomendado usar el entorno virtual configurado:
```powershell
pip install pandas numpy geopandas scikit-learn
```

### 2. Generación del Dashboard
Para actualizar la visualización con los últimos datos descargados:
```powershell
python scripts/enrich_dataset.py
python scripts/create_interactive_dashboard.py
```

---
*Última actualización: 28 de Febrero, 2026 - Dashboard de Perfilado Ciudadano e Impacto Estructural.*

