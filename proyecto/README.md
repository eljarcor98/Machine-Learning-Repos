# Proyecto de Análisis de Terremotos (USGS)

Este proyecto tiene como objetivo analizar los datos sísmicos obtenidos de la USGS para un área geográfica específica (Colombia y alrededores).

## Estructura del Proyecto

- `data/`: Contiene los archivos de datos crudos y procesados.
- `documentacion/`: Archivos Markdown con la descripción detallada del proyecto y análisis. Incluye el mapa interactivo `mapa_sismos.html` y el `registro_cambios.md`.
- `reporte_final/`: Informe consolidado siguiendo la metodología CRISP-DM.
- `scripts/`: Scripts de Python para la descarga, limpieza y análisis de datos.
- `.venv/`: Entorno virtual de Python.

## Progresos

### [2026-02-24] - Inicialización
- Se creó la estructura básica del proyecto.
- Se configuró el entorno virtual.
- Se creó el script `scripts/load_data.py` para automatizar la descarga de datos desde la API de USGS.
- Se creó la carpeta `documentacion/` con el diccionario de datos y el análisis inicial.
- Se implementó un **mapa interactivo animado** (`scripts/create_map.py`) que muestra la evolución de los sismos en una línea de tiempo.
- Configuración inicial de la URL de consulta con filtros de tiempo (2010-2026), área geográfica y magnitud mínima (1.5).

## Cómo empezar

1. Activa el entorno virtual:
   ```powershell
   .\.venv\Scripts\activate
   ```
2. Instala las dependencias necesarias:
   ```powershell
   pip install pandas
   ```
3. Ejecuta el script de carga de datos:
   ```powershell
   python scripts/load_data.py
   ```
