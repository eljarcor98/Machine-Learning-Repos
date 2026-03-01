# Reporte Ejecutivo: Clustering de Actividad Sísmica en Colombia

## Resumen
Este reporte presenta los resultados de una investigación avanzada sobre la sismicidad en Colombia (2010-2026), utilizando técnicas de **Machine Learning (Clustering K-Means)** para segmentar el territorio en provincias sismotectónicas. El objetivo principal fue identificar patrones ocultos entre la magnitud, profundidad y ubicación geográfica de los sismos registrados por la USGS.

A través de un análisis dinámico, se logró clasificar la actividad sísmica en **7 clusters óptimos** que reflejan fielmente la dinámica de subducción de la placa de Nazca y las fallas corticales activas. El hallazgo principal revela una clara diferenciación entre los **sismos de gran profundidad (nidos sísmicos)** en Santander y los **eventos superficiales de alta peligrosidad** en el eje andino, permitiendo una visualización intuitiva para la gestión del riesgo ciudadano.

## Metodología (CRISP-DM resumido)
El proyecto se ejecutó bajo el estándar industrial CRISP-DM:
1.  **Comprensión del Negocio**: Definición del riesgo sísmico y necesidad de alertas no técnicas.
2.  **Comprensión de los Datos**: Auditoría de sismos históricos de la USGS y el Atlas de Fallas del SGC.
3.  **Preparación de Datos**: Georreferenciación de 1,412 registros. Esta fase fue crítica para la precisión del modelo, donde se realizaron las siguientes acciones:
    *   **Integración de Fallas Geológicas (SGC)**: Se incorporó la base de datos del **Atlas Geológico de Colombia 2020 (AGC)**, específicamente la capa de Fallas Geológicas del Servicio Geológico Colombiano. Este recurso permitió validar que los clusters identificados coinciden con estructuras tectónicas reales, como los sistemas de fallas de Romeral y del Piedemonte Llanero. La actualización del AGC (3ra edición) incluyó mapas a escala 1:100,000 y datos científicos indexados hasta 2019, ajustados mediante imágenes de relieve sombreado.
    *   **Completado de Tablas de Referencia**: Se completaron manualmente tablas de municipios y departamentos para asegurar que cada sismo tuviera un contexto administrativo claro. Este proceso de "curaduría de datos" permitió una mejor comprensión del problema al vincular la geología técnica con la realidad demográfica de Colombia.
    *   **Normalización**: Aplicación de **StandardScaler** para equilibrar las escalas de magnitud y profundidad.

### Limpieza Geográfica (Antes vs Después)
Se eliminaron registros fuera del territorio nacional o en zonas oceánicas no pertinentes, reduciendo el ruido espacial para el clustering.

![Limpieza Geográfica](./assets/comparativa_limpieza_geografica.png)
*Figura 1: Filtrado de sismos para asegurar la exclusividad del territorio colombiano.*

4.  **Modelado**: Implementación de **K-Means (random_state=42)**.
5.  **Evaluación**: Confirmación de K=7 mediante métricas de rendimiento.

![Análisis de Codo y Silueta](./assets/elbow_silhouette_analysis.png)
*Figura 2: Validación estadística para la selección del número óptimo de clústeres.*

Para garantizar la rigidez científica del modelo, se utilizaron dos métricas complementarias:
*   **Método del Codo (Elbow Method)**: Esta gráfica mide la **Inercia** (suma de los cuadrados de las distancias internas de los clusters). A medida que aumentamos K, la inercia disminuye. El "punto de codo" es aquel donde la ganancia de información deja de ser significativa por cada cluster adicional. Para la sismicidad en Colombia, el codo se identifica claramente en **K=7**, logrando un equilibrio entre precisión y simplicidad.
*   **Coeficiente de Silueta (Silhouette Score)**: Mide qué tan similar es un punto a su propio grupo en comparación con otros grupos. Un valor cercano a 1 indica que los clusters están bien separados y definidos. Al analizar K=7, observamos una consistencia espacial y de atributos que valida la robustez de las provincias sismotectónicas identificadas.

