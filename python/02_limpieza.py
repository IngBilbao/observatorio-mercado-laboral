"""
02_limpieza.py
==============
Limpieza, validación y normalización del dataset consolidado.

Acciones:
- Eliminar duplicados por oferta_id.
- Validar y castear tipos (fechas, numéricos).
- Filtrar nulos críticos (rol, salario).
- Filtrar outliers de salario (winsorize p1–p99).
- Estandarizar texto (capitalización consistente).

Entrada:  data/processed/datos_consolidados.csv
Salida:   data/processed/datos_limpios.csv
"""
from __future__ import annotations

import pandas as pd

from utils import PATHS, load_csv, log, save_csv

COLUMNAS_CRITICAS = ["oferta_id", "fecha_publicacion", "rol_normalizado"]
# Nota: salario_anual_usd ya NO es critico - aceptamos ofertas sin salario
# (Adzuna ES/MX no siempre lo provee). El paso 06_regresion_salarios.py las filtra.


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)

    # Tipos
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"], errors="coerce")
    df["salario_anual_usd"] = pd.to_numeric(df["salario_anual_usd"], errors="coerce")
    df["anios_experiencia"] = pd.to_numeric(df["anios_experiencia"], errors="coerce")

    # Duplicados
    df = df.drop_duplicates(subset=["oferta_id"])
    log.info(f"🧹 Duplicados eliminados: {n0 - len(df):,}")

    # Nulos críticos
    n1 = len(df)
    df = df.dropna(subset=COLUMNAS_CRITICAS)
    log.info(f"🧹 Filas con nulos críticos descartadas: {n1 - len(df):,}")

    # Outliers de salario (winsorize)
    p01, p99 = df["salario_anual_usd"].quantile([0.01, 0.99])
    df["salario_anual_usd"] = df["salario_anual_usd"].clip(lower=p01, upper=p99)
    log.info(f"📐 Salarios winsorizados a rango USD ${p01:,.0f} – ${p99:,.0f}")

    # Texto consistente
    for col in ["rol_normalizado", "nivel_experiencia", "ciudad", "pais",
                "modalidad", "tipo_contrato"]:
        df[col] = df[col].astype(str).str.strip()

    # Skills detectadas: asegurar string
    df["skills_detectadas"] = df["skills_detectadas"].fillna("").astype(str)

    # Año y mes derivados (útil para Power BI / Excel)
    df["anio"] = df["fecha_publicacion"].dt.year
    df["mes"] = df["fecha_publicacion"].dt.month
    df["anio_mes"] = df["fecha_publicacion"].dt.to_period("M").astype(str)

    log.info(f"✅ Dataset limpio: {len(df):,} filas (de {n0:,} originales)")
    return df


def main() -> None:
    log.info("🧼 Limpieza y normalización")
    df = load_csv(PATHS.processed / "datos_consolidados.csv")
    df = limpiar(df)
    save_csv(df, PATHS.processed / "datos_limpios.csv")


if __name__ == "__main__":
    main()
