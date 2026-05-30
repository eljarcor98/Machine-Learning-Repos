# Resumen de Exploracion Inicial

## Objetivo

Entender como se comportan las variables del dataset Auto MPG antes de ajustar un modelo de regresion lineal.

## Archivo analizado

- Ruta: `data/raw/auto-mpg.csv`
- Filas originales: 398
- Filas limpias para exploracion: 392

## Limpieza aplicada

La columna `horsepower` venia como texto y contenia 6 valores faltantes representados con `?`. Para poder trabajarla:

- se convirtio `horsepower` a formato numerico
- los valores no convertibles pasaron a nulos
- se eliminaron las filas con valores faltantes en las variables clave

No se encontraron duplicados exactos.

## Graficas generadas

Las figuras se guardaron en `reports/figures/`.

### 1. Regresion lineal simple: potencia vs consumo

- Archivo: `01_linear_regression_horsepower_vs_mpg.png`
- Lectura inicial: la recta ajustada confirma una pendiente negativa
- Interpretacion: a medida que aumenta la potencia del motor, el `mpg` tiende a disminuir de manera sistematica
- Ecuacion ajustada: `mpg = 39.9359 - 0.1578 * horsepower`
- Relevancia para el taller: este es el primer modelo formal de regresion lineal del proyecto

![Regresion lineal simple potencia vs consumo](../reports/figures/01_linear_regression_horsepower_vs_mpg.png)

### 2. Proyeccion de puntos hacia la recta de regresion

- Archivo: `02_projection_to_regression_line.png`
- Lectura inicial: las lineas verticales muestran la distancia entre todos los puntos observados y la recta ajustada
- Interpretacion: esa distancia vertical es el residuo del modelo para cada observacion del dataset
- Relevancia: esta es la forma mas intuitiva de ver como la regresion se equivoca punto por punto

Colores usados:

- verde: el punto real quedo por encima de la recta, por lo tanto el residuo es positivo
- rojo: el punto real quedo por debajo de la recta, por lo tanto el residuo es negativo
- azul oscuro: punto proyectado sobre la recta de regresion

Que significa quedar arriba o abajo de la recta:

- si un punto queda arriba de la recta, el valor real de `mpg` fue mayor que el valor predicho por el modelo
- en ese caso, el residuo es positivo y el modelo subestimo el rendimiento de combustible
- si un punto queda abajo de la recta, el valor real de `mpg` fue menor que el valor predicho
- en ese caso, el residuo es negativo y el modelo sobreestimo el rendimiento de combustible

En formula:

`residuo = valor real - valor predicho`

Por tanto:

- si `real > predicho`, el residuo es positivo
- si `real < predicho`, el residuo es negativo

![Proyeccion de puntos hacia la recta](../reports/figures/02_projection_to_regression_line.png)

### 3. Residuos del modelo lineal

- Archivo: `03_residuals_horsepower_vs_mpg.png`
- Lectura inicial: los residuos positivos quedan por encima de 0 y los negativos por debajo
- Interpretacion: un residuo positivo significa que el valor real de `mpg` fue mayor que el predicho; uno negativo significa que el modelo sobreestimo el `mpg`
- Relevancia: esta grafica permite ver si la recta esta fallando con algun patron sistematico

Colores usados:

- verde: residuo positivo
- rojo: residuo negativo

![Residuos del modelo lineal](../reports/figures/03_residuals_horsepower_vs_mpg.png)

### 4. Residuos en grafica de barras

- Archivo: `04_residuals_bar_chart.png`
- Lectura inicial: cada barra representa cuantas observaciones caen dentro de un intervalo de residuos
- Interpretacion: permite ver en que rangos de error se concentra el modelo y si los residuos se acumulan mas cerca de 0 o en valores extremos
- Relevancia: esta grafica ayuda a responder cuantas observaciones tienen errores pequenos, moderados o grandes

![Residuos en barras](../reports/figures/04_residuals_bar_chart.png)

### 5. Potencia vs consumo

- Archivo: `05_horsepower_vs_mpg.png`
- Lectura inicial: la relacion es claramente negativa
- Interpretacion: a medida que aumenta la potencia del motor, el `mpg` tiende a disminuir
- Relevancia para el taller: esta es la grafica base que justifica el modelo lineal simple

![Potencia vs consumo](../reports/figures/05_horsepower_vs_mpg.png)

### 6. Peso vs consumo

- Archivo: `06_weight_vs_mpg.png`
- Lectura inicial: la relacion negativa parece incluso mas fuerte que en potencia
- Interpretacion: los vehiculos mas pesados tienden a consumir mas combustible
- Relevancia: `weight` podria ser una variable muy fuerte para comparar mas adelante

![Peso vs consumo](../reports/figures/06_weight_vs_mpg.png)

### 7. Aceleracion vs consumo

- Archivo: `07_acceleration_vs_mpg.png`
- Lectura inicial: la relacion es positiva, pero menos marcada
- Interpretacion: hay una asociacion moderada, aunque mas dispersa

![Aceleracion vs consumo](../reports/figures/07_acceleration_vs_mpg.png)

### 8. Distribucion de `mpg`

- Archivo: `08_distribution_mpg.png`
- Lectura inicial: permite ver el rango y la concentracion de valores del target
- Relevancia: ayuda a entender si el problema tiene sesgos fuertes o extremos notorios

