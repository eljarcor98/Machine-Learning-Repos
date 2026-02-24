# Guía Detallada: Implementación de KNN con el Dataset IRIS

Esta guía explica paso a paso cómo construir un modelo de **K-Nearest Neighbors (K-Vecinos más Cercanos)** utilizando Python y la librería `scikit-learn`.

## 1. Conceptos Básicos de KNN

El algoritmo **KNN** es un modelo de aprendizaje supervisado que clasifica un punto de datos basándose en la clase de sus "k" vecinos más cercanos. 

![Visualización Conceptual de KNN](images/knn_visualization.png)

### ¿Cómo se asigna la clase más frecuente?

Este proceso se conoce como **Votación por Mayoría** (Majority Voting):

1. **Cálculo de Distancia**: Cuando el modelo recibe una nueva flor de la que no sabe su nombre, calcula la distancia entre esa flor y **todas** las flores conocidas.
2. **Selección de Vecinos**: El modelo elige los **k** puntos con la distancia más corta.
3. **El Voto**: Los vecinos "votan" por su especie y gana la más frecuente.

#### Ejemplo Práctico con IRIS (k=3):

Supongamos que tenemos una flor desconocida con estas medidas:
- **Largo del pétalo**: 4.8 cm
- **Ancho del pétalo**: 1.5 cm

El algoritmo busca los 3 vecinos más cercanos en el espacio de datos y encuentra:
1.  **Vecino 1**: Distancia 0.1 → Especie: **Versicolor**
2.  **Vecino 2**: Distancia 0.15 → Especie: **Versicolor**
3.  **Vecino 3**: Distancia 0.2 → Especie: **Virginica**

**Conteo de votos:**
- Versicolor: 2 votos
- Virginica: 1 voto

**Resultado:** El modelo clasifica la nueva flor como **Versicolor**.

> [!TIP]
> Es recomendable usar un número **k impar** (3, 5, 7...) para evitar empates en la votación.

---

## 2. Preparación del Entorno

Primero, importamos las librerías necesarias:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
```

### Explicación de Comandos:
- `train_test_split`: Divide los datos para que el modelo "estudie" con unos y lo "evaluemos" con otros.
- `KNeighborsClassifier`: Es el "motor" del algoritmo KNN.
- `confusion_matrix`: Nos dice en qué flores se equivocó el modelo.

---

## 3. Carga y División de Datos

```python
# Carga del dataset
df = pd.read_csv('../dataset/iris.csv')

# Dividir en variables de entrada (X) y salida (y)
X = df.drop('species', axis=1)  # Las medidas de la flor
y = df['species']               # El nombre de la especie

# División 80% entrenamiento / 20% prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

---

## 4. Creación y Entrenamiento del Modelo

Aquí definimos cuántos vecinos queremos mirar (k) y ajustamos el modelo a nuestros datos de entrenamiento.

```python
# Crear el modelo con k=3
knn = KNeighborsClassifier(n_neighbors=3)

# Entrenamiento
knn.fit(X_train, y_train)
```

---

## 5. Evaluación y Gráficas de Resultados

Una vez entrenado, pedimos al modelo que prediga las especies de las flores que nunca ha visto (`X_test`).

### Matriz de Confusión (Gráfica)
Esta gráfica es fundamental para ver el rendimiento visualmente.

```python
# Predicciones
y_pred = knn.predict(X_test)

# Generar la matriz de confusión
cm = confusion_matrix(y_test, y_pred)

# Visualización
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=knn.classes_, yticklabels=knn.classes_)
plt.xlabel('Predicción del Modelo')
plt.ylabel('Valor Real')
plt.title('Matriz de Confusión - Modelo KNN')
plt.show()
```

### Explicación de la Gráfica:
- La **diagonal** muestra las flores clasificadas correctamente.
- Los valores **fuera de la diagonal** indican errores (ej: el modelo pensó que era *Versicolor* pero era *Virginica*).

---

## 6. Reporte de Clasificación

Finalmente, imprimimos un resumen de métricas clave:

```python
print(classification_report(y_test, y_pred))
```

- **Precision**: ¿Qué tan exacto es cuando dice que es una especie?
- **Recall**: ¿Cuántas flores de esa especie logró encontrar del total?
- **F1-Score**: Un equilibrio entre las dos anteriores.

---

## Resumen de Flujo de Trabajo
1. **Limpiar datos** (Ya lo hicimos en el EDA).
2. **Dividir datos** (`train_test_split`).
3. **Instanciar modelo** (`KNeighborsClassifier`).
4. **Entrenar** (`fit`).
5. **Predecir** (`predict`).
6. **Evaluar** (`confusion_matrix` y `classification_report`).
