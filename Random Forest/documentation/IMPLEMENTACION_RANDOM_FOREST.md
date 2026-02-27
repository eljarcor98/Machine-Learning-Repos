# Implementación de Random Forest - Predicción de Strokes

Este documento detalla la configuración y los resultados iniciales del modelo Random Forest aplicado al dataset de predicción de accidentes cerebrovasculares.

## Estructura del Proyecto

La carpeta `Random Forest` se ha organizado de la siguiente manera:

- `data/`: Contiene el dataset original `healthcare-dataset-stroke-data.csv`.
- `scripts/`: Contiene los scripts de procesamiento y modelado (`random_forest_analysis.py`).
- `images/`: Espacio reservado para gráficas, matrices de confusión e importancia de variables.
- `documentation/`: Documentación del proyecto (este archivo).

## 📊 Análisis Exploratorio del Dataset (Profilado)

Antes de profundizar en los modelos, es vital entender la materia prima. El dataset **Healthcare Stroke Data** contiene información detallada sobre 5,110 pacientes.

### 1. Resumen de Población
- **Total de Pacientes**: 5,110
- **Pacientes Sanos (Clase 0)**: 4,861 (95.13%)
- **Pacientes con Stroke (Clase 1)**: 249 (4.87%)

> [!IMPORTANT]
> Esta distribución confirma un **desbalanceo severo**. Por cada paciente con stroke, hay aproximadamente 19 pacientes sanos.

### 2. Perfil de las Variables (Features)

#### Variables Categóricas
| Variable | Categorías Principales | Observación |
| :--- | :--- | :--- |
| **Género** | Femenino: 58.6%, Masculino: 41.4% | Población mayoritariamente femenina. |
| **Hipertensión** | No: 90.3%, Sí: 9.7% | Menos del 10% sufre de hipertensión. |
| **Enf. Corazón** | No: 94.6%, Sí: 5.4% | Variable muy poco frecuente. |
| **Casado** | Sí: 65.6%, No: 34.4% | - |
| **Tipo Trabajo** | Privado: 57.2%, Autónomo: 16%, Niños: 13.4% | - |
| **Residencia** | Urbana: 50.8%, Rural: 49.2% | Distribución muy equilibrada. |
| **Fumador** | Nunca: 37%, Desconocido: 30.2%, Ex-fumador: 17.3%, Fuma: 15.4% | Un alto porcentaje (30%) de datos desconocidos. |

#### Variables Numéricas (Promedios)
- **Edad Media**: 43.2 años (Rango: 0.08 a 82 años).
- **Nivel Glucosa**: 106.1 mg/dL (Rango: 55.1 a 271.7).
- **IMC (BMI)**: 28.9 (Rango: 10.3 a 97.6).

### 3. Integridad de los Datos
- **Valores Nulos**: Se detectaron **201 valores faltantes** exclusivamente en la columna `bmi`.
- **Acción**: Estos valores se imputaron con la media (28.9) para mantener la integridad del análisis.

## 🚀 ¿Qué es un Baseline?

En Machine Learning, un **Baseline** (línea base) es el modelo más simple o el punto de partida con el que comparamos modelos más complejos. Sirve para:

1. **Contexto**: Saber si un algoritmo complejo (como Random Forest) realmente aporta valor sobre uno simple (como Naive Bayes).
2. **Detección de problemas**: Identificar rápidamente si los datos tienen sesgos, como el desbalanceo de clases que vemos aquí.
3. **Punto de comparación**: Establecer la métrica mínima aceptable. Si tu modelo "inteligente" no supera al baseline, algo anda mal.

En este estudio, nuestros baselines son los modelos entrenados "fuera de la caja" (out-of-the-box), sin balancear los datos ni ajustar sus parámetros.

### 🔍 ¿Qué se identifica en esta fase?
1. **Desbalanceo Crítico**: Identificamos que el dataset tiene un "sesgo de mayoría" (95% sanos vs 5% strokes). Sin el baseline, podríamos creer que un 94% de exactitud es excelente, cuando en realidad el modelo no está aprendiendo a detectar la enfermedad.
2. **Capacidad Atrapada**: Evaluamos qué tan "fácil" es el problema. Si un modelo simple como Naive Bayes ya detecta patrones, sabemos que hay información útil en las variables.
3. **Necesidad de Preprocesamiento**: Al ver que KNN falla sin escalar, identificamos que las unidades de medida (ej. edad vs glucosa) están afectando los cálculos.

