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

## Avances Recientes (Simulación WannaCry)

Se ha implementado una simulación interactiva de la propagación del ransomware **WannaCry** (2017) utilizando un modelo epidemiológico **SIR** sobre una red libre de escala (Barabási-Albert) en el notebook `05_sir_simulations_wannacry.ipynb`.

### Características de la Simulación:
- **Modelo SIR**: Nodos Susceptibles (vulnerables), Infectados (cifrados) y Recuperados (aislados/parcheados).
- **Escenario 1 (Sin contención)**: Alta tasa de transmisión (beta = 0.90) y baja recuperación, resultando en una red comprometida muy rápidamente.
- **Escenario 2 (Kill-Switch)**: Simulación de la medida de contención (descubierta por Marcus Hutchins), donde la transmisión cae drásticamente y aumenta la tasa de parcheo en un punto específico.
- **Visualización Interactiva**: Gráficos animados lado a lado utilizando `ipywidgets` y `matplotlib`.
  - **Red Dinámica**: Representación visual de los nodos y su estado de infección cambiando en el tiempo con un control de `Play`.
  - **Curva Epidémica**: Gráfico de líneas que muestra la evolución S-I-R, identificando automáticamente el **pico de infección** (el punto más crítico) y el progreso temporal mapeado a "horas simuladas" para dar contexto de un ataque real.

## Análisis PCAP de WannaCry

Se agregó soporte para procesar un fragmento local de tráfico de WannaCry ubicado en `data/external/wannaCry_15052017.pcap.gz`. El flujo reproducible es:

```powershell
.\.venv\Scripts\python.exe src\data\parse_wannacry_pcap.py
.\.venv\Scripts\python.exe src\wannacry_pcap_analysis.py
.\.venv\Scripts\python.exe src\wannacry_pcap_sir_simulation.py
.\.venv\Scripts\python.exe src\data\parse_hybrid_analysis_hosts.py
.\.venv\Scripts\python.exe src\graph\build_wannacry_geo_graph.py
```

Este proceso genera flujos agregados, resumen del PCAP, grafo observado, distribución de puertos, una simulación SIR informada por la intensidad del tráfico SMB/445 observado y un grafo geográfico basado en la tabla `Contacted Hosts` de Hybrid Analysis.

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
