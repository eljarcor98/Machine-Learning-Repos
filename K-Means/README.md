# Proyecto de Segmentación de Clientes: Online Retail (K-Means)

Este repositorio contiene un análisis detallado y modelos de segmentación para un dataset de ventas minoristas en línea. El objetivo es identificar perfiles de clientes y comportamientos de compra utilizando técnicas de aprendizaje no supervisado.

## Estructura del Proyecto

```text
K-Means/
├── docs/               # Documentación y reportes generales
│   ├── eda/           # Gráficos y visualizaciones generadas
│   ├── EDA_ONLINE_RETAIL.md  # Análisis Exploratorio de Datos detallado
│   ├── ANALISIS_ONLINE_RETAIL.md # Resumen estadístico inicial
│   ├── REPORTE_CLUSTERING_RFM.md # Resultados técnicos del modelo K-Means
│   └── REPORTE_FINAL_CRISP_DM.html # 🏆 REPORTAJE FINAL INTERACTIVO (CRISP-DM)
├── scripts/            # Código fuente en Python
│   ├── analisis_online_retail.py # EDA
│   ├── kmeans_productos_compradores.py # Primer intento
│   ├── prepare_rfm_data.py       # Preparación RFM
│   ├── advanced_rfm_kmeans.py    # K-Means Avanzado + PCA
│   └── generate_final_report.py  # Generador de Reporte HTML
├── README.md           # Descripción general del proyecto (este archivo)
├── Online Retail.xlsx  # Dataset original (Excel)
└── online_retail_rfm.csv # Dataset procesado listo para Advanced K-Means
```

## Requisitos

Para ejecutar los scripts, asegúrate de tener instaladas las siguientes librerías:

```bash
pip install pandas openpyxl matplotlib seaborn tabulate scikit-learn
```

## Módulos Principales

### 1. Análisis Exploratorio de Datos (EDA)
Ubicado en `scripts/analisis_online_retail.py`, este módulo realiza:
- Carga y limpieza inicial de datos.
- Cálculo de variables derivadas (`TotalPrice`, `Hour`).
- Identificación de outliers (Valores atípicos).
- Análisis de frecuencia de compra (incluyendo usuarios invitados).
- Generación de reportes automáticos en formato Markdown con visualizaciones.

### 2. Preparación RFM
Ubicado en `scripts/prepare_rfm_data.py`:
- Transforma los datos transaccionales en una matriz de clientes con métricas de Recencia, Frecuencia y Valor Monetario.

## Hallazgos del EDA
- **Mercado:** Masivamente concentrado en el Reino Unido (91%).
- **Calidad de Datos:** ~25% de los registros no tienen `CustomerID`, lo que requiere estrategias específicas para Clustering.
- **Análisis RFM Avanzado:** Se implementó normalización logarítmica y escalado. El Método del Codo confirmó que **K=4** es el número ideal de segmentos.
- **Segmentación RFM:**
    1. **Campeones (Clúster 1):** Alta frecuencia, altísimo gasto, recencia mínima.
    2. **Nuevos (Clúster 0):** Recencia baja, frecuencia en desarrollo.
    3. **En Riesgo (Clúster 2):** Clientes que gastaban bien pero no han vuelto en >70 días.
    4. **Perdidos (Clúster 3):** Inactivos por más de 180 días.

## Estado del Proyecto
- [x] Estructuración de carpetas (`docs/`, `scripts/`).
- [x] Análisis Exploratorio de Datos (EDA) completo.
- [x] Visualizaciones clave generadas.
- [x] Primer intento de K-Means (K=4).
- [x] Generación de Dataset RFM (`online_retail_rfm.csv`).
- [x] Refinamiento del modelo (Método del Codo, PCA, Snake Plot).
- [x] Reporte Gerencial Interactivo CRISP-DM (HTML).
- [x] Estrategia de negocio por segmentos definida.

## Próximos Pasos (Implementación)
1. Integrar las etiquetas en el CRM de la empresa.
2. Ejecutar campañas de email marketing personalizadas para el grupo "En Riesgo".
