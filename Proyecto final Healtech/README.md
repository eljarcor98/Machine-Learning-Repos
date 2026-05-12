# HealTech - Ciberseguridad Epidemiológica 🏥🛡️

El proyecto **HealTech** es una innovadora plataforma que explora la intersección entre la ciberseguridad y la epidemiología matemática. Representamos las redes informáticas como poblaciones de pacientes y las amenazas digitales (como ransomwares y gusanos) como virus patógenos reales.

El núcleo de este proyecto es simular cómo una amenaza puede propagarse entre nodos vulnerables mediante el uso de modelos epidemiológicos tipo **SIR (Susceptible, Infectado, Recuperado)** y **SEIR (Expuesto)**, y cómo los modelos de Machine Learning actúan como diagnósticos clínicos tempranos.

## La Analogía Médica

*   **Paciente Sano (Susceptible - S):** Un equipo vulnerable en la red.
*   **Enfermedad Latente (Expuesto - E):** Un equipo que ha recibido el malware (ej. SMB vulnerado) pero el payload aún no se ejecuta. Es la fase de incubación (parámetro $\sigma$).
*   **Paciente Contagioso (Infectado - I):** El malware está activo cifrando archivos y escaneando agresivamente la red para encontrar nuevos hosts (parámetro $\beta$).
*   **Cuarentena / Curado (Recuperado - R):** El equipo es parcheado o aislado mediante un firewall (parámetro $\gamma$). No puede infectar a otros ni ser infectado.

## Características Principales

1. **Modelado a Partir de Datos Reales:** Se utilizan datasets masivos de tráfico de red (UNSW-NB15 / CIC-IDS2017) para entrenar clasificadores de Machine Learning que detectan flujos maliciosos.
2. **Evaluación Clínica de Modelos:** Un modelo ML se evalúa como una prueba de laboratorio:
    * Un **Falso Negativo** es un paciente infectado que se escapa al diagnóstico, continuando la propagación e incrementando dramáticamente el $R_0$.
    * Se utiliza el **Índice de Youden** para maximizar la sensibilidad y especificidad, configurando umbrales de contención óptimos para los firewalls.
3. **Simulador Visual (WannaCry):** El proyecto incluye un **Dashboard Epidemiológico Standalone** que simula, de manera interactiva y estocástica, la propagación histórica del Ransomware WannaCry.

## El Caso WannaCry (PCAP Real - 15/05/2017)

La simulación se fundamenta en un análisis de capturas de paquetes (PCAPs) reales del ataque masivo de WannaCry que colapsó sistemas hospitalarios en 2017. 

A partir del tráfico en el puerto SMB/445, se extrajo empíricamente la violenta tasa de transmisión ($\beta$) del *worm* EternalBlue. El Dashboard visualiza este brote mapeándolo sobre un grafo topológico real con geolocalización IP.

**Hitos Históricos Representados:**
*  **Inicio (T=0):** Despliegue del ataque en mayo de 2017.
*  **Crecimiento Exponencial:** Propagación sin restricciones infectando miles de máquinas por hora ($R_0 \gg 1$).
*  **Kill-Switch:** El descubrimiento accidental del dominio *sinkhole* por Marcus Hutchins, lo cual frenó las infecciones globales al instante.

## Uso del Dashboard Multi-página

El dashboard se genera como un archivo `HTML` 100% estático (no requiere servidor). Ábrelo en cualquier navegador web moderno:

👉 `reports/dashboard_wannacry.html`

### Secciones del Dashboard:
1. **Contexto:** Explica los objetivos y datasets del proyecto.
2. **Análisis ML:** Presenta métricas como Sensibilidad, Especificidad, y el impacto clínico de un modelo (ej. Regresión Logística) en la contención de la amenaza.
3. **Simulación Interactiva:** Un visualizador a pantalla completa donde puedes:
    * Ver la propagación del malware sobre un mapamundi en tiempo real.
    * Pausar, reproducir y arrastrar la línea de tiempo.
    * Abrir el Panel Lateral para cambiar entre escenarios predefinidos (Sin Contención, Kill-Switch, SEIR) o ajustar manualmente variables epidemiológicas ($\beta$, $\gamma$, vacunas iniciales).

## Estructura del Proyecto

```text
Proyecto final Healtech/
|-- data/
|   |-- processed/
|   |   |-- ml_clinical_metrics.json          # Métricas del modelo ML
|   |   |-- wannacry_realistic_geo_host_graph.graphml # Grafo de red
|   |   `-- wannacry_pcap_sir_metadata.json   # Base empírica de parámetros
|-- reports/
|   `-- dashboard_wannacry.html               # DASHBOARD INTERACTIVO PRINCIPAL
`-- src/
    |-- models/
    |   `-- classifier.py                     # Cálculo de métricas ML y traslación SIR
    |-- graph/
    |   `-- build_wannacry_geo_graph.py       # Construcción del grafo SMB (Barabasi-Albert)
    `-- generate_dashboard.py                 # Motor generador del frontend HTML/CSS/JS
```

## Flujo de Trabajo (Ejecución Local)

Si realizas cambios en el código Python o en los datos, puedes regenerar el dashboard ejecutando el script generador desde el entorno virtual:

```powershell
.\.venv\Scripts\python.exe src\generate_dashboard.py
```