## Resultados
### Tabla Resumen de Provincias Sismotectónicas (K=7)

| Cluster | Tipo de Foco | Riesgo Estructural | Ubicación Principal | Impacto Típico |
| :--- | :--- | :--- | :--- | :--- |
| **Rojo** | Superficial (<30km) | **Muy Alto** | Eje Andino / Cauca | Daños en mampostería, sacudida brusca. |
| **Amarillo** | Intermedio (70-120km) | **Moderado** | Valle del Magdalena | Balanceo prolongado, bajo daño estructural. |
| **Verde** | Profundo (>150km) | **Bajo** | Mesa de los Santos | Alta frecuencia, vibración casi imperceptible. |

### Relación Magnitud vs Profundidad (Distribución Espacial)
El mapa de dispersión permite visualizar la concentración de eventos en el territorio nacional, destacando la silueta de las placas y fallas principales.

![Mapa de Dispersión con Silueta](./assets/scatter_map_depth_red.png)
*Figura 3: Distribución espacial de sismos con la silueta de Colombia.*

![Mapa de Evolución con Silueta](./assets/evolucion_clusters_geo.png)
*Figura 4: Evolución geográfica de la segmentación desde 2 hasta 10 zonas.*

## Impacto del Scaling
La estandarización fue el paso técnico más importante para evitar que la profundidad dominara el modelo.

| Variable | Sin Scaling (Rango) | Con Scaling (Z-Score) |
| :--- | :--- | :--- |
| **Profundidad** | 0 a 250 km | -1.5 a 3.2 |
| **Magnitud** | 2.5 a 7.2 ML | -2.1 a 3.5 |

![Efecto de la Estandarización](./assets/comparativa_estandarizacion.png)
*Figura 5: Distribución balanceada de variables tras el escalado.*

## Recomendaciones para el Servicio Geológico Colombiano (SGC)
1.  **Priorización de Monitoreo**: Se recomienda focalizar la densificación de estaciones acelerográficas en los clusters identificados como "Superficiales de Alto Riesgo" en los departamentos de Meta, Huila y Cauca, donde la energía se libera con mayor violencia.
2.  **Educación Diferenciada**: Utilizar la narrativa de "Nidos Símicos" para Santander para evitar el pánico ante sismos frecuentes pero profundos, mientras se refuerza el entrenamiento en sismo-resistencia en zonas de fallas corticales andinas.
3.  **Integración de Datos de Suelo**: Incorporar la microzonificación sísmica en los metadatos de los clusters para predecir efectos de amplificación local.

## Conclusiones
El uso de K-Means permitió transformar datos latentes en una narrativa geográfica inteligible. 
*   **¿Qué PUEDE hacer?**: Identificar regiones tectónicas estables y descubrir patrones de recurrencia espacial.
*   **¿Qué NO puede hacer?**: Predecir el *cuándo* de un sismo. Los clusters muestran "dónde y cómo" ocurre el riesgo, pero la predicción temporal sigue siendo una frontera tecnológica fuera del alcance de los algoritmos de clustering actuales.

## Referencias
*   **USGS Earthquakes Catalog**: Datos base de sismicidad histórica.
*   **Servicio Geológico Colombiano (SGC, 2020)**: [Atlas Geológico de Colombia 2020: Fallas Geológicas](https://datos.sgc.gov.co/datasets/e03339c845d24e7baceb6d67397a23b3_0/explore?location=5.539788%2C-74.391657%2C5). Esta edición actualiza la tectónica nacional con mapas a escala 1:100,000 y relieve sombreado.
*   **UNGRD (2021)**: Boletín "El Sismo es Real" - Guía de prevención.
*   **Metodología**: Pedregosa et al., Scikit-learn: Machine Learning in Python.
