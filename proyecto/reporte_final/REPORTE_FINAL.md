# Reporte Final: Análisis de Riesgo Sísmico en Colombia e Inmediaciones
## Metodología CRISP-DM

Este reporte sigue el estándar CRISP-DM (Cross-Industry Standard Process for Data Mining) para estructurar el análisis de datos sísmicos obtenidos de la USGS.

---

## Fase 1: Business Understanding (Comprensión del Negocio)

**Pregunta de investigación:** ¿Es posible identificar automáticamente zonas sísmicas diferenciadas en Colombia utilizando únicamente las características instrumentales de los sismos?

### 1.1 Contexto Geológico de Colombia
Colombia se encuentra en una de las regiones más complejas del mundo desde el punto de vista tectónico. Su sismicidad está gobernada por la interacción de tres placas principales: **Nazca**, **Sudamericana** y **Cocos**, además de microplacas como la de **Panamá-Azuero**.

*   **Falla de Romeral:** Uno de los sistemas más activos que atraviesa el país de norte a sur.
*   **Falla de Bucaramanga-Santa Marta:** Responsable del nido sísmico más activo del país.
*   **Falla Frontal de la Cordillera Oriental:** Define el límite entre los Andes y los Llanos Orientales.

### 1.2 Definición del Problema
El reto consiste en utilizar técnicas de **Aprendizaje No Supervisado (Clustering)** para agrupar miles de eventos sísmicos en regiones con "firmas sísmicas" similares. Esto permite pasar de ver puntos aislados en un mapa a identificar **provincias de riesgo**, facilitando la toma de decisiones en planeación urbana y respuesta ante desastres.

### 1.3 Stakeholders
*   **Servicio Geológico Colombiano (SGC):** Para el monitoreo y segmentación de alertas.
*   **UNGRD (Gestión del Riesgo):** Para priorizar recursos en zonas de alta frecuencia.
*   **Ingenieros Civiles:** Para el diseño de normativas sismorresistentes locales.

### 1.4 Hipótesis
Se estima que el algoritmo debería identificar al menos **entre 10 y 15 zonas diferenciadas**, capturando claramente el Nido sísmico de Bucaramanga, la subducción del Pacífico y las fallas corticales de los Andes.

---

## Fase 2: Data Understanding (Comprensión de los Datos)
Esta es la fase de **Análisis Exploratorio de Datos (EDA)**. Aquí conocemos profundamente el dataset antes de modelar.

### 2.1 Preguntas Guía y Hallazgos

*   **¿Cuántos registros tienes? ¿Cuántos corresponden a Colombia específicamente?**
    *   **Total de registros:** 2,792 eventos sísmicos (Periodo 2010-2026).
    *   **Registros en Colombia:** 1,412 eventos (**50.6%** del dataset), filtrados por ubicación geográfica (Lat: [-4.5, 13.5], Lon: [-82.0, -66.5]) y etiquetas de lugar.

*   **¿Cuáles variables tienen valores nulos? ¿En qué porcentaje?**
    *   Las variables críticas (`mag`, `latitude`, `longitude`, `time`) están al **100% completas** — sin ningún nulo.
    *   Las variables de error instrumental presentan altos porcentajes de nulos:

| Variable | Descripción | Nulos | % |
| :--- | :--- | :---: | :---: |
| `nst` | Número de estaciones usadas | 1,686 | 60.4% |
| `horizontalError` | Error horizontal de localización | 524 | 18.8% |
| `magError` | Error en la magnitud reportada | 458 | 16.4% |
| `dmin` | Distancia mínima a la estación | 392 | 14.0% |
| `magNst` | Número de estaciones de magnitud | 221 | 7.9% |
| `depthError` | Error en la profundidad | 109 | 3.9% |
| `gap` | Brecha azimutal entre estaciones | 54 | 1.9% |

![Porcentaje de Nulos por Variable](../documentacion/visualizaciones/porcentaje_nulos.png)

