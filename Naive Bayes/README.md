# Clasificación de Spam con Naive Bayes 📧

Este proyecto implementa un sistema de aprendizaje automático para la detección de mensajes basura (Spam) en SMS, utilizando el algoritmo **Multinomial Naive Bayes** y técnicas de Procesamiento de Lenguaje Natural (NLP).

## 📊 Estado Actual del Proyecto
El modelo ha sido entrenado y evaluado con éxito, alcanzando un rendimiento sobresaliente:
*   **Exactitud Global (Accuracy):** 98.57%
*   **Precisión (Spam):** 97% (Baja tasa de falsos positivos)
*   **Recall (Spam):** 92% (Alta capacidad de detección)

---

## 🚀 Implementación Passo a Passo

### 1. Preparación y Exploración (`analizar_spam.py`, `grafico_frecuencia.py`)
*   Carga robusta del dataset `spam.csv` (5,572 registros).
*   Identificación de desbalance de clases: **86.6% Ham** vs **13.4% Spam**.
*   Generación de `graphs/frecuencia_clases.png`.

### 2. Análisis de Vocabulario (`frecuencia_palabras.py`)
*   Extracción de las palabras más frecuentes en mensajes de Spam (ej. "free", "claim", "txt").
*   Comparativa visual guardada en `graphs/frecuencia_palabras.png`.

### 3. Entrenamiento del Modelo (`entrenamiento_modelo.py`)
*   **División de Datos:** Split 80/20 con **Estratificación** para mantener las proporciones de spam.
*   **Vectorización:** Implementación de **Bag of Words (CountVectorizer)** eliminando *Stop Words* en inglés.
*   **Modelo:** Multinomial Naive Bayes.
*   **Evaluación:** Generación de reporte de métricas y Matriz de Confusión (`graphs/matriz_confusion.png`).

---

## 📂 Estructura de Archivos

### Scripts Principales
- `entrenamiento_modelo.py`: El núcleo del proyecto. Entrena, evalúa y permite pruebas manuales.
- `frecuencia_palabras.py`: Script para visualizar el peso de las palabras clave.
- `grafico_frecuencia.py`: Análisis del balance de clases.
- `analizar_spam.py`: Exploración básica del dataframe.

### Documentación de Soporte
- [PLAN_IMPLEMENTACION.md](./PLAN_IMPLEMENTACION.md): Detalle de las 5 fases del proyecto.
- [METRICAS_EVALUACION.md](./METRICAS_EVALUACION.md): Explicación teórica de Accuracy, Precision y Recall.

### Recursos y Salidas
- `spam.csv`: Dataset original.
- `matriz_confusion.png`: Visualización de aciertos y errores del modelo.
- `frecuencia_palabras.png`: Gráfico comparativo de palabras.

---

## 🛠️ Cómo Ejecutar

1.  **Instalar dependencias:**
    ```bash
    pip install pandas scikit-learn matplotlib seaborn
    ```
2.  **Entrenar y probar el modelo:**
    ```bash
    python src/entrenamiento_modelo.py
    ```
3.  **Ver análisis de palabras:**
    ```bash
    python src/frecuencia_palabras.py
    ```

---
📅 **Última actualización:** 11 de febrero de 2026
