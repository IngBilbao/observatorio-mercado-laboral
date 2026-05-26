# 🐛 Fix urgente: bug de locale en Power Query

## El problema

Al inspeccionar el `.pbix` vía XMLA endpoint detecté que las columnas numéricas con decimales están corrompidas porque Power BI Desktop tiene el locale en español y Power Query interpreta el `.` (punto) como separador de miles en lugar de separador decimal.

### Síntomas

| Columna | Valor esperado (del CSV) | Valor leído por Power BI | Magnitud del error |
|---|---|---|---|
| `salario_anual_usd` | $65,500 | $655,000 | 10× |
| `latitud` (San Francisco) | 37.7749 | 377749 | × 10,000 |
| `longitud` (San Francisco) | -122.4194 | -1,224,194 | × 10,000 |
| Salario top | $273,010 | $27,301,000,000,000,024 | × 10¹¹ (overflow) |

### Causa raíz

```m
// ❌ Incorrecto (usa cultura del sistema = español)
Table.TransformColumnTypes(Tabla, {
    {"salario_anual_usd", type number},
    {"latitud", type number}
})

// ✅ Correcto (fuerza interpretación con punto decimal)
Table.TransformColumnTypes(Tabla, {
    {"salario_anual_usd", type number},
    {"latitud", type number}
}, "en-US")
```

El tercer parámetro de `Table.TransformColumnTypes` es la **cultura** usada para parsear. Sin él, Power Query usa la del sistema operativo / Power BI Desktop, que en español interpreta `.` como separador de miles.

---

## Cómo aplicar el fix

### Opción 1 — Editar cada query manualmente (más rápido, ~5 min)

En **Power BI Desktop → Inicio → Transformar datos → Editor de Power Query**:

Para cada una de estas 4 consultas:
- `Fact_Ofertas`
- `Fact_Predicciones`
- `Dim_Clusters`
- `Fact_ModeloSalarios`
- `Fact_Coef_Salarios`

1. Selecciona la consulta en el panel izquierdo
2. Inicio → **Editor avanzado**
3. Busca la línea que dice `Table.TransformColumnTypes(...)` con la lista de columnas
4. Localiza el `})` que cierra la transformación
5. **Cambia** `})` por `}, "en-US")`
6. Click **Listo**

Repite para las 5 consultas. Luego **Inicio → Cerrar y aplicar**.

### Opción 2 — Pegar los `.pq` actualizados (más limpio)

Los archivos en `powerbi/etl/` ya están corregidos. En Power Query, para cada consulta:

1. Editor avanzado
2. Borra todo el código M
3. Copia y pega desde el archivo `.pq` correspondiente (versión más reciente del repo)
4. Listo

---

## Verificación del fix

Después de aplicar, ejecuta esta consulta DAX en Power BI (Vista → Editor DAX o Performance Analyzer):

```dax
EVALUATE ROW(
    "Mediana", [Salario Mediano USD],
    "P10",     [Salario P10 USD],
    "P90",     [Salario P90 USD]
)
```

**Valores esperados (después del fix):**

| Métrica | Valor |
|---|---|
| Mediana | ~ $65,500 |
| P10 | ~ $28,000 |
| P90 | ~ $149,000 |

**Si todavía ves valores 10× más grandes**, faltó aplicar el fix a alguna consulta.

---

## ⚠️ Nota adicional sobre los datos

Tu `.pbix` está cargado con **5,000 ofertas** (solo sintéticas, sin las 237 de Adzuna que añadí después). Para incluir Adzuna:

1. Abre Power BI Desktop
2. **Inicio → Actualizar** — recarga los CSVs (que ya están con Adzuna)
3. Aplica el fix de locale (si no lo has hecho)
4. **Publicar** al workspace para actualizar la versión cloud

El total debería pasar de 5,000 → **5,237** ofertas.

---

## ✅ Estado del fix en el repo

| Archivo | Estado |
|---|---|
| `powerbi/etl/05_Fact_Ofertas.pq` | ✅ Corregido |
| `powerbi/etl/07_Fact_Predicciones.pq` | ✅ Corregido |
| `powerbi/etl/08_Dim_Clusters_y_ModeloSalarios.pq` | ✅ Corregido (3 bloques) |
| `powerbi/etl/01_Dim_Calendario.pq` | ✅ No requiere (no usa CSV) |
| `powerbi/etl/02_Dim_Skills.pq` | ✅ No requiere (data inline) |
| `powerbi/etl/03_Dim_Roles.pq` | ✅ No requiere (data inline) |
| `powerbi/etl/04_Dim_Ubicacion.pq` | ✅ No requiere (deriva de Fact_Ofertas) |
| `powerbi/etl/06_Fact_Skills_Oferta.pq` | ✅ No requiere (solo strings) |
