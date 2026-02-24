# Plan de Implementación: Clasificación de Spam con Naive Bayes

Este plan detalla el flujo de trabajo seguido para construir un modelo de Machine Learning capaz de clasificar mensajes SMS.

## Fase 1: Exploración y Análisis de Datos (EDA)
**Objetivo:** Entender la estructura del dataset y el balance de las clases.
1.  **Carga de datos:** Lectura de `spam.csv` usando codificación `latin-1`.
2.  **Limpieza inicial:** Selección de columnas relevantes (`Label` y `Message`).
3.  **Análisis de balance:** Identificación de la proporción (87% Ham / 13% Spam).
4.  **Visualización:** Creación de gráficos de barras para confirmar el desbalance.

## Fase 2: Preprocesamiento de Texto
**Objetivo:** Convertir el lenguaje humano en datos numéricos.
1.  **Limpieza:** Conversión a minúsculas y eliminación de caracteres especiales.
2.  **Tokenización:** División de frases en palabras individuales.
3.  **Codificación (Bag of Words):**
    *   Uso de `CountVectorizer`.
    *   Eliminación de *Stop Words* (palabras comunes como "the", "a" que no aportan valor).
    *   Construcción del vocabulario basado en la frecuencia.

## Fase 3: Estrategia de Entrenamiento
**Objetivo:** Asegurar que el modelo aprenda correctamente a pesar del desbalance.
1.  **Split Train-Test:** División de datos en **80% Entrenamiento** y **20% Prueba**.
2.  **Estratificación (`stratify=y`):** Garantizar que el 13% de Spam esté presente tanto en el entrenamiento como en la prueba.
3.  **Selección de Modelo:** Uso de **Multinomial Naive Bayes**, ideal para datos que representan conteos de palabras.

## Fase 4: Evaluación del Modelo
**Objetivo:** Medir el rendimiento real del predictor.
1.  **Matriz de Confusión:** Visualizar aciertos y tipos de errores (Falsos Positivos vs. Falsos Negativos).
2.  **Métricas Clave:**
    *   **Accuracy:** Exactitud global.
    *   **Precision:** Fiabilidad de la predicción de Spam.
    *   **Recall:** Capacidad de atrapar todos los mensajes de Spam.
3.  **Análisis de Resultados:** Identificar palabras que confunden al modelo.

## Fase 5: Pruebas y Validación
**Objetivo:** Verificar el modelo con datos nuevos.
1.  **Predicción Manual:** Creación de una función para introducir mensajes personalizados.
2.  **Análisis de Probabilidades:** Revisar con qué nivel de confianza el modelo toma sus decisiones (uso de `predict_proba`).

---
**Resultado Final:** Un modelo con ~98.5% de exactitud y alta precisión para evitar el bloqueo de mensajes legítimos.
