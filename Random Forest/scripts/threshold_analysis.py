import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv')
output_path = os.path.join(script_dir, '..', 'documentation', 'threshold_comparison.html')

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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Entrenamiento de modelos
print("Entrenando modelos...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)

nb = GaussianNB()
nb.fit(X_train, y_train)

# Generar datos para el gráfico
thresholds = np.linspace(0.01, 0.99, 100)
models = {
    'Random Forest': rf.predict_proba(X_test)[:, 1],
    'KNN': knn.predict_proba(X_test_scaled)[:, 1],
    'Naive Bayes': nb.predict_proba(X_test)[:, 1]
}

# Crear la figura Plotly
fig = go.Figure()

# Colores sugeridos por modelo
colors = {
    'Random Forest': '#1f77b4', # Azul
    'KNN': '#2ca02c',           # Verde
    'Naive Bayes': '#ff7f0e'    # Naranja
}

for model_name, probs in models.items():
    acc_list = []
    rec_list = []
    pre_list = []
    f1_list = []
    
    for t in thresholds:
        preds = (probs >= t).astype(int)
        acc_list.append(accuracy_score(y_test, preds))
        rec_list.append(recall_score(y_test, preds, zero_division=0))
        pre_list.append(precision_score(y_test, preds, zero_division=0))
        f1_list.append(f1_score(y_test, preds, zero_division=0))
    
    # Añadir trazas
    base_style = dict(line=dict(width=2), x=thresholds)
    
    # Accuracy (Sólida)
    fig.add_trace(go.Scatter(
        y=acc_list, name=f'{model_name} (Accuracy)',
        visible=True, line=dict(color=colors[model_name], width=3), x=thresholds
    ))
    
    # Recall (Guiones)
    fig.add_trace(go.Scatter(
        y=rec_list, name=f'{model_name} (Recall)',
        visible='legendonly', line=dict(color=colors[model_name], dash='dash'), x=thresholds
    ))
    
    # Precision (Puntos)
    fig.add_trace(go.Scatter(
        y=pre_list, name=f'{model_name} (Precision)',
        visible='legendonly', line=dict(color=colors[model_name], dash='dot'), x=thresholds
    ))
    
    # F1-Score (Guion-Punto)
    fig.add_trace(go.Scatter(
        y=f1_list, name=f'{model_name} (F1-Score)',
        visible='legendonly', line=dict(color=colors[model_name], dash='dashdot'), x=thresholds
    ))

# Configuración del diseño
fig.update_layout(
    title='Curvas de Desempeño Multimétrica por Umbral',
    xaxis_title='Umbral de Clasificación (Threshold)',
    yaxis_title='Puntuación (0 a 1)',
    template='plotly_white',
    hovermode='x unified',
    height=700,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    annotations=[
        dict(
            text="Haz clic en la leyenda para activar/desactivar Recall, Precision y F1",
            xref="paper", yref="paper",
            x=0.5, y=-0.15, showarrow=False,
            font=dict(size=12, color="gray")
        )
    ]
)

# Guardar como HTML
fig.write_html(output_path)
print(f"Visualización multivariante guardada en: {output_path}")
