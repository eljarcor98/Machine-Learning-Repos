import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv')
output_path = os.path.join(script_dir, '..', 'documentation', 'interactive_matrices.html')

# Cargar el dataset
if not os.path.exists(data_path):
    print(f"Error: No se encontró el archivo {data_path}")
    exit()

df = pd.read_csv(data_path)
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

# Modelos y sus probabilidades
model_probs = {
    'Random Forest': rf.predict_proba(X_test)[:, 1],
    'KNN': knn.predict_proba(X_test_scaled)[:, 1],
    'Naive Bayes': nb.predict_proba(X_test)[:, 1]
}

thresholds = np.round(np.linspace(0.01, 0.99, 50), 2)
n_models = len(model_probs)
total_test = len(y_test)

# Crear subplots (1 fila, 3 columnas)
fig = make_subplots(
    rows=1, cols=n_models,
    subplot_titles=list(model_probs.keys()),
    horizontal_spacing=0.1
)

# Paleta de colores para las matrices
colorscale = 'Blues'

def get_full_data(probs, threshold, y_true):
    preds = (probs >= threshold).astype(int)
    cm = confusion_matrix(y_true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    # Cálculos con números (fórmulas dinámicas)
    acc_calc = f"({tp} + {tn}) / {total_test}"
    rec_calc = f"{tp} / ({tp} + {fn})" if (tp + fn) > 0 else "0/0"
    pre_calc = f"{tp} / ({tp} + {fp})" if (tp + fp) > 0 else "0/0"
    
    acc = (tp + tn) / total_test
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    pre = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * (pre * rec) / (pre + rec) if (pre + rec) > 0 else 0
    
    text = (f"<b>Accuracy</b>: {acc:.3f}<br><span style='font-size:10px'>{acc_calc}</span><br>"
            f"<b>Recall</b>: {rec:.3f}<br><span style='font-size:10px'>{rec_calc}</span><br>"
            f"<b>F1-Score</b>: {f1:.3f}")
    return cm, text

# Preparar pasos para el slider
steps = []
for t in thresholds:
    # Restyle para las trazas (Heatmaps)
    restyle_dict = {'z': [], 'text': []}
    new_annotations = []
    
    best_model_name = ""
    max_recall = -1
    
    for i, (model_name, probs) in enumerate(model_probs.items()):
        cm, metrics_text = get_full_data(probs, t, y_test)
        restyle_dict['z'].append(cm)
        restyle_dict['text'].append([[str(x) for x in row] for row in cm])
        
        # Guardar para comparar mejor modelo
        preds = (probs >= t).astype(int)
        rec = recall_score(y_test, preds, zero_division=0)
        if rec > max_recall:
            max_recall = rec
            best_model_name = model_name
        elif rec == max_recall and rec > 0:
            # En caso de empate en recall, buscamos mejor F1/Precision (opcional, simplificamos)
            best_model_name += " y " + model_name

        x_pos = (i / n_models) + (1 / (2 * n_models))
        new_annotations.append(dict(
            text=f"<b>{model_name}</b><br>{metrics_text}",
            x=x_pos, y=1.2, xref="paper", yref="paper", showarrow=False, align="center",
            font=dict(size=11)
        ))
    
    # Añadir recomendación clínica al pie
    rec_text = f"🩺 <b>Recomendación Clínica (Umbral {t}):</b> "
    if max_recall > 0.9:
        rec_text += f"El modelo <b>{best_model_name}</b> es excelente detectando casos (Recall {max_recall:.2f})."
    elif max_recall > 0.5:
        rec_text += f"<b>{best_model_name}</b> detecta algunos casos, pero el riesgo de omitir enfermos es alto."
    else:
        rec_text += "A este umbral, <b>ningún modelo es seguro</b> para detectar la enfermedad."

    new_annotations.append(dict(
        text=rec_text,
        x=0.5, y=-0.25, xref="paper", yref="paper", showarrow=False, align="center",
        font=dict(size=13, color="DarkSlateGray"),
        bgcolor="rgba(240, 240, 240, 0.8)", bordercolor="gray", borderwidth=1, borderpad=10
    ))

    step = {
        "method": "update",
        "label": str(t),
        "args": [
            restyle_dict,
            {"annotations": new_annotations, "title.text": f"Análisis Dinámico de Resultados - Umbral: {t}"}
        ]
    }
    steps.append(step)

# Inicializar gráfico
initial_idx = int(len(thresholds) / 2)
initial_t = thresholds[initial_idx]
for j, (model_name, probs) in enumerate(model_probs.items()):
    cm, _ = get_full_data(probs, initial_t, y_test)
    fig.add_trace(
        go.Heatmap(
            z=cm, x=['Pred: Sano', 'Pred: Stroke'], y=['Real: Sano', 'Real: Stroke'],
            text=[[str(x) for x in row] for row in cm], texttemplate="%{text}",
            colorscale=colorscale, showscale=False, zmin=0, zmax=total_test
        ),
        row=1, col=j+1
    )

# Configuración Layout
fig.update_layout(
    height=850, # Aumentado para el footer
    margin=dict(t=180, b=150, l=80, r=80),
    template='plotly_white',
    sliders=[{
        "active": initial_idx, "currentvalue": {"prefix": "Umbral Seleccionado: "},
        "pad": {"t": 90}, "steps": steps
    }]
)

# Forzar la primera actualización de anotaciones
fig.layout.annotations = []
best_model_name_init = ""
max_recall_init = -1

for i, (model_name, probs) in enumerate(model_probs.items()):
    cm, metrics_text = get_full_data(probs, initial_t, y_test)
    
    preds = (probs >= initial_t).astype(int)
    rec = recall_score(y_test, preds, zero_division=0)
    if rec > max_recall_init:
        max_recall_init = rec
        best_model_name_init = model_name
    elif rec == max_recall_init and rec > 0:
        best_model_name_init += " y " + model_name

    x_pos = (i / n_models) + (1 / (2 * n_models))
    fig.add_annotation(
        text=f"<b>{model_name}</b><br>{metrics_text}",
        x=x_pos, y=1.2, xref="paper", yref="paper", showarrow=False, align="center",
        font=dict(size=11)
    )

# Recomendación inicial
rec_text_init = f"🩺 <b>Recomendación Clínica (Umbral {initial_t}):</b> "
if max_recall_init > 0.9:
    rec_text_init += f"El modelo <b>{best_model_name_init}</b> es excelente detectando casos (Recall {max_recall_init:.2f})."
elif max_recall_init > 0.5:
    rec_text_init += f"<b>{best_model_name_init}</b> detecta algunos casos, pero el riesgo de omitir enfermos es alto."
else:
    rec_text_init += "A este umbral, <b>ningún modelo es seguro</b> para detectar la enfermedad."

fig.add_annotation(
    text=rec_text_init,
    x=0.5, y=-0.25, xref="paper", yref="paper", showarrow=False, align="center",
    font=dict(size=13, color="DarkSlateGray"),
    bgcolor="rgba(240, 240, 240, 0.8)", bordercolor="gray", borderwidth=1, borderpad=10
)

fig.update_xaxes(side="bottom")
fig.update_yaxes(autorange="reversed")

# Guardar
fig.write_html(output_path)
print(f"Tablero corregido guardado en: {output_path}")
