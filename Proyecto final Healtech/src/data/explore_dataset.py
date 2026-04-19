#!/usr/bin/env python3
"""
Script de exploración rápida del dataset CIC-IDS2017
Lee muestras de cada archivo para identificar tipos de ataque disponibles
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

data_raw = Path('data/raw/MachineLearningCVE')
csv_files = sorted([f for f in data_raw.glob('*.csv')])

print("=" * 80)
print("EXPLORACIÓN DEL DATASET CIC-IDS2017")
print("=" * 80)

attack_distribution = defaultdict(lambda: defaultdict(int))

for csv_file in csv_files:
    print(f"\n\n📄 Archivo: {csv_file.name}")
    print("-" * 80)
    
    # Leer solo primeras filas para ver estructura
    try:
        # Leer con bajo memory footprint
        df_sample = pd.read_csv(csv_file, nrows=1000)
        
        print(f"  Total de filas en archivo: {len(pd.read_csv(csv_file, usecols=['Label']))}")
        print(f"  Muestra cargada: {df_sample.shape[0]} filas, {df_sample.shape[1]} columnas")
        
        if 'Label' in df_sample.columns:
            print(f"\n  Tipos de ataque en MUESTRA (primeras 1000 filas):")
            for label, count in df_sample['Label'].value_counts().items():
                print(f"    • {label}: {count} casos")
                attack_distribution[csv_file.name][label] += count
        else:
            print("  ⚠️ No se encontró columna 'Label'")
            
    except Exception as e:
        print(f"  ❌ Error al procesar: {e}")

print("\n\n" + "=" * 80)
print("RESUMEN DE ATAQUES POR ARCHIVO")
print("=" * 80)

for filename in sorted(attack_distribution.keys()):
    print(f"\n{filename}")
    attacks = attack_distribution[filename]
    for attack_type, count in sorted(attacks.items(), key=lambda x: -x[1]):
        print(f"  • {attack_type}: {count}")

print("\n\n" + "=" * 80)
print("IDENTIFICACIÓN DE ATAQUES DE INTERÉS PARA SIR/SEIR")
print("=" * 80)

# Buscar ataques de propagación
propagation_keywords = ['Botnet', 'Infiltration', 'Backdoor']
all_attacks = set()

for filename, attacks in attack_distribution.items():
    for attack_type in attacks.keys():
        all_attacks.add(attack_type)

print("\nAtaques de interés (con potencial de propagación):")
for attack in sorted(all_attacks):
    if any(kw.lower() in attack.lower() for kw in propagation_keywords):
        print(f"  ✓ {attack}")

print("\nOtros ataques disponibles:")
for attack in sorted(all_attacks):
    if not any(kw.lower() in attack.lower() for kw in propagation_keywords):
        print(f"  - {attack}")
