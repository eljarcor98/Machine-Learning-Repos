#!/usr/bin/env python3
"""
EDA Script - Análisis rápido de Payload_data_CICIDS2017.csv
Ejecutar desde línea de comandos si el notebook no funciona
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def main():
    print("\n" + "="*90)
    print("EDA - Exploratory Data Analysis")
    print("Archivo: Payload_data_CICIDS2017.csv")
    print("="*90)
    
    payload_file = Path('data/raw/Payload_data_CICIDS2017.csv')
    
    if not payload_file.exists():
        print(f"❌ Archivo no encontrado: {payload_file}")
        return
    
    print(f"\n📂 Leyendo archivo ({payload_file.stat().st_size / (1024**3):.2f} GB)...")
    
    try:
        df = pd.read_csv(payload_file, low_memory=False)
    except Exception as e:
        print(f"❌ Error al leer CSV: {e}")
        return
    
    print(f"✓ {len(df):,} filas, {df.shape[1]} columnas cargadas\n")
    
    # 1. COLUMNAS
    print("="*90)
    print("1. COLUMNAS DISPONIBLES")
    print("="*90)
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        print(f"{i:2}. {col:35} | tipo: {dtype:10}")
    
    # 2. SEARCH FOR KEY COLUMNS
    print("\n" + "="*90)
    print("2. BÚSQUEDA DE COLUMNAS CLAVE")
    print("="*90)
    
    # IPs
    ip_cols = [col for col in df.columns 
               if any(x in col.lower() for x in ['ip', 'source', 'destination', 'host', 'addr'])]
    if ip_cols:
        print(f"🌐 Columnas de IP encontradas: {ip_cols}")
        print(f"   Primeros valores:")
        for col in ip_cols[:2]:
            print(f"   - {col}: {df[col].unique()[:3]}")
    else:
        print(f"🌐 Columnas de IP: NINGUNA")
    
    # Puertos
    port_cols = [col for col in df.columns if 'port' in col.lower()]
    if port_cols:
        print(f"\n🔌 Columnas de Puerto: {port_cols}")
    else:
        print(f"\n🔌 Columnas de Puerto: NINGUNA")
    
    # Labels
    label_cols = [col for col in df.columns 
                  if any(x in col.lower() for x in ['label', 'class', 'attack', 'attack_type'])]
    if label_cols:
        label_col = label_cols[0]
        print(f"\n🏷️ Columna de Etiqueta: {label_col}")
        print(f"   Tipos de ataque:")
        for attack_type, count in df[label_col].value_counts().head(10).items():
            pct = (count / len(df)) * 100
            print(f"     • {attack_type:25} : {count:10,} ({pct:5.2f}%)")
    else:
        print(f"\n🏷️ Columnas de Etiqueta: NINGUNA")
    
    # 3. DATA QUALITY
    print("\n" + "="*90)
    print("3. CALIDAD DE DATOS")
    print("="*90)
    
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    
    print(f"Valores faltantes: {missing:,} ({(missing/(len(df)*df.shape[1])*100):.3f}%)")
    print(f"Filas duplicadas: {duplicates:,} ({(duplicates/len(df)*100):.3f}%)")
    print(f"Memoria: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
    
    # 4. NUMERIC STATS
    print("\n" + "="*90)
    print("4. ESTADÍSTICAS DE VARIABLES NUMÉRICAS")
    print("="*90)
    
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) > 0:
        print("\nPrimeras variables numéricas (8):")
        print(numeric_df.iloc[:, :8].describe().to_string())
    
    # 5. CORRELATIONS
    print("\n" + "="*90)
    print("5. CORRELACIONES ALTAS (>0.9)")
    print("="*90)
    
    if numeric_df.shape[1] > 1:
        corr_matrix = numeric_df.corr()
        high_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.9:
                    high_corr.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_matrix.iloc[i, j]
                    ))
        
        if high_corr:
            for col1, col2, corr in sorted(high_corr, key=lambda x: abs(x[2]), reverse=True)[:10]:
                print(f"  {col1:30} <-> {col2:30} = {corr:.4f}")
        else:
            print("  Ninguna correlación >0.9 encontrada")
    else:
        print("  Insuficientes variables numéricas")
    
    # 6. SUMMARY
    print("\n" + "="*90)
    print("6. RESUMEN & RECOMENDACIONES")
    print("="*90)
    
    if ip_cols:
        print("✓ El CSV TIENE columnas de IP - Se puede construir grafo real")
        print("  Columnas: " + ", ".join(ip_cols))
    else:
        print("⚠️ El CSV NO tiene IPs - Se usará clustering de comportamiento")
    
    if label_cols:
        print(f"✓ El CSV tiene etiquetas de ataque")
    else:
        print(f"⚠️ El CSV NO tiene etiquetas de ataque")
    
    if numeric_df.shape[1] > 50:
        print(f"✓ {numeric_df.shape[1]} features numéricas - Buen dataset")
    elif numeric_df.shape[1] > 10:
        print(f"⚠️ {numeric_df.shape[1]} features numéricas - Moderado")
    else:
        print(f"⚠️ {numeric_df.shape[1]} features numéricas - Pocas para modelado")
    
    print("\n" + "="*90)
    print("EDA COMPLETADO")
    print("="*90)
    
    # Save summary
    with open('data/processed/eda_summary.txt', 'w') as f:
        f.write("EDA SUMMARY - Payload_data_CICIDS2017.csv\n")
        f.write("="*90 + "\n\n")
        f.write(f"Filas: {len(df):,}\n")
        f.write(f"Columnas: {df.shape[1]}\n")
        f.write(f"IP Columns: {ip_cols}\n")
        f.write(f"Label Columns: {label_cols}\n")
        f.write(f"Numeric Columns: {numeric_df.shape[1]}\n")
        f.write(f"Missing Values: {missing:,}\n")
        f.write(f"Duplicates: {duplicates:,}\n")
    
    print("✓ Resumen guardado en: data/processed/eda_summary.txt\n")

if __name__ == '__main__':
    main()
