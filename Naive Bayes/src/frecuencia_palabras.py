import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Usar backend no interactivo
from collections import Counter
import re

# Ruta del archivo
file_path = "spam.csv"

def clean_text(text):
    # Convertir a minúsculas y eliminar caracteres no alfabéticos
    text = str(text).lower()
    words = re.findall(r'\b[a-z]{3,}\b', text) # Palabras de al menos 3 letras
    return words

try:
    # Cargar el dataset (reutilizando la lógica de codificación)
    try:
        df = pd.read_csv(file_path, encoding='latin-1')
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df[['v1', 'v2']]
            df.columns = ['Label', 'Message']
    except Exception:
        df = pd.read_csv(file_path, sep='\t', names=['Label', 'Message'], encoding='latin-1')

    # Separar mensajes por clase
    ham_messages = df[df['Label'] == 'ham']['Message']
    spam_messages = df[df['Label'] == 'spam']['Message']

    # Contar palabras para ham
    ham_words = []
    for msg in ham_messages:
        ham_words.extend(clean_text(msg))
    ham_counts = Counter(ham_words)

    # Contar palabras para spam
    spam_words = []
    for msg in spam_messages:
        spam_words.extend(clean_text(msg))
    spam_counts = Counter(spam_words)

    # Obtener las palabras más comunes en total para mostrar en el gráfico
    # Vamos a tomar las 15 palabras más comunes en Spam para que el gráfico sea legible
    top_n = 15
    common_spam = spam_counts.most_common(top_n)
    palabras = [item[0] for item in common_spam]
    
    # Obtener frecuencias para esas palabras en ambas categorías
    freq_spam = [spam_counts[w] for w in palabras]
    freq_ham = [ham_counts[w] for w in palabras]

    # Crear un DataFrame para ordenar fácilmente de menor a mayor
    plot_df = pd.DataFrame({
        'Palabra': palabras,
        'Spam': freq_spam,
        'Ham': freq_ham
    })
    
    # Ordenar por frecuencia de Spam (o total) de menor a mayor
    plot_df['Total'] = plot_df['Spam'] + plot_df['Ham']
    plot_df = plot_df.sort_values(by='Total', ascending=True)

    # --- Configuración del Gráfico ---
    plt.figure(figsize=(12, 8))
    
    y = range(len(plot_df))
    height = 0.4
    
    # Barras horizontales para mejor lectura de palabras
    plt.barh([i - height/2 for i in y], plot_df['Ham'], height=height, label='Ham (No Spam)', color='#4CAF50', alpha=0.8)
    plt.barh([i + height/2 for i in y], plot_df['Spam'], height=height, label='Spam', color='#F44336', alpha=0.8)
    
    plt.yticks(y, plot_df['Palabra'])
    plt.title(f'Top {top_n} Palabras más frecuentes en Spam vs Ham (Ordenadas de menor a mayor)', fontsize=15)
    plt.xlabel('Frecuencia (Cantidad de apariciones)', fontsize=12)
    plt.ylabel('Palabras', fontsize=12)
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    
    plt.tight_layout()

    # Guardar la imagen
    output_image = "graphs/frecuencia_palabras.png"
    plt.savefig(output_image)
    print(f"\n[INFO] Gráfico de frecuencia de palabras guardado en: {output_image}")
    
    # Mostrar resultados en consola
    print("\n### Top Palabras más frecuentes (Ordenadas para el gráfico):")
    print(plot_df[['Palabra', 'Ham', 'Spam', 'Total']].to_string(index=False))

except Exception as e:
    print(f"Error: {e}")
