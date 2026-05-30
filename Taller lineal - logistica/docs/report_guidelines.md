# Guia de Documentacion

Para que la documentacion del taller sea clara y consistente, conviene escribir siempre con esta secuencia.

## 1. Planteamiento del problema

- Que se quiere predecir
- Por que el problema es de regresion y no de clasificacion
- Cual es la pregunta central del ejercicio

Ejemplo para este taller:

`Se busca predecir el consumo de combustible medido en mpg a partir de caracteristicas del vehiculo, en especial la potencia del motor.`

## 2. Descripcion del dataset

- Fuente del dataset
- Numero de observaciones
- Variable objetivo
- Variables candidatas para el analisis
- Problemas de calidad encontrados

## 3. Hipotesis inicial

Antes de correr modelos, deja por escrito la expectativa conceptual.

Ejemplo:

- a mayor `horsepower`, menor `mpg`
- a mayor `weight`, menor `mpg`
- vehiculos de anos mas recientes pueden tener mejor eficiencia

## 4. Limpieza y preparacion

Documenta con precision:

- que columnas se transformaron
- que faltantes se encontraron
- cuantas filas se eliminaron o imputaron
- que variables se dejaron por fuera y por que

## 5. Analisis exploratorio

Incluye las visualizaciones mas importantes y explica que muestran.

- dispersion `horsepower` vs `mpg`
- dispersion `weight` vs `mpg`
- distribucion de `mpg`
- mapa de correlaciones

No basta con insertar la figura. Debes decir que patron se observa y por que importa para el modelo.

## 6. Modelado

Cuando empecemos a ajustar el modelo, la documentacion debe incluir:

- tipo de modelo
- variable o variables predictoras
- division entre entrenamiento y prueba
- supuestos o limitaciones observadas

## 7. Metricas

Las metricas deben reportarse con interpretacion, no solo como numeros.

- `MAE`: error absoluto promedio en unidades de `mpg`
- `MSE`: error cuadratico promedio, util para castigar errores grandes
- `RMSE`: raiz del error cuadratico medio, interpretable en unidades de `mpg`
- `R²`: proporcion de variacion explicada respecto a predecir siempre la media

## 8. Conclusiones

Al cerrar una seccion o el informe final, responde:

- que relacion principal se encontro
- que tan bien se comporto el modelo
- que limitaciones tiene
- si un modelo mas complejo realmente aporta

## 9. Criterio de escritura

- escribir en lenguaje claro
- conectar cada grafica con una idea
- evitar decir que una correlacion prueba causalidad
- preferir interpretaciones defendibles antes que afirmaciones exageradas