*   **¿Cómo se distribuyen las magnitudes? ¿Y las profundidades?**
    *   **Magnitudes:** Promedio de **4.47**, rango de 2.0 a 6.8. La mayoría se concentra entre 4.0 y 5.0.
    *   **Profundidades:** Promedio de **74.47 km**. Presenta una distribución **bimodal**: sismos superficiales (< 30 km) e intermedios (~150 km, típicos del Nido de Bucaramanga).

| Métrica | Magnitud (mag) | Profundidad (depth) |
| :--- | :---: | :---: |
| **Media** | 4.47 | 74.47 km |
| **Mínimo** | 2.00 | 0.00 km |
| **Máximo** | 6.80 | 661.10 km |

*   **¿Hay correlaciones interesantes entre variables?**
    *   La correlación entre **Magnitud y Profundidad** es casi nula (**-0.06**): sismos fuertes pueden ocurrir a cualquier profundidad.
    *   Hay una correlación moderada (**0.63**) entre Latitud y Longitud, reflejando la orientación NE-SW de las estructuras tectónicas colombianas.

### 2.2 Mapas de Dispersión Geográficos (Scatter Maps)
Para visualizar la distribución espacial bajo una perspectiva de alerta, se generaron mapas con silueta geográfica y paletas "alarmistas":

#### 2.2.1 Mapa de Riesgo por Profundidad
Tonos rojos intensos y puntos más grandes indican sismos a profundidades críticas (subducción profunda).

![Mapa de Riesgo por Profundidad](../documentacion/visualizaciones/scatter_map_depth_red.png)

#### 2.2.2 Mapa de Alerta por Magnitud
Concentración de puntos rojos sobre el Pacífico y el centro de Colombia indica las zonas de mayor peligrosidad.

![Mapa de Alerta por Magnitud](../documentacion/visualizaciones/scatter_map_mag_red.png)

#### 2.2.3 Relación Magnitud vs Profundidad
La independencia visual confirma la correlación de -0.06: cualquier zona puede experimentar un sismo de alta magnitud.

![Relación Magnitud vs Profundidad](../documentacion/visualizaciones/scatter_mag_depth_refined.png)

### 2.3 Análisis de Frecuencia por Región
La frecuencia de sismos por municipio revela los focos de actividad territorial:

![Frecuencia por Región](../documentacion/visualizaciones/frecuencia_municipios.png)

*   **Hallazgo Principal:** Los municipios de **Cepitá** y **Jordán** (Santander) lideran la actividad debido al **Nido Sísmico de Bucaramanga**, uno de los más densos del mundo.

---

## Fase 3: Data Preparation (Preparación de los Datos)
En esta fase se decide qué variables (features) usar y cómo transformarlas para que el modelo de clustering sea efectivo.

### 3.1 Selección de Features
*   **¿Qué variables describen la ubicación del sismo?**
    *   `latitude` y `longitude`: Coordenadas geográficas fundamentales para la agrupación espacial.
    *   `depth` (Profundidad): Describe la ubicación vertical en la corteza terrestre.
*   **¿Qué variables describen la naturaleza del sismo?**
    *   `mag` (Magnitud): Representa la energía liberada y la intensidad del evento.
*   **¿Hay variables con demasiados nulos que debas excluir?**
    *   **Sí.** Las variables de error instrumental (`nst`, `horizontalError`, `magError`) presentan hasta un **60% de nulos**. Se excluyen para mantener la integridad del dataset sin perder registros.

### 3.2 Manejo de Datos Faltantes
*   **Decisión:** Se seleccionan únicamente features sin nulos significativos y se eliminan las columnas técnicas de error.
*   **Justificación:** Conservamos el **100% de las filas (2,792 registros)**. No se requiere imputación ya que las variables clave (`mag`, `latitude`, `longitude`) estaban completas. Eliminar filas habría eliminado hasta el 60% del dataset.

### 3.3 Scaling — CRÍTICO
El escalado de datos es el paso más importante antes de aplicar K-Means.

#### Experimento: K-Means sin escalar vs. con StandardScaler

| Escenario | Resultado |
| :--- | :--- |
| **Sin Escalar** | Clusters agrupados por "capas horizontales" de profundidad. Geográficamente inútiles. |
| **Con StandardScaler** | Clusters geográficos coherentes que integran ubicación, profundidad y magnitud. |

