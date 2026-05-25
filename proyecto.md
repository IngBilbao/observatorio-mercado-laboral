# CLAUDE.md — Observatorio del Mercado Laboral en Datos & Tecnología
**Proyecto Bilbao Analytics | Autor: Bilbao Analytics**

---

## 🎯 Objetivo del Proyecto

Construir un sistema integral que recolecte, procese, analice y presente automáticamente información sobre la demanda de habilidades tecnológicas en el mercado laboral (Excel, Power BI, Python, SQL, etc.), integrando Power Automate, Excel, Power BI, Python (data science) y modelos estadísticos.

---

## 🏗️ Arquitectura General

```
[APIs / Datasets públicos]
        ↓
[Python: scraping + limpieza + modelos ML]
        ↓
[Excel: staging, transformaciones ETL, modelo financiero]
        ↓
[Power BI: dashboard interactivo + insights]
        ↓
[Power Automate: reportes automáticos + alertas por email]
```

---

## 🗂️ Estructura de Carpetas del Proyecto

```
observatorio-mercado-laboral/
│
├── CLAUDE.md                        ← este archivo
├── README.md                        ← documentación general
│
├── data/
│   ├── raw/                         ← datos sin procesar descargados
│   ├── processed/                   ← datos limpios listos para usar
│   └── outputs/                     ← archivos finales para Power BI y Excel
│
├── python/
│   ├── 01_extraccion.py             ← descarga de datasets y scraping
│   ├── 02_limpieza.py               ← limpieza y normalización de datos
│   ├── 03_nlp_skills.py             ← extracción de habilidades con NLP
│   ├── 04_clustering.py             ← segmentación de perfiles (K-means)
│   ├── 05_series_tiempo.py          ← predicción de demanda (Prophet/ARIMA)
│   ├── 06_regresion_salarios.py     ← estimación salarial (regresión múltiple)
│   └── requirements.txt
│
├── excel/
│   └── observatorio_staging.xlsx    ← archivo Excel con Power Query + tablas
│
├── powerbi/
│   └── observatorio.pbix            ← archivo Power BI Desktop
│
├── power_automate/
│   ├── flujo_reporte_semanal.json   ← exportación del flujo de reporte
│   └── flujo_alertas_skills.json    ← exportación del flujo de alertas
│
└── docs/
    ├── diccionario_datos.md
    └── guia_visualizaciones.md
```

---

## 📦 Fuentes de Datos (todas públicas y gratuitas)

| Dataset | URL | Uso |
|---|---|---|
| Stack Overflow Survey 2024 | https://survey.stackoverflow.co/datasets | Skills, salarios, tecnologías |
| Kaggle: DS Job Salaries | https://www.kaggle.com/datasets/hummaamqasim/ds-job-salaries | Salarios por rol y país |
| Kaggle: LinkedIn Job Postings | https://www.kaggle.com/datasets/arshkon/linkedin-job-postings | Ofertas laborales reales |
| BLS Occupational Employment | https://www.bls.gov/oes/tables.htm | Estadísticas de empleo EE.UU. |

> ⚠️ Descarga los archivos y colócalos en `data/raw/` antes de ejecutar los scripts de Python.

---

## 🐍 Módulo Python — Instrucciones por Script

### `requirements.txt` — Instalar con:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn prophet statsmodels nltk spacy openpyxl kaggle
python -m spacy download en_core_web_sm
```

### `01_extraccion.py`
- Cargar los CSV de Kaggle desde `data/raw/`
- Unificar datasets en un único DataFrame consolidado
- Exportar a `data/processed/datos_consolidados.csv`

### `02_limpieza.py`
- Eliminar duplicados y filas con nulos críticos
- Normalizar nombres de skills (ej: "Power BI" = "powerbi" = "Power BI Desktop" → "Power BI")
- Estandarizar monedas a USD usando tasa fija
- Exportar a `data/processed/datos_limpios.csv`

### `03_nlp_skills.py`
- Usar `spacy` para tokenizar descripciones de cargo
- Extraer menciones de: Python, SQL, Excel, Power BI, Tableau, R, Spark, dbt, Airflow, etc.
- Crear columnas booleanas por cada skill detectada
- Exportar matriz de skills a `data/processed/matriz_skills.csv`

### `04_clustering.py`
- Aplicar K-means (k=4 a 6) sobre la matriz de skills
- Identificar arquetipos: "Analista BI", "Data Scientist", "Data Engineer", "Analista Generalista"
- Graficar clusters con PCA (2D) usando Matplotlib
- Exportar resultados a `data/outputs/clusters_perfiles.csv`

### `05_series_tiempo.py`
- Agregar conteo mensual de ofertas por skill
- Aplicar modelo **Prophet** para proyectar los próximos 12 meses
- Generar gráficas de tendencia + intervalos de confianza
- Exportar predicciones a `data/outputs/predicciones_skills.csv`

### `06_regresion_salarios.py`
- Variable dependiente: salario anual (USD)
- Variables independientes: skills (booleanas), años de experiencia, ubicación, tipo de contrato
- Usar regresión lineal múltiple + validación con R² y RMSE
- Exportar coeficientes y predicciones a `data/outputs/modelo_salarios.csv`

---

## 📊 Módulo Excel — `observatorio_staging.xlsx`

Crear las siguientes hojas con Power Query conectado a los CSV de `data/outputs/`:

| Hoja | Contenido |
|---|---|
| `Datos_Base` | Dataset completo limpio |
| `Resumen_Skills` | Top 20 skills más demandadas (tabla dinámica) |
| `Análisis_Salarial` | Rangos salariales por rol y región |
| `Predicciones` | Tabla con proyecciones de Prophet por skill |
| `Skill_Gap` | Comparativo demanda vs. oferta educativa estimada |
| `Dashboard_Excel` | Mini-dashboard con gráficos y segmentadores |

> Usar Power Query para automatizar la actualización desde los CSV. Configurar conexión en: Datos → Obtener datos → Desde texto/CSV.

---

## 📈 Módulo Power BI — `observatorio.pbix`

### Modelo de Datos (Esquema Estrella)
```
Fact_Ofertas ──→ Dim_Skills
             ──→ Dim_Roles
             ──→ Dim_Ubicacion
             ──→ Dim_Calendario
             ──→ Dim_Empresa
