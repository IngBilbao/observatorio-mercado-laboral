# 🎨 Guía de Visualizaciones — Observatorio del Mercado Laboral

Estándar visual y de diseño para Excel y Power BI bajo la identidad **Bilbao Analytics** (temática universo).

---

## 🌌 Tokens de Marca

| Rol             | Hex       | Uso principal                            |
|-----------------|-----------|------------------------------------------|
| Fondo profundo  | `#0D0D1A` | Background de páginas Power BI.          |
| Fondo medio     | `#1A1A2E` | Tarjetas, paneles, áreas de gráficos.    |
| Texto principal | `#E8E8F0` | Títulos y etiquetas.                     |
| Texto secundario| `#9090A8` | Subtítulos, gridlines, ejes.             |
| Azul eléctrico  | `#00D4FF` | KPIs primarios, series temporales.       |
| Violeta         | `#7B2FBE` | Series secundarias, comparativos.        |
| Verde           | `#00E396` | Cambios positivos, crecimiento.          |
| Ámbar           | `#FFB020` | Advertencias, umbrales.                  |
| Rojo            | `#FF4D6D` | Cambios negativos, alertas críticas.     |

**Tipografía:** Segoe UI en Power BI (Light para títulos grandes, Semibold para KPIs). Calibri 11 en Excel.

---

## 📊 Catálogo de Visualizaciones por Página

### Página 1 — Resumen Ejecutivo
**Objetivo:** estado del mercado en 5 segundos.

| Visual           | Tipo                    | Métricas / Dimensión                       |
|------------------|-------------------------|--------------------------------------------|
| KPI · Total Ofertas | Card con sparkline    | `[Total Ofertas]` + MoM%.                  |
| KPI · Salario Mediano | Card                | `[Salario Mediano USD]`.                   |
| KPI · % Remoto   | Card con icono          | `[Pct Remoto]`.                            |
| KPI · Skill #1 del mes | Card                | Top skill (filtrada por mes actual).       |
| Top 10 Skills    | Barras horizontales     | Eje X: % de ofertas; Eje Y: skill.         |
| Tendencia mensual| Línea                   | Ofertas por mes (últimos 24 meses).        |
| Salario por rol  | Boxplot o barras + IC   | Eje X: rol; Eje Y: salario USD.            |

### Página 2 — Análisis de Skills
- **Ranking de skills** (barras + filtro por país).
- **Heatmap de correlación entre skills** (top 15) — identificar combos populares.
- **Evolución temporal** (líneas multi-serie, top 8 skills).
- **Treemap** por categoría (BI, Cloud, ML/AI, Lenguajes, Bases de datos).

### Página 3 — Inteligencia Salarial
- **Distribución de salarios** por rol (boxplot + jitter).
- **Salario vs. años de experiencia** (scatter con tendencia).
- **Top features del modelo** (barras: `impacto_pct` desde `modelo_salarios_coeficientes.csv`).
- **Salary calculator** — slicer interactivo (rol, país, skills) que muestra salario estimado.

### Página 4 — Mapa Geográfico
- **Mapa de burbujas** (lat/lon, tamaño = ofertas, color = salario mediano).
- **Tabla** ordenable por ciudad con conteo, salario mediano, % remoto.
- **Comparador 2 países** (slicers paralelos).

### Página 5 — Predicciones (Prophet)
- **Línea con banda de confianza** por skill seleccionada (slicer).
- **Tabla resumen**: skill, valor mes próximo, IC 80%, % vs mismo mes año anterior.
- **Top 5 skills al alza** vs **Top 5 a la baja** (delta forecast - histórico).

### Página 6 — Perfiles / Clusters
- **Scatter PCA** (importar `clusters_pca.png` o recrear con visual nativo).
- **Tarjetas por cluster** con nombre, n_ofertas, salario mediano, top skills.
- **Radar chart** por cluster comparando intensidad de skills.

---

## 🧩 Componentes Reutilizables

### Tooltip personalizado
Crear página oculta `Tooltip_Skill` con: nombre skill, frecuencia, salario premium, evolución 12m.

### Barra de navegación
Iconos en la parte superior izquierda de cada página. Tamaño 28×28, color `#9090A8`, hover `#00D4FF`.

### Slicers globales
Sincronizar en todas las páginas: País · Modalidad · Nivel de experiencia · Rango de fechas.

---

## ✅ Checklist antes de publicar

- [ ] Todos los visuales usan paleta de marca (sin azules genéricos de PBI por defecto).
- [ ] Tipografía Segoe UI en todos los textos.
- [ ] Eje Y de salarios formateado como `$0K`.
- [ ] Tooltips activos en todos los visuales con métricas relevantes.
- [ ] Página de portada con logo Bilbao Analytics + última fecha de refresh.
- [ ] Drill-through configurado: clic en skill → tooltip / página de detalle.
- [ ] Modo accesibilidad: contraste AA en todos los textos sobre fondo oscuro.
- [ ] Tamaño de página 16:9 (1280×720) — estándar para presentaciones.

---

## 📐 Excel — Dashboard

Mini-dashboard en hoja `Dashboard_Excel`:

- **3 KPI cards** (formato condicional sobre celdas).
- **Tabla dinámica top skills** + gráfico de barras.
- **Gráfico de línea** con tendencia (12 meses).
- **Segmentadores** de rol y país conectados a tabla dinámica.
- Fondos oscuros aplicados con relleno de celda; texto blanco; gridlines ocultas.

---

## 🚫 Anti-patterns a evitar

- ❌ Gráficos 3D o pies con >5 categorías.
- ❌ Colores aleatorios sin significado.
- ❌ Tablas con >20 columnas sin congelar paneles.
- ❌ KPIs sin contexto (mostrar variación vs. periodo anterior).
- ❌ Ejes truncados que exageran diferencias.
