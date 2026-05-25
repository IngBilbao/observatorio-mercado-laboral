# 📖 Diccionario de Datos — Observatorio del Mercado Laboral

Este documento describe el esquema canónico del dataset consolidado y los outputs intermedios del pipeline. Todos los CSVs usan codificación **UTF-8 con BOM** y separador `,`.

---

## 1. `data/processed/datos_consolidados.csv`

Dataset crudo unificado (sintético en fase 1; sintético + Kaggle + Adzuna + Remotive en fase 2).

| Columna              | Tipo          | Descripción                                                              |
|----------------------|---------------|--------------------------------------------------------------------------|
| `oferta_id`          | string        | Identificador único de la oferta (formato `OBS-######` para sintéticos). |
| `fecha_publicacion`  | date          | Fecha de publicación de la oferta (ISO `YYYY-MM-DD`).                    |
| `titulo_cargo`       | string        | Título tal como aparece en la oferta.                                    |
| `rol_normalizado`    | categórica    | Rol estandarizado (ver catálogo abajo).                                  |
| `nivel_experiencia`  | categórica    | `Junior` · `Mid` · `Senior` · `Lead`.                                    |
| `anios_experiencia`  | int           | Años de experiencia requeridos.                                          |
| `empresa`            | string        | Razón social / nombre comercial.                                         |
| `ciudad`             | string        | Ciudad de la oferta (o `Remoto`).                                        |
| `pais`               | string        | País de la oferta (o `Global` para remoto sin restricción).              |
| `codigo_pais`        | ISO 3166-1    | Código de 2 letras (`ES`, `US`, `MX`, `WW` para global).                 |
| `latitud`            | float         | Latitud de la ciudad (para mapa en Power BI).                            |
| `longitud`           | float         | Longitud de la ciudad.                                                   |
| `modalidad`          | categórica    | `Remoto` · `Híbrido` · `Presencial`.                                     |
| `tipo_contrato`      | categórica    | `Indefinido` · `Temporal` · `Freelance` · `Prácticas`.                   |
| `moneda_original`    | ISO 4217      | Moneda original del salario (`EUR`, `USD`, `GBP`, etc.).                 |
| `salario_anual_usd`  | float         | Salario anual normalizado a USD.                                         |
| `skills_detectadas`  | string        | Lista de skills separadas por `\|` (ej. `Python\|SQL\|Power BI`).        |
| `n_skills`           | int           | Conteo de skills detectadas.                                             |
| `descripcion`        | string        | Texto descriptivo de la oferta (para NLP).                               |
| `fuente`             | string        | Origen del dato (`sintetico_v1`, `kaggle_so2024`, `adzuna`, etc.).       |

### Catálogo de `rol_normalizado`
`Data Analyst` · `BI Analyst` · `Data Scientist` · `Data Engineer` · `ML Engineer` · `Analytics Engineer` · `Business Analyst` · `Financial Analyst`.

---

## 2. `data/processed/datos_limpios.csv`

Mismo esquema que el anterior + columnas derivadas:

| Columna  | Tipo  | Descripción                              |
|----------|-------|------------------------------------------|
| `anio`   | int   | Año extraído de `fecha_publicacion`.     |
| `mes`    | int   | Mes (1–12).                              |
| `anio_mes` | string | `YYYY-MM` — útil como dimensión PBI. |

---

## 3. `data/processed/matriz_skills.csv`

Igual a `datos_limpios.csv` + **una columna booleana por skill** del catálogo.

Convención de nombre: `skill_<nombre_en_snake_case>` — ejemplos:

`skill_python`, `skill_sql`, `skill_excel`, `skill_power_bi`, `skill_tableau`, `skill_looker`, `skill_r`, `skill_sas`, `skill_spss`, `skill_spark`, `skill_hadoop`, `skill_airflow`, `skill_dbt`, `skill_snowflake`, `skill_bigquery`, `skill_redshift`, `skill_databricks`, `skill_aws`, `skill_azure`, `skill_gcp`, `skill_docker`, `skill_kubernetes`, `skill_git`, `skill_pandas`, `skill_numpy`, `skill_scikit_learn`, `skill_tensorflow`, `skill_pytorch`, `skill_power_automate`, `skill_power_query`, `skill_dax`, `skill_vba`, `skill_machine_learning`, `skill_deep_learning`, `skill_nlp`.

Cada columna es `True/False`.

---

## 4. `data/outputs/clusters_perfiles.csv`

Matriz de skills + asignación de cluster:

| Columna           | Tipo   | Descripción                                          |
|-------------------|--------|------------------------------------------------------|
| `cluster_id`      | int    | ID numérico del cluster (0 a k-1).                   |
| `cluster_nombre`  | string | Etiqueta legible (rol dominante + top 2 skills).     |

## 5. `data/outputs/clusters_resumen.csv`

Una fila por cluster.

| Columna             | Tipo   | Descripción                                |
|---------------------|--------|--------------------------------------------|
| `cluster_id`        | int    | ID del cluster.                            |
| `cluster_nombre`    | string | Nombre legible del cluster.                |
| `n_ofertas`         | int    | Ofertas asignadas.                         |
| `pct_total`         | float  | % del total de ofertas.                    |
| `rol_dominante`     | string | Rol más frecuente en el cluster.           |
| `salario_mediano_usd`| float | Mediana del salario USD.                   |
| `anios_exp_promedio`| float  | Años de experiencia promedio.              |
| `top_skills`        | string | Top 3 skills del cluster.                  |

---

## 6. `data/outputs/predicciones_skills.csv` (formato largo)

| Columna       | Tipo    | Descripción                                              |
|---------------|---------|----------------------------------------------------------|
| `ds`          | date    | Mes (primer día del mes).                                |
| `yhat`        | float   | Valor central predicho por Prophet.                      |
| `yhat_lower`  | float   | Banda inferior IC 80%.                                   |
| `yhat_upper`  | float   | Banda superior IC 80%.                                   |
| `skill`       | string  | Nombre legible de la skill.                              |
| `historico`   | bool    | `True` si la fila corresponde a un mes histórico; `False` si es forecast. |

## 7. `data/outputs/skills_serie_historica.csv` (formato ancho)

Una fila por mes, una columna por skill. Pensado para gráficas multi-línea en Power BI.

---

## 8. `data/outputs/modelo_salarios_*.csv`

### `modelo_salarios_coeficientes.csv`
| Columna       | Descripción                                                       |
|---------------|-------------------------------------------------------------------|
| `feature`     | Nombre del predictor (skill, nivel, país, modalidad...).          |
| `coef_log`    | Coeficiente sobre `log(salario)`.                                 |
| `impacto_pct` | Impacto interpretable: `(exp(coef) - 1) × 100` ≈ % cambio en salario al activar la variable, ceteris paribus. |

### `modelo_salarios_predicciones.csv`
Predicción individual por oferta con residuos.

### `modelo_salarios_metricas.csv`
R², RMSE, n_features, n_train, n_test.

---

## Convenciones de tipos al cargar en Power BI / Excel

- Fechas → tipo **Fecha** (no datetime).
- Booleanos de skills → tipo **Verdadero/Falso**.
- Salarios → tipo **Decimal fijo**.
- Códigos de país → tipo **Texto** (para evitar pérdida del `0` inicial).