![Distribucion de mpg](../reports/figures/08_distribution_mpg.png)

### 9. Distribucion de `horsepower`

- Archivo: `09_distribution_horsepower.png`
- Lectura inicial: la potencia no esta distribuida de manera uniforme
- Relevancia: puede afectar la forma visual del ajuste y la presencia de regiones con distinta densidad de datos

![Distribucion de horsepower](../reports/figures/09_distribution_horsepower.png)

### 10. Mapa de correlacion

- Archivo: `10_correlation_heatmap.png`
- Lectura inicial: confirma relaciones fuertes entre `mpg` y varias variables mecanicas
- Relevancia: da una vista global antes de decidir que variables probar despues

![Mapa de correlacion](../reports/figures/10_correlation_heatmap.png)

### 11. MPG por origen

- Archivo: `11_mpg_by_origin.png`
- Lectura inicial: hay diferencias de consumo entre regiones
- Relevancia: sugiere que `origin` podria aportar si luego se construye un modelo mas rico

![MPG por origen](../reports/figures/11_mpg_by_origin.png)

## Resultados del modelo lineal simple

El primer modelo formal usa `horsepower` para predecir `mpg`.

### Ajuste sobre todos los datos

| Metrica | Valor |
|---|---|
| Pendiente | -0.1578 |
| Intercepto | 39.9359 |
| MAE | 3.8276 |
| MSE | 23.9437 |
| RMSE | 4.8932 |
| R² | 0.6059 |

### Evaluacion con train/test

Para tener una lectura mas realista del rendimiento, tambien se separaron los datos en entrenamiento y prueba con `test_size = 0.2` y `random_state = 42`.

| Conjunto | MAE | MSE | RMSE | R² |
|---|---:|---:|---:|---:|
| Train | 3.8473 | 24.4752 | 4.9472 | 0.6121 |
| Test | 3.7825 | 22.1532 | 4.7067 | 0.5660 |

Coeficientes del modelo train/test:

- Pendiente: `-0.1626`
- Intercepto: `40.6061`

## Interpretacion de las metricas

- La pendiente negativa indica que, en promedio, al aumentar una unidad de `horsepower`, el `mpg` disminuye en aproximadamente `0.1578`, manteniendo el resto del contexto fuera del modelo.
- El `MAE` de `3.8276` sugiere que el modelo se equivoca en promedio por cerca de 3.83 millas por galon.
- El `RMSE` de `4.8932` es mayor que el `MAE`, lo que sugiere que existen errores relativamente grandes que pesan mas al cuadrado.
- El `R²` de `0.6059` indica que el modelo explica cerca del 60.59% de la variacion de `mpg` frente a un baseline que siempre predice la media.
- En evaluacion `test`, el `MAE` de `3.7825` indica que el error promedio sigue rondando las 3.8 millas por galon cuando el modelo enfrenta datos no usados en el ajuste.
- El `R²` de `0.5660` en `test` muestra que el modelo conserva capacidad explicativa razonable fuera del entrenamiento, aunque menor que dentro de `train`, como es normal.

## Lectura de los residuos

- La grafica de proyeccion hace visible el residuo directamente como una distancia vertical entre el punto real y su valor estimado en la recta.
- La grafica de barras por intervalos permite ver cuantos residuos caen dentro de ciertos rangos de error.
- Los puntos verdes representan observaciones cuyo `mpg` real fue mayor que el predicho por el modelo.
- Los puntos rojos representan observaciones cuyo `mpg` real fue menor que el predicho.
- Si un punto queda arriba de la recta, el modelo se queda corto y subestima el `mpg`.
- Si un punto queda abajo de la recta, el modelo se pasa y sobreestima el `mpg`.
- La nube de residuos no parece completamente aleatoria, lo que sugiere que la relacion entre `horsepower` y `mpg` podria no ser perfectamente lineal.
- Esto respalda la idea de que mas adelante valdra la pena comparar esta recta con un ajuste polinomial de bajo grado.

## Correlaciones principales con `mpg`

| Variable | Correlacion |
|---|---|
| weight | -0.832 |
| displacement | -0.805 |
| horsepower | -0.778 |
| cylinders | -0.778 |
| model year | 0.581 |
| origin | 0.565 |
| acceleration | 0.423 |

## Lecturas iniciales

- `horsepower` es una muy buena variable para empezar porque la relacion con `mpg` es fuerte y coincide con la pregunta de la guia.
- `weight` parece incluso mas asociado con `mpg`, por lo que mas adelante puede servir para comparar modelos.
- La relacion entre potencia y consumo no parece perfectamente lineal; podria haber cierta curvatura.
- Los residuos del modelo lineal sugieren que la recta captura una parte importante de la tendencia, pero no toda la estructura.
- Eso hace razonable que, despues del modelo lineal simple, evaluemos si un ajuste polinomial de grado bajo mejora sin sobreajustar.

## Conclusion provisional

La exploracion inicial respalda el uso de una regresion lineal simple con `horsepower` para empezar el taller. Visual y numericamente, hay una relacion negativa clara con `mpg`, y el dataset ya quedo en un estado adecuado para pasar a la fase de modelado.
