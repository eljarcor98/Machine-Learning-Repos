import pandas as pd
import os
from datetime import timedelta

# Configuración de rutas
root_dir = r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\K-Means"
file_path = os.path.join(root_dir, "Online Retail.xlsx")
output_file = os.path.join(root_dir, "online_retail_rfm.csv")

def prepare_rfm():
    print("Cargando el dataset original...")
    df = pd.read_excel(file_path)

    print("Limpiando datos...")
    # 1. Eliminar registros sin CustomerID
    df = df.dropna(subset=['CustomerID'])
    
    # 2. Filtrar devoluciones y precios erróneos
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    
    # 3. Calcular el precio total por línea
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # 4. Asegurar formato de fecha
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    print("Calculando métricas RFM...")
    # Definimos la "fecha actual" como el día después del último registro para calcular la Recencia
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)

    # Agrupamos por cliente para calcular R, F y M
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days, # Recency
        'InvoiceNo': 'nunique',                                  # Frequency
        'TotalPrice': 'sum'                                      # Monetary
    })

    # Renombramos las columnas
    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalPrice': 'Monetary'
    }, inplace=True)

    print(f"Dataset RFM creado con {rfm.shape[0]} clientes únicos.")
    
    # Guardar el nuevo dataset
    rfm.to_csv(output_file)
    print(f"Nuevo dataset guardado en: {output_file}")
    
    # Mostrar las primeras filas
    print("\nPrimeras filas del dataset RFM:")
    print(rfm.head())

if __name__ == "__main__":
    prepare_rfm()
