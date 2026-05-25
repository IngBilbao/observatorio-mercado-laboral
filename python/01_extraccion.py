"""
01_extraccion.py
================
Consolida las fuentes disponibles en un único DataFrame.

Fase actual: lee el dataset sintético generado por 00_generar_datos_sinteticos.py.
Cuando se conecten fuentes reales (Kaggle, Adzuna, Remotive), este script las
unificará al mismo esquema.

Entrada:  data/processed/datos_consolidados.csv  (sintético)
          data/raw/*.csv                          (futuro: Kaggle, APIs)
Salida:   data/processed/datos_consolidados.csv  (sobrescrito)
"""
from __future__ import annotations

import pandas as pd

from utils import PATHS, load_csv, log, save_csv

SCHEMA_ESPERADO = [
    "oferta_id", "fecha_publicacion", "titulo_cargo", "rol_normalizado",
    "nivel_experiencia", "anios_experiencia", "empresa", "ciudad", "pais",
    "codigo_pais", "latitud", "longitud", "modalidad", "tipo_contrato",
    "moneda_original", "salario_anual_usd", "skills_detectadas", "n_skills",
    "descripcion", "fuente",
]


def cargar_sinteticos() -> pd.DataFrame:
    return load_csv(PATHS.processed / "datos_consolidados.csv")


# TODO (fase 2): cargar_kaggle_stackoverflow(), cargar_kaggle_salarios(),
# cargar_adzuna(), cargar_remotive() — todas deben devolver DataFrames con
# SCHEMA_ESPERADO antes de concatenarse.


def consolidar() -> pd.DataFrame:
    """Une todas las fuentes disponibles. Hoy solo hay datos sintéticos."""
    fuentes = [cargar_sinteticos()]
    df = pd.concat(fuentes, ignore_index=True)
    faltantes = set(SCHEMA_ESPERADO) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en el esquema: {faltantes}")
    return df[SCHEMA_ESPERADO]


def main() -> None:
    log.info("🚚 Extracción y consolidación de fuentes")
    df = consolidar()
    save_csv(df, PATHS.processed / "datos_consolidados.csv", backup=False)
    log.info(f"✨ Consolidación completada con {df['fuente'].nunique()} fuente(s).")


if __name__ == "__main__":
    main()
