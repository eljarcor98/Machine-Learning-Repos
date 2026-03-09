# Premier League Project

Este proyecto está dedicado al análisis de la Premier League utilizando técnicas de Machine Learning.

## Estructura del Proyecto

- `data/`: Contiene los conjuntos de datos originales (`raw`) y procesados (`processed`).
- `notebooks/`: Cuadernos de Jupyter para análisis exploratorio y prototipado.
- `src/`: Código fuente del proyecto.
- `models/`: Modelos entrenados y serializados.
- `reports/`: Informes generados, gráficos y resultados finales.

## Recursos Identificados

- **Fuentes de Datos**: [Football-Data.co.uk](https://www.football-data.co.uk/englandm.php) (Histórico CSV), [API-Football](https://www.api-football.com/).
- **Librerías Recomendadas**: `soccerdata`, `mplsoccer`, `pandas`, `scikit-learn`.
- **Guía de Dominio**: Consulta [football_guide.md](./football_guide.md) para entender los términos y métricas.

## Uso de la API (Opcional)

Si prefieres obtener datos en tiempo real en lugar de usar los CSV, te recomiendo **Football-Data.org**.

1.  **Obtener API Key**: Regístrate gratis en [Football-Data.org](https://www.football-data.org/client/register) para obtener tu token.
2.  **Ejemplo rápido en Python**:
    ```python
    import requests

    uri = 'https://api.football-data.org/v4/competitions/PL/matches'
    headers = { 'X-Auth-Token': 'TU_API_KEY' }

    response = requests.get(uri, headers=headers)
    data = response.json()
    print(data['matches'][0]) # Primer partido de la lista
    ```

3.  **Script Automatizado**: He creado un script en `src/fetch_api_data.py` que ya tiene tu llave configurada. Puedes ejecutarlo con:
    ```bash
    python src/fetch_api_data.py
    ```
    Este script guarda los datos automáticamente en `data/raw/api_sample_matches.json`.

## Cómo Empezar

1. Lee la [Guía de Fútbol](./football_guide.md) para familiarizarte con los datos.
2. Instalar las dependencias:
   ```bash
   pip install pandas matplotlib seaborn scikit-learn soccerdata mplsoccer
   ```
3. Explora los datos en `notebooks/`.
