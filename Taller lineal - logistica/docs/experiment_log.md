# Bitacora de Experimentos

Este documento registra decisiones, hallazgos y pruebas del taller.

## Experimento 1

- Fecha: 2026-04-08
- Objetivo: revisar el dataset Auto MPG y validar si es adecuado para la parte de regresion lineal del taller.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: todas las columnas para inspeccion inicial
- Modelo: ninguno, fase exploratoria
- Configuracion: lectura directa con `pandas`
- Metricas: no aplica
- Resultado: el dataset es adecuado para regresion lineal; `mpg` puede usarse como target continuo.
- Observaciones: `horsepower` viene como texto y contiene valores faltantes representados con `?`.

---

## Experimento 2

- Fecha: 2026-04-08
- Objetivo: realizar limpieza minima para explorar relaciones entre variables y `mpg`.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `mpg`, `horsepower`, `weight`, `acceleration`, `model year`, `displacement`, `cylinders`, `origin`
- Modelo: ninguno, fase exploratoria
- Configuracion: conversion de `horsepower` a numerico y eliminacion de filas faltantes
- Metricas: correlaciones exploratorias
- Resultado: quedaron 392 registros limpios a partir de 398 filas originales.
- Observaciones: se eliminaron 6 filas con valores faltantes en `horsepower`; no se encontraron duplicados exactos.

---

## Experimento 3

- Fecha: 2026-04-08
- Objetivo: visualizar la relacion entre `mpg` y variables relevantes para el taller.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `horsepower`, `weight`, `acceleration`, `origin`, `mpg`
- Modelo: ninguno, analisis exploratorio visual
- Configuracion: graficas de dispersion con linea de tendencia, histogramas, mapa de correlacion y boxplot por origen
- Metricas: correlaciones simples con `mpg`
- Resultado: se generaron 7 figuras en `reports/figures/`.
- Observaciones: `weight` y `horsepower` muestran relacion negativa fuerte con `mpg`; `acceleration` muestra relacion positiva mas moderada.

---

## Siguiente experimento sugerido

- Fecha: pendiente
- Objetivo: ajustar una regresion lineal simple con `horsepower` como predictor de `mpg`.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `horsepower`, `mpg`
- Modelo: regresion lineal simple
- Configuracion: division train/test y evaluacion con `MAE`, `MSE`, `RMSE` y `R²`
- Metricas: pendiente, intercepto, `MAE`, `MSE`, `RMSE`, `R²`
- Resultado: pendiente
- Observaciones: pendiente

---

## Experimento 4

- Fecha: 2026-04-08
- Objetivo: ajustar y evaluar una regresion lineal simple usando `horsepower` para predecir `mpg`.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `horsepower`, `mpg`
- Modelo: regresion lineal simple
- Configuracion: `train_test_split(test_size=0.2, random_state=42)`
- Metricas: `MAE`, `MSE`, `RMSE`, `R²`, pendiente e intercepto
- Resultado: el modelo obtuvo en test `MAE = 3.7825`, `RMSE = 4.7067` y `R² = 0.5660`
- Observaciones: la pendiente fue negativa (`-0.1626`), coherente con la hipotesis de que mayor potencia se asocia con menor rendimiento en `mpg`

---

## Experimento 5

- Fecha: 2026-04-10
- Objetivo: comparar una regresion lineal multivariable con ajustes polinomiales de varios grados para predecir `mpg`.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `horsepower, weight, acceleration, model year`, `mpg`
- Modelo: `LinearRegression` con `PolynomialFeatures`
- Configuracion: `train_test_split(test_size=0.2, random_state=42)` y grados `1, 2, 3, 5`
- Metricas: `MAE`, `RMSE`, `R²` y proporcion de predicciones dentro de umbrales de error absoluto
- Resultado: el mejor grado por `RMSE` en test fue `grado 3` con `RMSE = 2.3348` y `R² = 0.8932`
- Observaciones: se generaron graficas para comparar train/test, visualizar umbrales de error y analizar como cambia la prediccion por variable al aumentar el grado
