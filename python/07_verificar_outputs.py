"""
07_verificar_outputs.py
========================
Valida que todos los CSVs de salida del pipeline existen, no estan vacios,
tienen el esquema esperado y los rangos de valores son razonables.

Esta validacion es CRITICA para Power BI / Power Automate: si un CSV queda
mal generado, Power Query falla con un mensaje opaco. Aqui detectamos los
problemas antes con un mensaje claro.

Ejecutar despues de correr 01..06. Devuelve exit code != 0 si hay errores
(util para CI/CD o para que Power Automate aborte el flujo).

Salida: data/outputs/_verificacion.json (resumen estructurado)
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

from utils import PATHS, log


@dataclass
class VerificacionTabla:
    archivo: str
    existe: bool = False
    filas: int = 0
    columnas: int = 0
    columnas_esperadas_ok: bool = False
    columnas_faltantes: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    tamano_bytes: int = 0


ESQUEMAS_ESPERADOS: dict[str, dict] = {
    # archivo: {cols_obligatorias, filas_min, validaciones_extra}
    "processed/datos_consolidados.csv": {
        "cols": ["oferta_id", "fecha_publicacion", "rol_normalizado",
                 "salario_anual_usd", "ciudad", "pais"],
        "filas_min": 1000,
    },
    "processed/datos_limpios.csv": {
        "cols": ["oferta_id", "fecha_publicacion", "anio_mes", "salario_anual_usd"],
        "filas_min": 1000,
    },
    "processed/matriz_skills.csv": {
        "cols": ["oferta_id", "rol_normalizado", "salario_anual_usd",
                 "skill_python", "skill_sql", "skill_excel", "skill_power_bi"],
        "filas_min": 1000,
    },
    "outputs/clusters_perfiles.csv": {
        "cols": ["oferta_id", "cluster_id", "cluster_nombre"],
        "filas_min": 1000,
    },
    "outputs/clusters_resumen.csv": {
        "cols": ["cluster_id", "cluster_nombre", "n_ofertas", "rol_dominante",
                 "salario_mediano_usd", "top_skills"],
        "filas_min": 3,
    },
    "outputs/predicciones_skills.csv": {
        "cols": ["ds", "yhat", "yhat_lower", "yhat_upper", "skill", "historico"],
        "filas_min": 100,
    },
    "outputs/skills_serie_historica.csv": {
        "cols": ["mes"],
        "filas_min": 12,
    },
    "outputs/modelo_salarios_coeficientes.csv": {
        "cols": ["feature", "coef_log", "impacto_pct"],
        "filas_min": 20,
    },
    "outputs/modelo_salarios_predicciones.csv": {
        "cols": ["oferta_id", "salario_anual_usd", "salario_predicho_usd",
                 "residuo_usd", "residuo_pct"],
        "filas_min": 1000,
    },
    "outputs/modelo_salarios_metricas.csv": {
        "cols": ["metric", "valor"],
        "filas_min": 3,
    },
}


def verificar_uno(ruta_relativa: str, esquema: dict) -> VerificacionTabla:
    if ruta_relativa.startswith("processed/"):
        full = PATHS.processed / ruta_relativa.split("/", 1)[1]
    else:
        full = PATHS.outputs / ruta_relativa.split("/", 1)[1]

    res = VerificacionTabla(archivo=ruta_relativa)

    if not full.exists():
        res.errores.append(f"Archivo no existe en {full}")
        return res

    res.existe = True
    res.tamano_bytes = full.stat().st_size

    if res.tamano_bytes < 100:
        res.errores.append(f"Archivo demasiado pequeno: {res.tamano_bytes} bytes")
        return res

    try:
        df = pd.read_csv(full, nrows=5)  # leer solo cabeceras para esquema
    except Exception as e:  # noqa: BLE001
        res.errores.append(f"No se puede leer CSV: {e}")
        return res

    res.columnas = len(df.columns)
    cols_faltantes = [c for c in esquema["cols"] if c not in df.columns]
    res.columnas_faltantes = cols_faltantes
    res.columnas_esperadas_ok = len(cols_faltantes) == 0

    if cols_faltantes:
        res.errores.append(
            f"Columnas obligatorias faltantes: {cols_faltantes}"
        )

    # Conteo completo de filas (mas barato que cargar el df entero para grandes archivos)
    with open(full, "r", encoding="utf-8-sig") as f:
        res.filas = sum(1 for _ in f) - 1  # -1 por la cabecera

    if res.filas < esquema["filas_min"]:
        res.errores.append(
            f"Filas insuficientes: {res.filas} (esperado >= {esquema['filas_min']})"
        )

    # Validaciones especificas
    if ruta_relativa == "outputs/modelo_salarios_metricas.csv":
        df_full = pd.read_csv(full)
        r2_row = df_full[df_full["metric"] == "R2_test"]
        if not r2_row.empty:
            r2 = float(r2_row["valor"].iloc[0])
            if r2 < 0.5:
                res.advertencias.append(f"R2 bajo: {r2:.3f}")
            elif r2 > 0.99:
                res.advertencias.append(f"R2 sospechosamente alto (overfit?): {r2:.3f}")

    if ruta_relativa == "outputs/predicciones_skills.csv":
        df_full = pd.read_csv(full)
        if "skill" in df_full.columns:
            n_skills = df_full["skill"].nunique()
            if n_skills < 5:
                res.advertencias.append(f"Solo {n_skills} skills con forecast (esperado >=8)")

    return res


def main() -> int:
    log.info("🔎 Verificacion de outputs del pipeline")
    resultados: list[VerificacionTabla] = []
    for ruta, esquema in ESQUEMAS_ESPERADOS.items():
        r = verificar_uno(ruta, esquema)
        resultados.append(r)
        if r.errores:
            log.info(f"❌ {ruta}")
            for e in r.errores:
                log.info(f"      • {e}")
        elif r.advertencias:
            log.info(f"⚠️  {ruta} ({r.filas:,} filas)")
            for a in r.advertencias:
                log.info(f"      • {a}")
        else:
            log.info(f"✅ {ruta} ({r.filas:,} filas × {r.columnas} columnas)")

    # Resumen
    total = len(resultados)
    ok = sum(1 for r in resultados if not r.errores)
    con_warnings = sum(1 for r in resultados if r.advertencias and not r.errores)
    con_errores = sum(1 for r in resultados if r.errores)
    log.info("")
    log.info(f"📊 Resumen: {ok}/{total} OK  |  {con_warnings} con advertencias  |  {con_errores} con errores")

    # Exportar reporte JSON (consumible por Power Automate)
    reporte = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_tablas": total,
        "tablas_ok": ok,
        "tablas_con_warnings": con_warnings,
        "tablas_con_errores": con_errores,
        "status_global": "OK" if con_errores == 0 else "FAIL",
        "detalle": [asdict(r) for r in resultados],
    }
    out_path = PATHS.outputs / "_verificacion.json"
    out_path.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"💾 Reporte exportado: {out_path.relative_to(PATHS.root)}")

    return 0 if con_errores == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
