from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


BASE_DIR = Path(r"C:\Users\Arnold's\Documents\Repositorios Machine Learning\Taller lineal - logistica")
DATA_PATH = BASE_DIR / "data" / "raw" / "auto-mpg.csv"
FIGURES_DIR = BASE_DIR / "reports" / "figures"


def load_and_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["horsepower"] = pd.to_numeric(df["horsepower"], errors="coerce")
    df["model year"] = df["model year"].astype(int)
    clean_df = df.dropna(subset=["mpg", "horsepower", "weight", "acceleration", "model year"]).copy()
    return clean_df


def save_scatterplot(df: pd.DataFrame, x: str, y: str, filename: str, title: str) -> None:
    plt.figure(figsize=(9, 6))
    sns.regplot(
        data=df,
        x=x,
        y=y,
        scatter_kws={"alpha": 0.7, "s": 45},
        line_kws={"color": "#c0392b", "linewidth": 2},
    )
    plt.title(title)
    plt.xlabel(x.title())
    plt.ylabel(y.upper() if y == "mpg" else y.title())
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_distribution(df: pd.DataFrame, column: str, filename: str, title: str) -> None:
    plt.figure(figsize=(9, 6))
    sns.histplot(df[column], kde=True, bins=25, color="#2e86ab")
    plt.title(title)
    plt.xlabel(column.title())
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_correlation_heatmap(df: pd.DataFrame, filename: str) -> None:
    numeric_df = df[["mpg", "horsepower", "weight", "acceleration", "displacement", "cylinders", "model year", "origin"]]
    plt.figure(figsize=(10, 7))
    sns.heatmap(numeric_df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="RdBu_r", center=0)
    plt.title("Mapa de correlacion de variables numericas")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_linear_regression_plot(df: pd.DataFrame, filename: str) -> dict:
    model = LinearRegression()
    X = df[["horsepower"]]
    y = df["mpg"]
    model.fit(X, y)
    y_pred = model.predict(X)

    plot_df = df.copy()
    plot_df["predicted_mpg"] = y_pred

    plt.figure(figsize=(9, 6))
    sns.scatterplot(data=plot_df, x="horsepower", y="mpg", alpha=0.65, s=45, color="#4c78a8")
    order = plot_df.sort_values("horsepower")
    plt.plot(order["horsepower"], order["predicted_mpg"], color="#c0392b", linewidth=2.5)
    plt.title("Regresion lineal simple: potencia vs MPG")
    plt.xlabel("Horsepower")
    plt.ylabel("MPG")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()

    return {
        "slope": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "mae": float(mean_absolute_error(y, y_pred)),
        "mse": float(mean_squared_error(y, y_pred)),
        "rmse": float(mean_squared_error(y, y_pred) ** 0.5),
        "r2": float(r2_score(y, y_pred)),
    }


