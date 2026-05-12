"""
classifier.py
=============
Módulo reutilizable de clasificadores ML para el dataset UNSW-NB15.
Incluye métricas clínicas (sensibilidad, especificidad, VPP, VPN, MCC)
y traducción directa de resultados a parámetros β/γ del modelo SIR/SEIR.

Analogía médica
---------------
  Flujo de red normal  → Paciente sano (S)
  Flujo de red ataque  → Paciente infectado (I)
  Clasificador ML      → Médico diagnóstico
  Falso Negativo (FN)  → Infectado no detectado → sigue propagando (β sube)
  Falso Positivo (FP)  → Sano aislado innecesariamente (cuarentena)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    matthews_corrcoef,
    f1_score,
    classification_report,
    roc_curve,
    precision_recall_curve,
)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class ClinicalMetrics:
    """
    Métricas clínicas derivadas de la matriz de confusión.
    Terminología médica aplicada a detección de ataques de red.
    """
    # Matriz de confusión
    TP: int = 0   # Verdadero Positivo  – ataque detectado
    FP: int = 0   # Falso Positivo      – normal clasificado como ataque
    TN: int = 0   # Verdadero Negativo  – normal correcto
    FN: int = 0   # Falso Negativo      – ataque NO detectado ← crítico para SIR

    # Métricas primarias
    sensitivity: float = 0.0    # Recall / TPR  → capacidad de detectar infectados
    specificity: float = 0.0    # TNR           → no aislar sanos innecesariamente
    ppv: float = 0.0            # Precisión / VPP – confianza al aislar un nodo
    npv: float = 0.0            # VPN             – confianza al dejar libre un nodo
    f1: float = 0.0
    mcc: float = 0.0            # Matthews Corr. Coef. – métrica más robusta
    auc_roc: float = 0.0
    auc_pr: float = 0.0         # AUC Precisión-Recall – honesto con desbalance

    # Parámetros SIR/SEIR derivados
    beta_effective: float = 0.0    # β·(1 - sensibilidad)  → FN se siguen propagando
    gamma_effective: float = 0.0   # γ·sensibilidad         → solo detectados se recuperan
    r0_effective: float = 0.0      # β_eff / γ_eff          → número reproductivo real

    # Umbrales
    youden_index: float = 0.0      # Sensibilidad + Especificidad - 1
    containment_threshold: float = 0.0  # Sensibilidad mínima para contener el brote

    model_name: str = ""
    threshold: float = 0.5


@dataclass
class SIRParameters:
    """Parámetros SIR/SEIR calibrados desde métricas de un clasificador."""
    beta_base: float
    gamma_base: float
    beta_effective: float
    gamma_effective: float
    r0_base: float
    r0_effective: float
    sensitivity_used: float
    model_name: str
    interpretation: str = ""


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

COLS_DROP = ["srcip", "dstip", "Stime", "Ltime", "attack_cat"]
TARGET_COL = "Label"

CAT_COLS = ["proto", "state", "service"]


def preprocess_unsw(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Preprocesa el dataframe UNSW-NB15 para clasificación binaria.

    Pasos:
    1. Drop de columnas no predictivas (IPs, timestamps, categoría de ataque)
    2. Forzar Label a numérico
    3. Encoding de variables categóricas (one-hot)
    4. Imputación de NaN con mediana/moda
    5. Retorna (X, y)
    """
    df = df.copy()

    # --- Target ---
    df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="coerce")
    df = df.dropna(subset=[TARGET_COL])
    y = df[TARGET_COL].astype(int)

    # --- Drop columnas no predictivas ---
    cols_to_drop = [c for c in COLS_DROP if c in df.columns] + [TARGET_COL]
    X = df.drop(columns=cols_to_drop, errors="ignore")

    # --- Encoding categórico ---
    cat_present = [c for c in CAT_COLS if c in X.columns]
    if cat_present:
        X = pd.get_dummies(X, columns=cat_present, drop_first=False, dtype=np.float32)

    # --- Forzar numérico y rellenar NaN ---
    X = X.apply(pd.to_numeric, errors="coerce")
    for col in X.columns:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())

    return X.astype(np.float32), y


# ---------------------------------------------------------------------------
# Clinical Metrics Calculator
# ---------------------------------------------------------------------------

def compute_clinical_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    beta_base: float = 0.9223,
    gamma_base: float = 0.04,
    threshold: float = 0.5,
    model_name: str = "Model",
) -> ClinicalMetrics:
    """
    Calcula métricas clínicas completas y deriva parámetros SIR.

    Parameters
    ----------
    y_true     : etiquetas reales (0=normal, 1=ataque)
    y_prob     : probabilidades predichas para clase positiva (ataque)
    beta_base  : tasa de transmisión base calibrada desde PCAP WannaCry
    gamma_base : tasa de recuperación base calibrada desde PCAP WannaCry
    threshold  : umbral de clasificación (default 0.5, ajustable con Youden)
    model_name : nombre del modelo para identificación
    """
    y_pred = (y_prob >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    # --- Métricas clínicas ---
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0   # Recall
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0            # Precisión
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0

    f1 = f1_score(y_true, y_pred, zero_division=0)
    mcc = matthews_corrcoef(y_true, y_pred)
    auc_roc = roc_auc_score(y_true, y_prob)
    auc_pr = average_precision_score(y_true, y_prob)

    youden = sensitivity + specificity - 1.0

    # --- Parámetros SIR derivados ---
    # Los FN (ataques no detectados) siguen propagándose → aumentan β efectivo
    # Solo los ataques detectados (VP) se "recuperan" → γ efectivo proporcional a sensibilidad
    beta_eff = beta_base * (1.0 - sensitivity)
    gamma_eff = gamma_base * sensitivity if sensitivity > 0 else gamma_base * 0.01
    r0_eff = beta_eff / gamma_eff if gamma_eff > 0 else float("inf")

    # Umbral de contención: sensibilidad mínima para que R₀_eff < 1
    # R₀_base * (1 - s) / (s) < 1  →  s > R₀_base / (1 + R₀_base)
    r0_base = beta_base / gamma_base
    containment_threshold = r0_base / (1.0 + r0_base)

    return ClinicalMetrics(
        TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn),
        sensitivity=round(sensitivity, 4),
        specificity=round(specificity, 4),
        ppv=round(ppv, 4),
        npv=round(npv, 4),
        f1=round(f1, 4),
        mcc=round(mcc, 4),
        auc_roc=round(auc_roc, 4),
        auc_pr=round(auc_pr, 4),
        youden_index=round(youden, 4),
        beta_effective=round(beta_eff, 4),
        gamma_effective=round(gamma_eff, 4),
        r0_effective=round(r0_eff, 4),
        containment_threshold=round(containment_threshold, 4),
        model_name=model_name,
        threshold=threshold,
    )


