# Proyecto Final Healtech

Proyecto orientado al analisis de amenazas en red usando `CIC-IDS2017`, grafos y modelos de propagacion tipo `SIR/SEIR`.

## Idea base

El proyecto busca representar una red como un grafo a partir de flujos etiquetados de `CIC-IDS2017` y simular como una amenaza puede propagarse entre nodos vulnerables, asi como evaluar estrategias de contencion.

## Dataset objetivo

- **Dataset principal**: `UNSW-NB15`
- **Fuente**: `mrwellsdavid/unsw-nb15` (vía Kaggle)
- **Tipo de datos**: Flujos de red etiquetados con 49 características, incluyendo direcciones IP (Source/Destination).
- **Ventaja**: A diferencia de otros datasets, este incluye IPs reales/anonimizadas que permiten la construcción de grafos de comunicación de red.

## Alcance metodológico

- **Modelado de Red**: El dataset se utiliza para construir un grafo donde los nodos son direcciones IP y las aristas representan flujos de comunicación.
- **Simulación**: Se implementarán modelos `SIR/SEIR` para simular la propagación de amenazas (ej. Botnets, Infiltración) sobre la topología del grafo.
- **Estrategias de Contención**: Evaluación de impacto de medidas preventivas sobre la red modelada.

## Estructura

```text
Proyecto final Healtech/
|-- data/
|   |-- external/
|   |-- processed/
|   `-- raw/
|-- docs/
|-- notebooks/
|-- reports/
|   `-- figures/
`-- src/
    |-- data/
    |-- graph/
    |-- models/
    |-- simulation/
    `-- visualization/
```

## Flujo sugerido

1. Descargar el dataset usando `kagglehub` en `data/raw/unsw-nb15/`.
2. Preparar una versión procesada o subsets para el análisis inicial.
3. Seleccionar ataques compatibles con dinamica de propagacion.
4. Construir el grafo de comunicaciones o interacciones en `src/graph/`.
5. Implementar la simulacion SIR/SEIR en `src/simulation/`.
6. Evaluar escenarios de contencion y visualizarlos en `reports/figures/`.
7. Documentar decisiones, supuestos y hallazgos en `docs/`.
