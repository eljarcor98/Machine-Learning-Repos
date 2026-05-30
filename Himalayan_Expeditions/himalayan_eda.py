import pandas as pd

# 1. URL del dataset
url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-09-22/members.csv"

# 2. Cargar en DataFrame 'df'
print(f"Descargando y cargando datos desde {url}...\n")
df = pd.read_csv(url)

# 3. Mostrar métricas iniciales
print("--- df.shape ---")
print(df.shape)

print("\n--- df.dtypes ---")
print(df.dtypes)

print("\n--- df.head() ---")
# Usamos head(3) para que no sea demasiado largo en la consola, o el default head()
print(df.head())

print("\n--- df['success'].value_counts(normalize=True) ---")
print(df['success'].value_counts(normalize=True))

# 4. Reportar NaN por columna
print("\n--- NaN por columna (orden descendente) ---")
print(df.isna().sum().sort_values(ascending=False))
