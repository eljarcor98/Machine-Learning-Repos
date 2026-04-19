from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.config import (
    DEFAULT_DESTINATION_COLUMN_CANDIDATES,
    DEFAULT_LABEL_COLUMN_CANDIDATES,
    DEFAULT_SOURCE_COLUMN_CANDIDATES,
    EXTERNAL_DATA_DIR,
)


def list_csv_files(data_dir: Path | None = None) -> list[Path]:
    base_dir = data_dir or EXTERNAL_DATA_DIR
    return sorted(base_dir.rglob("*.csv"))


def load_csv_files(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        raise FileNotFoundError("No se encontraron archivos CSV para cargar.")

    frames = []
    for path in paths:
        frame = pd.read_csv(path, low_memory=False)
        frame["source_file"] = path.name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def find_first_existing_column(columns: list[str], candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise KeyError(f"No se encontro ninguna de las columnas esperadas: {candidates}")


def standardize_labels(df: pd.DataFrame, label_column: str | None = None) -> pd.DataFrame:
    df = df.copy()
    resolved_label = label_column or find_first_existing_column(df.columns.tolist(), DEFAULT_LABEL_COLUMN_CANDIDATES)
    df[resolved_label] = df[resolved_label].astype(str).str.strip()
    df["label_normalized"] = df[resolved_label].str.lower().str.replace(" ", "_", regex=False)
    return df


def select_attack_subset(
    df: pd.DataFrame,
    allowed_labels: list[str],
    label_column: str = "label_normalized",
) -> pd.DataFrame:
    allowed = {value.lower().replace(" ", "_") for value in allowed_labels}
    return df[df[label_column].isin(allowed)].copy()


def resolve_network_columns(df: pd.DataFrame) -> tuple[str, str]:
    source_column = find_first_existing_column(df.columns.tolist(), DEFAULT_SOURCE_COLUMN_CANDIDATES)
    destination_column = find_first_existing_column(df.columns.tolist(), DEFAULT_DESTINATION_COLUMN_CANDIDATES)
    return source_column, destination_column


def load_cicids2017_subset(
    data_dir: Path | None = None,
    allowed_labels: list[str] | None = None,
) -> pd.DataFrame:
    csv_files = list_csv_files(data_dir)
    df = load_csv_files(csv_files)
    df = standardize_labels(df)

    if allowed_labels:
        df = select_attack_subset(df, allowed_labels=allowed_labels)

    return df.reset_index(drop=True)
