# Descripción del Dataset: Credit Card Fraud

Este dataset contiene transacciones realizadas con tarjetas de crédito en septiembre de 2013 por titulares de tarjetas europeos. Contiene transacciones ocurridas en dos días, donde hay 492 fraudes de un total de 284,807 transacciones.

## Variables del Dataset

Debido a problemas de confidencialidad, no se proporcionan las características originales ni más información sobre los datos. Las características **V1, V2, ..., V28** son los componentes principales obtenidos con PCA.

| Variable | Descripción |
| :--- | :--- |
| **Time** | Segundos transcurridos entre cada transacción y la primera transacción en el dataset. |
| **V1 - V28** | Características numéricas resultantes de una transformación PCA. |
| **Amount** | Monto de la transacción. Puede ser utilizado para aprendizaje sensible al costo. |
| **Class** | Variable de respuesta. Toma el valor **1** en caso de fraude y **0** en caso contrario. |

## Información Relevante para el Análisis

1.  **Desbalance de Clases:** El dataset está altamente desbalanceado. La clase positiva (fraude) representa solo el **0.172%** de todas las transacciones. Es fundamental manejar este desbalance (por ejemplo, usando técnicas como SMOTE, submuestreo o métricas como AUPRC en lugar de precisión simple).
2.  **Escalado de Datos:** Las variables `V1` a `V28` ya están escaladas (como resultado de PCA), pero `Time` y `Amount` no lo están. Se recomienda escalar estas dos variables antes de entrenar modelos sensibles a la magnitud (como KNN o SVM).
3.  **Métrica de Evaluación:** Debido al desequilibrio, la **Precisión (Accuracy)** no es una buena métrica. Se recomienda usar el **Área bajo la Curva de Precisión-Recall (AUPRC)** o la **Matriz de Confusión**.
