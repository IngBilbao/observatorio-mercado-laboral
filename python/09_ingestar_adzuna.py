"""
09_ingestar_adzuna.py
======================
Ingesta ofertas reales desde la API de Adzuna (https://api.adzuna.com/v1/api/).

Características:
- Credenciales desde .env (NUNCA hardcodear).
- Multipais x multi-query con control de cuota (1000 calls/mes free tier).
- Mapeo al esquema canonico del Observatorio (mismo que datos sinteticos).
- Modos:
    --validar           1 sola llamada para validar credenciales (NO ingesta).
    --pais ES --paginas 1   ingesta minima (testing).
    (sin args)          ingesta completa segun config.

Entrada:  variables ADZUNA_APP_ID, ADZUNA_APP_KEY en .env
Salida:   data/raw/adzuna_YYYY-MM-DD.csv
          + actualiza data/processed/datos_consolidados.csv mergeando con sintetico
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests
from dotenv import load_dotenv

from utils import PATHS, log, save_csv

# ───────────────────────── Configuración ─────────────────────────

API_BASE = "https://api.adzuna.com/v1/api/jobs"
ENV_PATH = PATHS.root / ".env"
load_dotenv(ENV_PATH)

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

PAISES = {
    # codigo: (label_pais, codigo_iso, moneda_local, tasa_a_usd_aprox)
    "es": ("España",          "ES", "EUR", 1.08),
    "gb": ("Reino Unido",     "GB", "GBP", 1.27),
    "us": ("EE.UU.",          "US", "USD", 1.00),
    "de": ("Alemania",        "DE", "EUR", 1.08),
    "fr": ("Francia",         "FR", "EUR", 1.08),
    "nl": ("Paises Bajos",    "NL", "EUR", 1.08),
    "br": ("Brasil",          "BR", "BRL", 0.20),
    "mx": ("Mexico",          "MX", "MXN", 0.05),
    "in": ("India",           "IN", "INR", 0.012),
}

# Queries que vamos a hacer en cada pais (5 por pais)
QUERIES = [
    "data analyst",
    "data scientist",
    "data engineer",
    "business intelligence",
    "machine learning",
]

# Regex para normalizar titulo → rol canonico (orden importa, prim matches first)
PATRONES_ROL = [
    (r"\b(machine learning|ml)\s+(engineer|eng)\b", "ML Engineer"),
    (r"\banalytics\s+engineer\b",                   "Analytics Engineer"),
    (r"\bdata\s+engineer\b",                        "Data Engineer"),
    (r"\b(data scientist|cientifico de datos)\b",   "Data Scientist"),
    (r"\b(bi|business intelligence)\b",             "BI Analyst"),
    (r"\b(business analyst|analista de negocio)\b", "Business Analyst"),
    (r"\b(financial analyst|analista financiero)\b","Financial Analyst"),
    (r"\b(data analyst|analista de datos)\b",       "Data Analyst"),
]

RESULTS_PER_PAGE = 25
PAUSA_ENTRE_CALLS = 1.2  # segundos (respeta rate limit ~1 call/seg)


# ───────────────────────── Helpers ─────────────────────────

def _check_credenciales() -> None:
    if not APP_ID or not APP_KEY:
        log.error(f"❌ Faltan credenciales. Crea {ENV_PATH} con ADZUNA_APP_ID y ADZUNA_APP_KEY.")
        sys.exit(2)


def _llamar_api(pais: str, pagina: int, what: str | None = None,
                timeout: int = 20) -> dict:
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "content-type": "application/json",
    }
    if what:
        params["what"] = what
    url = f"{API_BASE}/{pais}/search/{pagina}?{urlencode(params)}"
    r = requests.get(url, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


def _normalizar_rol(titulo: str) -> str:
    t = (titulo or "").lower()
    for patron, rol in PATRONES_ROL:
        if re.search(patron, t):
            return rol
    return "Otros"


def _detectar_nivel(titulo: str, anios_extraidos: int | None = None) -> tuple[str, int]:
    t = (titulo or "").lower()
    if re.search(r"\b(lead|principal|head|chief|director)\b", t):
        return "Lead", 12
    if re.search(r"\b(senior|sr\.?|snr)\b", t):
        return "Senior", 7
    if re.search(r"\b(junior|jr\.?|entry|trainee|graduate)\b", t):
        return "Junior", 1
    return "Mid", 3


def _convertir_salario(salary_min, salary_max, moneda_local: str,
                       tasa: float) -> float | None:
    if salary_min is None and salary_max is None:
        return None
    s_min = salary_min if salary_min else salary_max
    s_max = salary_max if salary_max else salary_min
    promedio_local = (s_min + s_max) / 2
    return round(promedio_local * tasa, 2)


def _mapear_oferta(raw: dict, cod_pais: str) -> dict | None:
    """Mapea respuesta de Adzuna al esquema canonico del Observatorio."""
    label_pais, iso, moneda, tasa = PAISES[cod_pais]
    titulo = raw.get("title", "")
    descripcion = raw.get("description", "") or ""
    rol = _normalizar_rol(titulo + " " + descripcion)
    if rol == "Otros":
        return None  # filtramos ofertas no relevantes

    nivel, anios = _detectar_nivel(titulo)

    # Ubicacion: Adzuna devuelve location.area = [pais, region, ciudad...] o similar
    location = raw.get("location", {})
    area = location.get("area", []) or []
    ciudad = area[-1] if area else (location.get("display_name") or label_pais)
    # Algunas ofertas remotas
    if re.search(r"\bremote\b", titulo, re.IGNORECASE):
        modalidad = "Remoto"
    else:
        modalidad = "Presencial"  # Adzuna no distingue hibrido/remoto bien

    # Coordenadas si vienen
    lat = raw.get("latitude")
    lon = raw.get("longitude")

    salario_usd = _convertir_salario(
        raw.get("salary_min"), raw.get("salary_max"), moneda, tasa
    )
    if salario_usd is None:
        return None  # ofertas sin salario no son utiles para regresion

    contrato_raw = (raw.get("contract_type") or "").lower()
    if "permanent" in contrato_raw:
        tipo_contrato = "Indefinido"
    elif "contract" in contrato_raw:
        tipo_contrato = "Temporal"
    else:
        tipo_contrato = "Indefinido"  # default Adzuna

    fecha = raw.get("created", "")
    try:
        fecha_iso = datetime.fromisoformat(fecha.replace("Z", "+00:00")).date().isoformat()
    except Exception:  # noqa: BLE001
        fecha_iso = datetime.now().date().isoformat()

    return {
        "oferta_id": f"ADZUNA-{cod_pais.upper()}-{raw.get('id', '')}",
        "fecha_publicacion": fecha_iso,
        "titulo_cargo": titulo,
        "rol_normalizado": rol,
        "nivel_experiencia": nivel,
        "anios_experiencia": anios,
        "empresa": (raw.get("company") or {}).get("display_name", "Desconocida"),
        "ciudad": ciudad,
        "pais": label_pais,
        "codigo_pais": iso,
        "latitud": lat if lat is not None else 0.0,
        "longitud": lon if lon is not None else 0.0,
        "modalidad": modalidad,
        "tipo_contrato": tipo_contrato,
        "moneda_original": moneda,
        "salario_anual_usd": float(salario_usd),
        "skills_detectadas": "",  # se rellena en 03_nlp_skills.py
        "n_skills": 0,
        "descripcion": descripcion[:1500],
        "fuente": "adzuna",
    }


# ───────────────────────── Comandos ─────────────────────────

def cmd_validar() -> int:
    """1 sola llamada para validar credenciales."""
    log.info("🔐 Validando credenciales Adzuna (1 sola llamada)...")
    try:
        data = _llamar_api("gb", 1, what="data analyst")
        n = len(data.get("results", []))
        total = data.get("count", "?")
        log.info(f"✅ Credenciales validas. Devuelve {n} resultados (de {total} totales en UK).")
        if n > 0:
            ejemplo = data["results"][0]
            log.info(f"   Ejemplo: '{ejemplo.get('title', '')[:60]}' en {ejemplo.get('location', {}).get('display_name', '')}")
        return 0
    except Exception as e:  # noqa: BLE001
        log.error(f"❌ Error: {e}")
        return 1


def cmd_ingestar(paises: list[str], paginas: int, queries: list[str]) -> int:
    log.info(f"📥 Ingestando Adzuna — paises={paises}, paginas={paginas}, queries={len(queries)}")
    n_calls_esperadas = len(paises) * len(queries) * paginas
    log.info(f"   📞 Se haran ~{n_calls_esperadas} llamadas (de tu cuota mensual de 1000)")

    ofertas: list[dict] = []
    n_filtradas = 0
    n_call = 0

    for cod_pais in paises:
        if cod_pais not in PAISES:
            log.warning(f"⚠️  Pais {cod_pais} desconocido, saltando")
            continue
        for query in queries:
            for pagina in range(1, paginas + 1):
                n_call += 1
                try:
                    data = _llamar_api(cod_pais, pagina, what=query)
                    raw_results = data.get("results", [])
                    log.info(f"   [{n_call:>3}] {cod_pais.upper()} '{query[:20]}' p{pagina} → {len(raw_results)} ofertas")
                    for raw in raw_results:
                        mapeada = _mapear_oferta(raw, cod_pais)
                        if mapeada is None:
                            n_filtradas += 1
                            continue
                        ofertas.append(mapeada)
                    time.sleep(PAUSA_ENTRE_CALLS)
                except Exception as e:  # noqa: BLE001
                    log.error(f"   ❌ {cod_pais} '{query}' p{pagina}: {e}")
                    continue

    log.info(f"📊 Resumen: {len(ofertas)} ofertas mapeadas, {n_filtradas} filtradas (sin rol claro o sin salario)")

    if not ofertas:
        log.warning("⚠️  No se obtuvieron ofertas. Abortando.")
        return 1

    df = pd.DataFrame(ofertas)
    # Dedup por oferta_id
    df = df.drop_duplicates(subset=["oferta_id"])
    log.info(f"🧹 Tras dedup: {len(df):,} filas")

    # Guardar archivo crudo del dia
    raw_path = PATHS.raw / f"adzuna_{datetime.now().date().isoformat()}.csv"
    save_csv(df, raw_path, backup=False)
    return 0


def cmd_merge() -> int:
    """Mergea TODOS los CSVs de adzuna_*.csv con datos_consolidados.csv (que ya
    tiene los sinteticos). Lo deja listo para que 02_limpieza.py procese todo."""
    sinteticos = PATHS.processed / "datos_consolidados.csv"
    if not sinteticos.exists():
        log.error(f"❌ No existe {sinteticos}. Ejecuta 00_generar_datos_sinteticos.py primero.")
        return 1

    base = pd.read_csv(sinteticos)
    base = base[base["fuente"] == "sintetico_v1"]  # conservar solo sintetico, no duplicar adzuna anterior

    adzuna_files = sorted(PATHS.raw.glob("adzuna_*.csv"))
    log.info(f"🔗 Mergeando {len(adzuna_files)} archivos de Adzuna con sinteticos")
    extras = [pd.read_csv(f) for f in adzuna_files]
    if not extras:
        log.warning("⚠️  No hay archivos adzuna_*.csv. Solo se conservan sinteticos.")
        return 0

    df_full = pd.concat([base] + extras, ignore_index=True)
    df_full["fecha_publicacion"] = pd.to_datetime(df_full["fecha_publicacion"])
    df_full = df_full.drop_duplicates(subset=["oferta_id"])
    log.info(f"📊 Total tras merge: {len(df_full):,} ofertas "
             f"({(df_full['fuente'] == 'sintetico_v1').sum():,} sinteticos + "
             f"{(df_full['fuente'] == 'adzuna').sum():,} adzuna)")

    save_csv(df_full, sinteticos)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingesta ofertas desde Adzuna API")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("validar", help="1 sola llamada para validar credenciales")

    p_ing = sub.add_parser("ingestar", help="Descargar ofertas")
    p_ing.add_argument("--paises", nargs="+", default=["es", "gb", "us"],
                       help=f"Codigos ISO de paises. Disponibles: {list(PAISES)}")
    p_ing.add_argument("--paginas", type=int, default=1, help="Paginas por pais+query")
    p_ing.add_argument("--queries", nargs="+", default=QUERIES, help="Terminos de busqueda")

    sub.add_parser("merge", help="Mergear CSVs Adzuna con datos_consolidados.csv")

    args = parser.parse_args()
    _check_credenciales()

    if args.cmd == "validar":
        return cmd_validar()
    elif args.cmd == "ingestar":
        return cmd_ingestar(args.paises, args.paginas, args.queries)
    elif args.cmd == "merge":
        return cmd_merge()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
