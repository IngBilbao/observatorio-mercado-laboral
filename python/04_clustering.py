"""
04_clustering.py
================
Segmenta perfiles profesionales con K-means sobre la matriz de skills.

- Selecciona k óptimo en [3..7] mediante silueta (silhouette score).
- Asigna etiqueta de cluster por oferta.
- Etiqueta cada cluster con el rol_normalizado predominante + top skills.
- Reduce a 2D con PCA y exporta gráfico a docs/imagenes/.

Entrada:  data/processed/matriz_skills.csv
Salidas:
  - data/outputs/clusters_perfiles.csv  (matriz + columna cluster_id + cluster_nombre)
  - data/outputs/clusters_resumen.csv   (resumen por cluster)
  - docs/imagenes/clusters_pca.png      (visualización)
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils import (BRAND, PATHS, SKILLS_CATALOG, apply_matplotlib_theme,
                   load_csv, log, save_csv, skill_to_column)

K_RANGE = range(3, 8)
RNG_SEED = 42


def _skill_cols() -> list[str]:
    return [skill_to_column(s) for s in SKILLS_CATALOG.keys()]


def encontrar_k_optimo(X: np.ndarray) -> int:
    log.info(f"🔍 Buscando k óptimo en {list(K_RANGE)}...")
    mejor_k, mejor_score = K_RANGE.start, -1.0
    # Muestreo para silueta (es O(n²))
    rng = np.random.default_rng(RNG_SEED)
    idx_muestra = rng.choice(len(X), size=min(2000, len(X)), replace=False)
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=RNG_SEED, n_init=10).fit(X)
        score = silhouette_score(X[idx_muestra], km.labels_[idx_muestra])
        log.info(f"   k={k}  silueta={score:.4f}")
        if score > mejor_score:
            mejor_k, mejor_score = k, score
    log.info(f"🏅 k óptimo: {mejor_k} (silueta={mejor_score:.4f})")
    return mejor_k


def etiquetar_clusters(df: pd.DataFrame, k: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Asigna nombre legible a cada cluster: rol mayoritario + top 3 skills."""
    resumen = []
    nombres = {}
    skill_cols = _skill_cols()
    for cid in sorted(df["cluster_id"].unique()):
        sub = df[df["cluster_id"] == cid]
        rol_top = sub["rol_normalizado"].mode().iat[0]
        top_skills = sub[skill_cols].mean().sort_values(ascending=False).head(3)
        skills_nombres = [c.replace("skill_", "").replace("_", " ").title()
                          for c in top_skills.index]
        nombre = f"{rol_top} · {' + '.join(skills_nombres[:2])}"
        nombres[cid] = nombre
        resumen.append({
            "cluster_id": cid,
            "cluster_nombre": nombre,
            "n_ofertas": len(sub),
            "pct_total": len(sub) / len(df) * 100,
            "rol_dominante": rol_top,
            "salario_mediano_usd": sub["salario_anual_usd"].median(),
            "anios_exp_promedio": sub["anios_experiencia"].mean(),
            "top_skills": ", ".join(skills_nombres),
        })
    df["cluster_nombre"] = df["cluster_id"].map(nombres)
    return df, pd.DataFrame(resumen)


def visualizar_pca(X: np.ndarray, labels: np.ndarray, nombres_cluster: dict[int, str]) -> None:
    apply_matplotlib_theme()
    pca = PCA(n_components=2, random_state=RNG_SEED).fit_transform(X)
    fig, ax = plt.subplots(figsize=(11, 7))
    colores = BRAND.matplotlib_palette
    for cid in sorted(set(labels)):
        mask = labels == cid
        ax.scatter(pca[mask, 0], pca[mask, 1],
                   s=18, alpha=0.55, color=colores[cid % len(colores)],
                   label=nombres_cluster.get(cid, f"Cluster {cid}"))
    ax.set_title("Perfiles profesionales — K-means + PCA (2D)", fontsize=14, pad=14)
    ax.set_xlabel("Componente principal 1")
    ax.set_ylabel("Componente principal 2")
    ax.legend(loc="best", fontsize=9, framealpha=0.3)

    out_dir = PATHS.docs / "imagenes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "clusters_pca.png"
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=BRAND.bg_deep)
    plt.close(fig)
    log.info(f"🖼️  Gráfico PCA → {out_path.relative_to(PATHS.root)}")


def main() -> None:
    df = load_csv(PATHS.processed / "matriz_skills.csv")
    skill_cols = _skill_cols()
    X = StandardScaler().fit_transform(df[skill_cols].astype(int).values)

    k = encontrar_k_optimo(X)
    km = KMeans(n_clusters=k, random_state=RNG_SEED, n_init=10).fit(X)
    df["cluster_id"] = km.labels_

    df, resumen = etiquetar_clusters(df, k)
    visualizar_pca(X, km.labels_, dict(zip(resumen["cluster_id"], resumen["cluster_nombre"])))

    save_csv(df, PATHS.outputs / "clusters_perfiles.csv")
    save_csv(resumen, PATHS.outputs / "clusters_resumen.csv")
    log.info("📋 Resumen de clusters:\n" + resumen.to_string(index=False))


if __name__ == "__main__":
    main()
