import pandas as pd
import matplotlib.pyplot as plt
import re

# Ruta del archivo
file_path = "spam.csv"

def get_stats(text):
    # Longitud del mensaje (caracteres)
    length = len(str(text))
    # Cantidad de palabras
    words = len(re.findall(r'\w+', str(text)))
    return length, words

try:
    # Intento de carga robusta (idéntica a los scripts anteriores que funcionan)
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        # El dataset de spam suele tener columnas extra vacías (v3, v4, etc.)
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df[['v1', 'v2']]
            df.columns = ['Label', 'Message']
    except Exception:
        # Intento alternativo con tabulador si falla el anterior
        df = pd.read_csv(file_path, sep='\t', names=['Label', 'Message'], encoding='latin-1')
    
    # Extraer características numéricas
    df['Length'] = df['Message'].apply(lambda x: len(str(x)))
    df['Words'] = df['Message'].apply(lambda x: len(re.findall(r'\w+', str(x))))

    # --- Configuración de Estilo ---
    plt.style.use('ggplot') # Un estilo más limpio que el predeterminado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # 1. Distribución de Longitud de Mensajes (Histogramas)
    ham_lengths = df[df['Label'] == 'ham']['Length']
    spam_lengths = df[df['Label'] == 'spam']['Length']

    ax1.hist(ham_lengths, bins=50, alpha=0.6, label='Ham', color='#4CAF50', density=True)
    ax1.hist(spam_lengths, bins=50, alpha=0.6, label='Spam', color='#F44336', density=True)
    ax1.set_title('Distribución de Longitud de Mensajes', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Número de Caracteres')
    ax1.set_ylabel('Densidad')
    ax1.legend()
    ax1.set_xlim(0, 300) # Limitar para mejor visualización de la mayoría

    # 2. Gráfico de Dispersión: Longitud vs Cantidad de Palabras
    ham_data = df[df['Label'] == 'ham']
    spam_data = df[df['Label'] == 'spam']

    ax2.scatter(ham_data['Length'], ham_data['Words'], alpha=0.3, label='Ham', color='#4CAF50', s=15)
    ax2.scatter(spam_data['Length'], spam_data['Words'], alpha=0.5, label='Spam', color='#F44336', s=15)
    ax2.set_title('Dispersión: Longitud vs Total de Palabras', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Número de Caracteres')
    ax2.set_ylabel('Número de Palabras')
    ax2.legend()
    ax2.set_xlim(0, 400) # Limitar outliers para ver el patrón principal
    ax2.set_ylim(0, 80)

    plt.tight_layout()
    
    # Guardar el gráfico
    output_path = "graphs/distribuciones_y_dispersion.png"
    plt.savefig(output_path, dpi=300)
    print(f"\n[ÉXITO] Los gráficos han sido generados y guardados en:\n{output_path}")

    # Mostrar algunas estadísticas descriptivas
    print("\n### Estadísticas por Clase:")
    print(df.groupby('Label')[['Length', 'Words']].describe().T)

except Exception as e:
    print(f"Error al procesar los datos: {e}")
