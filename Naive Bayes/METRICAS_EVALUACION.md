# Métricas de Evaluación de Modelos de Clasificación

Este documento explica las fórmulas fundamentales utilizadas para evaluar el rendimiento de un modelo de clasificación, como el de Naive Bayes para Spam.

## 1. Conceptos Básicos (Matriz de Confusión)

Para entender las fórmulas, primero debemos identificar los cuatro resultados posibles de una predicción:

| Sigla | Nombre | Significado |
| :--- | :--- | :--- |
| **VP** | Verdadero Positivo | Predijo **SPAM** y era **SPAM** (Acierto). |
| **VN** | Verdadero Negativo | Predijo **HAM** y era **HAM** (Acierto). |
| **FP** | Falso Positivo | Predijo **SPAM** pero era **HAM** (Falsa alarma). |
| **FN** | Falso Negativo | Predijo **HAM** pero era **SPAM** (Se le escapó). |

---

## 2. Las Fórmulas

### 📊 Exactitud (Accuracy)
Mide el porcentaje total de aciertos del modelo.
> **Fórmula:**
> $$\text{Accuracy} = \frac{VP + VN}{VP + VN + FP + FN}$$
> **En resumen:** ¿Qué tan bien funciona el modelo en general?

### 🎯 Precisión (Precision)
Mide la calidad de las predicciones positivas. Es crucial para evitar "falsas alarmas".
> **Fórmula:**
> $$\text{Precision} = \frac{VP}{VP + FP}$$
> **En resumen:** De todo lo que el modelo marcó como SPAM, ¿cuánto era verdad?

### 🔎 Exhaustividad (Recall / Sensibilidad)
Mide la capacidad del modelo para encontrar todos los casos positivos reales.
> **Fórmula:**
> $$\text{Recall} = \frac{VP}{VP + FN}$$
> **En resumen:** De todos los mensajes de SPAM reales, ¿cuántos logró atrapar?

---

## 3. ¿Cuál es más importante para el Spam?

*   **Si priorizas la Precisión:** Estás cuidando que ningún mensaje legítimo (**Ham**) se pierda en la carpeta de Spam. Es la métrica más importante en este proyecto.
*   **Si priorizas el Recall:** Estás intentando que no llegue ni un solo mensaje de **Spam** a la bandeja de entrada, aunque corras el riesgo de bloquear algún mensaje bueno por error.

---

## 4. F1-Score (El Equilibrio)
Si quieres una sola métrica que combine la Precisión y el Recall, usamos el F1-Score:
$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
