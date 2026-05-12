# Análisis de Propagación de Malware a partir de modelos SEIR 🏥🛡️

Este proyecto es una plataforma que explora la intersección entre la ciberseguridad y la epidemiología matemática. Representamos las redes informáticas como poblaciones de pacientes y las amenazas digitales (como ransomwares y gusanos) como virus patógenos reales.

El núcleo de este proyecto es simular cómo una amenaza puede propagarse entre nodos vulnerables mediante el uso de modelos epidemiológicos tipo **SIR (Susceptible, Infectado, Recuperado)** y **SEIR (Expuesto)**, priorizando el análisis de estrategias de mitigación dinámica sobre grafos.

## La Analogía Médica

*   **Paciente Sano (Susceptible - S):** Un equipo vulnerable en la red con puertos críticos expuestos.
*   **Enfermedad Latente (Expuesto - E):** Un equipo que ha recibido el malware (ej. vía EternalBlue) pero el payload aún no se ejecuta. Fase de incubación (parámetro $\sigma$).
*   **Paciente Contagioso (Infectado - I):** El malware está activo, cifrando archivos y escaneando agresivamente la red para encontrar nuevos hosts (parámetro $\beta$).
*   **Cuarentena / Curado (Recuperado - R):** El equipo es parcheado o aislado mediante un firewall (parámetro $\gamma$). No puede infectar a otros ni ser infectado.

## Características Principales

1. **Modelado Informado por Datos Reales:**
    *   **UNSW-NB15:** Utilizado para extraer la topología de red y flujos de tráfico modernos. [Fuente Oficial](https://research.unsw.edu.au/projects/unsw-nb15-dataset).
    *   **WannaCry PCAP:** Análisis empírico del brote de mayo de 2017 para calcular la tasa de transmisión ($\beta$). [Análisis en Hybrid Analysis](https://hybrid-analysis.com/sample/24d004a104d4d54034dbcffc2a4b19a11f39008a575aa614ea04703480b1022c/5915accbaac2eda8675a17d2).
2. **Estrategias de Mitigación (Enfoque MDPI 2024):**
    *   Análisis del **Número Reproductivo Básico ($R_0$)** como indicador de potencial pandémico.
    *   Comparativa de estrategias de parcheo: **Aleatorio** vs. **Basado en Grado (Hubs)**.
3. **Simulador Visual Interactivos:** Un dashboard standalone que permite modificar parámetros epidemiológicos en tiempo real y observar la propagación sobre un mapamundi.

## Uso del Dashboard

El dashboard se genera como un archivo `HTML` 100% estático (no requiere servidor). Ábrelo en cualquier navegador web moderno:

👉 `reports/dashboard_wannacry.html`

### Secciones:
1. **Contexto:** Teoría de la analogía médica y definiciones de parámetros.
2. **Dataset & EDA:** Especificaciones técnicas de UNSW-NB15 y análisis de topología de red.
3. **Mitigación:** Análisis matemático del impacto de $R_0$ y el umbral crítico de inmunidad.
4. **Simulación:** Visualizador interactivo con control de línea de tiempo y escenarios predefinidos.

## Estructura del Proyecto

```text
Proyecto final Healtech/
|-- data/
|   |-- external/     # Datasets originales (PCAPs, CSVs)
|   |-- processed/    # Grafos procesados y metadatos SIR
|-- notebooks/        # EDA y prototipado de modelos epidemiológicos
|-- reports/
|   |-- figures/      # Gráficos estadísticos y de red
|   `-- dashboard_wannacry.html # DASHBOARD PRINCIPAL
`-- src/
    |-- graph/        # Construcción de grafos a partir de flujos
    |-- simulation/   # Lógica de modelos SIR/SEIR
    `-- generate_dashboard.py # Motor generador del frontend
```

## Ejecución Local

Para regenerar el dashboard tras modificar parámetros o datos:

```powershell
python src\generate_dashboard.py
```
