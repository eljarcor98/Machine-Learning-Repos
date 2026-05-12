"""
Genera el notebook 06_ml_classifiers_unsw.ipynb con enfoque medico-epidemiologico.
Ejecutar desde la raiz del proyecto: python notebooks/make_notebook_06.py
"""
import json, textwrap
from pathlib import Path

import uuid
def _id(): return str(uuid.uuid4())[:8]
def md(src): return {"cell_type":"markdown","id":_id(),"metadata":{},"source":src.strip().splitlines(True)}
def code(src): return {"cell_type":"code","id":_id(),"execution_count":None,"metadata":{},"outputs":[],"source":textwrap.dedent(src).strip().splitlines(True)}

cells = []

# ── 1. Titulo ─────────────────────────────────────────────────────────────────
cells.append(md("""# 🏥 Clasificadores ML con Enfoque Médico-Epidemiológico
## UNSW-NB15 → WannaCry como pequeña pandemia

**Analogía:**
| Medicina | Ciberseguridad |
|---|---|
| Paciente sano | Flujo normal (`Label=0`) |
| Paciente infectado | Flujo de ataque (`Label=1`) |
| Médico diagnóstico | Clasificador ML |
| Falso Negativo | Ataque no detectado → sigue propagando → **β sube** |
| Falso Positivo | Flujo normal aislado → cuarentena innecesaria |

Los parámetros **β** y **γ** del modelo SIR/SEIR de WannaCry se calibran
directamente con la **sensibilidad** del clasificador.
"""))

# ── 2. Imports ────────────────────────────────────────────────────────────────
cells.append(code("""
import sys, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (confusion_matrix, roc_curve, precision_recall_curve,
                             roc_auc_score, average_precision_score,
                             matthews_corrcoef, f1_score)
import networkx as nx
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path("..").resolve()))
from src.models.classifier import (
    preprocess_unsw, compute_clinical_metrics, get_sir_parameters_from_metrics,
    find_optimal_threshold_youden, metrics_to_dataframe, save_metrics
)
from src.data.unsw_loader import UNSWLoader
from src.simulation.epidemic_models import run_sir_simulation

ROOT = Path("..").resolve()
PROCESSED = ROOT / "data" / "processed"
FIGURES   = ROOT / "reports" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# Parametros WannaCry calibrados desde PCAP real
with open(PROCESSED / "wannacry_pcap_sir_metadata.json") as f:
    meta = json.load(f)
BETA_BASE  = meta["beta_from_pcap"]          # 0.9223
GAMMA_BASE = meta["baseline_gamma"]          # 0.04
R0_BASE    = round(BETA_BASE / GAMMA_BASE, 2)

print(f"β_base  = {BETA_BASE}  (calibrado desde PCAP WannaCry)")
print(f"γ_base  = {GAMMA_BASE}")
print(f"R₀_base = {R0_BASE}  → sin detección, {R0_BASE}x más infecciones por caso")
"""))

# ── 3. Carga de datos ─────────────────────────────────────────────────────────
cells.append(md("## 📦 Carga del Dataset UNSW-NB15 (sample estratificado)"))
cells.append(code("""
loader = UNSWLoader(str(ROOT / "data" / "raw" / "unsw-nb15"))
print("Cargando muestra estratificada (100K por archivo)...")
df_raw = loader.load_consolidated_sample(nrows_per_file=100_000)
print(f"Shape: {df_raw.shape}")
print(f"Distribución Label:\\n{df_raw['Label'].value_counts(normalize=True).round(3)}")
df_raw.head(3)
"""))

# ── 4. Preprocesamiento ───────────────────────────────────────────────────────
cells.append(md("## 🔬 Preprocesamiento"))
cells.append(code("""
X, y = preprocess_unsw(df_raw)
print(f"Features: {X.shape[1]}  |  Muestras: {len(y)}")
print(f"Ataques: {y.sum()} ({y.mean():.1%})  |  Normales: {(1-y).sum()} ({(1-y).mean():.1%})")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)
print(f"Train: {X_train.shape}  |  Test: {X_test.shape}")
"""))

