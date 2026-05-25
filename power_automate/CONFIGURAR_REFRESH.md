# 🔄 Configurar el refresh del dataset de Power BI

> **Importante.** Antes de construir el Flujo 1 (Reporte Semanal), necesitas que Power BI Service pueda refrescar tu dataset. Hoy `observatorio.pbix` conecta a CSVs **locales** (en tu OneDrive sincronizado) — Power BI Service en la nube no ve esos archivos directamente. Hay dos estrategias.

---

## Estrategia A — On-premises Data Gateway (Personal Mode) — **RECOMENDADA para arrancar**

✅ Funciona ya, sin cambiar las consultas Power Query.
❌ Tu PC debe estar encendido cuando se haga el refresh (Power Automate lo intentará programado).

### Pasos

1. Descargar Gateway:
   **https://www.microsoft.com/en-us/download/details.aspx?id=53127** → bajar "**On-premises data gateway (personal mode)**".
2. Instalar y abrir el Gateway.
3. Iniciar sesión con tu cuenta M365 (la misma que usas para Power BI).
4. En Power BI Service:
   - Workspace → conjunto de datos `observatorio` → **⋯ → Configuración**.
   - Sección **Credenciales del origen de datos**: clic en cada origen → **Editar credenciales**.
     - Método de autenticación: **Windows**
     - Nivel de privacidad: **Organizativo**
   - Sección **Actualización programada**: opcional ahora (Power Automate la disparará).

5. Probar el refresh:
   - En Configuración del dataset → **Actualizar ahora**.
   - Si funciona ✅ — Gateway listo.

> **Pega aquí (cuando lo configures) el nombre del Gateway que aparece en Power BI Service** — útil como referencia para futuros flujos:
> ```
> Gateway: ___________________________
> ```

---

## Estrategia B — Mover los CSVs a OneDrive for Business "puro" + reescribir Power Query

✅ Refresh en la nube, sin Gateway, sin que tu PC esté encendido.
❌ Requiere reescribir las 9 consultas Power Query usando el conector `SharePoint.Files` o `OneDrive.Files`.
❌ Los CSVs en OneDrive deben actualizarse vía Power Automate también (no solo localmente).

### Si decides ir por esta vía más adelante

Cambiar en cada `.pq` el bloque:

```m
// ANTES (estrategia A)
Csv.Document(
    File.Contents(RutaProcesados & "matriz_skills.csv"), ...
)
```

por:

```m
// DESPUÉS (estrategia B)
Csv.Document(
    Web.Contents("https://onedrive.live.com/...direct-download-url..."),
    [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
)
```

Pero **no recomiendo hacerlo ahora**: complica la primera iteración sin aportar valor inmediato. Vamos con Estrategia A.

---

## 🎯 Plan actual

1. Hoy: instalar **Personal Gateway** (Estrategia A) — 15 minutos.
2. Probar refresh manual desde Power BI Service.
3. Construir Flujo 1 (Reporte Semanal) que usa la API de refresh.
4. Más adelante (cuando el proyecto madure): migrar a Estrategia B.

Una vez que el refresh manual funcione, avísame y seguimos con el Flujo 1.
