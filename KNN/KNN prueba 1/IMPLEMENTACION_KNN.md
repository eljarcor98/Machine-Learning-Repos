# Plan de Implementación: KNN con Optimización de K

Este documento describe la lógica para implementar un modelo KNN sobre el dataset IRIS, evaluando múltiples valores de **K** para encontrar el que ofrece mayor precisión.

## 1. Preparación de Datos
- Cargar el dataset `iris.csv`.
- Separar las características (`X`) de la etiqueta (`y`).
- Dividir el conjunto en entrenamiento (Train) y prueba (Test) (ej. 80/20).

## 2. Creación y Entrenamiento Iterativo
El objetivo es probar diferentes valores de vecinos (K) para ver cuál generaliza mejor.

**Pseudocódigo del proceso:**
1. Definir un rango de N (ejemplo: de 1 a 30).
2. Crear un ciclo `for k in range(1, 31)`.
3. En cada iteración:
    - Inicializar `KNeighborsClassifier(n_neighbors=k)`.
    - Entrenar con `X_train`.
    - Predecir `X_test`.
    - Calcular el `accuracy_score`.
    - Guardar el par `(k, accuracy)` en una lista.

## 3. Tabla de Resultados (Accuracy por K)
El script debe generar una salida estructurada similar a esta tabla, donde se podrá identificar visualmente el desempeño de cada configuración.

| K (Vecinos) | Accuracy (Precisión) |
| :---: | :---: |
| 1 | 0.96 |
| 2 | 0.95 |
| 3 | 0.98 |
| ... | ... |
| n | ... |

## 4. Selección del Mejor Modelo
- Identificar el valor máximo de accuracy.
- Seleccionar el **K** más pequeño que logre ese máximo (para evitar *overfitting* innecesario).
- (Opcional) Graficar `K` vs `Accuracy` para visualizar el "codo" o punto óptimo.
