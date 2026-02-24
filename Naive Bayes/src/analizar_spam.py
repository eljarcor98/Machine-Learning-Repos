import pandas as pd
import matplotlib.pyplot as plt

# Path to the file
file_path = "spam.csv"

def print_table(df, title):
    print(f"\n### {title}")
    try:
        from tabulate import tabulate
        print(tabulate(df, headers='keys', tablefmt='github', showindex=False))
    except ImportError:
        print(df.to_string(index=False))

try:
    # Most SMS spam datasets are latin-1 and use ',' or '\t'
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df[['v1', 'v2']]
            df.columns = ['Label', 'Message']
    except Exception:
        df = pd.read_csv(file_path, sep='\t', names=['Label', 'Message'], encoding='latin-1')

    # Display results
    print_table(df.head(), "Primeras 5 filas del DataFrame")

    print("\n### Descripción de las Variables")
    print(df.describe(include='all'))

    print("\n### Información General")
    print(f"- **Número de filas:** {df.shape[0]}")
    print(f"- **Número de columnas:** {df.shape[1]}")
    print(f"- **Columnas:** {', '.join(df.columns)}")
    
    if 'Label' in df.columns:
        counts = df['Label'].value_counts()
        print("\n### Distribución de Clases (Label)")
        print(counts)
        
        # --- Gráfico de Barras con Matplotlib puro ---
        plt.figure(figsize=(8, 6))
        
        bars = plt.bar(counts.index, counts.values, color=['#4CAF50', '#F44336'])
        
        plt.title('Frecuencia de Clases (Ham vs Spam)', fontsize=15)
        plt.xlabel('Clase', fontsize=12)
        plt.ylabel('Cantidad', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Añadir etiquetas de conteo sobre las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 5,
                     f'{int(height)}', ha='center', va='bottom', fontsize=11)
        
        # Guardar el gráfico
        plot_path = "graphs/frecuencia_clases.png"
        plt.savefig(plot_path)
        print(f"\n[INFO] Gráfico guardado en: {plot_path}")
        
except Exception as e:
    print(f"Error: {e}")
