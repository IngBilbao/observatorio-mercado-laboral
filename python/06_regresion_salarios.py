"""
06_regresion_salarios.py
========================
Modelo de regresión lineal múltiple para estimar el salario anual (USD)
en función de skills, experiencia, ubicación, modalidad y tipo de contrato.

- Variable dependiente: log(salario_anual_usd) → estabiliza varianza.
- Variables independientes:
    * skills booleanas (skill_*)
    * anios_experiencia
    * nivel_experiencia (one-hot)
    * pais (one-hot, top 10 + "Otros")
    * modalidad (one-hot)
    * tipo_contrato (one-hot)
- Validación: split 80/20, métricas R² y RMSE.
- Exporta coeficientes interpretables (impacto en %) y predicciones.

Entrada:  data/processed/matriz_skills.csv
Salidas:
  - data/outputs/modelo_salarios_coeficientes.csv
  - data/outputs/modelo_salarios_predicciones.csv
  - data/outputs/modelo_salarios_metricas.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from utils import PATHS, SKILLS_CATALOG, load_csv, log, save_csv, skill_to_column

RNG_SEED = 42
TOP_N_PAISES = 10


def _preparar_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    skill_cols = [skill_to_column(s) for s in SKILLS_CATALOG.keys()]
    base = df[skill_cols + ["anios_experiencia"]].copy()

    # Top N países, resto agrupado
    top_paises = df["pais"].value_counts().head(TOP_N_PAISES).index.tolist()
    df["pais_grp"] = df["pais"].where(df["pais"].isin(top_paises), other="Otros")

    dummies = pd.get_dummies(df[["nivel_experiencia", "pais_grp", "modalidad",
                                  "tipo_contrato"]], drop_first=True)
    X = pd.concat([base, dummies], axis=1).astype(float)
    return X, skill_cols


def entrenar(df: pd.DataFrame) -> dict:
    X, skill_cols = _preparar_features(df)
    y = np.log(df["salario_anual_usd"].clip(lower=1))

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, random_state=RNG_SEED)
    modelo = LinearRegression().fit(X_tr, y_tr)
    y_pred_te = modelo.predict(X_te)

    r2 = r2_score(y_te, y_pred_te)
    rmse_log = np.sqrt(mean_squared_error(y_te, y_pred_te))
    # RMSE en USD (aprox) tras revertir log
    rmse_usd = np.sqrt(mean_squared_error(np.exp(y_te), np.exp(y_pred_te)))
    log.info(f"📈 R² test: {r2:.4f}")
    log.info(f"📉 RMSE log-USD: {rmse_log:.4f}  |  RMSE USD aprox: ${rmse_usd:,.0f}")

    # Coeficientes interpretables (impacto en % sobre salario)
    coefs = pd.DataFrame({
        "feature": X.columns,
        "coef_log": modelo.coef_,
        "impacto_pct": (np.exp(modelo.coef_) - 1) * 100,
    }).sort_values("impacto_pct", ascending=False)

    # Predicciones sobre el dataset completo
    y_pred_full = np.exp(modelo.predict(X))
    df_pred = df[["oferta_id", "rol_normalizado", "nivel_experiencia", "pais",
                  "salario_anual_usd"]].copy()
    df_pred["salario_predicho_usd"] = y_pred_full
    df_pred["residuo_usd"] = df_pred["salario_anual_usd"] - df_pred["salario_predicho_usd"]
    df_pred["residuo_pct"] = df_pred["residuo_usd"] / df_pred["salario_anual_usd"] * 100

    metricas = pd.DataFrame([{
        "metric": "R2_test", "valor": r2,
    }, {
        "metric": "RMSE_log", "valor": rmse_log,
    }, {
        "metric": "RMSE_USD_aprox", "valor": rmse_usd,
    }, {
        "metric": "n_features", "valor": X.shape[1],
    }, {
        "metric": "n_train", "valor": len(X_tr),
    }, {
        "metric": "n_test", "valor": len(X_te),
    }])

    return {"coefs": coefs, "predicciones": df_pred, "metricas": metricas}


def main() -> None:
    df = load_csv(PATHS.processed / "matriz_skills.csv")
    out = entrenar(df)
    save_csv(out["coefs"], PATHS.outputs / "modelo_salarios_coeficientes.csv")
    save_csv(out["predicciones"], PATHS.outputs / "modelo_salarios_predicciones.csv")
    save_csv(out["metricas"], PATHS.outputs / "modelo_salarios_metricas.csv")
    log.info("🏁 Modelo de salarios entrenado y exportado.")
    log.info("🔝 Top 10 features con mayor impacto positivo:\n" +
             out["coefs"].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
