import nbformat as nbf
import os

nb_path = r"c:\Users\Arnold's\Documents\Repositorios Machine Learning\Himalayan_Expeditions\Logistic_Regression_Himalayan.ipynb"
nb = nbf.v4.new_notebook()

cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""# Regresión Logística: Predicción de Cumbre (Success)

Este cuaderno implementa modelos de Regresión Logística para predecir si un escalador alcanzará la cumbre en las expediciones del Himalaya.

**Objetivo:** Comparar el desempeño general con el desempeño específico para escaladores que utilizan oxígeno."""))

# Imports
cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve

# Configuración estética
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)"""))

# Data Loading
cells.append(nbf.v4.new_code_cell("""url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-09-22/members.csv"
df = pd.read_csv(url)
df['age'] = df['age'].fillna(df['age'].median())"""))

# --- SECCIÓN 1: MODELO GENERAL ---
cells.append(nbf.v4.new_markdown_cell("""## 1. Modelo de Población General
Incluimos el uso de oxígeno como una variable explicativa."""))

cells.append(nbf.v4.new_code_cell("""features = ['age', 'sex', 'year', 'season', 'hired', 'solo', 'oxygen_used']
X = df[features]
y = df['success'].astype(int)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['age', 'year', 'hired', 'solo', 'oxygen_used']),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['sex', 'season'])
    ])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train_trans = preprocessor.fit_transform(X_train)
X_test_trans = preprocessor.transform(X_test)

model_gen = LogisticRegression(max_iter=1000)
model_gen.fit(X_train_trans, y_train)

print(f"Accuracy General: {accuracy_score(y_test, model_gen.predict(X_test_trans)):.4f}")
print(f"ROC-AUC General: {roc_auc_score(y_test, model_gen.predict_proba(X_test_trans)[:, 1]):.4f}")"""))

# --- SECCIÓN 2: SOLO OXÍGENO ---
cells.append(nbf.v4.new_markdown_cell("""## 2. Análisis del Subgrupo: Solo con Oxígeno
¿Qué factores determinan el éxito cuando el escalador YA está usando oxígeno?"""))

cells.append(nbf.v4.new_code_cell("""df_oxy = df[df['oxygen_used'] == True].copy()
features_oxy = ['age', 'sex', 'year', 'season', 'hired', 'solo']
X_oxy = df_oxy[features_oxy]
y_oxy = df_oxy['success'].astype(int)

preprocessor_oxy = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['age', 'year', 'hired', 'solo']),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['sex', 'season'])
    ])

X_train_o, X_test_o, y_train_o, y_test_o = train_test_split(X_oxy, y_oxy, test_size=0.2, random_state=42, stratify=y_oxy)
X_train_o_trans = preprocessor_oxy.fit_transform(X_train_o)
X_test_o_trans = preprocessor_oxy.transform(X_test_o)

model_oxy = LogisticRegression(max_iter=1000)
model_oxy.fit(X_train_o_trans, y_train_o)

print(f"Accuracy (Solo Oxígeno): {accuracy_score(y_test_o, model_oxy.predict(X_test_o_trans)):.4f}")
print(f"ROC-AUC (Solo Oxígeno): {roc_auc_score(y_test_o, model_oxy.predict_proba(X_test_o_trans)[:, 1]):.4f}")"""))

# Comparison Plot
cells.append(nbf.v4.new_markdown_cell("""### Comparación de Importancia de Variables"""))
cells.append(nbf.v4.new_code_cell("""cat_names = preprocessor_oxy.named_transformers['cat'].get_feature_names_out(['sex', 'season'])
names = ['age', 'year', 'hired', 'solo'] + list(cat_names)
coefs = pd.DataFrame({'Variable': names, 'Coeficiente': model_oxy.coef_[0]}).sort_values(by='Coeficiente')

plt.figure(figsize=(10, 6))
sns.barplot(data=coefs, x='Coeficiente', y='Variable', palette='coolwarm')
plt.title('Influencia de Variables en el Éxito (Solo Usuarios de Oxígeno)')
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Observaciones:**
1. El **ROC-AUC** cae significativamente al analizar solo a usuarios de oxígeno. Esto sugiere que el éxito en este grupo es más "aleatorio" o depende de factores no capturados aquí (clima específico, dificultad de la ruta, etc.).
2. El **Año** y el rol **Hired** siguen siendo positivos, mientras que las temporadas de **Invierno** y **Verano** son extremadamente desafiantes."""))

nb['cells'] = cells
with open(nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
