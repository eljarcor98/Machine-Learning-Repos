import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuración de rutas
root_dir = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means"
rfm_clusters_path = os.path.join(root_dir, "online_retail_rfm_clusters.csv")
original_data_path = os.path.join(root_dir, "Online Retail.xlsx")
output_html = os.path.join(root_dir, "docs", "REPORTE_FINAL_CRISP_DM.html")

def generate_report():
    print("Iniciando generación de reporte interactivo...")
    
    # Cargar datos
    rfm = pd.read_csv(rfm_clusters_path)
    # Mapeo de nombres de segmentos
    segment_map = {
        1: "Campeones (VIP)",
        2: "En Riesgo",
        0: "Nuevos / Potenciales",
        3: "Perdidos / Inactivos"
    }
    rfm['Segmento'] = rfm['Cluster'].map(segment_map)
    
    # --- 1. Gráfico: Distribución de Ingresos por Segmento ---
    revenue_summary = rfm.groupby('Segmento')['Monetary'].sum().reset_index()
    fig_revenue = px.pie(revenue_summary, values='Monetary', names='Segmento', 
                         title='<b>Distribución de Ingresos Totales por Segmento</b>',
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_revenue.update_traces(textposition='inside', textinfo='percent+label')

    # --- 2. Gráfico: Cantidad de Clientes por Segmento ---
    count_summary = rfm['Segmento'].value_counts().reset_index()
    count_summary.columns = ['Segmento', 'Clientes']
    fig_count = px.bar(count_summary, x='Segmento', y='Clientes', 
                       title='<b>Número de Clientes por Segmento</b>',
                       color='Segmento', color_discrete_sequence=px.colors.qualitative.Safe)

    # --- 3. Gráfico: PCA Clustering (Visualización de Grupos) ---
    fig_pca = px.scatter(rfm, x='PCA1', y='PCA2', color='Segmento',
                         title='<b>Mapa de Segmentación (PCA 2D)</b>',
                         labels={'PCA1': 'Componente 1', 'PCA2': 'Componente 2'},
                         hover_data=['Recency', 'Frequency', 'Monetary'],
                         opacity=0.6)

    # --- 4. Gráfico: Perfil RFM (Snake Plot) ---
    # Normalizamos para comparar en la misma escala
    metrics = ['Recency', 'Frequency', 'Monetary']
    rfm_norm = rfm.copy()
    for col in metrics:
        rfm_norm[col] = (rfm_norm[col] - rfm_norm[col].mean()) / rfm_norm[col].std()
    
    snake_df = rfm_norm.groupby('Segmento')[metrics].mean().reset_index()
    snake_melted = pd.melt(snake_df, id_vars='Segmento', var_name='Métrica', value_name='Valor')
    
    fig_snake = px.line(snake_melted, x='Métrica', y='Valor', color='Segmento', markers=True,
                        title='<b>Perfil de Comportamiento (Centroides Normalizados)</b>')

    # --- Construcción del HTML Final ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte Gerencial CRISP-DM - Online Retail</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 40px 0; margin-bottom: 30px; border-bottom: 5px solid #ffcc00; }}
            .card {{ border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px; border-radius: 15px; }}
            .card-header {{ background-color: white; border-bottom: 2px solid #f1f1f1; font-weight: bold; color: #1e3c72; font-size: 1.2rem; border-radius: 15px 15px 0 0 !important; }}
            .step-title {{ color: #2a5298; border-left: 5px solid #ffcc00; padding-left: 15px; margin-top: 40px; margin-bottom: 20px; }}
            .highlight {{ color: #d9534f; font-weight: bold; }}
            .footer {{ background-color: #343a40; color: white; padding: 20px 0; margin-top: 50px; }}
        </style>
    </head>
    <body>
        <div class="header text-center">
            <h1>Reporte Gerencial de Segmentación de Clientes</h1>
            <p class="lead">Metodología CRISP-DM | Proyecto: Online Retail K-Means</p>
        </div>

        <div class="container">
            <div class="row">
                <div class="col-12">
                    <h2 class="step-title">1. Comprensión del Negocio (Business Understanding)</h2>
                    <div class="card p-4">
                        <p>El objetivo principal es identificar grupos de clientes con comportamientos similares para optimizar las campañas de marketing y aumentar la retención. Se busca responder: <b>¿Quiénes son nuestros mejores clientes y quiénes están a punto de irse?</b></p>
                        <ul>
                            <li><b>KPI Clave:</b> Valor del Cliente (Monetary), Lealtad (Frequency) y Novedad (Recency).</li>
                            <li><b>Reto:</b> Manejar un alto volumen de transacciones de usuarios invitados (~25%).</li>
                        </ul>
                    </div>
                </div>

                <div class="col-12">
                    <h2 class="step-title">2. Comprensión y Preparación de Datos</h2>
                    <div class="card p-4">
                        <div class="row">
                            <div class="col-md-6">
                                <p>Se analizaron <b>541,909 registros</b> correspondientes al periodo 2010-2011.</p>
                                <p><b>Acciones realizadas:</b></p>
                                <ul>
                                    <li>Tratamiento de valores negativos (devoluciones).</li>
                                    <li>Asignación de "Guests" para análisis de volumen, pero filtrados para el clúster individualizado.</li>
                                    <li>Transformación Logarítmica para corregir el sesgo en gastos extremos.</li>
                                </ul>
                            </div>
                            <div class="col-md-6 text-center">
                                <span class="badge bg-primary fs-5 p-3 m-2">4,070 Productos Únicos</span>
                                <span class="badge bg-success fs-5 p-3 m-2">38 Países</span>
                                <span class="badge bg-danger fs-5 p-3 m-2">91% Ventas en UK</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <h2 class="step-title">3. Modelado y Resultados Operativos</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Impacto Financiero por Segmento</div>
                                <div class="card-body">
                                    {fig_revenue.to_html(full_html=False, include_plotlyjs='cdn')}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Volumen de Clientes</div>
                                <div class="card-body">
                                    {fig_count.to_html(full_html=False, include_plotlyjs=False)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="card">
                        <div class="card-header">Análisis de Clústeres (PCA)</div>
                        <div class="card-body">
                            {fig_pca.to_html(full_html=False, include_plotlyjs=False)}
                            <p class="mt-3 text-muted">Este mapa muestra cómo el algoritmo separó a los clientes. Cada punto es un cliente único.</p>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <h2 class="step-title">4. Hallazgos Relevantes y Evaluación</h2>
                    <div class="row">
                        <div class="col-md-7">
                            <div class="card">
                                <div class="card-header">ADN de los Segmentos (Snake Plot)</div>
                                <div class="card-body">
                                    {fig_snake.to_html(full_html=False, include_plotlyjs=False)}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-5">
                            <div class="card p-4">
                                <h4 class="text-primary">Hallazgos Críticos:</h4>
                                <p><span class="highlight">La Regla de Pareto:</span> El 16% de los clientes (Campeones) genera el <b>65% de los ingresos</b>.</p>
                                <p><span class="highlight">Oportunidad de Oro:</span> El segmento "En Riesgo" representa <b>£1.8 Millones</b> en ingresos que se están enfriando (>70 días de inactividad).</p>
                                <p><span class="highlight">Crecimiento:</span> El 32% de los clientes son "Nuevos", lo que indica una buena captación pero baja retención inmediata.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <h2 class="step-title">5. Plan de Acción (Estrategia Gerencial)</h2>
                    <div class="card p-4 bg-light border-primary">
                        <div class="row">
                            <div class="col-md-3 text-center border-end">
                                <h5 class="text-success">CAMPEONES</h5>
                                <p class="small">Ventas exclusivas, acceso anticipado y programas VIP.</p>
                            </div>
                            <div class="col-md-3 text-center border-end">
                                <h5 class="text-primary">NUEVOS</h5>
                                <p class="small">Descuento de segunda compra y encuestas de satisfacción.</p>
                            </div>
                            <div class="col-md-3 text-center border-end">
                                <h5 class="text-danger">EN RIESGO</h5>
                                <p class="small">Cupones de reactivación "Te extrañamos" con fecha de caducidad.</p>
                            </div>
                            <div class="col-md-3 text-center">
                                <h5 class="text-secondary">PERDIDOS</h5>
                                <p class="small">Campañas de limpieza de base de datos o correos masivos de bajo coste.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer text-center">
            <p>&copy; 2026 - Proyecto K-Means Online Retail | Preparado para la Gerencia de Marketing</p>
        </footer>
    </body>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Reporte final generado con éxito en: {output_html}")

if __name__ == "__main__":
    generate_report()
