# Reporte Ejecutivo: Clustering de Actividad Sísmica en Colombia

## Resumen
Este reporte presenta los resultados de una investigación avanzada sobre la sismicidad en Colombia (2010-2026), utilizando técnicas de **Machine Learning (Clustering K-Means)** para segmentar el territorio en provincias sismotectónicas. El objetivo principal fue identificar patrones ocultos entre la magnitud, profundidad y ubicación geográfica de los sismos registrados por la USGS.

A través de un análisis dinámico, se logró clasificar la actividad sísmica en **7 clusters óptimos** que reflejan fielmente la dinámica de subducción de la placa de Nazca y las fallas corticales activas. El hallazgo principal revela una clara diferenciación entre los **sismos de gran profundidad (nidos sísmicos)** en Santander y los **eventos superficiales de alta peligrosidad** en el eje andino, permitiendo una visualización intuitiva para la gestión del riesgo ciudadano.

## Metodología (CRISP-DM resumido)
El proyecto se ejecutó bajo el estándar industrial CRISP-DM:
1.  **Comprensión del Negocio**: Definición del riesgo sísmico y necesidad de alertas no técnicas.
2.  **Comprensión de los Datos**: Auditoría de sismos históricos de la USGS y el Atlas de Fallas del SGC.
3.  **Preparación de Datos**: Georreferenciación de 1,412 registros para asignar municipios y departamentos. Aplicación de **StandardScaler** para nivelar la influencia de la profundidad frente a la magnitud.
4.  **Modelado**: Implementación de **K-Means (random_state=42)** con un rango dinámico de K=2 a 10 para evaluar la evolución de las zonas.
5.  **Evaluación**: Validación mediante el **Método del Codo (Elbow)** y el **Coeficiente de Silhouette**, confirmando K=7 como el punto de mayor cohesión.
6.  **Despliegue**: Creación de un Dashboard Interactivo Dinámico (v3.13) con narrativa educativa.

## Resultados
### Perfil de Clusters y Hallazgos Clave
Se identificaron tres grandes tipologías de zonas sísmicas:
*   **Zonas de Foco Profundo (Nidos)**: Principalmente en la Mesa de los Santos (Santander). Estos clusters (Verdes) agrupan sismos a >150km de profundidad, con alta frecuencia pero bajo impacto estructural directo.
*   **Zonas de Falla Cortical (Peligro Alto)**: Sismos superficiales (<30km) en el eje andino y Cauca. Estos clusters (Rojos) representan el mayor riesgo para la infraestructura civil debido a su cercanía a centros poblados.
*   **Zonas de Subducción Pacífica**: Eventos intermedios originados por la placa de Nazca, con magnitudes significativas que generan impacto regional en el sur y occidente del país.

![Evolución de Clusters](file:///C:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/proyecto/documentacion/visualizaciones/evolucion_clusters_k2_k10.png)

## Impacto del Scaling
Uno de los aprendizajes técnicos más críticos fue la influencia de la escala de las variables. 
*   **Sin Scaling**: El algoritmo priorizaba la **profundidad** (valores de 0 a >200km) sobre la **magnitud** (valores de 2 a 7), creando grupos basados casi exclusivamente en la profundidad.
*   **Con Scaling (StandardScaler)**: Al normalizar ambas variables a una escala estándar, el modelo empezó a identificar "regiones de riesgo" donde sismos de distinta profundidad pero similar localización y magnitud se agrupan coherentemente. 

![Comparativa de Escalas](file:///C:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/proyecto/documentacion/visualizaciones/comparativa_estandarizacion.png)

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
*   **SGC (2020)**: Atlas Geológico de Colombia - Fallas Cuaternarias.
*   **UNGRD (2021)**: Boletín "El Sismo es Real" - Guía de prevención.
*   **Metodología**: Pedregosa et al., Scikit-learn: Machine Learning in Python.