```

### Páginas del Dashboard

1. **Resumen Ejecutivo** — KPIs principales: total ofertas, top 5 skills, salario promedio, variación mensual
2. **Análisis de Skills** — Ranking, matriz de correlación entre skills, evolución temporal
3. **Inteligencia Salarial** — Distribución por rol, región, nivel de experiencia
4. **Mapa Geográfico** — Densidad de ofertas por ciudad/país
5. **Predicciones** — Gráfico de serie de tiempo con forecast de Prophet importado
6. **Perfiles / Clusters** — Visualización de los arquetipos identificados en Python

### Medidas DAX Clave a Crear
```dax
-- Total Ofertas
Total Ofertas = COUNTROWS(Fact_Ofertas)

-- Salario Promedio
Salario Promedio = AVERAGE(Fact_Ofertas[Salario_USD])

-- % Ofertas con Python
% Python = DIVIDE(CALCULATE([Total Ofertas], Fact_Ofertas[skill_python]=TRUE()), [Total Ofertas])

-- Variación MoM
Var MoM Ofertas = 
    VAR MesActual = [Total Ofertas]
    VAR MesAnterior = CALCULATE([Total Ofertas], DATEADD(Dim_Calendario[Fecha], -1, MONTH))
    RETURN DIVIDE(MesActual - MesAnterior, MesAnterior)
```

---

## ⚡ Módulo Power Automate — Flujos a Crear

### Flujo 1: Reporte Semanal Automático
- **Trigger:** Recurrencia → cada lunes a las 8:00 AM
- **Paso 1:** Actualizar dataset en SharePoint (subir nuevo CSV procesado)
- **Paso 2:** Actualizar Power BI dataset vía API REST de Power BI
- **Paso 3:** Exportar página del dashboard como imagen/PDF
- **Paso 4:** Enviar email con resumen + imagen adjunta a lista de contactos

### Flujo 2: Alertas de Cambio en Skills
- **Trigger:** Cuando se actualiza el archivo Excel en OneDrive/SharePoint
- **Condición:** Si alguna skill supera el 30% de variación MoM
- **Acción:** Enviar notificación push o email con la skill destacada y el % de cambio

---

## 📐 Modelos Estadísticos — Resumen

| Modelo | Librería | Objetivo | Output |
|---|---|---|---|
| K-means Clustering | scikit-learn | Segmentar perfiles profesionales | Etiqueta de cluster por oferta |
| Prophet (Serie de Tiempo) | prophet | Predecir demanda de skills a 12 meses | Proyección + intervalos |
| Regresión Lineal Múltiple | scikit-learn / statsmodels | Estimar salario según skills y perfil | Coeficientes + R² + RMSE |
| Análisis de Correlación | pandas / seaborn | Detectar skills que van juntas | Heatmap de correlaciones |

---

## ✅ Orden de Ejecución del Proyecto

```
1. Descargar datasets → data/raw/
2. Ejecutar: python python/01_extraccion.py
3. Ejecutar: python python/02_limpieza.py
4. Ejecutar: python python/03_nlp_skills.py
5. Ejecutar: python python/04_clustering.py
6. Ejecutar: python python/05_series_tiempo.py
7. Ejecutar: python python/06_regresion_salarios.py
8. Abrir Excel → Actualizar conexiones Power Query
9. Abrir Power BI → Actualizar modelo y construir dashboard
10. Configurar flujos en Power Automate
```

---

## 🎨 Estilo y Marca

- **Marca:** Bilbao Analytics (temática universo / espacio exterior)
- **Paleta Power BI:** Fondos oscuros (#0D0D1A, #1A1A2E), acentos en azul eléctrico (#00D4FF) y violeta (#7B2FBE)
- **Tipografía:** Segoe UI en Power BI; Calibri en Excel
- **Tono de documentación:** Profesional, claro, orientado a insights de negocio

---

## 📝 Convenciones de Código Python

- Nombres de variables en `snake_case`
- Comentarios en español
- Cada script debe tener un bloque `if __name__ == "__main__":`
- Usar `print()` con emojis para indicar progreso (ej: `print("✅ Limpieza completada")`)
- Guardar siempre una copia de respaldo antes de sobreescribir archivos procesados

```
