"""
00_generar_datos_sinteticos.py
==============================
Genera un dataset sintético realista de ofertas laborales del mercado de datos
y tecnología para alimentar el pipeline mientras se configuran los datos reales
(Kaggle / Adzuna / Remotive).

Características:
- ~5000 ofertas distribuidas en los últimos 24 meses (para series de tiempo).
- Roles, skills, salarios y ubicaciones con distribuciones plausibles.
- Skills correlacionadas por rol (un DS suele tener Python+SQL+ML; un BI Analyst
  suele tener Power BI+Excel+SQL).
- Variación temporal: la demanda de algunas skills crece en el tiempo (Python,
  Power BI), otras decrecen (SAS, SPSS).

Salida: data/processed/datos_consolidados.csv
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from utils import PATHS, SKILLS_CATALOG, log, save_csv

RNG_SEED = 42
N_OFERTAS = 5000
FECHA_FIN = datetime(2026, 5, 1)
MESES_HISTORICO = 24

random.seed(RNG_SEED)
np.random.seed(RNG_SEED)
fake = Faker("es_ES")
Faker.seed(RNG_SEED)


# ───────────────────────── Catálogos ─────────────────────────

ROLES = {
    "Data Analyst":      {"peso": 0.22, "salario_base": 55_000,  "salario_sd": 12_000},
    "BI Analyst":        {"peso": 0.15, "salario_base": 58_000,  "salario_sd": 13_000},
    "Data Scientist":    {"peso": 0.16, "salario_base": 85_000,  "salario_sd": 22_000},
    "Data Engineer":     {"peso": 0.14, "salario_base": 95_000,  "salario_sd": 25_000},
    "ML Engineer":       {"peso": 0.08, "salario_base": 110_000, "salario_sd": 28_000},
    "Analytics Engineer":{"peso": 0.06, "salario_base": 88_000,  "salario_sd": 18_000},
    "Business Analyst":  {"peso": 0.10, "salario_base": 52_000,  "salario_sd": 10_000},
    "Financial Analyst": {"peso": 0.09, "salario_base": 60_000,  "salario_sd": 14_000},
}

# Skills probables por rol (probabilidad 0..1 de aparición).
SKILLS_POR_ROL = {
    "Data Analyst":       {"SQL": 0.92, "Excel": 0.88, "Power BI": 0.62, "Tableau": 0.40,
                           "Python": 0.55, "R": 0.18, "DAX": 0.30, "Power Query": 0.35},
    "BI Analyst":         {"Power BI": 0.92, "Excel": 0.90, "SQL": 0.88, "DAX": 0.80,
                           "Power Query": 0.75, "Power Automate": 0.40, "Tableau": 0.25,
                           "Python": 0.30, "Azure": 0.35},
    "Data Scientist":     {"Python": 0.95, "SQL": 0.78, "scikit-learn": 0.82, "Pandas": 0.85,
                           "NumPy": 0.75, "Machine Learning": 0.88, "Deep Learning": 0.40,
                           "TensorFlow": 0.30, "PyTorch": 0.28, "R": 0.25, "NLP": 0.30,
                           "AWS": 0.35, "Databricks": 0.30},
    "Data Engineer":      {"Python": 0.88, "SQL": 0.95, "Spark": 0.70, "Airflow": 0.65,
                           "dbt": 0.50, "Snowflake": 0.55, "BigQuery": 0.40, "AWS": 0.65,
                           "Azure": 0.45, "GCP": 0.35, "Docker": 0.55, "Kubernetes": 0.30,
                           "Databricks": 0.40, "Hadoop": 0.20},
    "ML Engineer":        {"Python": 0.98, "Machine Learning": 0.95, "TensorFlow": 0.55,
                           "PyTorch": 0.55, "Docker": 0.70, "Kubernetes": 0.45, "AWS": 0.60,
                           "scikit-learn": 0.78, "SQL": 0.65, "Spark": 0.45, "NLP": 0.35,
                           "Deep Learning": 0.70, "Databricks": 0.40},
    "Analytics Engineer": {"SQL": 0.95, "dbt": 0.88, "Snowflake": 0.70, "BigQuery": 0.55,
                           "Python": 0.65, "Power BI": 0.40, "Looker": 0.45, "Git": 0.75,
                           "Airflow": 0.45},
    "Business Analyst":   {"Excel": 0.95, "SQL": 0.72, "Power BI": 0.55, "Tableau": 0.35,
                           "VBA": 0.30, "Power Automate": 0.25},
    "Financial Analyst":  {"Excel": 0.98, "Power BI": 0.55, "SQL": 0.55, "VBA": 0.45,
                           "Python": 0.30, "SAS": 0.15, "SPSS": 0.10},
}

# Factor temporal (tendencia): ajuste aditivo a la prob. base por mes_offset.
# 0 = mes más antiguo, MESES_HISTORICO-1 = mes más reciente.
# Se aplica SOLO a skills que ya son típicas del rol (presentes en SKILLS_POR_ROL[rol]).
# Magnitudes calibradas: en 24 meses el ajuste total no supera ±0.30 (es decir,
# una skill puede crecer/decrecer máx ~30 puntos porcentuales en 2 años).
TENDENCIA_MENSUAL = {
    "Python":          +0.006,
    "Power BI":        +0.008,
    "dbt":             +0.012,
    "Snowflake":       +0.010,
    "Databricks":      +0.010,
    "Power Automate":  +0.007,
    "Deep Learning":   +0.005,
    "NLP":             +0.006,
    "SAS":             -0.010,
    "SPSS":            -0.008,
    "Hadoop":          -0.008,
    "R":               -0.004,
    "VBA":             -0.003,
    "Tableau":         -0.002,
}
PROB_SKILL_FUERA_DE_ROL = 0.025  # spillover bajo para skills no típicas del rol

UBICACIONES = [
    # (ciudad, país, código_país, lat, lon, factor_salario)
    ("Madrid",         "España",       "ES", 40.4168, -3.7038, 0.85),
    ("Barcelona",      "España",       "ES", 41.3851,  2.1734, 0.90),
    ("Valencia",       "España",       "ES", 39.4699, -0.3763, 0.75),
    ("Sevilla",        "España",       "ES", 37.3891, -5.9845, 0.70),
    ("Bilbao",         "España",       "ES", 43.2630, -2.9350, 0.82),
    ("Lisboa",         "Portugal",     "PT", 38.7223, -9.1393, 0.72),
    ("Bogotá",         "Colombia",     "CO",  4.7110, -74.0721, 0.45),
    ("Medellín",       "Colombia",     "CO",  6.2442, -75.5812, 0.42),
    ("Ciudad de México","México",       "MX", 19.4326, -99.1332, 0.55),
    ("Monterrey",      "México",       "MX", 25.6866, -100.3161, 0.60),
    ("Buenos Aires",   "Argentina",    "AR", -34.6037, -58.3816, 0.50),
    ("Santiago",       "Chile",        "CL", -33.4489, -70.6693, 0.58),
    ("Lima",           "Perú",         "PE", -12.0464, -77.0428, 0.48),
    ("Londres",        "Reino Unido",  "GB", 51.5074, -0.1278, 1.45),
    ("Berlín",         "Alemania",     "DE", 52.5200, 13.4050, 1.30),
    ("Ámsterdam",      "Países Bajos", "NL", 52.3676,  4.9041, 1.40),
    ("Dublín",         "Irlanda",      "IE", 53.3498, -6.2603, 1.35),
    ("Nueva York",     "EE.UU.",       "US", 40.7128, -74.0060, 1.80),
    ("San Francisco",  "EE.UU.",       "US", 37.7749, -122.4194, 2.10),
    ("Austin",         "EE.UU.",       "US", 30.2672, -97.7431, 1.55),
    ("Remoto",         "Global",       "WW",  0.0,     0.0,    1.10),
]
PESOS_UBICACION = [0.10, 0.09, 0.04, 0.03, 0.03, 0.03, 0.06, 0.03, 0.06, 0.03,
                   0.04, 0.03, 0.03, 0.06, 0.05, 0.05, 0.04, 0.05, 0.04, 0.03, 0.08]

MODALIDADES = ["Remoto", "Híbrido", "Presencial"]
PESOS_MODALIDAD = [0.32, 0.45, 0.23]

CONTRATOS = ["Indefinido", "Temporal", "Freelance", "Prácticas"]
PESOS_CONTRATO = [0.62, 0.20, 0.13, 0.05]

NIVELES_EXPERIENCIA = ["Junior", "Mid", "Senior", "Lead"]
PESOS_NIVEL = [0.28, 0.40, 0.25, 0.07]
ANIOS_POR_NIVEL = {"Junior": (0, 2), "Mid": (2, 5), "Senior": (5, 10), "Lead": (10, 18)}
FACTOR_NIVEL = {"Junior": 0.65, "Mid": 1.00, "Senior": 1.45, "Lead": 1.85}

EMPRESAS_FICTICIAS = [
    "Nebula Data", "Orion Insights", "Stellar Analytics", "Quasar Tech",
    "Pleiades AI", "Andromeda Labs", "Helios BI", "Aurora Data Co.",
    "Cosmos Consulting", "Galaxy Ventures", "Nova Analytics", "Lyra Systems",
    "Vega Intelligence", "Polaris Data", "Sirius Software", "Cygnus Solutions",
    "Phoenix Insights", "Hydra Tech", "Draco Labs", "Centauri AI",
    "Bilbao Analytics",  # 😉
]


# ───────────────────────── Generación ─────────────────────────

def _muestrear_fechas(n: int) -> list[datetime]:
    """Genera fechas en los últimos 24 meses con leve crecimiento hacia hoy."""
    inicio = FECHA_FIN - timedelta(days=MESES_HISTORICO * 30)
    dias_total = (FECHA_FIN - inicio).days
    # Distribución sesgada hacia fechas recientes (más ofertas hoy que hace 2 años).
    pesos_dia = np.linspace(0.5, 1.5, dias_total)
    pesos_dia /= pesos_dia.sum()
    dias = np.random.choice(dias_total, size=n, p=pesos_dia)
    return [inicio + timedelta(days=int(d)) for d in dias]


def _mes_offset(fecha: datetime) -> int:
    """0 para la fecha más antigua, MESES_HISTORICO-1 para la más reciente."""
    inicio = FECHA_FIN - timedelta(days=MESES_HISTORICO * 30)
    return min(MESES_HISTORICO - 1, max(0, (fecha - inicio).days // 30))


def _generar_oferta(idx: int) -> dict:
    # Rol
    rol = random.choices(list(ROLES.keys()), weights=[v["peso"] for v in ROLES.values()])[0]
    cfg_rol = ROLES[rol]

    # Nivel y experiencia
    nivel = random.choices(NIVELES_EXPERIENCIA, weights=PESOS_NIVEL)[0]
    a_min, a_max = ANIOS_POR_NIVEL[nivel]
    anios_exp = random.randint(a_min, a_max)

    # Ubicación y modalidad
    ubic = random.choices(UBICACIONES, weights=PESOS_UBICACION)[0]
    ciudad, pais, cod_pais, lat, lon, fac_loc = ubic
    if ciudad == "Remoto":
        modalidad = "Remoto"
    else:
        modalidad = random.choices(MODALIDADES, weights=PESOS_MODALIDAD)[0]

    # Fecha
    fecha = _muestrear_fechas(1)[0]
    mes_off = _mes_offset(fecha)

    # Skills: probabilidad base por rol + ajuste temporal (solo si la skill es típica del rol)
    skills_seleccionadas = []
    probs_rol = SKILLS_POR_ROL.get(rol, {})
    for skill in SKILLS_CATALOG.keys():
        if skill in probs_rol:
            p_base = probs_rol[skill]
            ajuste = TENDENCIA_MENSUAL.get(skill, 0.0) * mes_off
        else:
            # Skill no típica del rol: prob. constante baja, sin tendencia.
            p_base = PROB_SKILL_FUERA_DE_ROL
            ajuste = 0.0
        p_final = max(0.0, min(0.97, p_base + ajuste))
        if random.random() < p_final:
            skills_seleccionadas.append(skill)
    # Garantizar al menos 2 skills
    if len(skills_seleccionadas) < 2:
        top = [s for s, p in sorted(probs_rol.items(), key=lambda x: -x[1])[:3]]
        skills_seleccionadas = list(set(skills_seleccionadas + top))[:3]

    # Salario: base * factor_nivel * factor_ubicación * ruido normal
    ruido = np.random.normal(1.0, 0.12)
    salario_anual_usd = (
        cfg_rol["salario_base"] * FACTOR_NIVEL[nivel] * fac_loc * ruido
    )
    # Bonus por skills "premium"
    skills_premium = {"Spark", "dbt", "Snowflake", "Databricks", "Kubernetes",
                      "PyTorch", "TensorFlow", "Deep Learning"}
    bonus = sum(0.025 for s in skills_seleccionadas if s in skills_premium)
    salario_anual_usd *= (1 + bonus)
    salario_anual_usd = round(salario_anual_usd / 500) * 500  # redondeo a 500

    # Moneda original (luego se "convierte" a USD)
    moneda_original = {
        "ES": "EUR", "PT": "EUR", "DE": "EUR", "NL": "EUR", "IE": "EUR",
        "GB": "GBP", "US": "USD", "CO": "COP", "MX": "MXN",
        "AR": "ARS", "CL": "CLP", "PE": "PEN", "WW": "USD",
    }.get(cod_pais, "USD")

    # Descripción sintética (para NLP)
    skills_str = ", ".join(skills_seleccionadas)
    descripcion = (
        f"Buscamos un {nivel} {rol} con {anios_exp} años de experiencia. "
        f"Stack: {skills_str}. Modalidad {modalidad.lower()}, ubicación {ciudad}. "
        f"Salario competitivo, beneficios y plan de carrera."
    )

    empresa = random.choice(EMPRESAS_FICTICIAS)
    titulo = f"{nivel} {rol}" if random.random() < 0.7 else f"{rol} ({nivel})"

    return {
        "oferta_id": f"OBS-{idx:06d}",
        "fecha_publicacion": fecha.date().isoformat(),
        "titulo_cargo": titulo,
        "rol_normalizado": rol,
        "nivel_experiencia": nivel,
        "anios_experiencia": anios_exp,
        "empresa": empresa,
        "ciudad": ciudad,
        "pais": pais,
        "codigo_pais": cod_pais,
        "latitud": lat,
        "longitud": lon,
        "modalidad": modalidad,
        "tipo_contrato": random.choices(CONTRATOS, weights=PESOS_CONTRATO)[0],
        "moneda_original": moneda_original,
        "salario_anual_usd": float(salario_anual_usd),
        "skills_detectadas": "|".join(skills_seleccionadas),
        "n_skills": len(skills_seleccionadas),
        "descripcion": descripcion,
        "fuente": "sintetico_v1",
    }


def generar_dataset(n: int = N_OFERTAS) -> pd.DataFrame:
    log.info(f"🛠️  Generando {n:,} ofertas sintéticas (seed={RNG_SEED})...")
    registros = [_generar_oferta(i) for i in range(1, n + 1)]
    df = pd.DataFrame(registros)
    # Tipos correctos
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"])
    df = df.sort_values("fecha_publicacion").reset_index(drop=True)
    return df


def main() -> None:
    df = generar_dataset()

    # Resumen rápido en stdout para validar realismo
    log.info("📊 Distribución por rol:")
    log.info("\n" + df["rol_normalizado"].value_counts().to_string())
    log.info(f"💰 Salario USD — mediana: ${df['salario_anual_usd'].median():,.0f}  "
             f"p10: ${df['salario_anual_usd'].quantile(0.1):,.0f}  "
             f"p90: ${df['salario_anual_usd'].quantile(0.9):,.0f}")
    log.info(f"📅 Rango fechas: {df['fecha_publicacion'].min().date()} → "
             f"{df['fecha_publicacion'].max().date()}")

    save_csv(df, PATHS.processed / "datos_consolidados.csv")
    log.info("🎉 Dataset sintético listo — alimenta el resto del pipeline.")


if __name__ == "__main__":
    main()
