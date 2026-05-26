"""
99_pipeline.py
==============
Orquestador del pipeline completo del Observatorio.

Ejecuta TODOS los pasos en orden y aborta si alguno falla:

  00 → datos sintéticos     (solo si --regenerar-sinteticos)
  09 → Adzuna ingestar       (solo si --con-adzuna)
  09 → Adzuna merge          (solo si --con-adzuna)
  01 → extracción
  02 → limpieza
  03 → NLP skills
  04 → clustering
  05 → series tiempo (Prophet)
  06 → regresión salarios
  07 → verificar outputs
  08 → generar alertas

Uso típico:
    py python/99_pipeline.py                    # pipeline ML completo (sin re-ingestar Adzuna)
    py python/99_pipeline.py --con-adzuna       # incluye ingesta + merge
    py python/99_pipeline.py --rapido           # salta 05 (Prophet) que es el mas lento
    py python/99_pipeline.py --regenerar-sinteticos --con-adzuna

Exit code: 0 si todo OK, != 0 si algún paso falló.

Diseñado para ser invocado por Power Automate Desktop Flow o por Task Scheduler.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from utils import PATHS, log


PYTHON_DIR = PATHS.root / "python"


@dataclass
class Paso:
    nombre: str
    script: str
    args: list[str]
    obligatorio: bool = True


def construir_pipeline(args) -> list[Paso]:
    pasos: list[Paso] = []

    if args.regenerar_sinteticos:
        pasos.append(Paso("00 · Datos sintéticos", "00_generar_datos_sinteticos.py", []))

    if args.con_adzuna:
        adzuna_args = [
            "ingestar",
            "--paises", *args.adzuna_paises,
            "--paginas", str(args.adzuna_paginas),
        ]
        pasos.append(Paso("09 · Adzuna ingest", "09_ingestar_adzuna.py", adzuna_args))
        pasos.append(Paso("09 · Adzuna merge",  "09_ingestar_adzuna.py", ["merge"]))

    pasos += [
        Paso("01 · Extracción",      "01_extraccion.py", []),
        Paso("02 · Limpieza",         "02_limpieza.py", []),
        Paso("03 · NLP skills",       "03_nlp_skills.py", []),
        Paso("04 · Clustering",       "04_clustering.py", []),
    ]
    if not args.rapido:
        pasos.append(Paso("05 · Series tiempo (Prophet)", "05_series_tiempo.py", []))
    pasos += [
        Paso("06 · Regresión salarios", "06_regresion_salarios.py", []),
        Paso("07 · Verificar outputs",  "07_verificar_outputs.py", []),
        Paso("08 · Generar alertas",    "08_generar_alertas.py", []),
    ]
    return pasos


def ejecutar(paso: Paso) -> tuple[int, float]:
    script_path = PYTHON_DIR / paso.script
    if not script_path.exists():
        log.error(f"❌ No existe el script: {script_path}")
        return 2, 0.0

    t0 = time.time()
    cmd = [sys.executable, str(script_path), *paso.args]
    result = subprocess.run(cmd, cwd=str(PATHS.root))
    elapsed = time.time() - t0
    return result.returncode, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestador del pipeline Observatorio")
    parser.add_argument("--regenerar-sinteticos", action="store_true",
                        help="Regenerar el dataset sintetico desde cero")
    parser.add_argument("--con-adzuna", action="store_true",
                        help="Ingestar ofertas reales desde Adzuna API")
    parser.add_argument("--adzuna-paises", nargs="+", default=["es", "gb", "us"],
                        help="Paises a consultar en Adzuna (ISO codes)")
    parser.add_argument("--adzuna-paginas", type=int, default=1,
                        help="Paginas por pais+query en Adzuna")
    parser.add_argument("--rapido", action="store_true",
                        help="Saltar Prophet (paso 05) — para pruebas rapidas")
    parser.add_argument("--continuar-si-error", action="store_true",
                        help="No abortar si un paso falla")
    args = parser.parse_args()

    pasos = construir_pipeline(args)
    log.info("=" * 68)
    log.info(f"🚀 PIPELINE OBSERVATORIO — {len(pasos)} pasos")
    log.info("=" * 68)

    t_total = time.time()
    resultados: list[tuple[Paso, int, float]] = []

    for i, paso in enumerate(pasos, 1):
        log.info("")
        log.info(f"▶️  [{i}/{len(pasos)}] {paso.nombre}  ({paso.script} {' '.join(paso.args)})")
        log.info("─" * 68)
        rc, elapsed = ejecutar(paso)
        resultados.append((paso, rc, elapsed))
        if rc != 0:
            log.error(f"❌ FALLO en '{paso.nombre}' (exit code {rc}) tras {elapsed:.1f}s")
            if not args.continuar_si_error:
                log.error("🛑 Abortando pipeline. Usa --continuar-si-error para ignorar fallos.")
                return rc
        else:
            log.info(f"✅ OK ({elapsed:.1f}s)")

    t_total = time.time() - t_total
    log.info("")
    log.info("=" * 68)
    log.info(f"🏁 PIPELINE COMPLETO — {t_total/60:.1f} minutos totales")
    log.info("=" * 68)
    for paso, rc, elapsed in resultados:
        marca = "✅" if rc == 0 else "❌"
        log.info(f"  {marca}  {paso.nombre:<40}  {elapsed:>6.1f}s")
    n_fallos = sum(1 for _, rc, _ in resultados if rc != 0)
    return 0 if n_fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
