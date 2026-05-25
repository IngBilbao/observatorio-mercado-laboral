# 📊 Power BI — Observatorio del Mercado Laboral

Guía paso a paso para construir el dashboard `observatorio.pbix` con ETL hecho **íntegramente en Power Query** (sin Excel intermedio).

---

## 🗂️ Estructura de esta carpeta

```
powerbi/
├── README.md                              ← este archivo (guía paso a paso)
├── observatorio.pbix                      ← tu archivo Power BI (se crea en el paso 1)
├── theme/
│   └── bilbao_analytics_theme.json        ← tema visual (paleta universo)
├── etl/
│   ├── 00_Parametro_RutaBase.pq           ← definición conceptual de parámetros
│   ├── 01_Dim_Calendario.pq
│   ├── 02_Dim_Skills.pq
│   ├── 03_Dim_Roles.pq
│   ├── 04_Dim_Ubicacion.pq
│   ├── 05_Fact_Ofertas.pq
│   ├── 06_Fact_Skills_Oferta.pq
│   ├── 07_Fact_Predicciones.pq
│   └── 08_Dim_Clusters_y_ModeloSalarios.pq  (3 consultas dentro)
└── dax/
    ├── 01_medidas_base.dax
    ├── 02_medidas_skills.dax
    ├── 03_medidas_salarios.dax
    ├── 04_medidas_tiempo.dax
    └── 05_medidas_alertas.dax
```

---

## 🏗️ Esquema dimensional (modelo estrella)

```
Dim_Calendario ──┐
Dim_Roles ───────┤
Dim_Ubicacion ───┼──→ Fact_Ofertas ──→ Fact_Skills_Oferta ←── Dim_Skills
Dim_Clusters ────┘         │
                           ▼
                  Fact_ModeloSalarios

Dim_Skills ←── Fact_Predicciones
                  (relación con Dim_Calendario por fecha)

Fact_Coef_Salarios  (tabla suelta para gráfico drivers)
```

**Cardinalidades de las relaciones:**

| De                       | A                       | Cardinalidad | Filtro       |
|--------------------------|-------------------------|--------------|--------------|
| `Fact_Ofertas[fecha_publicacion]` | `Dim_Calendario[Fecha]`  | Muchos a Uno | Single       |
| `Fact_Ofertas[rol_normalizado]`   | `Dim_Roles[rol]`         | Muchos a Uno | Single       |
| `Fact_Ofertas[ciudad]`            | `Dim_Ubicacion[ciudad]`  | Muchos a Uno | Single       |
| `Fact_Skills_Oferta[oferta_id]`   | `Fact_Ofertas[oferta_id]`| Muchos a Uno | **Both** ⚠️  |
| `Fact_Skills_Oferta[skill_id]`    | `Dim_Skills[skill_id]`   | Muchos a Uno | Single       |
| `Fact_ModeloSalarios[oferta_id]`  | `Fact_Ofertas[oferta_id]`| Uno a Uno    | Single       |
| `Fact_Predicciones[skill]`        | `Dim_Skills[skill]`      | Muchos a Uno | Single       |
| `Fact_Predicciones[fecha]`        | `Dim_Calendario[Fecha]`  | Muchos a Uno | Single       |

> ⚠️ La relación bridge `Fact_Skills_Oferta ↔ Fact_Ofertas` debe ser bidireccional para que los filtros de skills propaguen a salarios y viceversa.

---

## 🚀 Paso a paso

### Paso 1 — Crear archivo y aplicar tema

1. Abre **Power BI Desktop**.
2. Guarda el archivo como `powerbi/observatorio.pbix` dentro de este repo.
3. Aplica el tema: **Ver → Temas → Examinar temas →** selecciona `powerbi/theme/bilbao_analytics_theme.json`.

### Paso 2 — Crear los 2 parámetros de ruta

**Inicio → Transformar datos → Administrar parámetros → Nuevo**

Crear **dos parámetros**:

