# Regresion multivariable polinomial

## Configuracion

- Dataset: `data/raw/auto-mpg.csv`
- Variables de entrada: `cylinders, displacement, horsepower, weight, acceleration, model year, origin`
- Variable objetivo: `mpg`
- Division: `train_test_split(test_size=0.2, random_state=42)`
- Grados comparados: `1, 2, 3, 5`

## Lectura principal

- El mejor grado por `RMSE` en `test` fue `grado 2`.
- Su `RMSE` en test fue `2.6752` y su `R²` en test fue `0.8598`.
- La comparacion train/test sigue la recomendacion del PDF para detectar subajuste y sobreajuste.

## Umbrales de error absoluto en test

- grado 1: <= 2 mpg: 54.4%, <= 4 mpg: 79.7%, <= 6 mpg: 92.4%
- grado 2: <= 2 mpg: 63.3%, <= 4 mpg: 83.5%, <= 6 mpg: 96.2%
- grado 3: <= 2 mpg: 46.8%, <= 4 mpg: 72.2%, <= 6 mpg: 88.6%
- grado 5: <= 2 mpg: 17.7%, <= 4 mpg: 34.2%, <= 6 mpg: 48.1%

## Tabla de metricas

| Grado | Train MAE | Train RMSE | Train R² | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 2.5482 | 3.3135 | 0.8260 | 2.4198 | 3.2727 | 0.7902 |
| 2 | 1.8376 | 2.5291 | 0.8986 | 1.9719 | 2.6752 | 0.8598 |
| 3 | 1.3405 | 1.8640 | 0.9449 | 3.0008 | 4.1790 | 0.6578 |
| 5 | 0.0000 | 0.0000 | 1.0000 | 15.3338 | 34.4324 | -22.2284 |
