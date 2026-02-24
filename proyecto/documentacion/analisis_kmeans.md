# Análisis de Zonas Sísmicas con K-Means

## Justificación del Cambio (DBSCAN a K-Means)
Aunque DBSCAN es excelente para encontrar nidos sísmicos densos (como Bucaramanga), tiende a agrupar zonas cercanas en un solo bloque gigante si no se ajustan los parámetros de forma minuciosa para cada región. 

Se optó por **K-Means Clustering** para:
1.  **Partición Espacial Equilibrada:** Dividir la geografía de Colombia y regiones limítrofes en 15 zonas de interés.
2.  **Identificación Gradual:** Permitir una clasificación de riesgo más granular basada en la distribución de puntos por cada centroide geográfico.

## Metodología
- **Algoritmo:** K-Means sobre Latitud/Longitud.
- **Número de Clusters ($k$):** 15.
- **Escalado:** Se aplicó `StandardScaler` para balancear las coordenadas.
- **Clasificación de Riesgo:** Basada en la frecuencia histórica de eventos dentro de cada cluster geográfico.

| Conteo de Sismos | Nivel de Riesgo | Color en Mapa |
| :--- | :--- | :--- |
| $\geq$ 400 | Muy alto riesgo | 🔴 Rojo |
| $\geq$ 150 | Alto riesgo | 🟠 Naranja |
| $\geq$ 50 | Riesgo moderado | 🟡 Amarillo |
| $\geq$ 20 | Riesgo bajo | 🟢 Verde |
| $<$ 20 | Zona segura | 🔵 Azul |

## Resultados de las Zonas (Top 5)

| ID Zona | Ubicación Representativa | Conteo | Nivel de Riesgo |
| :--- | :--- | :---: | :--- |
| **Zona 5** | Northern Colombia (Nido de Bucaramanga) | 768 | 🔴 Muy alto riesgo |
| **Zona 2** | Ecuador-Colombia border | 265 | 🟠 Alto riesgo |
| **Zona 7** | Peru-Ecuador border | 233 | 🟠 Alto riesgo |
| **Zona 12** | Near the coast of Ecuador | 223 | 🟠 Alto riesgo |
| **Zona 6** | Near the coast of Ecuador | 191 | 🟠 Alto riesgo |

## Visualización
El mapa interactivo **`documentacion/mapa_kmeans.html`** muestra los 15 centroides identificados y los sismos coloreados por su nivel de riesgo gradual. 

### Observaciones
- **K-Means** logra separar mejor las zonas de la costa pacífica y las fronteras que DBSCAN trataba como un solo conjunto.
- Se identifica un patrón claro de riesgo descendente desde el Nido de Bucaramanga y la frontera sur hacia el interior y norte del país.
