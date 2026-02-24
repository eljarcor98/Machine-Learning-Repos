# Resumen de Carga y Exploración Inicial

**Fecha:** 2026-02-24

## Detalles de la Fuente de Datos
- **Fuente:** USGS Earthquake Hazards Program.
- **Rango de Fechas:** 2010-01-01 a 2026-02-20.
- **Límites Geográficos:**
  - Latitud: [-4.5, 13.5]
  - Longitud: [-82.0, -66.5]
- **Filtros Aplicados:** Magnitud mínima 1.5, Ordenado por tiempo, Límite de 20,000 registros.

## Resultados de la Carga
- **Registros obtenidos:** 2792.
- **Variables identificadas:** 22.
- **Archivo generado:** `data/earthquakes_raw.csv`.

## Análisis Estadístico Inicial
| Métrica | Magnitud (mag) | Profundidad (depth) |
| :--- | :--- | :--- |
| **Promedio** | 4.48 | 74.47 km |
| **Mínimo** | 2.30 | 0.00 km |
| **Máximo** | 7.80 | 239.40 km |
| **Desviación Estándar** | 0.44 | 63.25 km |

## Observaciones
- El dataset cubre principalmente la región de Colombia y áreas marítimas circundantes.
- Existen valores nulos en variables técnicas como `nst`, `gap`, `dmin`, `horizontalError`, `depthError` y `magError`. Las variables de ubicación, tiempo y magnitud están completas.
- La mayoría de los terremotos registrados tienen una profundidad menor a 150 km, aunque existen eventos de profundidad intermedia (>200 km).
