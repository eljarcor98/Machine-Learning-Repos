# Estudio del Dataset IRIS

Este proyecto contiene scripts para el análisis estadístico del dataset IRIS, enfocándose en medidas de tendencia central y de dispersión.

## Contenido

- `medidas_dispersion.py`: Script principal que carga el dataset y muestra tablas comparativas de estadísticas descriptivas.

## Funcionalidades del Script

El script `medidas_dispersion.py` calcula y muestra las siguientes medidas para las características numéricas del dataset (longitud y ancho de sépalos y pétalos):

### Medidas de Tendencia Central
- **Media**: El promedio aritmético de los valores.
- **Mediana**: El valor central de los datos ordenados.
- **Moda**: El valor que ocurre con mayor frecuencia.

### Medidas de Dispersión
- **Rango**: La diferencia entre el valor máximo y el mínimo.
- **Varianza**: Qué tan dispersos están los datos respecto a la media.
- **Desviación Estándar**: La raíz cuadrada de la varianza, en las mismas unidades que los datos.
- **IQR (Rango Intercuartílico)**: La diferencia entre el tercer y el primer cuartil, mostrando la dispersión del 50% central de los datos.

## Requisitos

- Python 3.x
- Pandas

## Uso

Para ejecutar el análisis, navega hasta la carpeta y ejecuta:

```bash
python medidas_dispersion.py
```

El script buscará automáticamente el archivo `iris.csv` en la carpeta `../KNN/dataset/`.
