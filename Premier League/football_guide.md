# Guía de Fútbol para Análisis de Datos

Esta guía te ayudará a entender los conceptos básicos de la Premier League y las métricas que encontrarás en los datasets.

## Conceptos Básicos

- **Temporada (Season)**: En la Premier League, la temporada va de agosto a mayo. Se suele denotar como `24/25` o `2024-2025`.
- **Jornada (Matchweek)**: Hay 38 jornadas en una temporada completa. Cada equipo juega contra todos los demás dos veces (local y visitante).
- **Puntos**:
    - Victoria: 3 puntos.
    - Empate: 1 punto.
    - Derrota: 0 puntos.

## Glosario de Términos en Datasets

Cuando descargues datos (especialmente de Football-Data.co.uk), verás estas siglas:

| Sigla | Término | Descripción |
| :--- | :--- | :--- |
| **FTHG** | Full Time Home Goals | Goles del equipo local al final del partido. |
| **FTAG** | Full Time Away Goals | Goles del equipo visitante al final del partido. |
| **FTR** | Full Time Result | Resultado final (H=Local, A=Visitante, D=Empate). |
| **HS / AS** | Home/Away Shots | Remates totales realizados. |
| **HST / AST** | Home/Away Shots on Target | Remates que fueron a portería. |
| **HC / AC** | Home/Away Corners | Saques de esquina. |
| **HY / AY** | Home/Away Yellow Cards | Tarjetas amarillas. |
| **HR / AR** | Home/Away Red Cards | Tarjetas rojas. |

## Métricas Avanzadas (Para Machine Learning)

Si usas librerías como `soccerdata`, verás métricas modernas:

1. **xG (Expected Goals)**: Probabilidad de que un remate termine en gol basado en la posición, ángulo, etc. Es la métrica reina para predecir rendimiento futuro.
2. **xA (Expected Assists)**: Probabilidad de que un pase se convierta en una asistencia de gol.
3. **PPDA (Passes Allowed per Defensive Action)**: Mide la intensidad de la presión de un equipo. Un número bajo significa mucha presión.
4. **Possession**: Porcentaje de tiempo que un equipo tiene el balón.

## Consejos para el Análisis

- **Ventaja de Local (Home Advantage)**: Históricamente, los equipos locales ganan más seguido. Es un factor clave en cualquier modelo.
- **Forma del Equipo (Form)**: Los resultados de los últimos 5 partidos suelen ser un buen predictor del siguiente.
- **Diferencia de Goles**: A menudo es mejor indicador de la calidad real de un equipo que su posición en la tabla.

---
> [!NOTE]
> No necesitas saber jugar fútbol para analizarlo. Los datos cuentan la historia a través de la eficiencia y las probabilidades.
