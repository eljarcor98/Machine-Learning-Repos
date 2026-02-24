import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuración de rutas para que funcione desde cualquier lugar
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, '..', 'dataset', 'iris.csv')
output_dir = current_dir

# Cargar datos
print(f"Cargando datos desde: {dataset_path}")
try:
    df = pd.read_csv(dataset_path)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en {dataset_path}")
    exit()

# 1. Pairplot (Relaciones entre todas las variables)
print("Generando Pairplot (Relaciones entre variables)...")
sns.pairplot(df, hue='species', palette='husl', markers=["o", "s", "D"])
plt.suptitle('Relaciones entre variables del Iris dataset', y=1.02)
plt.savefig(os.path.join(output_dir, '1_pairplot_iris.png'))
print("Guardado: 1_pairplot_iris.png")

# 2. Boxplot (Distribución de Pétalos por Especie)
print("Generando Boxplots (Análisis de Pétalos)...")
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.boxplot(x='species', y='petal_length', data=df, palette='Set2')
plt.title('Longitud del Pétalo por Especie')

plt.subplot(1, 2, 2)
sns.boxplot(x='species', y='petal_width', data=df, palette='Set2')
plt.title('Ancho del Pétalo por Especie')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '2_boxplot_petalos.png'))
print("Guardado: 2_boxplot_petalos.png")

# 3. Heatmap de Correlación
print("Generando Heatmap (Correlación de características)...")
plt.figure(figsize=(8, 6))
# Excluimos la columna categórica 'species' para el cálculo de correlación
correlation_matrix = df.drop('species', axis=1).corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f")
plt.title('Matriz de Correlación de Características')
plt.savefig(os.path.join(output_dir, '3_correlacion_heatmap.png'))
print("Guardado: 3_correlacion_heatmap.png")

# 4. Distribución de Sépalos
print("Generando Gráfico de Dispersión de Sépalos...")
plt.figure(figsize=(8, 6))
sns.scatterplot(x='sepal_length', y='sepal_width', hue='species', data=df, palette='viridis', s=100)
plt.title('Dispersión de Sépalos (Largo vs Ancho)')
plt.savefig(os.path.join(output_dir, '4_dispersion_sepalos.png'))
print("Guardado: 4_dispersion_sepalos.png")

print(f"\n✅ Proceso completado exitosamente.")
print(f"Las gráficas han sido guardadas en: {output_dir}")
print("Puedes ejecutar este script para ver las gráficas interactivas si tienes el entorno configurado.")
