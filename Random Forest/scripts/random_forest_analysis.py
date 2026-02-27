import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de diseño
sns.set(style="whitegrid")

# Cargar el dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv')

if not os.path.exists(data_path):
    print(f"Error: No se encontró el archivo {data_path}")
else:
    df = pd.read_csv(data_path)
    
    print("--- Primeras 5 filas del dataset ---")
    print(df.head())
    
    print("\n--- Información del dataset ---")
    print(df.info())
    
    print("\n--- Valores nulos ---")
    print(df.isnull().sum())
    
    # Preprocesamiento básico (ejemplo interactivo)
    # Llenar valores nulos en 'bmi'
    df['bmi'] = df['bmi'].fillna(df['bmi'].mean())
    
    # Codificación de variables categóricas (ejemplo simple)
    df_encoded = pd.get_dummies(df, columns=['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status'], drop_first=True)
    
    # Definir X e y
    X = df_encoded.drop(['id', 'stroke'], axis=1)
    y = df_encoded['stroke']
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Inicializar y entrenar Random Forest
    print("\nEntrenando modelo Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Predicciones
    y_pred = rf_model.predict(X_test)
    
    # Evaluación
    print("\n--- Reporte de Clasificación ---")
    print(classification_report(y_test, y_pred))
    print(f"Precisión (Accuracy): {accuracy_score(y_test, y_pred):.4f}")
    
    # Importancia de características
    feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\n--- Importancia de Características (Top 10) ---")
    print(feature_importances.head(10))
