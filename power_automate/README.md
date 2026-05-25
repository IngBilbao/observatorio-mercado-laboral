# ⚡ Power Automate — Flujos del Observatorio

Esta carpeta contiene la documentación y los exports JSON de los flujos de Power Automate que automatizan el ciclo de vida del Observatorio.

---

## 📋 Inventario de flujos

| Archivo                          | Tipo de flujo       | Trigger                                       |
|----------------------------------|---------------------|-----------------------------------------------|
| `flujo_reporte_semanal.json`     | Cloud (programado)  | Cada lunes 8:00 AM.                            |
| `flujo_alertas_skills.json`      | Cloud (event)       | Cuando se actualiza el Excel en SharePoint.    |
| `flujo_pipeline_python.json`     | Cloud (programado)  | Diario 6:00 AM — ejecuta scripts Python local. |
| `flujo_ingesta_adzuna.json`      | Cloud (programado)  | Diario 5:00 AM — llama API Adzuna.            |

> ⚠️ Los archivos `.json` se generan exportando los flujos desde Power Automate (`Mis flujos` → flujo → `Exportar` → `Paquete (.zip)`). Una vez exportados, se descomprimen y el `definition.json` interno se copia a esta carpeta con el nombre del flujo.

---

## 🔧 Prerequisitos antes de crear los flujos

1. **Cuenta M365 con licencia de Power Automate** ✅ (ya tienes).
2. **Conectores que necesitarás:**
   - SharePoint (carpeta del proyecto) o OneDrive for Business.
   - Outlook 365 (para enviar email).
   - Power BI REST API (premium connector — viene con licencia Pro).
   - HTTP (para llamadas a Adzuna / Remotive).
   - **Premium opcional:** Desktop Flows (para ejecutar Python local) — requiere licencia per-user o per-flow.
3. **Power BI Workspace** con el `.pbix` publicado y un dataset configurado.
4. **App registration en Azure AD** si vas a usar Service Principal para refresh de PBI (recomendado vs. usuario personal).

---

## 🛠️ Flujo 1 — Reporte Semanal

**Objetivo:** cada lunes a las 8:00 AM, refrescar el dataset de Power BI, exportar el dashboard como PDF y enviarlo por email a una lista de stakeholders.

### Pasos detallados

```
1. Trigger: Recurrencia → Frecuencia "Semana", día Lunes, hora 8:00 AM (zona Europe/Madrid)

2. Acción: Inicializar variable
   - Nombre: WorkspaceId
   - Tipo: String
   - Valor: <tu workspace ID de Power BI>

3. Acción: Inicializar variable
   - Nombre: ReportId
   - Tipo: String
   - Valor: <ID del reporte publicado>

4. Acción: Power BI → "Actualizar conjunto de datos"
   - Workspace: @{variables('WorkspaceId')}
   - Dataset: <DatasetId>
   - Esperar a que termine: Sí

5. Acción: Power BI → "Exportar a archivo para reportes"
   - Workspace: @{variables('WorkspaceId')}
   - Report: @{variables('ReportId')}
   - File Format: PDF

6. Acción: Outlook 365 → "Enviar un correo electrónico (V2)"
   - Para: distribución@tudominio.com
   - Asunto: "📊 Observatorio Datos & Tech — Resumen semanal {{fecha}}"
   - Cuerpo: plantilla HTML con KPIs principales (ver template abajo)
   - Adjuntos: salida del paso 5
```

### Template HTML del email
Guardar en `power_automate/templates/email_reporte_semanal.html` (crear cuando se implemente).

---

## 🛠️ Flujo 2 — Alertas de Cambio en Skills

**Objetivo:** detectar variaciones MoM > 30% en cualquier skill y notificar.

### Estrategia de implementación

Hay dos opciones:

**Opción A (más simple):** Power Automate lee directamente `data/outputs/skills_serie_historica.csv` desde SharePoint, calcula MoM en el flujo con expresiones, y dispara si supera umbral.

**Opción B (más limpia):** Python escribe un `data/outputs/alertas_skills.csv` con solo las skills que pasaron el umbral. Power Automate solo recorre ese archivo y manda emails. Recomendamos B.

### Pasos (opción B)

```
1. Trigger: SharePoint → "Cuando se crea o modifica un archivo (solo propiedades)"
   - Carpeta: /sites/.../observatorio/outputs
   - Filtro: nombre archivo = "alertas_skills.csv"

2. Acción: SharePoint → "Obtener contenido del archivo"

3. Acción: "Crear tabla CSV" → parsear

4. Acción: "Aplicar a cada" sobre filas
   4.1. Condición: variacion_pct >= 30
   4.2. (True) Enviar email con plantilla
```

---

## 🛠️ Flujo 3 — Pipeline Python Local (Desktop Flow)

**Opcional** — requiere licencia Premium de Desktop Flows.

Ejecuta secuencialmente:
```powershell
cd "C:\Users\bilba\OneDrive - Bilbao Analytics\Bilbao Analitycs\Proyectos\Proyecto analista de datos\observatorio-mercado-laboral"
.\.venv\Scripts\Activate.ps1
py python/01_extraccion.py
py python/02_limpieza.py
py python/03_nlp_skills.py
py python/04_clustering.py
py python/05_series_tiempo.py
py python/06_regresion_salarios.py
```

**Alternativa sin licencia premium:** programar el script con el **Programador de Tareas de Windows** y dejar que Power Automate solo se encargue del refresh/notificación.

---

## 🛠️ Flujo 4 — Ingesta Adzuna (cuando se conecte la API real)

```
1. Trigger: Recurrencia diaria 5:00 AM
2. HTTP GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id=...&app_key=...&what=data%20analyst
3. Parsear JSON
4. Crear/actualizar CSV en SharePoint: /raw/adzuna_YYYYMMDD.csv
5. (Opcional) Disparar flujo 3 al terminar
```

API key: registrarse en https://developer.adzuna.com/signup — tier free 1000 calls/mes.

---

## 🔐 Manejo de secretos

- **Nunca** subir `kaggle.json`, app IDs o API keys a GitHub. El `.gitignore` ya cubre esto.
- En Power Automate usar **Conexiones** (no hardcodear keys en pasos HTTP).
- Para credenciales sensibles considerar **Azure Key Vault** + conector.

---

## 📦 Cómo exportar/importar un flujo

**Exportar:**
1. Power Automate → Mis flujos → seleccionar flujo
2. `...` → Exportar → Paquete (.zip)
3. Descomprimir el zip → buscar `Microsoft.Flow/flows/<id>/definition.json`
4. Copiar a esta carpeta con el nombre apropiado

**Importar:**
1. Power Automate → Mis flujos → Importar → Paquete (.zip)
2. Mapear conexiones (SharePoint, Outlook, Power BI) a las tuyas
3. Activar el flujo

---

## ✅ Estado de implementación

| Flujo                  | Diseñado | Construido | Probado | En producción |
|------------------------|----------|------------|---------|---------------|
| Reporte semanal        | ✅        | ⏳          | ⏳       | ⏳             |
| Alertas skills         | ✅        | ⏳          | ⏳       | ⏳             |
| Pipeline Python        | ✅        | ⏳          | ⏳       | ⏳             |
| Ingesta Adzuna         | ✅        | ⏳          | ⏳       | ⏳             |