# ── 5. Entrenamiento ──────────────────────────────────────────────────────────
cells.append(md("## 🤖 Entrenamiento de Clasificadores\n\n| Modelo | Analogía médica |\n|---|---|\n| Regresión Logística | Médico generalista: rápido, interpretable |\n| Random Forest | Junta médica: consenso de múltiples especialistas |\n| Gradient Boosting | Especialista que aprende de errores anteriores |\n| Red Neuronal MLP | Diagnóstico por imagen profunda |"))
cells.append(code("""
models = {
    "Regresión Logística": LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=42, C=0.1),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, class_weight="balanced", random_state=42,
        n_jobs=-1, max_depth=15),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42,
        subsample=0.8),
    "MLP": MLPClassifier(
        hidden_layer_sizes=(128, 64, 32), max_iter=200,
        random_state=42, early_stopping=True, validation_fraction=0.1),
}

probs = {}
for name, mdl in models.items():
    use_scaled = name in ("Regresión Logística", "MLP")
    Xtr = X_train_sc if use_scaled else X_train
    Xte = X_test_sc  if use_scaled else X_test
    print(f"Entrenando {name}...", end=" ")
    mdl.fit(Xtr, y_train)
    probs[name] = mdl.predict_proba(Xte)[:, 1]
    print("✓")

print("\\nEntrenamiento completo.")
"""))

# ── 6. Metricas clinicas ──────────────────────────────────────────────────────
cells.append(md("## 🩺 Métricas Clínicas + Parámetros SIR Derivados"))
cells.append(code("""
all_metrics = []
all_sir_params = []

for name, prob in probs.items():
    # Umbral optimo (Youden)
    thr = find_optimal_threshold_youden(y_test.values, prob)
    m   = compute_clinical_metrics(
            y_test.values, prob,
            beta_base=BETA_BASE, gamma_base=GAMMA_BASE,
            threshold=thr, model_name=name)
    sp  = get_sir_parameters_from_metrics(m, BETA_BASE, GAMMA_BASE)
    all_metrics.append(m)
    all_sir_params.append(sp)
    print(f"[{name}]  Sens={m.sensitivity:.3f}  Spec={m.specificity:.3f}  "
          f"F1={m.f1:.3f}  AUC-ROC={m.auc_roc:.3f}  R₀_eff={m.r0_effective:.2f}")

df_metrics = metrics_to_dataframe(all_metrics)
save_metrics(all_metrics, PROCESSED / "ml_clinical_metrics.json")
df_metrics[["Modelo","Sensibilidad","Especificidad","F1-Score","AUC-ROC","AUC-PR",
            "MCC","β efectivo","γ efectivo","R₀ efectivo"]].round(4)
"""))

