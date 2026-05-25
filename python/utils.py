"""
utils.py — Utilidades compartidas del pipeline.

Centraliza rutas, paleta de marca Bilbao Analytics, configuración de logging
y helpers de I/O. Importar desde cualquier script:

    from utils import PATHS, BRAND, log, save_csv, backup_existing
"""
from __future__ import annotations

import io
import logging
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

# Forzar UTF-8 en stdout para que los emojis no rompan la consola de Windows (cp1252).
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ───────────────────────── Rutas del proyecto ─────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@dataclass(frozen=True)
class _Paths:
    root: Path = ROOT
    data: Path = DATA
    raw: Path = DATA / "raw"
    processed: Path = DATA / "processed"
    outputs: Path = DATA / "outputs"
    excel: Path = ROOT / "excel"
    powerbi: Path = ROOT / "powerbi"
    docs: Path = ROOT / "docs"
    assets: Path = ROOT / "assets"


PATHS = _Paths()


# ───────────────────────── Identidad de marca ─────────────────────────
@dataclass(frozen=True)
class _Brand:
    """Paleta y tipografía Bilbao Analytics (temática universo)."""

    bg_deep: str = "#0D0D1A"
    bg_mid: str = "#1A1A2E"
    accent_blue: str = "#00D4FF"
    accent_violet: str = "#7B2FBE"
    text_main: str = "#E8E8F0"
    text_muted: str = "#9090A8"
    success: str = "#00E396"
    warning: str = "#FFB020"
    danger: str = "#FF4D6D"

    font_main: str = "Segoe UI"
    font_excel: str = "Calibri"

    @property
    def matplotlib_palette(self) -> list[str]:
        return [self.accent_blue, self.accent_violet, self.success,
                self.warning, self.danger, self.text_muted]


BRAND = _Brand()


def apply_matplotlib_theme() -> None:
    """Aplica el tema oscuro Bilbao Analytics a matplotlib."""
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": BRAND.bg_deep,
        "axes.facecolor": BRAND.bg_mid,
        "axes.edgecolor": BRAND.text_muted,
        "axes.labelcolor": BRAND.text_main,
        "axes.titlecolor": BRAND.text_main,
        "xtick.color": BRAND.text_main,
        "ytick.color": BRAND.text_main,
        "text.color": BRAND.text_main,
        "grid.color": BRAND.text_muted,
        "grid.alpha": 0.2,
        "font.family": BRAND.font_main,
        "axes.prop_cycle": plt.cycler(color=BRAND.matplotlib_palette),
    })


# ───────────────────────── Logging ─────────────────────────
def get_logger(name: str) -> logging.Logger:
    """Logger con formato consistente y emojis para indicar progreso."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(name)-22s  %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


log = get_logger("observatorio")


# ───────────────────────── I/O helpers ─────────────────────────
def backup_existing(path: Path) -> Path | None:
    """Si el archivo existe, crea copia con timestamp. Devuelve la ruta del backup."""
    if not path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(f".bak.{ts}{path.suffix}")
    shutil.copy2(path, backup)
    log.info(f"💾 Backup creado: {backup.name}")
    return backup


def save_csv(df: pd.DataFrame, path: Path, *, backup: bool = True) -> None:
    """Guarda DataFrame a CSV con backup opcional y mensaje de progreso."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup:
        backup_existing(path)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    log.info(f"✅ {path.relative_to(ROOT)}  ({len(df):,} filas × {len(df.columns)} columnas)")


def load_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Carga CSV con mensaje de progreso. Falla limpiamente si no existe."""
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {path}. Ejecuta primero los scripts anteriores del pipeline."
        )
    df = pd.read_csv(path, **kwargs)
    log.info(f"📥 {path.relative_to(ROOT)}  ({len(df):,} filas)")
    return df


# ───────────────────────── Catálogo de skills ─────────────────────────
# Diccionario canónico: clave = forma normalizada, valor = aliases comunes.
SKILLS_CATALOG: dict[str, list[str]] = {
    "Python":        ["python", "py", "python3", "python 3"],
    "SQL":           ["sql", "tsql", "t-sql", "pl/sql", "ansi-sql"],
    "Excel":         ["excel", "ms excel", "microsoft excel", "advanced excel"],
    "Power BI":      ["power bi", "powerbi", "power-bi", "pbi", "power bi desktop"],
    "Tableau":       ["tableau", "tableau desktop"],
    "Looker":        ["looker", "looker studio", "google data studio"],
    "R":             ["r ", " r,", "rstudio", "r language"],
    "SAS":           ["sas"],
    "SPSS":          ["spss"],
    "Spark":         ["spark", "apache spark", "pyspark"],
    "Hadoop":        ["hadoop", "hdfs", "hive"],
    "Airflow":       ["airflow", "apache airflow"],
    "dbt":           ["dbt", "dbt cloud"],
    "Snowflake":     ["snowflake"],
    "BigQuery":      ["bigquery", "big query", "bq"],
    "Redshift":      ["redshift"],
    "Databricks":    ["databricks"],
    "AWS":           ["aws", "amazon web services", "s3", "ec2", "lambda"],
    "Azure":         ["azure", "microsoft azure", "synapse", "data factory"],
    "GCP":           ["gcp", "google cloud", "google cloud platform"],
    "Docker":        ["docker"],
    "Kubernetes":    ["kubernetes", "k8s"],
    "Git":           ["git", "github", "gitlab"],
    "Pandas":        ["pandas"],
    "NumPy":         ["numpy"],
    "scikit-learn":  ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow":    ["tensorflow", "tf"],
    "PyTorch":       ["pytorch", "torch"],
    "Power Automate":["power automate", "microsoft flow", "ms flow"],
    "Power Query":   ["power query", "m language"],
    "DAX":           ["dax"],
    "VBA":           ["vba", "visual basic for applications"],
    "Machine Learning": ["machine learning", "ml ", "ml,"],
    "Deep Learning":    ["deep learning", "dl ", "dl,"],
    "NLP":              ["nlp", "natural language processing"],
}


def all_skill_columns() -> list[str]:
    """Lista de nombres de columnas booleanas para skills."""
    return [f"skill_{s.lower().replace(' ', '_').replace('-', '_')}"
            for s in SKILLS_CATALOG.keys()]


def skill_to_column(skill: str) -> str:
    return f"skill_{skill.lower().replace(' ', '_').replace('-', '_')}"
