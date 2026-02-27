import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv')
images_dir = os.path.join(script_dir, '..', 'images')
os.makedirs(images_dir, exist_ok=True)

# Cargar el dataset
if not os.path.exists(data_path):
    print(f"Error: No se encontró el archivo {data_path}")
    exit()

df = pd.read_csv(data_path)

# Preprocesamiento
df['bmi'] = df['bmi'].fillna(df['bmi'].mean())
df_encoded = pd.get_dummies(df.drop(['id'], axis=1), columns=['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status'], drop_first=True)

X = df_encoded.drop(['stroke'], axis=1)
y = df_encoded['stroke']

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Escalar datos (necesario para KNN y KMeans)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

def save_confusion_matrix(y_true, y_pred, model_name, filename):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f'Matriz de Confusión - {model_name}')
    plt.xlabel('Predicción')
    plt.ylabel('Real')
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, filename))
    plt.close()

# 1. Random Forest
print("\n--- Evaluando Random Forest ---")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print(classification_report(y_test, y_pred_rf))
save_confusion_matrix(y_test, y_pred_rf, 'Random Forest', 'cm_random_forest.png')

# 2. KNN
print("\n--- Evaluando KNN (k=5) ---")
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)
y_pred_knn = knn.predict(X_test_scaled)
print(classification_report(y_test, y_pred_knn))
save_confusion_matrix(y_test, y_pred_knn, 'KNN', 'cm_knn.png')

# 3. Naive Bayes
print("\n--- Evaluando Naive Bayes ---")
nb = GaussianNB()
nb.fit(X_train, y_train)
y_pred_nb = nb.predict(X_test)
print(classification_report(y_test, y_pred_nb))
save_confusion_matrix(y_test, y_pred_nb, 'Naive Bayes', 'cm_naive_bayes.png')

# 4. K-Means (Clustering as Classification)
print("\n--- Evaluando K-Means (2 clusters) ---")
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans.fit(X_train_scaled)
y_pred_kmeans = kmeans.predict(X_test_scaled)

# Mapear clusters a la clase mayoritaria para comparar
# Esto es una simplificación para "evaluar" clustering como si fuera clasificación
labels = np.zeros_like(y_pred_kmeans)
for i in range(2):
    mask = (y_pred_kmeans == i)
    if mask.any():
        labels[mask] = np.bincount(y_test[mask]).argmax()

print(classification_report(y_test, labels))
save_confusion_matrix(y_test, labels, 'K-Means (Mapeado)', 'cm_kmeans.png')

print(f"\nProceso completado. Imágenes guardadas en: {images_dir}")