# ── 7. Visualizaciones ────────────────────────────────────────────────────────
cells.append(md("## 📊 Panel de Visualizaciones Clínicas"))
cells.append(code("""
COLORS = ["#6C5CE7","#00B894","#E17055","#FDCB6E"]
fig = plt.figure(figsize=(20, 18))
fig.patch.set_facecolor("#0D1117")
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

ax_roc = fig.add_subplot(gs[0, 0])
ax_pr  = fig.add_subplot(gs[0, 1])
ax_r0  = fig.add_subplot(gs[0, 2])
ax_cm  = [fig.add_subplot(gs[1, i]) for i in range(len(all_metrics) if len(all_metrics)<=3 else 3)]
ax_sir = fig.add_subplot(gs[2, :])

style = dict(facecolor="#161B22", edgecolor="#30363D")

# --- ROC ---
ax_roc.set_facecolor("#161B22")
ax_roc.set_title("Curvas ROC", color="white", fontsize=12, fontweight="bold")
for (name, prob), col in zip(probs.items(), COLORS):
    fpr, tpr, _ = roc_curve(y_test, prob)
    auc = roc_auc_score(y_test, prob)
    ax_roc.plot(fpr, tpr, color=col, lw=2, label=f"{name} ({auc:.3f})")
ax_roc.plot([0,1],[0,1],"--", color="#636e72", lw=1)
ax_roc.set_xlabel("1 - Especificidad (FPR)", color="#DFE6E9")
ax_roc.set_ylabel("Sensibilidad (TPR)", color="#DFE6E9")
ax_roc.tick_params(colors="#DFE6E9")
ax_roc.legend(fontsize=7, facecolor="#0D1117", labelcolor="white")
ax_roc.spines[:].set_edgecolor("#30363D")

# --- PR ---
ax_pr.set_facecolor("#161B22")
ax_pr.set_title("Curvas Precisión-Recall", color="white", fontsize=12, fontweight="bold")
for (name, prob), col in zip(probs.items(), COLORS):
    prec, rec, _ = precision_recall_curve(y_test, prob)
    ap = average_precision_score(y_test, prob)
    ax_pr.plot(rec, prec, color=col, lw=2, label=f"{name} (AP={ap:.3f})")
ax_pr.set_xlabel("Recall (Sensibilidad)", color="#DFE6E9")
ax_pr.set_ylabel("Precisión (VPP)", color="#DFE6E9")
ax_pr.tick_params(colors="#DFE6E9")
ax_pr.legend(fontsize=7, facecolor="#0D1117", labelcolor="white")
ax_pr.spines[:].set_edgecolor("#30363D")

# --- R0 efectivo por modelo ---
ax_r0.set_facecolor("#161B22")
ax_r0.set_title("R₀ Efectivo por Clasificador", color="white", fontsize=12, fontweight="bold")
nombres = [m.model_name for m in all_metrics]
r0s = [min(m.r0_effective, R0_BASE*1.05) for m in all_metrics]
bar_cols = ["#00B894" if r < 1 else "#E17055" for r in r0s]
bars = ax_r0.barh(nombres, r0s, color=bar_cols, edgecolor="#30363D")
ax_r0.axvline(1.0, color="#FDCB6E", lw=2, ls="--", label="R₀=1 (umbral)")
ax_r0.axvline(R0_BASE, color="#E17055", lw=1.5, ls=":", label=f"R₀_base={R0_BASE}")
for bar, r in zip(bars, r0s):
    ax_r0.text(bar.get_width()+0.2, bar.get_y()+bar.get_height()/2,
               f"{r:.2f}", va="center", color="white", fontsize=9)
ax_r0.set_xlabel("R₀ Efectivo", color="#DFE6E9")
ax_r0.tick_params(colors="#DFE6E9")
ax_r0.legend(fontsize=8, facecolor="#0D1117", labelcolor="white")
ax_r0.spines[:].set_edgecolor("#30363D")

# --- Matrices de Confusion (primeros 3 modelos) ---
for i, (m, ax) in enumerate(zip(all_metrics[:3], ax_cm)):
    ax.set_facecolor("#161B22")
    cm = np.array([[m.TN, m.FP],[m.FN, m.TP]])
    sns.heatmap(cm, annot=True, fmt="d", cmap="RdYlGn",
                xticklabels=["Normal","Ataque"],
                yticklabels=["Normal","Ataque"],
                ax=ax, cbar=False, linewidths=1)
    ax.set_title(f"Confusión: {m.model_name}", color="white", fontsize=9, fontweight="bold")
    ax.set_xlabel("Predicho", color="#DFE6E9"); ax.set_ylabel("Real", color="#DFE6E9")
    ax.tick_params(colors="#DFE6E9")

# --- Curvas SIR comparativas ---
ax_sir.set_facecolor("#161B22")
ax_sir.set_title(
    "Simulación SIR WannaCry: Curvas de Infección según Clasificador\\n"
    "(β y γ calibrados por sensibilidad del modelo — red Barabási-Albert, 300 nodos)",
    color="white", fontsize=12, fontweight="bold")

G = nx.barabasi_albert_graph(300, 3, seed=42)
G = nx.relabel_nodes(G, {n: f"Host_{n:03d}" for n in G.nodes()})
STEPS = 80

for sp, col in zip(all_sir_params, COLORS):
    res = run_sir_simulation(G, beta=sp.beta_effective,
                             gamma=sp.gamma_effective,
                             steps=STEPS,
                             initial_infected=["Host_004"])
    df_sir = res.history
    pct_i  = df_sir["I"] / 300 * 100
    ax_sir.plot(df_sir["step"], pct_i, color=col, lw=2.5,
                label=f"{sp.model_name} (R₀_eff={sp.r0_effective:.2f}, sens={sp.sensitivity_used:.2f})")
    peak = df_sir.loc[df_sir["I"].idxmax()]
    ax_sir.scatter(peak["step"], peak["I"]/300*100, color=col, s=80, zorder=5)

# Sin deteccion (β y γ base)
res_base = run_sir_simulation(G, beta=BETA_BASE, gamma=GAMMA_BASE,
                              steps=STEPS, initial_infected=["Host_004"])
ax_sir.plot(res_base.history["step"],
            res_base.history["I"]/300*100,
            color="#FF6B6B", lw=2, ls="--",
            label=f"Sin detección (R₀_base={R0_BASE})")

ax_sir.set_xlabel("Paso temporal (~ horas de infección activa)", color="#DFE6E9", fontsize=11)
ax_sir.set_ylabel("% Nodos Infectados", color="#DFE6E9", fontsize=11)
ax_sir.tick_params(colors="#DFE6E9")
ax_sir.legend(fontsize=9, facecolor="#0D1117", labelcolor="white")
ax_sir.spines[:].set_edgecolor("#30363D")
ax_sir.grid(alpha=0.15, color="#636e72")

fig.suptitle("🏥 Diagnóstico Epidemiológico — WannaCry como Pandemia de Red",
             color="white", fontsize=16, fontweight="bold", y=1.01)

plt.savefig(FIGURES / "06_ml_clinical_sir_panel.png",
            dpi=150, bbox_inches="tight", facecolor="#0D1117")
plt.show()
print("Figura guardada.")
"""))

