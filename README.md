# 🌌 Observatorio del Mercado Laboral en Datos & Tecnología

> Proyecto integral de **Bilbao Analytics** que recolecta, procesa, analiza y presenta automáticamente información sobre la demanda de habilidades tecnológicas (Excel, Power BI, Python, SQL, etc.) en el mercado laboral, con modelos estadísticos y alertas automatizadas.

---

## 🎯 Propósito

1. **Inteligencia de mercado:** entender en tiempo casi-real qué skills demandan los empleadores, cómo evolucionan los salarios y dónde están las oportunidades.
2. **Portafolio profesional:** demostrar dominio end-to-end de un stack analítico moderno — Python (data science), Excel avanzado (Power Query), Power BI y Power Automate.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│  FUENTES                                                          │
│  • Datos sintéticos (fase 1 — bootstrap)                          │
│  • Kaggle: Stack Overflow Survey, DS Salaries, LinkedIn postings  │
│  • APIs: Adzuna + Remotive (ofertas reales, legales y estables)   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  PYTHON  (data/processed/ + data/outputs/)                        │
│  00 → datos sintéticos                                            │
│  01 → extracción y consolidación                                  │
│  02 → limpieza y normalización                                    │
│  03 → NLP de skills (spaCy)                                       │
│  04 → clustering de perfiles (K-means + PCA)                      │
│  05 → series de tiempo (Prophet, forecast 12 meses)               │
│  06 → regresión salarial (multilineal)                            │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  EXCEL  (observatorio_staging.xlsx — Power Query)                 │
│  Datos_Base · Resumen_Skills · Análisis_Salarial ·                │
│  Predicciones · Skill_Gap · Dashboard_Excel                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  POWER BI  (observatorio.pbix — esquema estrella)                 │
│  Resumen Ejecutivo · Skills · Salarios · Mapa · Predicciones ·    │
│  Perfiles (Clusters)                                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  POWER AUTOMATE                                                   │
│  • Reporte semanal (lunes 8AM → refresh PBI → email con PDF)      │
│  • Alertas de cambio en skills (umbral 30% MoM → email/push)      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```powershell
# 1. Crear entorno virtual (recomendado)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r python/requirements.txt
py -m spacy download en_core_web_sm

# 3. Generar dataset sintético (5000 ofertas)
py python/00_generar_datos_sinteticos.py

# 4. Ejecutar el pipeline completo
py python/01_extraccion.py
py python/02_limpieza.py
py python/03_nlp_skills.py
py python/04_clustering.py
py python/05_series_tiempo.py
py python/06_regresion_salarios.py

# 5. Abrir Excel y refrescar Power Query (excel/observatorio_staging.xlsx)
# 6. Abrir Power BI y refrescar (powerbi/observatorio.pbix)
# 7. Importar flujos a Power Automate (power_automate/*.json)
```

---

## 📁 Estructura del Repositorio

```
observatorio-mercado-laboral/
├── README.md                     ← este archivo
├── proyecto.md                   ← spec original
├── .gitignore
│
├── data/
│   ├── raw/                      ← datasets descargados (no versionados)
│   ├── processed/                ← datos limpios
│   └── outputs/                  ← outputs finales (PBI/Excel)
│
├── python/
│   ├── requirements.txt
│   ├── utils.py                  ← paths, branding, helpers compartidos
│   ├── 00_generar_datos_sinteticos.py
│   ├── 01_extraccion.py
│   ├── 02_limpieza.py
│   ├── 03_nlp_skills.py
│   ├── 04_clustering.py
│   ├── 05_series_tiempo.py
│   └── 06_regresion_salarios.py
│
├── excel/
│   └── observatorio_staging.xlsx
│
├── powerbi/
│   └── observatorio.pbix
│
├── power_automate/
│   ├── README.md                 ← guía para crear/importar flujos
│   ├── flujo_reporte_semanal.json
│   └── flujo_alertas_skills.json
│
├── notebooks/                    ← exploración ad-hoc
├── assets/                       ← logos, imágenes, paleta
└── docs/
    ├── diccionario_datos.md
    └── guia_visualizaciones.md
```

---

## 🧪 Modelos Estadísticos

| Modelo                     | Librería                  | Propósito                                    |
|----------------------------|---------------------------|----------------------------------------------|
| K-means + PCA              | scikit-learn              | Segmentar arquetipos profesionales (k=4–6)   |
| Prophet                    | prophet                   | Forecast 12 meses de demanda por skill       |
| Regresión Lineal Múltiple  | statsmodels / sklearn     | Estimación salarial multivariable            |
| Correlación de Pearson     | pandas + seaborn          | Skills que aparecen juntas (heatmap)         |

---

## 🎨 Identidad Visual — Bilbao Analytics

Temática **universo / espacio exterior**.

| Token         | Hex       | Uso                                  |
|---------------|-----------|--------------------------------------|
| Fondo profundo| `#0D0D1A` | Background principal Power BI        |
| Fondo medio   | `#1A1A2E` | Tarjetas, paneles                    |
| Azul eléctrico| `#00D4FF` | KPIs, líneas, acentos primarios      |
| Violeta       | `#7B2FBE` | Acentos secundarios, categorías      |
| Texto         | `#E8E8F0` | Texto principal sobre fondo oscuro   |

Tipografía: **Segoe UI** (Power BI), **Calibri** (Excel).

---

## 📊 Estado del Proyecto

| Fase                              | Estado  |
|-----------------------------------|---------|
| Scaffold del repositorio          | ✅       |
| Generador de datos sintéticos     | ✅       |
| Pipeline Python (esqueletos)      | ✅       |
| Pipeline Python (implementación)  | 🚧       |
| Excel + Power Query               | ⏳       |
| Dashboard Power BI                | ⏳       |
| Flujos Power Automate             | ⏳       |
| Integración Adzuna + Remotive     | ⏳       |
| Sustitución datos reales (Kaggle) | ⏳       |

---

## 👤 Autor

**Bilbao Analytics** — consultoría en datos e inteligencia analítica.
Construido como caso de estudio integral para demostrar dominio del stack moderno de análisis de datos.

## 📜 Licencia

MIT — ver `LICENSE` (pendiente).
