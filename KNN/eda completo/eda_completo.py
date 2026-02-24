import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuración de rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(os.path.dirname(current_dir), 'dataset', 'iris.csv')
images_dir = os.path.join(current_dir, 'images')

# Crear carpeta de imágenes si no existe
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

def cargar_datos():
    if not os.path.exists(dataset_path):
        print(f"Error: No se encontró el archivo en {dataset_path}")
        return None
    return pd.read_csv(dataset_path)

def eda_basico(df):
    print("\n" + "="*50)
    print("      --- EXPLORACIÓN BÁSICA DE DATOS ---")
    print("="*50)
    
    print("\n1. Primeras 5 filas:")
    print(df.head())
    
    print("\n2. Información del Dataset:")
    print(df.info())
    
    print("\n3. Resumen Estadístico:")
    print(df.describe().T)
    
    print("\n4. Conteo de Especies:")
    print(df['species'].value_counts())
    
    print("\n5. Valores Nulos:")
    print(df.isnull().sum())

def visualizaciones(df):
    print("\nGenerando visualizaciones...")
    
    # Configuración de estilo
    sns.set_theme(style="whitegrid")
    
    # 1. Distribución de especies (Univariado)
    plt.figure(figsize=(8, 6))
    sns.countplot(x='species', data=df, palette='viridis')
    plt.title('Distribución de Especies en el Dataset IRIS')
    plt.savefig(os.path.join(images_dir, 'especies_distribucion.png'))
    plt.show()

    # 2. Histogramas de todas las variables (Univariado)
    df.drop('species', axis=1).hist(figsize=(12, 10), bins=20, color='skyblue', edgecolor='black')
    plt.suptitle('Histogramas de Características Numéricas')
    plt.savefig(os.path.join(images_dir, 'histogramas_caracteristicas.png'))
    plt.show()

    # 3. Boxplots por especie (Bivariado)
    plt.figure(figsize=(15, 10))
    features = df.columns[:-1]
    for i, feature in enumerate(features):
        plt.subplot(2, 2, i+1)
        sns.boxplot(x='species', y=feature, data=df, palette='Set2')
        plt.title(f'Distribución de {feature} por Especie')
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'boxplots_especie.png'))
    plt.show()

    # 4. Pairplot (Multivariado)
    g = sns.pairplot(df, hue='species', height=2.5, palette='bright')
    g.fig.suptitle('Pairplot: Relaciones entre todas las características', y=1.02)
    plt.savefig(os.path.join(images_dir, 'pairplot_iris.png'))
    plt.show()

    # 5. Mapa de calor de correlación
    plt.figure(figsize=(10, 8))
    numeric_df = df.select_dtypes(include=['number'])
    correlation_matrix = numeric_df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Mapa de Calor de Correlación')
    plt.savefig(os.path.join(images_dir, 'mapa_calor_correlacion.png'))
    plt.show()

def main():
    df = cargar_datos()
    if df is not None:
        eda_basico(df)
        visualizaciones(df)
        print("\nEDA completo finalizado con éxito.")

if __name__ == "__main__":
    main()
