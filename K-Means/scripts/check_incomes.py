import pandas as pd
import os

# Usamos rutas absolutas para evitar confusiones de directorio
file_path = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means\online_retail_rfm_clusters.csv"

if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo en {file_path}")
else:
    rfm = pd.read_csv(file_path)
    
    # Agregación por Cluster
    summary = rfm.groupby('Cluster')['Monetary'].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
    
    # Calcular el porcentaje del ingreso total
    total_income = summary['sum'].sum()
    summary['percentage_of_total_income'] = (summary['sum'] / total_income) * 100
    
    # Formatear números para lectura humana
    pd.options.display.float_format = '{:,.2f}'.format
    
    print("\n### Análisis de Ingresos por Clúster ###\n")
    print(summary.to_markdown())
    
    # Mapeo de nombres (basado en el análisis previo)
    nombres = {
        1: "Campeones (VIP)",
        0: "Nuevos / Potenciales",
        2: "Leales en Riesgo",
        3: "Perdidos / Inactivos"
    }
    
    print("\n\n### Resumen Ejecutivo ###")
    for cluster, row in summary.iterrows():
        nombre = nombres.get(cluster, f"Cluster {cluster}")
        print(f"- **{nombre}**: Genera **£{row['sum']:,.2f}** ({row['percentage_of_total_income']:.1f}% del total).")