def save_regression_projection_plot(df: pd.DataFrame, filename: str) -> None:
    model = LinearRegression()
    X = df[["horsepower"]]
    y = df["mpg"]
    model.fit(X, y)
    y_pred = model.predict(X)

    plot_df = df.copy()
    plot_df["predicted_mpg"] = y_pred
    plot_df["residual"] = plot_df["mpg"] - plot_df["predicted_mpg"]
    plot_df["residual_sign"] = plot_df["residual"].apply(
        lambda value: "Positivo" if value >= 0 else "Negativo"
    )

    ordered_df = plot_df.sort_values("horsepower")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=plot_df, x="horsepower", y="mpg", color="#9fb3c8", alpha=0.2, s=20, legend=False)
    plt.plot(ordered_df["horsepower"], ordered_df["predicted_mpg"], color="#1f3a5f", linewidth=2.5)

    for _, row in ordered_df.iterrows():
        color = "#2e8b57" if row["residual"] >= 0 else "#d1495b"
        plt.plot(
            [row["horsepower"], row["horsepower"]],
            [row["predicted_mpg"], row["mpg"]],
            color=color,
            linewidth=0.8,
            alpha=0.35,
        )
    sns.scatterplot(
        data=ordered_df,
        x="horsepower",
        y="mpg",
        hue="residual_sign",
        palette={"Positivo": "#2e8b57", "Negativo": "#d1495b"},
        alpha=0.75,
        s=24,
    )

    plt.title("Proyeccion de puntos hacia la recta de regresion")
    plt.xlabel("Horsepower")
    plt.ylabel("MPG")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_residual_plot(df: pd.DataFrame, filename: str) -> None:
    model = LinearRegression()
    X = df[["horsepower"]]
    y = df["mpg"]
    model.fit(X, y)
    y_pred = model.predict(X)

    residual_df = df.copy()
    residual_df["predicted_mpg"] = y_pred
    residual_df["residual"] = residual_df["mpg"] - residual_df["predicted_mpg"]
    residual_df["residual_sign"] = residual_df["residual"].apply(
        lambda value: "Positivo" if value >= 0 else "Negativo"
    )

    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=residual_df,
        x="horsepower",
        y="residual",
        hue="residual_sign",
        palette={"Positivo": "#2e8b57", "Negativo": "#d1495b"},
        alpha=0.75,
        s=50,
    )
    plt.axhline(0, color="black", linestyle="--", linewidth=1.2)
    plt.title("Residuos del modelo lineal: potencia vs MPG")
    plt.xlabel("Horsepower")
    plt.ylabel("Residuo")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_residual_bar_plot(df: pd.DataFrame, filename: str) -> None:
    model = LinearRegression()
    X = df[["horsepower"]]
    y = df["mpg"]
    model.fit(X, y)
    y_pred = model.predict(X)

    residual_df = df.copy()
    residual_df["predicted_mpg"] = y_pred
    residual_df["residual"] = residual_df["mpg"] - residual_df["predicted_mpg"]

    plt.figure(figsize=(12, 6))
    plt.hist(
        residual_df["residual"],
        bins=24,
        color="#4c78a8",
        edgecolor="white",
        alpha=0.9,
    )
    plt.axvline(0, color="#c0392b", linestyle="--", linewidth=1.2)
    plt.title("Distribucion de residuos por intervalos")
    plt.xlabel("Residuo")
    plt.ylabel("Cantidad de observaciones")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def save_origin_boxplot(df: pd.DataFrame, filename: str) -> None:
    labels = {1: "USA", 2: "Europe", 3: "Japan"}
    plot_df = df.copy()
    plot_df["origin_label"] = plot_df["origin"].map(labels).fillna(plot_df["origin"].astype(str))

    plt.figure(figsize=(9, 6))
    sns.boxplot(data=plot_df, x="origin_label", y="mpg", hue="origin_label", palette="Set2", legend=False)
    plt.title("Distribucion de MPG por origen")
    plt.xlabel("Origen")
    plt.ylabel("MPG")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close()


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    df = load_and_clean_data()

    metrics = save_linear_regression_plot(
        df,
        filename="01_linear_regression_horsepower_vs_mpg.png",
    )
    save_regression_projection_plot(
        df,
        filename="02_projection_to_regression_line.png",
    )
    save_residual_plot(
        df,
        filename="03_residuals_horsepower_vs_mpg.png",
    )
    save_residual_bar_plot(
        df,
        filename="04_residuals_bar_chart.png",
    )
    save_scatterplot(
        df,
        x="horsepower",
        y="mpg",
        filename="05_horsepower_vs_mpg.png",
        title="Potencia vs consumo (MPG)",
    )
    save_scatterplot(
        df,
        x="weight",
        y="mpg",
        filename="06_weight_vs_mpg.png",
        title="Peso vs consumo (MPG)",
    )
    save_scatterplot(
        df,
        x="acceleration",
        y="mpg",
        filename="07_acceleration_vs_mpg.png",
        title="Aceleracion vs consumo (MPG)",
    )
    save_distribution(
        df,
        column="mpg",
        filename="08_distribution_mpg.png",
        title="Distribucion de MPG",
    )
    save_distribution(
        df,
        column="horsepower",
        filename="09_distribution_horsepower.png",
        title="Distribucion de potencia",
    )
    save_correlation_heatmap(df, filename="10_correlation_heatmap.png")
    save_origin_boxplot(df, filename="11_mpg_by_origin.png")

    print(f"Filas originales: {pd.read_csv(DATA_PATH).shape[0]}")
    print(f"Filas limpias: {df.shape[0]}")
    print(f"Valores faltantes en horsepower removidos: {pd.read_csv(DATA_PATH)['horsepower'].eq('?').sum()}")
    print(
        "Modelo lineal simple:",
        {
            "pendiente": round(metrics["slope"], 4),
            "intercepto": round(metrics["intercept"], 4),
            "mae": round(metrics["mae"], 4),
            "mse": round(metrics["mse"], 4),
            "rmse": round(metrics["rmse"], 4),
            "r2": round(metrics["r2"], 4),
        },
    )
    print("Figuras generadas:")
    for figure in sorted(FIGURES_DIR.glob("*.png")):
        print(figure.name)


if __name__ == "__main__":
    main()