| Nombre            | Tipo  | Valor actual                                                                                                                                                  |
|-------------------|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `RutaBase`        | Texto | `C:\Users\bilba\OneDrive - Bilbao Analytics\Bilbao Analitycs\Proyectos\Proyecto analista de datos\observatorio-mercado-laboral\data\outputs\`                  |
| `RutaProcesados`  | Texto | `C:\Users\bilba\OneDrive - Bilbao Analytics\Bilbao Analitycs\Proyectos\Proyecto analista de datos\observatorio-mercado-laboral\data\processed\`                |

> 💡 Cuando muevas el proyecto a otra carpeta o máquina, solo cambias estos dos parámetros.

### Paso 3 — Crear las 8 consultas Power Query

En el **Editor de Power Query** (Inicio → Transformar datos):

Para cada archivo `.pq` en `powerbi/etl/`:

1. **Inicio → Nueva consulta → Consulta vacía**
2. **Inicio → Editor avanzado**
3. Borra el contenido y **pega el código M** del archivo correspondiente.
4. Cierra el editor — la consulta se ejecuta.
5. **Renombra la consulta** (panel izquierdo) según el nombre del archivo, sin prefijo numérico ni extensión:
   - `01_Dim_Calendario.pq` → consulta llamada **`Dim_Calendario`**
   - `02_Dim_Skills.pq` → **`Dim_Skills`**
   - `03_Dim_Roles.pq` → **`Dim_Roles`**
   - `04_Dim_Ubicacion.pq` → **`Dim_Ubicacion`** *(depende de Fact_Ofertas — cargar después)*
   - `05_Fact_Ofertas.pq` → **`Fact_Ofertas`**
   - `06_Fact_Skills_Oferta.pq` → **`Fact_Skills_Oferta`**
   - `07_Fact_Predicciones.pq` → **`Fact_Predicciones`**
   - `08_Dim_Clusters_y_ModeloSalarios.pq` → **3 consultas separadas:** `Dim_Clusters`, `Fact_ModeloSalarios`, `Fact_Coef_Salarios`

**Orden recomendado:** `Fact_Ofertas` primero (otras dependen) → `Dim_Ubicacion` → el resto.

6. **Inicio → Cerrar y aplicar.**

### Paso 4 — Configurar el modelo (vista de Modelo)

1. **Vista → Modelo** (icono de relaciones a la izquierda).
2. Crear las relaciones según la tabla del esquema (arriba).
3. **Marcar `Dim_Calendario` como tabla de fechas:**
   - Click derecho sobre `Dim_Calendario` → *Marcar como tabla de fechas* → columna `Fecha`.
4. **Ocultar de la vista de informe** (click derecho → *Ocultar*):
   - Columnas `oferta_id` en todas las tablas
   - Columnas `skill_id` en `Fact_Skills_Oferta` y `Dim_Skills`
   - La tabla `Fact_Coef_Salarios` puede quedar visible — la usaremos en un visual

### Paso 5 — Crear tabla de medidas y pegar DAX

1. **Inicio → Especificar datos** → Crear tabla vacía llamada `_Medidas`.
2. Cargar.
3. En el panel de campos, click derecho sobre `_Medidas` → **Nueva medida**.
4. Por cada bloque en los 5 archivos `.dax`, pegar la fórmula completa (Power BI detecta automáticamente el nombre antes del `=`).
5. Agrupar las medidas en **Carpetas de visualización** (panel derecho de propiedades) con los nombres:
   - `00 · KPIs` (medidas de `01_medidas_base.dax`)
   - `01 · Skills` (medidas de `02_medidas_skills.dax`)
   - `02 · Salarios` (medidas de `03_medidas_salarios.dax`)
   - `03 · Tiempo` (medidas de `04_medidas_tiempo.dax`)
   - `04 · Alertas` (medidas de `05_medidas_alertas.dax`)
6. **Ocultar** la columna `Columna1` que se creó con la tabla vacía.

### Paso 6 — Construir las 6 páginas del dashboard

Ver sección "Páginas del Dashboard" abajo.

### Paso 7 — Publicar a Power BI Service

1. **Inicio → Publicar**
2. Workspace: tu workspace de Bilbao Analytics
3. Anotar **Workspace ID** y **Dataset ID** — los necesitarás para Power Automate.

---

## 📄 Páginas del Dashboard

> **Tamaño de página:** 16:9 (Vista → Tamaño de página → 16:9, o `1280×720`).
> **Fondo:** ya viene del tema (`#0D0D1A`).

### Página 1 · Resumen Ejecutivo

**Layout sugerido (zonas):**
```
┌─────────────────────────────────────────────────────────────────┐
│  LOGO + TITULO        [Slicer Periodo]   [Slicer Region]        │
├──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ KPI      │ KPI      │ KPI      │ KPI      │  Tendencia mensual  │
│ Ofertas  │ Salario  │ % Remoto │ Top skill│  (linea + area)     │
│ MoM ↑↓   │ Mediano  │          │ del mes  │                     │
├──────────┴──────────┴──────────┴──────────┴─────────────────────┤
│   Top 10 Skills (barras)        │   Salario por Rol (boxplot)   │
└─────────────────────────────────┴───────────────────────────────┘
```

**Visuales y medidas a usar:**
- 4 tarjetas (cards): `Total Ofertas` + `Var MoM Ofertas`, `Salario Mediano USD`, `Pct Remoto`, `Top Skill del Mes`
- Línea: eje X = `Dim_Calendario[InicioMes]`, eje Y = `Total Ofertas` + `Promedio Movil 3M Ofertas` (línea adicional)
- Barras horizontales: categoría = `Dim_Skills[skill]`, valor = `Pct Ofertas con Skill`, filtro nivel visual = `Top 10 Skill Flag = 1`
- Visual boxplot (importar visual personalizado desde marketplace): por `Dim_Roles[rol]`

### Página 2 · Análisis de Skills