## 🛠️ Manejo del Dataset (Data Handling)

Para trabajar el dataset en esta fase inicial, seguimos estos pasos técnicos:

1. **Limpieza e Imputación**:
   - Se identificaron 201 valores nulos en `bmi`.
   - Se utilizó la **imputación por media**, rellenando los huecos con el promedio del resto de pacientes para no perder esos registros.
2. **Codificación Categórica (Encoding)**:
   - Variables como `gender` o `smoking_status` son texto. Los modelos solo entienden números.
   - Usamos **One-Hot Encoding** (a través de `pd.get_dummies`), creando columnas binarias (0 y 1) para cada categoría.
3. **Escalado de Características (Scaling)**:
   - Algoritmos como KNN y K-Means calculan distancias. Si la "glucosa" llega a 200 y la "edad" a 80, la glucosa dominará el cálculo.
   - Usamos `StandardScaler` para que todas las variables tengan media 0 y desviación 1, poniéndolas en "igualdad de condiciones".
4. **División de Datos (Train/Test Split)**:
   - Dividimos el dataset en **80% para entrenar** y **20% para evaluar**. Esto nos asegura que el modelo sea capaz de predecir casos que nunca ha visto, evitando que simplemente "memorice" los datos.

## Comparativa de Modelos Base (Baseline)

Se evaluaron cuatro modelos sin ajuste de hiperparámetros para establecer una línea base de comparación.

### Resumen de Desempeño

| Modelo | Exactitud (Accuracy) | Recall (Clase 1) | Observaciones |
| :--- | :---: | :---: | :--- |
| **Random Forest** | 93.93% | 0.00% | No detecta ningún caso de stroke. |
| **KNN (k=5)** | 93.35% | 0.00% | Similar a RF, dominado por la clase mayoritaria. |
| **Naive Bayes** | 55.00% | 98.00% | **Alta sensibilidad**: detecta casi todos los strokes pero tiene muchos falsos positivos. |
| **K-Means** | 93.93% | 0.00% | El clustering asignó todo a la clase mayoritaria. |

### Interpretación de las Matrices

Una **Matriz de Confusión** nos dice cuántas veces el modelo acertó y dónde se equivocó:

- **Verdaderos Negativos (TN)**: El paciente está sano y el modelo dijo "sano" (Arriba-Izquierda).
- **Verdaderos Positivos (TP)**: El paciente tiene stroke y el modelo dijo "stroke" (Abajo-Derecha).
- **Falsos Negativos (FN)**: El paciente tiene stroke pero el modelo dijo "sano" (Abajo-Izquierda). **¡El error más peligroso aquí!**
- **Falsos Positivos (FP)**: El paciente está sano pero el modelo dijo "stroke" (Arriba-Derecha).

## 📐 Fórmulas de Evaluación

Para calcular las métricas que ves en los reportes, utilizamos las cantidades de la Matriz de Confusión:

### 1. Exactitud (Accuracy)
Mide la proporción total de predicciones correctas.
$$Accuracy = \frac{TP + TN}{Total}$$

- **Random Forest**: $\frac{0 + 960}{1022} = \mathbf{0.9393}$
- **KNN (k=5)**: $\frac{0 + 954}{1022} = \mathbf{0.9335}$
- **Naive Bayes**: $\frac{61 + 499}{1022} = \mathbf{0.5479}$
- **K-Means**: $\frac{0 + 960}{1022} = \mathbf{0.9393}$

### 2. Sensibilidad (Recall)
Mide qué tan bien detectamos los casos reales (Stroke = 1).
$$Recall = \frac{TP}{TP + FN}$$

- **Random Forest**: $\frac{0}{0 + 62} = \mathbf{0.00}$
- **KNN (k=5)**: $\frac{0}{0 + 62} = \mathbf{0.00}$
- **Naive Bayes**: $\frac{61}{61 + 1} = \mathbf{0.98}$
- **K-Means**: $\frac{0}{0 + 62} = \mathbf{0.00}$

