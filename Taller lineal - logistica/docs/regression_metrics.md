# Metricas de Regresion Lineal

## Para que sirven

En regresion lineal las metricas no solo sirven para poner numeros en una tabla. Sirven para entender:

- cuanto se equivoca el modelo
- si los errores grandes estan pesando mucho
- si el modelo mejora de verdad frente a una prediccion ingenua

## Residuo

La idea mas importante antes de hablar de metricas es el residuo:

`residuo = valor real - valor predicho`

Interpretacion:

- residuo positivo: el valor real quedo por encima de lo que esperaba el modelo
- residuo negativo: el valor real quedo por debajo
- residuo grande en valor absoluto: el error fue grande

Los residuos ayudan a detectar si el modelo esta fallando de forma sistematica.

## MAE

`MAE = Mean Absolute Error`

Es el promedio de los errores absolutos.

Que responde:

`En promedio, cuanto se equivoca el modelo en unidades reales del problema?`

En este taller, se leeria asi:

`En promedio, el modelo se equivoca en X mpg.`

Ventajas:

- es facil de explicar
- esta en las mismas unidades de `mpg`
- no exagera tanto el efecto de errores extremos

Limitacion:

- no castiga especialmente los errores grandes

## MSE

`MSE = Mean Squared Error`

Es el promedio de los errores al cuadrado.

Que aporta:

- penaliza mucho mas los errores grandes
- es util cuando queremos notar la presencia de predicciones muy malas
- es la funcion de costo clasica de la regresion lineal

Limitacion principal:

- queda en unidades cuadradas, asi que es menos intuitiva

## RMSE

`RMSE = Root Mean Squared Error`

Es la raiz cuadrada del `MSE`.

Que aporta:

- mantiene la sensibilidad a errores grandes
- vuelve a las unidades originales del target

Interpretacion util:

`El error tipico del modelo, dando mas peso a fallos grandes, es de X mpg.`

## R²

`R² = coeficiente de determinacion`

No mide perfeccion absoluta. Mide cuanto mejora el modelo respecto a un baseline que siempre predice el promedio de `mpg`.

Interpretacion correcta:

`El modelo explica cierta proporcion de la variacion de mpg frente a predecir siempre la media.`

Ideas importantes:

- un `R²` alto no prueba causalidad
- un `R²` bajo no significa automaticamente que no haya relacion
- un `R²` mayor no siempre justifica un modelo mas complejo

## Como leerlas juntas

Ninguna metrica deberia interpretarse sola.

- usa `MAE` para hablar de error promedio en unidades naturales
- usa `RMSE` para notar si los errores grandes estan afectando bastante
- usa `R²` para comparar contra el baseline

Una lectura tipica seria:

- si `MAE` es bajo, el modelo suele equivocarse poco
- si `RMSE` es mucho mayor que `MAE`, probablemente hay errores grandes u outliers
- si `R²` mejora poco al hacer el modelo mas complejo, quizas no vale la pena complicarlo

## Que esperamos en este taller

Cuando ajustemos el primer modelo con `horsepower`, la interpretacion ideal no sera solo reportar numeros. La meta sera responder cosas como:

- cuanto se equivoca el modelo al predecir `mpg`
- si la relacion lineal captura bien la tendencia general
- si queda evidencia de curvatura en los residuos
- si un polinomio de grado 2 o 3 mejora de verdad en test
