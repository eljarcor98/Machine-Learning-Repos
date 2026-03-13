# Credit Card Fraud Detection

Este proyecto tiene como objetivo detectar transacciones fraudulentas en tarjetas de crédito utilizando técnicas de Machine Learning.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

- **src/**: Contiene los scripts de Python para descarga, procesamiento y modelado.
  - `download_dataset.py`: Descarga el dataset original desde Kaggle.
  - `balance_dataset.py`: Aplica la técnica SMOTE para balancear las clases.
- **data/**: Almacena los datasets utilizados en el proyecto.
  - `creditcard_balanced.csv`: Dataset generado después de aplicar SMOTE.
- **plots/**: Contiene las visualizaciones y gráficos generados durante el análisis.
  - `comparacion_balanceo.png`: Gráfico que muestra la distribución de clases antes y después de SMOTE.
- **docs/**: Documentación detallada sobre el dataset y los resultados.

## Cómo empezar

1.  Asegúrate de tener instaladas las dependencias:
    ```bash
    pip install kagglehub imbalanced-learn pandas matplotlib seaborn
    ```
2.  Ejecuta `src/download_dataset.py` para obtener los datos.
3.  Ejecuta `src/balance_dataset.py` para generar el dataset balanceado y ver la comparativa.

## Análisis de Datos

- El dataset original es altamente desbalanceado (0.172% de fraude).
- Se utilizó **SMOTE** para crear ejemplos sintéticos de la clase minoritaria y equilibrar la distribución al 50/50.
