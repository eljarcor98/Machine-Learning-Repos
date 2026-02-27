import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv')

if not os.path.exists(data_path):
    print(f"Error: No se encontró el archivo {data_path}")
    exit()

df = pd.read_csv(data_path)

print("--- Resumen General ---")
print(f"Total de registros: {len(df)}")
print(f"Columnas: {list(df.columns)}")

print("\n--- Distribución de Clase (Target) ---")
stroke_counts = df['stroke'].value_counts()
stroke_pct = df['stroke'].value_counts(normalize=True) * 100
for val, count in stroke_counts.items():
    label = "Sano" if val == 0 else "Stroke"
    print(f"{label}: {count} ({stroke_pct[val]:.2f}%)")

print("\n--- Variables Categóricas ---")
cat_cols = ['gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
for col in cat_cols:
    print(f"\nColumna: {col}")
    counts = df[col].value_counts()
    pcts = df[col].value_counts(normalize=True) * 100
    for val, count in counts.items():
        print(f"  - {val}: {count} ({pcts[val]:.2f}%)")

print("\n--- Variables Numéricas ---")
print(df[['age', 'avg_glucose_level', 'bmi']].describe())

print("\n--- Valores faltantes ---")
print(df.isnull().sum())
