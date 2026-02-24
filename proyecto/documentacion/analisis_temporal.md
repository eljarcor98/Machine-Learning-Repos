# Análisis Temporal de Sismos

Este documento detalla la distribución en el tiempo de los eventos sísmicos registrados.

## Período de Cobertura
- **Inicio:** 2 de enero de 2010
- **Fin:** 15 de febrero de 2026
- **Duración total:** Aproximadamente 16 años (5,888 días).

## Distribución Anual (Consolidado)
Se observa una tendencia creciente en el número de registros anuales, posiblemente debido a la mejora en la red de sensores.

| Año | Registros |
| :--- | :--- |
| 2010-2013 | ~100 por año |
| 2014-2015 | ~200 por año |
| **2016** | **304 (Pico de actividad)** |
| 2017-2025 | Estabilidad entre 170 y 200 por año |
| 2026 | 18 (Corte parcial a febrero) |

## Distribución por Mes
La actividad parece estar distribuida de manera relativamente uniforme a lo largo del año, con ligeros incrementos en los meses de **Abril (288)** y **Noviembre (267)**.

## Distribución por Hora (UTC)
El análisis horario muestra que no hay una diferencia drástica que indique patrones naturales (como sismos solo de día o noche), lo cual es consistente con la naturaleza tectónica. Las horas con mayores registros son:
- 01:00, 04:00, 06:00, 07:00 y 09:00 UTC.

## Observaciones Técnicas
- La variable `time` fue convertida de formato string a objeto `datetime` de Python para facilitar el cálculo de periodos y frecuencias.
- El salto en el número de registros en 2016 podría indicar una mejora en la sensibilidad de la red de monitoreo de la USGS en la región o un año de mayor actividad sísmica real.
