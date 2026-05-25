"""
08_generar_alertas.py
=====================
Detecta variaciones MoM (mes contra mes) significativas en la demanda de
skills y emite un CSV con SOLO las skills que superan el umbral.

Este es el insumo que el Flujo 2 de Power Automate (Alertas de Skills)
consume: cuando este CSV se actualiza en OneDrive, el flujo dispara
emails con las skills que pasaron el umbral.

Entrada:  data/outputs/skills_serie_historica.csv
Salida:   data/outputs/alertas_skills.csv
"""
from __future__ import annotations

import pandas as pd

from utils import PATHS, load_csv, log, save_csv

UMBRAL_PCT = 30.0  # variacion absoluta MoM que dispara alerta


def detectar_alertas() -> pd.DataFrame:
    df = load_csv(PATHS.outputs / "skills_serie_historica.csv")

    # Asegurar tipos
    df["mes"] = pd.to_datetime(df["mes"])
    df = df.sort_values("mes").set_index("mes")

    # Variacion MoM por columna (skill)
    var_mom = df.pct_change() * 100

    # Tomamos el ultimo mes con datos para evaluar alerta
    ultimo_mes = df.index.max()
    mes_anterior = df.index[-2] if len(df) >= 2 else None
    if mes_anterior is None:
        log.warning("⚠️  No hay suficiente historico para calcular MoM (necesita >=2 meses)")
        return pd.DataFrame()

    fila_var = var_mom.loc[ultimo_mes]
    fila_act = df.loc[ultimo_mes]
    fila_ant = df.loc[mes_anterior]

    alertas = pd.DataFrame({
        "skill": fila_var.index,
        "mes_actual": ultimo_mes.date().isoformat(),
        "mes_anterior": mes_anterior.date().isoformat(),
        "ofertas_mes_actual": fila_act.values,
        "ofertas_mes_anterior": fila_ant.values,
        "variacion_pct": fila_var.values,
    })

    # Filtrar a las que pasaron el umbral
    alertas = alertas.dropna(subset=["variacion_pct"])
    alertas = alertas[alertas["variacion_pct"].abs() >= UMBRAL_PCT]

    # Direccion + severidad
    alertas["direccion"] = alertas["variacion_pct"].apply(
        lambda v: "ALZA" if v > 0 else "BAJA"
    )
    alertas["severidad"] = alertas["variacion_pct"].abs().apply(
        lambda v: "CRITICA" if v >= 60 else ("ALTA" if v >= 45 else "MEDIA")
    )
    alertas["mensaje"] = alertas.apply(
        lambda r: f"{r['skill']}: {r['direccion']} de {abs(r['variacion_pct']):.1f}% "
                  f"({int(r['ofertas_mes_anterior'])} → {int(r['ofertas_mes_actual'])} ofertas)",
        axis=1,
    )
    alertas = alertas.sort_values("variacion_pct", key=abs, ascending=False)
    return alertas.reset_index(drop=True)


def main() -> None:
    log.info(f"🚨 Detectando alertas MoM (umbral ±{UMBRAL_PCT:.0f}%)")
    alertas = detectar_alertas()
    if alertas.empty:
        log.info("✅ Sin alertas — ninguna skill supero el umbral este mes.")
        # Igual generar el archivo (vacio pero con cabeceras) para que Power Automate
        # no falle si lo intenta leer.
        alertas = pd.DataFrame(columns=[
            "skill", "mes_actual", "mes_anterior", "ofertas_mes_actual",
            "ofertas_mes_anterior", "variacion_pct", "direccion", "severidad", "mensaje",
        ])
    else:
        log.info(f"🚨 {len(alertas)} skills disparan alerta:")
        for _, r in alertas.iterrows():
            log.info(f"   • [{r['severidad']:>7s}] {r['mensaje']}")

    save_csv(alertas, PATHS.outputs / "alertas_skills.csv")


if __name__ == "__main__":
    main()
