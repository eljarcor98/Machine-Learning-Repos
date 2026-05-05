# Uso del PCAP de WannaCry en la simulacion

## Fuente local

El archivo `data/external/wannaCry_15052017.pcap.gz` contiene un fragmento de trafico asociado a WannaCry. Este insumo permite pasar de una simulacion puramente sintetica a una simulacion informada por trafico observado.

## Que se extrae del PCAP

- IP origen e IP destino.
- Protocolo de red observado.
- Puertos origen y destino.
- Tiempos relativos de captura.
- Cantidad de paquetes y bytes por flujo.
- Indicadores TCP basicos, como SYN, ACK, RST y FIN.

## Relacion con WannaCry

WannaCry se propago explotando SMBv1 mediante EternalBlue. Por eso, el trafico hacia o desde el puerto `445/TCP` se usa como indicador principal de intentos de comunicacion SMB relevantes para el modelo.

## Uso dentro del modelo SIR

El PCAP no se interpreta como una epidemia completa por si solo. Se utiliza para estimar parametros y comportamiento de contacto:

- `S`: equipos susceptibles o vulnerables a SMBv1.
- `I`: equipos infectados o capaces de intentar propagacion.
- `R`: equipos aislados, parchados o contenidos.
- `beta`: probabilidad de transmision calibrada con la intensidad relativa del trafico SMB.
- `gamma`: tasa de aislamiento/parcheo definida por el escenario de contencion.

## Escenarios propuestos

1. Sin contencion: alta probabilidad de transmision y baja recuperacion.
2. Con kill-switch/contencion: reduccion de transmision y aumento de recuperacion desde un paso temporal especifico.
3. Segmentacion de red: eliminacion o debilitamiento de aristas entre subredes.
4. Parcheo preventivo: porcentaje inicial de nodos en estado `R`.

## Entregables derivados

- `data/processed/wannacry_flows.csv`: flujos agregados del PCAP.
- `data/processed/wannacry_pcap_summary.json`: resumen del archivo.
- `data/processed/wannacry_pcap_analysis.json`: metricas usadas para sustentar la simulacion.
- `data/processed/wannacry_pcap_sir_results.csv`: resultados temporales de los escenarios SIR.
- `data/processed/wannacry_pcap_sir_metadata.json`: parametros usados en la simulacion.
- `reports/figures/wannacry_pcap_top_ports.png`: distribucion de puertos.
- `reports/figures/wannacry_pcap_observed_graph.png`: grafo observado de comunicaciones.
- `reports/figures/wannacry_pcap_informed_sir.png`: comparacion SIR con y sin contencion.