### 3. Precisión (Precision)
Mide la fiabilidad de la predicción positiva.
$$Precision = \frac{TP}{TP + FP}$$

- **Naive Bayes**: $\frac{61}{61 + 461} = \mathbf{0.12}$
- **Modelos Inertes (RF, KNN, KMeans)**: No aplica o es **0.00** ya que no realizan predicciones positivas correctas.

### 4. Puntuación F1 (F1-Score)
Balance entre Precision y Recall.
$$F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$$

- **Naive Bayes**: $2 \times \frac{0.12 \times 0.98}{0.12 + 0.98} = \mathbf{0.21}$
- **Otros modelos**: **0.00** (debido al fallo en el Recall).

## 🎚️ Análisis Interactivo de Umbral (Threshold)

El **Umbral (Threshold)** es el valor de probabilidad (entre 0 y 1) que el modelo usa para decidir si un paciente tiene stroke. Por defecto es **0.5**.

### Herramientas de Análisis Dinámico

Hemos desarrollado dos herramientas interactivas para entender mejor el comportamiento de los modelos:

1. **Curvas de Desempeño Multimétrica**: Permite ver cómo varían simultáneamente el **Accuracy, Recall, Precision y F1-Score** al mover el umbral.
   > [!TIP]
   > **[Abrir Herramienta de Umbral Interactiva](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/documentation/threshold_comparison.html)**

2. **Matrices de Confusión Dinámicas**: Permite observar cómo se redistribuyen los aciertos y errores (Heatmaps) en tiempo real.
   > [!IMPORTANT]
   > **[Abrir Matrices de Confusión Interactivas](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/documentation/interactive_matrices.html)**

## 🩺 Análisis Clínico y Selección del Umbral

En un contexto médico (predicción de strokes):
- **Umbral bajo (0.05 - 0.20)**: Es preferible en medicina. Favorece la **Sensibilidad** (detectar la enfermedad), aceptando algunos Falsos Positivos para no dejar pasar ningún caso real (Falsos Negativos).
- **El Baseline (0.5)**: Resulta ser demasiado estricto para este dataset desbalanceado, haciendo que modelos potentes como Random Forest ignoren por completo la clase de riesgo.

#### Análisis por Modelo:
1. **Random Forest / KNN / K-Means**: Sus matrices muestran casi todo en la columna de "No Stroke" (TN altos, TP = 0). Son modelos "pesimistas" que ignoran la clase minoritaria por el desbalanceo.
2. **Naive Bayes**: Su matriz es la única con valores significativos en los TP (Abajo-Derecha), detectando los strokes, pero su número de FP es muy elevado, saturando la columna de predicción de stroke.

### Galería de Matrices de Confusión

A continuación, se presentan las matrices de cada modelo para facilitar la comparación visual:

#### 1. Random Forest (Predice mayoritariamente clase 0)
![Matriz RF](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/images/cm_random_forest.png)

#### 2. KNN (Predice mayoritariamente clase 0)
![Matriz KNN](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/images/cm_knn.png)

#### 3. Naive Bayes (Excelente para detectar strokes, pero con muchos Falsos Positivos)
![Matriz Naive Bayes](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/images/cm_naive_bayes.png)

#### 4. K-Means (Asocia clusters a la clase dominante)
![Matriz K-Means](file:///c:/Users/Arnold's/Documents/Repositorios%20Machine%20Learning/Random%20Forest/images/cm_kmeans.png)

## Análisis de Resultados

El desbalanceo de clases es el desafío principal. Mientras que **Random Forest** y **KNN** optan por la estrategia segura de predecir siempre "no stroke" (obteniendo alta exactitud pero nula utilidad clínica), **Naive Bayes** muestra un comportamiento opuesto: es extremadamente sensible (detecta el stroke), lo cual es deseable en medicina, pero a costa de una bajísima precisión (muchas falsas alarmas).

## Próximos Pasos
- [ ] Aplicar **SMOTE** para balancear las clases antes del entrenamiento.
- [ ] Optimizar **Random Forest** para mejorar el balance entre precisión y recall.
- [ ] Refinar las gráficas y guardarlas formalmente en la carpeta `images/`.

---
*Generado automáticamente por Antigravity*
