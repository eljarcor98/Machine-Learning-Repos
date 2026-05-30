# Vision General del Proyecto

## Nombre

Taller de regresion lineal con Auto MPG

## Contexto academico

Este proyecto sigue la guia del curso de Machine Learning I para la sesion de regresion lineal. Aunque la guia general menciona tambien regresion logistica, en este repositorio el enfoque actual se concentrara solo en la parte de regresion lineal.

## Problema del taller

Predecir el consumo de combustible de un vehiculo, medido en `mpg` (millas por galon), a partir de caracteristicas del automovil. La pregunta central propuesta por la guia es:

`Como cambia el consumo de combustible cuando cambia la potencia del motor?`

## Dataset seleccionado

- Dataset: Auto MPG
- Fuente: UCI Machine Learning Repository, distribuido tambien a traves de Kaggle
- Tipo de problema: regresion supervisada
- Variable objetivo: `mpg`

## Variables de interes para esta sesion

Segun la guia, las variables mas utiles para la sesion son:

- `horsepower`
- `weight`
- `acceleration`
- `model year`

La variable principal para el primer modelo sera `horsepower`, porque permite construir una relacion simple, interpretable y visualmente clara con `mpg`.

## Objetivo academico

Completar y documentar un flujo basico de regresion lineal que permita:

- explorar visualmente la relacion entre las variables y `mpg`
- limpiar datos faltantes en `horsepower`
- ajustar un modelo lineal simple
- interpretar residuos y metricas
- comparar, si aplica, con ajustes polinomiales de mayor complejidad

## Preguntas a responder

- La relacion entre `horsepower` y `mpg` parece lineal o curvada
- Cuanto error comete un modelo lineal al predecir `mpg`
- Que nos dicen `MAE`, `MSE`, `RMSE` y `R²`
- Cuando una mejora de ajuste representa una mejora real y no sobreajuste
- Que variables parecen asociarse mas fuertemente con `mpg`

## Estado actual

Hasta este punto ya se hizo lo siguiente:

- descarga y ubicacion del dataset en `data/raw/auto-mpg.csv`
- revision inicial de columnas y tipos de datos
- identificacion de valores faltantes en `horsepower`
- generacion de graficas exploratorias en `reports/figures/`

## Entregables esperados

- notebook de exploracion y modelado
- graficas de dispersion, distribucion y correlacion
- interpretacion escrita de resultados
- informe final del taller
- bitacora de decisiones y experimentos