#### Preguntas Obligatorias:
*   **¿Cambian los clusters al escalar? ¿Por qué?**
    *   **Sí, drásticamente.** K-Means utiliza distancias euclidianas. Sin escalar, las variables de mayor rango "opacan" a las de menor rango, forzando al algoritmo a ignorarlas por completo.

*   **¿Cuál es la escala de `latitude` vs `depth`? ¿Qué feature domina si no escalas?**
    *   `latitude`: varía en **~20 unidades** (de -5 a 15).
    *   `depth`: varía en **~660 unidades** (de 0 a 661 km).
    *   **Dominancia:** La **profundidad domina totalmente**. Un cambio de 1 grado en latitud (~111 km reales) es insignificante frente a 1 km en profundidad para el cálculo de distancias.

*   **¿Cuál versión produce clusters más interpretables para el SGC?**
    *   La versión con **StandardScaler**, ya que produce zonas geográficas reales (ej. "Cluster del Litoral Pacífico") que el Servicio Geológico Colombiano puede utilizar directamente para gestión del riesgo territorial.

### 3.4 Enriquecimiento de Datos (Feature Engineering)
Se añadieron variables derivadas para robustecer el modelo:

| Variable | Descripción | Lógica |
| :--- | :--- | :--- |
| `municipio_region` | Municipio/región del sismo | Extraído del campo `place` por limpieza de texto |
| `mag_depth_ratio` | Ratio de magnitud sobre profundidad | $mag / \log(1 + depth)$ — resalta sismos superficiales de alta energía |
| `sismos_por_zona` | Densidad histórica de eventos | Conteo en radio de ~50km — identifica "hotspots" |
| `proximidad_falla` | Cercanía a falla geológica | Fórmula de Haversine con umbral de 100km |

#### Vista Previa del Dataset Enriquecido:
| Lugar | Municipio | Mag/Depth Ratio | Sismos/Zona | Proximidad a Falla |
|:---|:---|:---:|:---:|:---|
| 3 km W of Jordán, Colombia | Jordán | 0.9632 | 25 | Falla Bucaramanga-Santa Marta |
| 5 km ENE of Cepitá, Colombia | Cepitá | 0.8262 | 27 | Falla Bucaramanga-Santa Marta |
| 42 km E of Mene Grande, Venezuela | Mene Grande | 1.7932 | 2 | Sin falla principal cercana |

---

## Fase 4: Modeling (Modelado)
Tras evaluar DBSCAN, se determinó que **K-Means Clustering** es más efectivo para una partición geográfica equilibrada y clasificación gradual.

*   **Algoritmo:** K-Means con `StandardScaler`.
*   **Parámetros:** $k=15$ clusters basados en coordenadas geográficas.
*   **Resultado:** 15 zonas de riesgo con clasificación gradual desde "Muy alto riesgo" hasta "Riesgo bajo".

---

## Fase 5: Evaluation (Evaluación)
Evaluación de la coherencia espacial y perfilado de cada cluster.

### 5.1 Preguntas de Evaluación
1.  **Sismicidad Profunda:** ¿Hay algún cluster concentrado en sismos profundos? (Ej. zona de subducción interior).
2.  **Zona de Subducción:** ¿Los clusters capturan adecuadamente la línea de subducción del Pacífico?
3.  **Magnitud Máxima:** ¿Cuál cluster concentra los sismos de mayor intensidad histórica?
4.  **Priorización de Alertas:** ¿Qué cluster debe priorizarse para sistemas de alerta temprana?

---

## Fase 6: Deployment (Despliegue / Comunicación de Resultados)
Visualización de resultados mediante narrativa de datos y el **Reporte Interactivo Premium**.

*   **Narrativa:** De lo general (mapa panorámico) a lo particular (clusters de mayor riesgo).
*   **Impacto Social:** Traducir clusters en acciones de prevención territorial.

---
*Este documento se actualizará conforme avancemos en las fases de Evaluación y Conclusiones.*
