"""
05_series_tiempo.py
===================
Forecast de demanda mensual de skills a 12 meses con Prophet.

- Agrega conteo mensual de ofertas por skill.
- Ajusta un modelo Prophet por cada skill del top-N.
- Exporta una tabla larga con histórico + forecast + intervalos de confianza,
  lista para visualizar en Power BI.

Entrada:  data/processed/matriz_skills.csv
Salidas:
  - data/outputs/predicciones_skills.csv      (formato largo)
  - data/outputs/skills_serie_historica.csv   (mensual, formato ancho)
  - docs/imagenes/forecast_top_skills.png
"""
from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import pandas as pd

from utils import (BRAND, PATHS, SKILLS_CATALOG, apply_matplotlib_theme,
                   load_csv, log, save_csv, skill_to_column)

warnings.filterwarnings("ignore", category=FutureWarning)

TOP_N_SKILLS = 12
MESES_FORECAST = 12


def _skill_cols() -> list[str]:
    return [skill_to_column(s) for s in SKILLS_CATALOG.keys()]


def agregar_mensual(df: pd.DataFrame) -> pd.DataFrame:
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"])
    df["mes"] = df["fecha_publicacion"].dt.to_period("M").dt.to_timestamp()
    skill_cols = _skill_cols()
    mensual = df.groupby("mes")[skill_cols].sum().reset_index()
    return mensual


def seleccionar_top_skills(mensual: pd.DataFrame, n: int = TOP_N_SKILLS) -> list[str]:
    skill_cols = _skill_cols()
    totales = mensual[skill_cols].sum().sort_values(ascending=False)
    return totales.head(n).index.tolist()


def forecast_skill(serie: pd.DataFrame, periodos: int = MESES_FORECAST) -> pd.DataFrame:
    """serie: DataFrame con cols [ds, y]. Devuelve DataFrame Prophet con forecast."""
    from prophet import Prophet
    modelo = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.80,
    )
    modelo.fit(serie)
    futuro = modelo.make_future_dataframe(periods=periodos, freq="MS")
    fcst = modelo.predict(futuro)
    return fcst[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def construir_predicciones(mensual: pd.DataFrame, top_skills: list[str]) -> pd.DataFrame:
    log.info(f"🔮 Prophet forecast de {len(top_skills)} skills × {MESES_FORECAST} meses")
    bloques = []
    for col in top_skills:
        skill_legible = col.replace("skill_", "").replace("_", " ").title()
        serie = mensual[["mes", col]].rename(columns={"mes": "ds", col: "y"})
        fcst = forecast_skill(serie)
        fcst["skill"] = skill_legible
        fcst["historico"] = fcst["ds"].isin(serie["ds"])
        bloques.append(fcst)
        log.info(f"   ✓ {skill_legible}")
    return pd.concat(bloques, ignore_index=True)


def visualizar(predicciones: pd.DataFrame, top_skills: list[str]) -> None:
    apply_matplotlib_theme()
    skills_a_graficar = [s.replace("skill_", "").replace("_", " ").title()
                         for s in top_skills[:6]]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), sharex=True)
    paleta = BRAND.matplotlib_palette
    for i, skill in enumerate(skills_a_graficar):
        ax = axes[i // 3][i % 3]
        sub = predicciones[predicciones["skill"] == skill]
        hist = sub[sub["historico"]]
        futuro = sub[~sub["historico"]]
        ax.plot(hist["ds"], hist["yhat"], color=paleta[0], linewidth=2, label="Histórico")
        ax.plot(futuro["ds"], futuro["yhat"], color=paleta[1], linewidth=2,
                linestyle="--", label="Forecast")
        ax.fill_between(futuro["ds"], futuro["yhat_lower"], futuro["yhat_upper"],
                        color=paleta[1], alpha=0.18)
        ax.set_title(skill, fontsize=12)
        ax.grid(True, alpha=0.2)
        if i == 0:
            ax.legend(fontsize=9)
    fig.suptitle("Forecast de demanda mensual por skill — 12 meses", fontsize=14, y=1.00)
    fig.tight_layout()

    out_dir = PATHS.docs / "imagenes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "forecast_top_skills.png"
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=BRAND.bg_deep)
    plt.close(fig)
    log.info(f"🖼️  Gráfico forecast → {out_path.relative_to(PATHS.root)}")


def main() -> None:
    df = load_csv(PATHS.processed / "matriz_skills.csv")
    mensual = agregar_mensual(df)

    # Exportar histórico mensual (ancho) para Power BI
    mensual_renombrado = mensual.rename(columns={
        c: c.replace("skill_", "").replace("_", " ").title() if c.startswith("skill_") else c
        for c in mensual.columns
    })
    save_csv(mensual_renombrado, PATHS.outputs / "skills_serie_historica.csv")

    top_skills = seleccionar_top_skills(mensual)
    predicciones = construir_predicciones(mensual, top_skills)
    save_csv(predicciones, PATHS.outputs / "predicciones_skills.csv")

    visualizar(predicciones, top_skills)


if __name__ == "__main__":
    main()
