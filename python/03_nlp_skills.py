"""
03_nlp_skills.py
================
Detecta menciones de skills en las descripciones de las ofertas y construye
una matriz booleana (una columna por skill).

Estrategia híbrida:
- Si la fila ya tiene `skills_detectadas` (caso datos sintéticos o pre-parseados),
  se usa esa lista canónica.
- Si solo hay texto libre (caso Adzuna/Remotive), se aplica matching por aliases
  del SKILLS_CATALOG (ver utils.py) usando expresiones regulares con límites de
  palabra para evitar falsos positivos.

Opcional: si spaCy está instalado, se lematiza la descripción para captar
variaciones (ej. "developing in Python" → token "python").

Entrada:  data/processed/datos_limpios.csv
Salida:   data/processed/matriz_skills.csv  (todas las cols + skill_* booleanas)
"""
from __future__ import annotations

import re

import pandas as pd

from utils import PATHS, SKILLS_CATALOG, load_csv, log, save_csv, skill_to_column

try:
    import spacy
    NLP = spacy.load("en_core_web_sm")
    SPACY_OK = True
except Exception:  # noqa: BLE001
    SPACY_OK = False
    NLP = None


def _patron_skill(aliases: list[str]) -> re.Pattern:
    """Compila una regex case-insensitive con límites de palabra para los aliases."""
    partes = [re.escape(a).replace(r"\ ", r"\s+") for a in aliases]
    return re.compile(r"(?<![a-zA-Z0-9])(?:" + "|".join(partes) + r")(?![a-zA-Z0-9])",
                      re.IGNORECASE)


PATRONES = {skill: _patron_skill(aliases) for skill, aliases in SKILLS_CATALOG.items()}


def detectar_skills_desde_texto(texto: str) -> set[str]:
    if not texto or pd.isna(texto):
        return set()
    detectadas = set()
    for skill, patron in PATRONES.items():
        if patron.search(texto):
            detectadas.add(skill)
    return detectadas


def detectar_skills_desde_lista(skills_str: str) -> set[str]:
    if not skills_str:
        return set()
    return {s.strip() for s in skills_str.split("|") if s.strip() in SKILLS_CATALOG}


def construir_matriz(df: pd.DataFrame) -> pd.DataFrame:
    log.info(f"🧠 NLP de skills (spaCy disponible: {SPACY_OK})")

    skills_por_oferta: list[set[str]] = []
    for _, row in df.iterrows():
        # Prioridad 1: skills ya canonizadas en el dataset
        skills = detectar_skills_desde_lista(row.get("skills_detectadas", ""))
        # Prioridad 2: complementar con detección sobre descripción
        if row.get("descripcion"):
            skills |= detectar_skills_desde_texto(row["descripcion"])
        skills_por_oferta.append(skills)

    # Construir columnas booleanas
    for skill in SKILLS_CATALOG.keys():
        col = skill_to_column(skill)
        df[col] = [skill in s for s in skills_por_oferta]

    # Recalcular n_skills
    skill_cols = [skill_to_column(s) for s in SKILLS_CATALOG.keys()]
    df["n_skills"] = df[skill_cols].sum(axis=1)
    df["skills_detectadas"] = ["|".join(sorted(s)) for s in skills_por_oferta]

    log.info(f"🎯 Skills detectadas: media {df['n_skills'].mean():.1f} por oferta, "
             f"máx {df['n_skills'].max()}")
    top10 = df[skill_cols].sum().sort_values(ascending=False).head(10)
    log.info("🏆 Top 10 skills por frecuencia:\n" +
             "\n".join(f"   {s.replace('skill_', '').replace('_', ' '):20s} {int(c):>5,}"
                       for s, c in top10.items()))
    return df


def main() -> None:
    df = load_csv(PATHS.processed / "datos_limpios.csv")
    df = construir_matriz(df)
    save_csv(df, PATHS.processed / "matriz_skills.csv")


if __name__ == "__main__":
    main()
