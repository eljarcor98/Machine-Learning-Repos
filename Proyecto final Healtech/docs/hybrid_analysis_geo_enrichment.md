# Enriquecimiento geografico desde Hybrid Analysis

## Fuente

El archivo HTML guardado en `data/external/` contiene la seccion `Contacted Hosts (324)` del analisis de Hybrid Analysis para `mssecsvc.exe`.

## Campos extraidos

- IP contactada.
- Puerto y protocolo.
- Proceso asociado y PID.
- Pais reportado por Hybrid Analysis.
- ASN y organizacion cuando aparecen en la tabla.

## Coordenadas

La tabla no incluye latitud y longitud exactas por IP. Para construir un grafo geografico reproducible, se asignan coordenadas aproximadas usando el centroide del pais reportado.

Esto permite visualizar distribucion global y rutas agregadas, pero no debe interpretarse como ubicacion exacta del host. Las entradas marcadas como `Reserved` se mantienen sin coordenadas.

## Archivos generados

- `data/processed/hybrid_analysis_contacted_hosts_geo.csv`: hosts contactados con pais, ASN y coordenadas.
- `data/processed/hybrid_analysis_contacted_countries.csv`: conteo agregado por pais.
- `data/processed/hybrid_analysis_contacted_hosts_geo.graphml`: grafo dirigido desde `mssecsvc.exe:3192` hacia las IPs contactadas.
- `data/processed/hybrid_analysis_contacted_hosts_summary.json`: resumen del enriquecimiento.
- `reports/figures/hybrid_analysis_contacted_hosts_geo.png`: visualizacion geografica agregada.
- `data/processed/wannacry_realistic_geo_host_graph.graphml`: grafo geografico a nivel host con dispersion visual deterministica.
- `data/processed/wannacry_realistic_geo_country_graph.graphml`: grafo geografico agregado por pais con pesos por cantidad de hosts.
- `reports/figures/wannacry_realistic_geo_graph.png`: visualizacion final del grafo geografico realista.

## Comando

```powershell
.\.venv\Scripts\python.exe src\data\parse_hybrid_analysis_hosts.py
.\.venv\Scripts\python.exe src\graph\build_wannacry_geo_graph.py
```
