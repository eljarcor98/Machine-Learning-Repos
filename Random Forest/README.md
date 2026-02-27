# 🩺 Stroke Prediction - Random Forest

Este proyecto tiene como objetivo predecir la probabilidad de que un paciente sufra un accidente cerebrovascular (stroke) utilizando algoritmos de Machine Learning, con un enfoque principal en **Random Forest**.

## 📊 Estructura del Proyecto

- **[data/](./data/)**: Contiene los datasets utilizados.
  - `healthcare-dataset-stroke-data.csv`: Datos de salud descargados de GitHub.
- **[scripts/](./scripts/)**: Scripts de análisis y modelado.
  - `random_forest_analysis.py`: Análisis básico inicial.
  - `model_comparison.py`: Comparativa de modelos base (KNN, Naive Bayes, K-Means, RF).
- **[images/](./images/)**: Visualizaciones y gráficas generadas (Matrices de Confusión).
- **[documentation/](./documentation/)**: Documentación detallada del proceso y métricas.
  - `IMPLEMENTACION_RANDOM_FOREST.md`: Reporte de implementación y resultados.

## 🚀 Inicio Rápido

Para ejecutar el análisis comparativo, asegúrate de tener el entorno virtual activo y ejecuta:

```powershell
python scripts/model_comparison.py
```

## 📈 Resultados Principales

En la fase de línea base (baseline), identificamos un fuerte desbalanceo de clases. Mientras que la mayoría de los modelos priorizan la exactitud global, **Naive Bayes** mostró la mayor sensibilidad (98%) para detectar casos positivos, a pesar de tener una exactitud menor.

---
*Generado por Antigravity*
