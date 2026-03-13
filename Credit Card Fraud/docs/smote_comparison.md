# Comparación: Dataset Original vs. Balanceado (SMOTE)

He aplicado la técnica SMOTE (Synthetic Minority Over-sampling Technique) para abordar el desbalance extremo de las clases en el dataset de fraude de tarjetas de crédito.

## Diferencias en la Distribución de Clases

| Característica | Dataset Original | Dataset con SMOTE |
| :--- | :--- | :--- |
| **Clase 0 (Normal)** | 284,315 | 284,315 |
| **Clase 1 (Fraude)** | 492 | 284,315 |
| **Total Transacciones** | 284,807 | 568,630 |
| **Ratio de Fraude** | 0.172% | 50.00% |

> [!IMPORTANT]
> **SMOTE** no solo duplica registros, sino que crea nuevos ejemplos sintéticos basados en la vecindad de los puntos de la clase minoritaria. Esto ayuda a que el modelo aprenda mejor las fronteras de decisión del fraude.

## Visualización
Puedes encontrar el gráfico comparativo en la carpeta del proyecto:
`[Archivo local: comparacion_balanceo.png](file:///c:/Users/Arnold's/Documents/Repositorios Machine Learning/Credit Card Fraud/comparacion_balanceo.png)`

## Impacto en el Modelado
1. **Sensibilidad:** El modelo ahora podrá "ver" tantos casos de fraude como normales durante el entrenamiento, lo que mejora drásticamente el **Recall** (capacidad de detectar fraudes).
2. **Sesgo:** Al estar balanceado, se reduce el sesgo hacia la clase mayoritaria (predecir todo como "no fraude").
3. **Validación:** Es crucial recordar que **SMOTE solo se aplica al conjunto de entrenamiento**. El conjunto de prueba debe mantenerse con la distribución original para reflejar el mundo real.