def find_optimal_threshold_youden(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> float:
    """
    Encuentra el umbral óptimo usando el Índice de Youden.
    Youden J = Sensibilidad + Especificidad - 1  (maximizar)
    Equivalente médico: maximizar detección de enfermos y sanos a la vez.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    specificity = 1.0 - fpr
    youden = tpr + specificity - 1.0
    best_idx = np.argmax(youden)
    return float(thresholds[best_idx])


# ---------------------------------------------------------------------------
# SIR Parameter Translation
# ---------------------------------------------------------------------------

def get_sir_parameters_from_metrics(
    metrics: ClinicalMetrics,
    beta_base: float = 0.9223,
    gamma_base: float = 0.04,
) -> SIRParameters:
    """
    Traduce métricas clínicas a parámetros SIR/SEIR.

    Lógica epidemiológica
    ---------------------
    - β_efectivo = β_base × (1 - sensibilidad)
      Los FN son nodos infectados que el sistema no detectó.
      Estos nodos siguen activos en la red propagando el ataque.
      Si sensibilidad=1.0 → β_eff=0 (contención perfecta)
      Si sensibilidad=0.0 → β_eff=β_base (sin detección)

    - γ_efectivo = γ_base × sensibilidad
      Solo los nodos que el clasificador detecta como infectados
      pueden ser aislados/parcheados (pasar a R).
      Si sensibilidad=1.0 → γ_eff=γ_base (máxima recuperación)
      Si sensibilidad=0.0 → γ_eff≈0 (nadie se recupera)

    - R₀_efectivo = β_eff / γ_eff
      Si R₀_eff < 1 → brote controlado
      Si R₀_eff > 1 → brote sostenido
    """
    r0_base = beta_base / gamma_base

    if metrics.r0_effective < 1.0:
        interpretation = (
            f"✅ BROTE CONTROLADO: Con {metrics.model_name} (sensibilidad={metrics.sensitivity:.1%}), "
            f"R₀_efectivo={metrics.r0_effective:.2f} < 1. "
            f"El sistema puede contener el ataque."
        )
    elif metrics.r0_effective < r0_base * 0.5:
        interpretation = (
            f"⚠️ PROPAGACIÓN REDUCIDA: R₀_efectivo={metrics.r0_effective:.2f}. "
            f"El clasificador reduce significativamente la velocidad del ataque, "
            f"pero no lo contiene completamente."
        )
    else:
        interpretation = (
            f"🔴 BROTE ACTIVO: R₀_efectivo={metrics.r0_effective:.2f} ≈ R₀_base={r0_base:.2f}. "
            f"El clasificador tiene baja sensibilidad ({metrics.sensitivity:.1%}). "
            f"Muchos nodos infectados no detectados siguen propagando el ataque."
        )

    return SIRParameters(
        beta_base=beta_base,
        gamma_base=gamma_base,
        beta_effective=metrics.beta_effective,
        gamma_effective=metrics.gamma_effective,
        r0_base=round(r0_base, 2),
        r0_effective=metrics.r0_effective,
        sensitivity_used=metrics.sensitivity,
        model_name=metrics.model_name,
        interpretation=interpretation,
    )


# ---------------------------------------------------------------------------
# Results Summary
# ---------------------------------------------------------------------------

def metrics_to_dataframe(metrics_list: list[ClinicalMetrics]) -> pd.DataFrame:
    """Convierte lista de métricas a DataFrame comparativo."""
    rows = []
    for m in metrics_list:
        rows.append({
            "Modelo": m.model_name,
            "Umbral": m.threshold,
            "Sensibilidad": m.sensitivity,
            "Especificidad": m.specificity,
            "VPP (Precisión)": m.ppv,
            "VPN": m.npv,
            "F1-Score": m.f1,
            "MCC": m.mcc,
            "AUC-ROC": m.auc_roc,
            "AUC-PR": m.auc_pr,
            "Youden J": m.youden_index,
            "β efectivo": m.beta_effective,
            "γ efectivo": m.gamma_effective,
            "R₀ efectivo": m.r0_effective,
            "Umbral contención": m.containment_threshold,
            "TP": m.TP, "FP": m.FP, "TN": m.TN, "FN": m.FN,
        })
    return pd.DataFrame(rows)


def save_metrics(metrics_list: list[ClinicalMetrics], output_path: str | Path) -> None:
    """Guarda métricas en JSON."""
    data = [asdict(m) for m in metrics_list]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Métricas guardadas en: {output_path}")
