# Reporte Final: Análisis de Riesgo Sísmico en Colombia e Inmediaciones
## Metodología CRISP-DM

Este reporte sigue el estándar CRISP-DM (Cross-Industry Standard Process for Data Mining) para estructurar el análisis de datos sísmicos obtenidos de la USGS.

---

## 1. Business Understanding (Comprensión del Negocio/Problema)
**Objetivo:** Identificar y categorizar las zonas geográficas con mayor propensión a eventos sísmicos en la región de Colombia y áreas circundantes, con el fin de proporcionar información accionable para la gestión del riesgo.

**Preguntas Clave:**
- ¿Cuáles son los puntos calientes (hotspots) de actividad sísmica?
- ¿Qué zonas pueden clasificarse como "seguras" vs "peligrosas" basado en un radio de acción de 50-100 km?
- ¿Existe una evolución temporal significativa en la frecuencia de los sismos?

---

## 2. Data Understanding (Comprensión de los Datos)
**Fuente:** API de la USGS (United States Geological Survey).
**Rango Temporal:** 2010-01-01 a 2026-02-20.
**Volumen:** 2,792 registros iniciales.

### Variables Principales:
- `mag`: Magnitud del sismo (Escala de Richter).
- `depth`: Profundidad (km).
- `latitude` / `longitude`: Coordenadas geográficas.
- `time`: Marca de tiempo UTC.

**Hallazgos Iniciales:**
- La magnitud promedio es de **4.48**.
- El evento máximo registrado fue de **7.8** en la costa de Ecuador.
- Existe una concentración masiva en el **Nido Sísmico de Bucaramanga**.

---

## 3. Data Preparation (Preparación de los Datos)
**Acciones Realizadas:**
- Conversión de formatos de tiempo a objetos `datetime`.
- Filtrado geográfico para Colombia y regiones limítrofes.
- Creación de variables derivadas para la clasificación de riesgo.
- **Clustering Espacial:** Implementación de DBSCAN para agrupar sismos por densidad geográfica (Radio=50km).

---

## 4. Modeling (Modelado)
Tras evaluar DBSCAN, se determinó que **K-Means Clustering** es más efectivo para realizar una partición geográfica equilibrada y clasificar las zonas de forma gradual.
- **Algoritmo:** K-Means.
- **Parámetros:** 15 clusters ($k=15$) basados en coordenadas geográficas.
- **Resultado:** Identificación de 15 zonas de riesgo con una distribución gradual desde "Muy alto riesgo" hasta "Riesgo bajo".

### Clasificación de Riesgo:
Se definieron umbrales basados en la frecuencia sísmica por zona para categorizar la peligrosidad.

### Clasificación de Riesgo:
Se creó una columna `es_zona_segura` basada en la densidad de eventos:
- **Peligrosa:** Zonas con >15 sismos en el radio definido.
- **Segura:** Eventos aislados o zonas con baja frecuencia histórica.

---

## 5. Evaluation (Evaluación)
*En desarrollo...* 
(Aquí se incluirán las métricas de precisión del clustering y la validación de las zonas detectadas con registros históricos conocidos).

---

## 6. Deployment (Despliegue/Comunicación)
Se han generado visualizaciones interactivas para facilitar la interpretación de los resultados:
- **[Mapa de Sismos Históricos](../documentacion/mapa_sismos.html)**
- **[Mapa de Riesgo (K-Means)](../documentacion/mapa_kmeans.html)**: Visualización de las 15 zonas identificadas con gradiente de riesgo por color y centroides geográficos.

---
*Este documento se actualizará conforme avancemos en las fases de Evaluación y Conclusiones.*
