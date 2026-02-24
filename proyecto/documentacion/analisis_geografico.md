# Análisis Geográfico de Sismos

Este documento describe la distribución espacial de los sismos en la región de Colombia y alrededores.

## Visualización Interactiva
Se ha generado un mapa dinámico que permite visualizar la evolución de los sismos mes a mes.

- **Archivo:** `documentacion/mapa_sismos.html` (Abrir en cualquier navegador).
- **Funcionalidades:** 
    - Botón de **Reproducir** para ver la evolución cronológica.
    - El tamaño de los puntos representa la **Magnitud**.
    - El color representa la intensidad (Escala de Rojos).
    - Información detallada al pasar el cursor sobre cada epicentro.

## Hallazgos Geográficos
1. **Nido Sísmico de Bucaramanga:** Se observa una concentración masiva y constante de puntos en la región de Santander. Esta es una de las zonas con mayor actividad sísmica del mundo.
2. **Cinturón del Pacífico:** Alta densidad de eventos a lo largo de la costa pacífica, relacionada con la subducción de la placa de Nazca bajo la placa Sudamericana.
3. **Zonas Marítimas:** Importante cantidad de registros en el Océano Pacífico (cerca de la frontera con Panamá y Ecuador) y en el Mar Caribe.
4. **Profundidad vs Ubicación:** Los sismos en la región andina tienden a ser de mayor profundidad, mientras que los eventos costeros suelen ser más superficiales.

## Notas Técnicas
- El mapa utiliza la proyección `carto-positron`.
- Se centró la vista en las coordenadas 4.57°N, -74.30°W (Centro Geográfico de Colombia).
- El rango de tiempo animado es de Enero 2010 a Febrero 2026.
