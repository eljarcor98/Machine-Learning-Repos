from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


DEFAULT_LABEL_COLUMN_CANDIDATES = [
    "label",
    "Label",
]

DEFAULT_SOURCE_COLUMN_CANDIDATES = [
    "Source IP",
    "Src IP",
    "src_ip",
]

DEFAULT_DESTINATION_COLUMN_CANDIDATES = [
    "Destination IP",
    "Dst IP",
    "dst_ip",
]