# ── 8. Tabla resumen SIR ─────────────────────────────────────────────────────
cells.append(md("## 📋 Interpretación Epidemiológica por Modelo"))
cells.append(code("""
print(f"{'='*80}")
print(f"{'PARÁMETROS SIR/SEIR CALIBRADOS POR CLASIFICADOR':^80}")
print(f"{'WannaCry — Datos reales del PCAP (15/05/2017)':^80}")
print(f"{'='*80}")
print(f"  β_base  = {BETA_BASE}   (intensidad SMB/445 observada en PCAP real)")
print(f"  γ_base  = {GAMMA_BASE}    (tasa de recuperación base)")
print(f"  R₀_base = {R0_BASE}    (sin ningún sistema de detección)")
print(f"{'='*80}\\n")

for sp in all_sir_params:
    print(f"  [{sp.model_name}]")
    print(f"    Sensibilidad usada : {sp.sensitivity_used:.1%}")
    print(f"    β_efectivo         : {sp.beta_effective:.4f}  (era {sp.beta_base})")
    print(f"    γ_efectivo         : {sp.gamma_effective:.4f}  (era {sp.gamma_base})")
    print(f"    R₀_efectivo        : {sp.r0_effective:.2f}")
    print(f"    → {sp.interpretation}")
    print()

# Umbral de contencion
cont_thr = all_metrics[0].containment_threshold
print(f"{'─'*80}")
print(f"  Sensibilidad mínima para contener el brote (R₀_eff < 1):")
print(f"  s > R₀_base / (1 + R₀_base) = {R0_BASE} / {1+R0_BASE} = {cont_thr:.1%}")
"""))

# ── 9. Feature Importance ─────────────────────────────────────────────────────
cells.append(md("## 🔑 Features Más Importantes (Random Forest)\n\nLas features más predictivas son los síntomas del ataque — análogo a los signos vitales que un médico examina."))
cells.append(code("""
rf = models["Random Forest"]
importances = pd.Series(rf.feature_importances_, index=X_train.columns)
top20 = importances.nlargest(20)

fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#0D1117")
ax.set_facecolor("#161B22")
colors_feat = plt.cm.YlOrRd(np.linspace(0.4, 1.0, 20))[::-1]
top20.sort_values().plot(kind="barh", ax=ax, color=colors_feat, edgecolor="#30363D")
ax.set_title("Top 20 Features — Random Forest\\n(Síntomas diagnósticos del ataque)",
             color="white", fontsize=13, fontweight="bold")
ax.set_xlabel("Importancia (Gini)", color="#DFE6E9")
ax.tick_params(colors="#DFE6E9")
ax.spines[:].set_edgecolor("#30363D")
plt.tight_layout()
plt.savefig(FIGURES / "06_feature_importance.png", dpi=150,
            bbox_inches="tight", facecolor="#0D1117")
plt.show()
"""))

# ── 10. Guardar metricas ─────────────────────────────────────────────────────
cells.append(md("## 💾 Guardar Resultados"))
cells.append(code("""
df_metrics.to_csv(PROCESSED / "ml_clinical_metrics.csv", index=False)
print("✅ Resultados guardados en data/processed/ml_clinical_metrics.csv")
print("✅ Figura principal: reports/figures/06_ml_clinical_sir_panel.png")
print("✅ Feature importance: reports/figures/06_feature_importance.png")
print()
print("Resumen final de métricas clave:")
print(df_metrics[["Modelo","Sensibilidad","F1-Score","AUC-ROC","R₀ efectivo"]]
      .sort_values("Sensibilidad", ascending=False)
      .to_string(index=False))
"""))

# ── Escribir notebook ─────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name":"Python (HealTech)","language":"python","name":"healtech_venv"},
        "language_info": {"name":"python","version":"3.12.0"},
    },
    "cells": cells,
}

out = Path(__file__).parent / "06_ml_classifiers_unsw.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[OK] Notebook generado: {out}")
