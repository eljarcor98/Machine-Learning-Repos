# Taller de Regresion Lineal y Logistica

Este repositorio organiza el desarrollo del taller de machine learning. En el estado actual, el trabajo se concentro en la parte de regresion lineal usando el dataset Auto MPG, dejando documentados el contexto, la exploracion inicial y la interpretacion de metricas.

## Objetivo del proyecto

Desarrollar, documentar y comparar ejercicios o experimentos relacionados con:

- Regresion lineal
- Regresion logistica
- Preparacion de datos
- Evaluacion de metricas
- Analisis de resultados

## Enfoque actual

Por decision de trabajo, primero se desarrollara solo la parte de regresion lineal.

- Dataset actual: `data/raw/auto-mpg.csv`
- Variable objetivo: `mpg`
- Predictor principal para iniciar: `horsepower`
- Enfoque metodologico: exploracion visual, limpieza, modelo lineal simple, residuos y metricas

## Estructura del proyecto

```text
Taller lineal - logistica/
|-- data/
|   |-- raw/
|   |-- interim/
|   `-- processed/
|-- docs/
|-- models/
|-- notebooks/
|-- reports/
|   `-- figures/
|-- src/
|   |-- data/
|   |-- features/
|   |-- models/
|   `-- visualization/
|-- tests/
|-- .gitignore
|-- requirements.txt
|-- README.md
`-- guia-ml1-lineal-logistica-sesiones.pdf
```

## Flujo de trabajo recomendado

1. Leer la guia del taller y registrar los objetivos en `docs/project_overview.md`.
2. Guardar los datos originales en `data/raw/`.
3. Realizar exploracion y pruebas en `notebooks/`.
4. Mover funciones reutilizables a `src/`.
5. Guardar datasets limpios en `data/processed/`.
6. Guardar graficas en `reports/figures/`.
7. Documentar decisiones, metricas y hallazgos en `docs/experiment_log.md`.
8. Consolidar resultados finales en `reports/final_report.md`.

## Documentacion disponible

- `docs/project_overview.md`: contexto, objetivo y alcance del taller actual
- `docs/data_dictionary.md`: descripcion del dataset y variables
- `docs/eda_summary.md`: resumen de exploracion inicial con figuras incrustadas
- `docs/regression_metrics.md`: explicacion de residuos, `MAE`, `MSE`, `RMSE` y `R²`
- `docs/experiment_log.md`: bitacora de avances y decisiones
- `docs/report_guidelines.md`: guia para redactar el informe

## Convenciones sugeridas

- No modificar directamente los datos en `data/raw/`.
- Nombrar notebooks con prefijo numerico, por ejemplo: `01_eda.ipynb`, `02_regresion_lineal.ipynb`.
- Registrar cada experimento importante en la bitacora.
- Mantener el codigo reutilizable en `src/` y no solo en notebooks.

## Requisitos

Crear un entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Exploracion visual inicial

Las primeras figuras del dataset quedaron guardadas en `reports/figures/` y tambien estan embebidas en `docs/eda_summary.md`.

Figura principal del taller:

![Regresion lineal simple potencia vs consumo](reports/figures/01_linear_regression_horsepower_vs_mpg.png)

Hallazgos iniciales:

- `horsepower` y `mpg` muestran una relacion negativa fuerte
- `weight` parece tener una relacion incluso mas fuerte con `mpg`
- `horsepower` contenia 6 valores faltantes codificados como `?`
- tras la limpieza quedaron 392 filas utiles para el analisis
- el primer modelo lineal simple obtuvo `R² = 0.6059`, `MAE = 3.8276` y `RMSE = 4.8932`
- en evaluacion `test`, el modelo obtuvo `R² = 0.5660`, `MAE = 3.7825` y `RMSE = 4.7067`
- ya existe una grafica de residuos coloreados por signo en `docs/eda_summary.md`

## Entregables sugeridos

- Notebooks con el desarrollo del taller
- Modelos o artefactos relevantes en `models/`
- Graficas en `reports/figures/`
- Informe final en `reports/final_report.md`
- Bitacora de experimentos en `docs/experiment_log.md`

## Estado

Proyecto inicializado con estructura base, dataset cargado, exploracion visual generada y documentacion actualizada.

## Cambios recientes

- se creo la estructura del proyecto
- se agrego documentacion base en `docs/`
- se descargo y ubico el dataset Auto MPG en `data/raw/`
- se limpio `horsepower` para exploracion inicial
- se generaron 7 figuras en `reports/figures/`
- se ajusto una regresion lineal simple con `horsepower -> mpg`
- se calcularon metricas de entrenamiento y prueba para el modelo lineal
- se genero la grafica de residuos positivos y negativos
- se documento la exploracion en `docs/eda_summary.md`
- se documento la interpretacion de metricas en `docs/regression_metrics.md`
