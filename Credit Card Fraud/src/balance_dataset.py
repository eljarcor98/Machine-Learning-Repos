import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.over_sampling import SMOTE
from collections import Counter
import os

# --- 1. Cargar el dataset ---
# Ruta obtenida del paso anterior
dataset_path = r"C:\Users\Arnold's\.cache\kagglehub\datasets\mlg-ulb\creditcardfraud\versions\3\creditcard.csv"

print("Cargando dataset...")
df = pd.read_csv(dataset_path)

# --- 2. Preparar los datos ---
X = df.drop('Class', axis=1)
y = df['Class']

# --- 3. Aplicar SMOTE ---
print("Aplicando SMOTE para balancear las clases...")
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

print(f"Distribución original: {Counter(y)}")
print(f"Distribución después de SMOTE: {Counter(y_res)}")

# --- 4. Comparación y Visualización ---
# Configuración estética similar a lo solicitado: moderna y clara
sns.set_theme(style="whitegrid", palette="muted")
plt.figure(figsize=(14, 6))

# Subplot 1: Distribución Original
plt.subplot(1, 2, 1)
sns.countplot(x=y)
plt.title('Distribución Original de Clases\n(Altamente Desbalanceado)', fontsize=14, fontweight='bold')
plt.xlabel('Clase (0: Normal, 1: Fraude)')
plt.ylabel('Cantidad de Transacciones')

# Subplot 2: Distribución con SMOTE
plt.subplot(1, 2, 2)
sns.countplot(x=y_res)
plt.title('Distribución después de SMOTE\n(Balanceado)', fontsize=14, fontweight='bold')
plt.xlabel('Clase (0: Normal, 1: Fraude)')
plt.ylabel('Cantidad de Transacciones')

plt.tight_layout()

# Guardar la visualización
# Subimos un nivel desde 'src/' y luego entramos en 'plots/'
plot_path = os.path.join("..", "plots", "comparacion_balanceo.png")
plt.savefig(plot_path)
print(f"Gráfico guardado en: {plot_path}")

# --- 5. Guardar el nuevo dataset balanceado ---
# Subimos un nivel desde 'src/' y luego entramos en 'data/'
balanced_csv_path = os.path.join("..", "data", "creditcard_balanced.csv")
print("Guardando dataset balanceado (esto puede tardar un poco debido al tamaño)...")
balanced_df = pd.concat([pd.DataFrame(X_res), pd.DataFrame(y_res, columns=['Class'])], axis=1)
balanced_df.to_csv(balanced_csv_path, index=False)
print(f"Dataset balanceado guardado en: {balanced_csv_path}")

plt.show()
