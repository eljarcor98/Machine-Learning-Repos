import nbformat as nbf
import os

nb_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Himalayan_Expeditions\Logistic_Regression_Himalayan.ipynb"
nb = nbf.v4.new_notebook()

cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""# Regresión Logística: Predicción de Cumbre (Success)

Este cuaderno implementa un modelo de Regresión Logística para predecir si un escalador alcanzará la cumbre en las expediciones del Himalaya.

**Objetivo:** Predecir `success` (1 o 0) y evaluar el desempeño del modelo."""))

# Imports
cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve, PrecisionRecallDisplay

# Configuración estética
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)"""))

# Data Loading
cells.append(nbf.v4.new_code_cell("""url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-09-22/members.csv"
df = pd.read_csv(url)
print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas.")"""))

# Preprocessing
cells.append(nbf.v4.new_markdown_cell("""### Preprocesamiento de Datos
- Imputación de edad.
- Selección de características relevantes.
- Codificación de variables categóricas."""))

cells.append(nbf.v4.new_code_cell("""# Imputar edad
df['age'] = df['age'].fillna(df['age'].median())

# Selección de variables
features = ['age', 'sex', 'year', 'season', 'hired', 'solo', 'oxygen_used']
X = df[features]
y = df['success'].astype(int)

# Definir transformaciones
categorical_features = ['sex', 'season']
numerical_features = ['age', 'year', 'hired', 'solo', 'oxygen_used']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features)
    ])"""))

# Model Training
cells.append(nbf.v4.new_markdown_cell("""### Entrenamiento del Modelo"""))
cells.append(nbf.v4.new_code_cell("""# División Entrenamiento/Prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Entrenar modelo con pipeline implícito (transformación + estimador)
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_transformed, y_train)

print("Modelo entrenado con éxito.")"""))

# Evaluation
cells.append(nbf.v4.new_markdown_cell("""### Evaluación de Desempeño"""))
cells.append(nbf.v4.new_code_cell("""y_pred = model.predict(X_test_transformed)
y_prob = model.predict_proba(X_test_transformed)[:, 1]

print("--- Métricas de Desempeño ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")
print("\\nReporte de Clasificación:")
print(classification_report(y_test, y_pred))"""))

# Visualizations
cells.append(nbf.v4.new_code_cell("""# Matriz de Confusión
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['No Éxito', 'Éxito'], yticklabels=['No Éxito', 'Éxito'])
plt.title('Matriz de Confusión')
plt.xlabel('Predicho')
plt.ylabel('Real')
plt.show()"""))

cells.append(nbf.v4.new_code_cell("""# Curva ROC
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
plt.plot(fpr, tpr, label=f'LogReg (AUC = {roc_auc_score(y_test, y_prob):.4f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('Tasa de Falsos Positivos')
plt.ylabel('Tasa de Verdaderos Positivos')
plt.title('Curva ROC')
plt.legend()
plt.show()"""))

# Coefficients
cells.append(nbf.v4.new_markdown_cell("""### Importancia de las Características (Coeficientes)"""))
cells.append(nbf.v4.new_code_cell("""cat_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
all_names = numerical_features + list(cat_names)

coef_df = pd.DataFrame({'Variable': all_names, 'Coeficiente': model.coef_[0]}).sort_values(by='Coeficiente', ascending=False)

sns.barplot(data=coef_df, x='Coeficiente', y='Variable', palette='coolwarm')
plt.title('Influencia de las Variables en el Éxito')
plt.show()"""))

nb['cells'] = cells
with open(nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at {nb_path}")