- **Ranking ampliado** (matriz): rows = `Dim_Skills[skill]`, columns = `Dim_Roles[rol]`, valor = `Pct Ofertas con Skill`, formato condicional gradiente.
- **Treemap por categoría:** `Dim_Skills[categoria]` → `Dim_Skills[skill]`, valor = `Ofertas con Skill`.
- **Evolución temporal multilínea:** eje X = `Dim_Calendario[InicioMes]`, leyenda = `Dim_Skills[skill]` (filtro nivel visual `Top 10 Skill Flag = 1`), valor = `Ofertas con Skill`.
- **Salario premium por skill:** barras con `Salario Premium por Skill` (rojo si negativo, verde si positivo via formato condicional).

### Página 3 · Inteligencia Salarial

- **Slicers globales:** rol, nivel, país, modalidad.
- **Card grande:** `Salario Mediano USD`.
- **Distribución (boxplot)** por nivel de experiencia.
- **Scatter:** eje X = `anios_experiencia`, eje Y = `salario_anual_usd`, tamaño = `n_skills`, color = `rol_normalizado`.
- **Drivers de salario (barras):** datos = `Fact_Coef_Salarios`, eje = `feature_legible`, valor = `Impacto Feature Pct`, color por `categoria_feature`, ordenado descendente.
- **Tabla:** mostrar `oferta_id`, `salario_anual_usd`, `Salario Predicho USD`, `residuo_pct`, `Es Subpagada` — útil para detectar outliers.

### Página 4 · Mapa Geográfico

- **Mapa de burbujas** (visual nativo "Mapa"): ubicación = `Dim_Ubicacion[latitud]` + `Dim_Ubicacion[longitud]` (o `Dim_Ubicacion[ciudad]`), tamaño = `Total Ofertas`, color saturación = `Salario Mediano USD`.
- **Tabla ranking** por ciudad: `Total Ofertas`, `Salario Mediano USD`, `Pct Remoto`.
- **Comparador 2 regiones** (slicer `Dim_Ubicacion[region]` con selección múltiple).

### Página 5 · Predicciones (Prophet)

- **Slicer:** `Dim_Skills[skill]` (selección única).
- **Visual de línea con banda:** usar visual "Gráfico de líneas y área de banda" (nativo) o el visual nativo de línea + crear gráfico combinado.
  - Eje X: `Fact_Predicciones[fecha]`
  - Y línea histórica: `Historico`
  - Y línea forecast: `Forecast Futuro`
  - Banda superior/inferior: `Banda Superior` / `Banda Inferior`
- **Tabla resumen:** skill, próximo mes esperado, % cambio vs último histórico — usar medida `Crecimiento Esperado Skill`.

### Página 6 · Perfiles / Clusters

- **Tarjetas (4 cards) por cluster:** una página visual con 4 paneles, cada uno mostrando `cluster_nombre`, `n_ofertas`, `salario_mediano_usd`, `top_skills`.
- **Imagen:** importar `docs/imagenes/clusters_pca.png` (visual "Imagen") como referencia del clustering.
- **Radar/Grafico de barras agrupadas:** comparar intensidad de skills entre clusters.
- **Tabla detalle:** ofertas del cluster seleccionado con `oferta_id`, `rol`, `salario`, `ciudad`.

---

## 🎨 Convenciones visuales

| Elemento                         | Estilo                                          |
|----------------------------------|-------------------------------------------------|
| Fondo página                     | `#0D0D1A` (viene del tema)                      |
| Fondo tarjeta / visual           | `#1A1A2E`                                       |
| Color KPI principal              | `#00D4FF` (azul eléctrico)                      |
| Color KPI secundario             | `#7B2FBE` (violeta)                             |
| Variación positiva               | `#00E396` (verde)                               |
| Variación negativa               | `#FF4D6D` (rojo)                                |
| Título de página                 | Segoe UI Light 22                               |
| Título de visual                 | Segoe UI Semibold 14                            |
| Etiquetas / ejes                 | Segoe UI 10, color `#9090A8`                    |
| Bordes / divisores               | Línea fina `#9090A8` 25% opacidad               |

---

## 🔁 Refrescar el dashboard

Cada vez que el pipeline Python genere nuevos CSVs:

1. **Inicio → Actualizar** en Power BI Desktop, o
2. Desde Power BI Service: programar refresh diario (necesita Gateway local porque las fuentes son archivos locales).

Para automatizar: ver `power_automate/README.md` — flujo "Reporte Semanal" incluye refresh vía API.

---

## ✅ Checklist final antes de publicar

- [ ] Las 9 consultas (1 calendario + 4 dims + 4 facts) se ejecutan sin error.
- [ ] Las relaciones del modelo están creadas con cardinalidades correctas.
- [ ] `Dim_Calendario` está marcada como tabla de fechas.
- [ ] Todas las medidas del `.dax` están creadas en `_Medidas` y agrupadas en carpetas.
- [ ] Cada página tiene título, slicers y al menos un KPI.
- [ ] Tema Bilbao Analytics aplicado en todas las páginas.
- [ ] Página 1 (Resumen) tiene los KPIs con variación MoM.
- [ ] Página 5 (Predicciones) muestra correctamente histórico vs forecast.
- [ ] Mapa renderiza burbujas en lat/lon correctos.
- [ ] Drill-through configurado: clic en skill → detalle de la skill.
- [ ] Publicado a workspace y refresh programado.
