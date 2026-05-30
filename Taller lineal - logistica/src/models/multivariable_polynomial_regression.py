from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


BASE_DIR = Path(r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Taller lineal - logistica")
DATA_PATH = BASE_DIR / "data" / "raw" / "auto-mpg.csv"
FIGURES_DIR = BASE_DIR / "reports" / "figures"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

TARGET = "mpg"
FEATURES = ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"]
DEGREES = [1, 2, 3, 5]
ERROR_THRESHOLDS = [2, 4, 6]
FEATURE_STEPS = [
    ["horsepower"],
    ["horsepower", "weight"],
    ["horsepower", "weight", "acceleration"],
    ["horsepower", "weight", "acceleration", "model year"],
    ["horsepower", "weight", "acceleration", "model year", "cylinders"],
    ["horsepower", "weight", "acceleration", "model year", "cylinders", "displacement"],
    FEATURES,
]


def load_and_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["horsepower"] = pd.to_numeric(df["horsepower"], errors="coerce")
    df["model year"] = df["model year"].astype(int)
    clean_df = df.dropna(subset=[TARGET, *FEATURES]).copy()
    return clean_df


def build_pipeline(degree: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
            ("model", LinearRegression()),
        ]
    )


def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate_feature_stages(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    rows = []
    staged_models = {}
    for stage_features in FEATURE_STEPS:
        model = LinearRegression()
        model.fit(X_train[stage_features], y_train)

        train_pred = model.predict(X_train[stage_features])
        test_pred = model.predict(X_test[stage_features])

        rows.append(
            {
                "features_label": " + ".join(stage_features),
                "n_features": len(stage_features),
                "train_mae": float(mean_absolute_error(y_train, train_pred)),
                "train_mse": float(mean_squared_error(y_train, train_pred)),
                "train_rmse": float(mean_squared_error(y_train, train_pred) ** 0.5),
                "test_rmse": float(mean_squared_error(y_test, test_pred) ** 0.5),
                "test_mae": float(mean_absolute_error(y_test, test_pred)),
                "test_mse": float(mean_squared_error(y_test, test_pred)),
                "train_r2": float(r2_score(y_train, train_pred)),
                "test_r2": float(r2_score(y_test, test_pred)),
            }
        )

        staged_models[len(stage_features)] = {
            "features": stage_features,
            "model": model,
            "X_train": X_train.copy(),
            "X_test": X_test.copy(),
            "y_train": y_train.copy(),
            "y_test": y_test.copy(),
        }

    return pd.DataFrame(rows), staged_models


def evaluate_models(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    metrics_rows = []
    threshold_rows = []
    fitted_models = {}

    for degree in DEGREES:
        pipeline = build_pipeline(degree)
        pipeline.fit(X_train, y_train)

        train_pred = pipeline.predict(X_train)
        test_pred = pipeline.predict(X_test)

        train_metrics = calculate_metrics(y_train, train_pred)
        test_metrics = calculate_metrics(y_test, test_pred)

        metrics_rows.append(
            {
                "degree": degree,
                "train_mae": train_metrics["mae"],
                "train_mse": train_metrics["mse"],
                "train_rmse": train_metrics["rmse"],
                "train_r2": train_metrics["r2"],
                "test_mae": test_metrics["mae"],
                "test_mse": test_metrics["mse"],
                "test_rmse": test_metrics["rmse"],
                "test_r2": test_metrics["r2"],
            }
        )

        abs_error = np.abs(y_test.to_numpy() - test_pred)
        for threshold in ERROR_THRESHOLDS:
            threshold_rows.append(
                {
                    "degree": degree,
                    "threshold_mpg": threshold,
                    "share_within_threshold": float((abs_error <= threshold).mean()),
                }
            )

        fitted_models[degree] = {
            "pipeline": pipeline,
            "X_train": X_train.copy(),
            "X_test": X_test.copy(),
            "y_train": y_train.copy(),
            "y_test": y_test.copy(),
            "train_pred": train_pred,
            "test_pred": test_pred,
        }

    metrics_df = pd.DataFrame(metrics_rows).sort_values("degree").reset_index(drop=True)
    threshold_df = pd.DataFrame(threshold_rows).sort_values(["degree", "threshold_mpg"]).reset_index(drop=True)
    return metrics_df, threshold_df, fitted_models


def save_metrics_plot(metrics_df: pd.DataFrame, filename: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(metrics_df["degree"], metrics_df["train_rmse"], marker="o", linewidth=2, label="Train")
    axes[0].plot(metrics_df["degree"], metrics_df["test_rmse"], marker="o", linewidth=2, label="Test")
    axes[0].set_title("RMSE por grado polinomial")
    axes[0].set_xlabel("Grado")
    axes[0].set_ylabel("RMSE")
    axes[0].set_xticks(DEGREES)
    axes[0].legend()

    axes[1].plot(metrics_df["degree"], metrics_df["train_r2"], marker="o", linewidth=2, label="Train")
    axes[1].plot(metrics_df["degree"], metrics_df["test_r2"], marker="o", linewidth=2, label="Test")
    axes[1].set_title("R² por grado polinomial")
    axes[1].set_xlabel("Grado")
    axes[1].set_ylabel("R²")
    axes[1].set_xticks(DEGREES)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close(fig)


def save_threshold_plot(threshold_df: pd.DataFrame, filename: str) -> None:
    plot_df = threshold_df.copy()
    plot_df["threshold_label"] = plot_df["threshold_mpg"].apply(lambda value: f"<= {value} mpg")
    pivot_df = plot_df.pivot(index="degree", columns="threshold_label", values="share_within_threshold")

    plt.figure(figsize=(8, 5))
    sns.heatmap(pivot_df, annot=True, fmt=".2%", cmap="YlGnBu", vmin=0, vmax=1)
    plt.title("Proporcion de predicciones dentro del umbral")
    plt.xlabel("Umbral de error absoluto")
    plt.ylabel("Grado")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_actual_vs_predicted_plot(fitted_models: dict, filename: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    min_value = min(bundle["y_test"].min() for bundle in fitted_models.values())
    max_value = max(bundle["y_test"].max() for bundle in fitted_models.values())

    for axis, degree in zip(axes.flatten(), DEGREES):
        bundle = fitted_models[degree]
        axis.scatter(bundle["y_test"], bundle["test_pred"], alpha=0.75, s=36, color="#33658a")
        axis.plot([min_value, max_value], [min_value, max_value], linestyle="--", color="#d1495b", linewidth=1.5)
        axis.set_title(f"Grado {degree}")
        axis.set_xlabel("MPG real")
        axis.set_ylabel("MPG predicho")
        axis.set_xlim(min_value - 1, max_value + 1)
        axis.set_ylim(min_value - 1, max_value + 1)

    fig.suptitle("Comparacion real vs predicho en test", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close(fig)


def save_feature_effects_plot(fitted_models: dict, df: pd.DataFrame, filename: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    reference_row = df[FEATURES].median(numeric_only=True).to_dict()

    for axis, feature in zip(axes.flatten(), FEATURES):
        feature_grid = np.linspace(df[feature].quantile(0.05), df[feature].quantile(0.95), 160)
        curve_base = pd.DataFrame([reference_row] * len(feature_grid))
        curve_base[feature] = feature_grid

        for degree in DEGREES:
            predictions = fitted_models[degree]["pipeline"].predict(curve_base)
            axis.plot(feature_grid, predictions, linewidth=2, label=f"Grado {degree}")

        axis.set_title(f"Efecto de {feature} sobre MPG")
        axis.set_xlabel(feature.title())
        axis.set_ylabel("MPG predicho")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False)
    fig.suptitle("Curvas de prediccion manteniendo fijas las otras variables", fontsize=14, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close(fig)


def save_curve_deformation_plot(fitted_models: dict, df: pd.DataFrame, filename: str) -> None:
    reference_row = df[FEATURES].median(numeric_only=True).to_dict()
    feature = "horsepower"
    feature_grid = np.linspace(df[feature].min(), df[feature].max(), 220)
    curve_base = pd.DataFrame([reference_row] * len(feature_grid))
    curve_base[feature] = feature_grid

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x=feature,
        y=TARGET,
        alpha=0.35,
        s=38,
        color="#7a8fa6",
        label="Datos reales",
    )

    palette = {
        1: "#1f77b4",
        2: "#2ca02c",
        3: "#ff7f0e",
        5: "#d62728",
    }
    for degree in DEGREES:
        predictions = fitted_models[degree]["pipeline"].predict(curve_base)
        plt.plot(
            feature_grid,
            predictions,
            linewidth=2.5,
            color=palette[degree],
            label=f"Grado {degree}",
        )

    plt.title("Deformacion de la curva sobre los puntos reales")
    plt.xlabel("Horsepower")
    plt.ylabel("MPG")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_normalized_curve_deformation_plot(fitted_models: dict, df: pd.DataFrame, filename: str) -> None:
    reference_row = df[FEATURES].median(numeric_only=True).to_dict()
    feature = "horsepower"
    feature_grid = np.linspace(df[feature].min(), df[feature].max(), 220)
    curve_base = pd.DataFrame([reference_row] * len(feature_grid))
    curve_base[feature] = feature_grid

    x_min = df[feature].min()
    x_max = df[feature].max()
    y_min = df[TARGET].min()
    y_max = df[TARGET].max()

    normalized_x = (df[feature] - x_min) / (x_max - x_min)
    normalized_y = (df[TARGET] - y_min) / (y_max - y_min)
    normalized_grid = (feature_grid - x_min) / (x_max - x_min)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=normalized_x,
        y=normalized_y,
        alpha=0.35,
        s=38,
        color="#7a8fa6",
        label="Datos reales normalizados",
    )

    palette = {
        1: "#1f77b4",
        2: "#2ca02c",
        3: "#ff7f0e",
        5: "#d62728",
    }
    for degree in DEGREES:
        predictions = fitted_models[degree]["pipeline"].predict(curve_base)
        normalized_predictions = (predictions - y_min) / (y_max - y_min)
        plt.plot(
            normalized_grid,
            normalized_predictions,
            linewidth=2.5,
            color=palette[degree],
            label=f"Grado {degree}",
        )

    plt.title("Deformacion de la curva normalizada")
    plt.xlabel("Horsepower normalizado")
    plt.ylabel("MPG normalizado")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_progressive_feature_curve_plot(staged_models: dict, df: pd.DataFrame, filename: str) -> None:
    feature = "horsepower"
    reference_row = df[FEATURES].median(numeric_only=True).to_dict()
    feature_grid = np.linspace(df[feature].min(), df[feature].max(), 220)

    stage_items = list(staged_models.items())
    n_stages = len(stage_items)
    ncols = 2
    nrows = int(np.ceil(n_stages / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.6 * nrows), sharex=True, sharey=True)
    axes = np.atleast_1d(axes).flatten()
    palette = sns.color_palette("tab10", n_colors=n_stages)

    for axis, ((stage_number, stage_bundle), color) in zip(axes, zip(stage_items, palette)):
        stage_features = stage_bundle["features"]
        curve_base = pd.DataFrame([reference_row] * len(feature_grid))
        curve_base[feature] = feature_grid

        predictions = stage_bundle["model"].predict(curve_base[stage_features])
        test_pred = stage_bundle["model"].predict(stage_bundle["X_test"][stage_features])
        test_rmse = mean_squared_error(stage_bundle["y_test"], test_pred) ** 0.5
        test_r2 = r2_score(stage_bundle["y_test"], test_pred)

        sns.scatterplot(
            data=df,
            x=feature,
            y=TARGET,
            alpha=0.28,
            s=34,
            color="#9aa7b3",
            ax=axis,
        )
        axis.plot(feature_grid, predictions, linewidth=2.8, color=color)
        axis.set_title(
            f"{stage_number} variable(s)\n"
            f"{' + '.join(stage_features)}\n"
            f"RMSE test={test_rmse:.2f} | R² test={test_r2:.3f}"
        )
        axis.set_xlabel("Horsepower")
        axis.set_ylabel("MPG")

    for axis in axes[n_stages:]:
        axis.set_visible(False)

    fig.suptitle("Como cambia la recta proyectada al meter mas variables", fontsize=15)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close(fig)


def save_markdown_report(metrics_df: pd.DataFrame, threshold_df: pd.DataFrame, filename: str) -> None:
    best_degree = int(metrics_df.loc[metrics_df["test_rmse"].idxmin(), "degree"])
    best_row = metrics_df.loc[metrics_df["degree"] == best_degree].iloc[0]

    threshold_lines = []
    for degree in DEGREES:
        degree_rows = threshold_df[threshold_df["degree"] == degree]
        shares = ", ".join(
            f"<= {int(row['threshold_mpg'])} mpg: {row['share_within_threshold']:.1%}"
            for _, row in degree_rows.iterrows()
        )
        threshold_lines.append(f"- grado {degree}: {shares}")

    report = f"""# Regresion multivariable polinomial

## Configuracion

- Dataset: `data/raw/auto-mpg.csv`
- Variables de entrada: `{", ".join(FEATURES)}`
- Variable objetivo: `{TARGET}`
- Division: `train_test_split(test_size=0.2, random_state=42)`
- Grados comparados: `{", ".join(str(degree) for degree in DEGREES)}`

## Lectura principal

- El mejor grado por `RMSE` en `test` fue `grado {best_degree}`.
- Su `RMSE` en test fue `{best_row["test_rmse"]:.4f}` y su `R²` en test fue `{best_row["test_r2"]:.4f}`.
- La comparacion train/test sigue la recomendacion del PDF para detectar subajuste y sobreajuste.

## Umbrales de error absoluto en test

{chr(10).join(threshold_lines)}

## Tabla de metricas

| Grado | Train MAE | Train RMSE | Train R² | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(
    f"| {int(row['degree'])} | {row['train_mae']:.4f} | {row['train_rmse']:.4f} | {row['train_r2']:.4f} | {row['test_mae']:.4f} | {row['test_rmse']:.4f} | {row['test_r2']:.4f} |"
    for _, row in metrics_df.iterrows()
)}
"""

    (REPORTS_DIR / filename).write_text(report, encoding="utf-8")


def update_experiment_log(metrics_df: pd.DataFrame) -> None:
    experiment_log_path = DOCS_DIR / "experiment_log.md"
    current_log = experiment_log_path.read_text(encoding="utf-8")
    if "## Experimento 5" in current_log:
        return

    best_degree = int(metrics_df.loc[metrics_df["test_rmse"].idxmin(), "degree"])
    best_row = metrics_df.loc[metrics_df["degree"] == best_degree].iloc[0]

    new_entry = f"""
---

## Experimento 5

- Fecha: 2026-04-10
- Objetivo: comparar una regresion lineal multivariable con ajustes polinomiales de varios grados para predecir `mpg`.
- Dataset: `data/raw/auto-mpg.csv`
- Variables usadas: `{", ".join(FEATURES)}`, `mpg`
- Modelo: `LinearRegression` con `PolynomialFeatures`
- Configuracion: `train_test_split(test_size=0.2, random_state=42)` y grados `{", ".join(str(degree) for degree in DEGREES)}`
- Metricas: `MAE`, `RMSE`, `R²` y proporcion de predicciones dentro de umbrales de error absoluto
- Resultado: el mejor grado por `RMSE` en test fue `grado {best_degree}` con `RMSE = {best_row["test_rmse"]:.4f}` y `R² = {best_row["test_r2"]:.4f}`
- Observaciones: se generaron graficas para comparar train/test, visualizar umbrales de error y analizar como cambia la prediccion por variable al aumentar el grado
"""

    experiment_log_path.write_text(current_log.rstrip() + "\n" + new_entry, encoding="utf-8")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    df = load_and_clean_data()
    stage_metrics_df, staged_models = evaluate_feature_stages(df)
    metrics_df, threshold_df, fitted_models = evaluate_models(df)

    save_metrics_plot(metrics_df, "12_multivariable_polynomial_metrics.png")
    save_threshold_plot(threshold_df, "13_multivariable_threshold_heatmap.png")
    save_actual_vs_predicted_plot(fitted_models, "14_multivariable_actual_vs_predicted.png")
    save_feature_effects_plot(fitted_models, df, "15_multivariable_feature_effects.png")
    save_curve_deformation_plot(fitted_models, df, "16_curve_deformation_over_points.png")
    save_normalized_curve_deformation_plot(fitted_models, df, "17_normalized_curve_deformation.png")
    save_progressive_feature_curve_plot(staged_models, df, "18_progressive_feature_curves.png")
    save_markdown_report(metrics_df, threshold_df, "multivariable_polynomial_report.md")
    update_experiment_log(metrics_df)

    print("Metricas por entrada progresiva de variables:")
    print(stage_metrics_df.round(4).to_string(index=False))
    print("Metricas por grado:")
    print(metrics_df.round(4).to_string(index=False))
    print("\nProporcion dentro de umbrales:")
    print(threshold_df.assign(share_within_threshold=lambda frame: frame["share_within_threshold"].round(4)).to_string(index=False))
    print("\nFiguras generadas:")
    for figure_name in [
        "12_multivariable_polynomial_metrics.png",
        "13_multivariable_threshold_heatmap.png",
        "14_multivariable_actual_vs_predicted.png",
        "15_multivariable_feature_effects.png",
        "16_curve_deformation_over_points.png",
        "17_normalized_curve_deformation.png",
        "18_progressive_feature_curves.png",
    ]:
        print(figure_name)


if __name__ == "__main__":
    main()
