# Análisis de Zonas Sísmicas Más Propensas (DBSCAN)

## Metodología
Se aplicó el algoritmo **DBSCAN** (Density-Based Spatial Clustering) con los siguientes parámetros:
- **Radio:** 50 km (métrica haversine sobre coordenadas esféricas)
- **Mínimo de sismos:** 15 eventos para formar un hotspot
- **Resultado:** 21 hotspots detectados, 409 eventos aislados.

## Dataset Enriquecido
El análisis generó el archivo `data/earthquakes_classified.csv`, que incluye las siguientes columnas nuevas:

| Columna | Descripción |
| :--- | :--- |
| **cluster** | ID numérico del hotspot (-1 = evento aislado) |
| **nivel_riesgo** | Clasificación por densidad: Muy alto, Alto, Moderado, Bajo o Segura |
| **es_zona_segura** | Etiqueta binaria: `Peligrosa` o `Segura` |

## Escala de Clasificación
| Umbral de Sismos | Nivel de Riesgo |
| :--- | :--- |
| ≥ 500 | 🔴 Muy alto riesgo |
| ≥ 200 | 🟠 Alto riesgo |
| ≥ 80 | 🟡 Riesgo moderado |
| ≥ 15 | 🟢 Riesgo bajo |
| < 15 o aislado | 🔵 Zona relativamente segura |

## Top Zonas Más Peligrosas

| Zona | Lugar de Referencia | Sismos | Mag. Promedio | Mag. Máxima | Nivel |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Zona 1** | Costa de Ecuador (frontera) | 986 | 4.52 | **7.8** | 🔴 Muy alto riesgo |
| **Zona 2** | Norte de Colombia | 682 | 4.36 | 6.2 | 🔴 Muy alto riesgo |
| **Zona 3** | Colombia (interior centro-sur) | 99 | 4.57 | 6.1 | 🟡 Riesgo moderado |
| **Zona 5** | Costa pacífica de Colombia | 80 | 4.65 | 6.7 | 🟡 Riesgo moderado |
| **Zona 7** | Murindó, Colombia | 74 | 4.55 | 6.0 | 🟢 Riesgo bajo |

## Interpretación Geológica

### Zona 1 — Costa de Ecuador / Pacífico Sur (986 sismos, Mag. máx. 7.8)
Es la zona con **mayor frecuencia e intensidad** registrada. Corresponde a la zona de subducción de la **Placa de Nazca** bajo la Placa Sudamericana. Esta interacción genera constantemente sismos de alta energía y es la fuente del mayor evento registrado en el dataset.

### Zona 2 — Norte de Colombia (682 sismos, Mag. máx. 6.2)
Alta densidad que engloba el famoso **Nido Sísmico de Bucaramanga**, considerado una de las concentraciones sísmica más densas del mundo. Esta zona es de especial interés dada su cercanía a centros poblados.

### Zona 5 — Costa Pacífica de Colombia (80 sismos, Mag. máx. 6.7)
Actividad relacionada con la subducción del Pacífico. La magnitud máxima de 6.7 indica que aunque la frecuencia es menor, el potencial destructivo es significativo.

## Visualización
El mapa interactivo `documentacion/mapa_hotspots.html` permite:
- Ver cada sismo coloreado según su **Zona (Clúster)** específica para una identificación visual rápida.
- Acceder a los **datos técnicos completos** del sismo al pasar el cursor (Magnitud, Profundidad, Fecha/Hora, NST, RMS).
- Identificar el **Nivel de Riesgo** y la clasificación binaria (Segura/Peligrosa) por punto individual.
