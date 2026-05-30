# Diccionario de Datos

## Dataset

- Nombre: Auto MPG
- Fuente: UCI Machine Learning Repository / Kaggle
- Ruta: `data/raw/auto-mpg.csv`
- Filas originales: 398
- Filas usables tras limpieza inicial: 392
- Descripcion: dataset de vehiculos usado para estudiar relaciones entre caracteristicas del automovil y consumo de combustible.

## Variable objetivo

- `mpg`: millas por galon. Es la variable continua que queremos predecir mediante regresion lineal.

## Variables del dataset

| Variable | Tipo original | Tipo de trabajo | Descripcion | Observaciones |
|---|---|---|---|---|
| mpg | float | numerica continua | Consumo de combustible en millas por galon | Variable objetivo |
| cylinders | int | numerica discreta | Numero de cilindros del motor | Asociada negativamente con `mpg` |
| displacement | float | numerica continua | Desplazamiento del motor | Relacion negativa con `mpg` |
| horsepower | object | numerica continua | Potencia del motor | Tiene valores faltantes codificados como `?` |
| weight | int | numerica continua | Peso del vehiculo | Una de las variables mas asociadas con `mpg` |
| acceleration | float | numerica continua | Aceleracion del vehiculo | Relacion positiva moderada con `mpg` |
| model year | int | numerica discreta | Ano del modelo del vehiculo | Los modelos mas recientes tienden a tener mejor `mpg` |
| origin | int | categorica codificada | Origen del vehiculo | 1, 2 y 3 representan regiones distintas |
| car name | object | texto | Nombre del vehiculo | No se usara inicialmente para el modelo |

## Calidad de datos

- Valores faltantes: `horsepower` tiene 6 valores faltantes codificados como `?`
- Duplicados exactos: 0
- Variables categoricas o de identificacion: `origin`, `car name`
- Variables numericas: `mpg`, `cylinders`, `displacement`, `horsepower`, `weight`, `acceleration`, `model year`

## Transformaciones realizadas

- conversion de `horsepower` de texto a numerico usando coercion
- reemplazo implicito de `?` por valores nulos
- eliminacion de filas con nulos en las variables clave del analisis

## Correlaciones iniciales con `mpg`

Estas correlaciones no prueban causalidad, pero sirven para orientar la exploracion:

| Variable | Correlacion con mpg |
|---|---|
| weight | -0.832 |
| displacement | -0.805 |
| horsepower | -0.778 |
| cylinders | -0.778 |
| acceleration | 0.423 |
| origin | 0.565 |
| model year | 0.581 |
