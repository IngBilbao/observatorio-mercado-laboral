# 🆔 Cómo obtener los IDs de Power BI

Para configurar los flujos de Power Automate necesitas tres identificadores GUID. Esta es la guía para obtenerlos.

---

## 1. Workspace ID

**Ya lo tienes:**
```
d287f4ea-8862-4da2-8291-ba4168afd518
```

Cómo encontrarlo si lo necesitas de nuevo:
1. Abre **https://app.powerbi.com**
2. Entra al workspace donde publicaste `observatorio.pbix`
3. Mira la URL del navegador. Tendrá esta forma:
   ```
   https://app.powerbi.com/groups/<WORKSPACE_ID>/list
                          ↑─────────────────────────────────↑
                          este GUID es el WorkspaceId
   ```

---

## 2. Dataset ID (Conjunto de datos)

1. En el workspace, hay una pestaña "**Conjuntos de datos + flujos de datos**" o ve a *Configuración → Configuración del conjunto de datos*.
2. Pasa el mouse sobre el dataset `observatorio` (o como lo hayas nombrado al publicar) y haz clic en **⋯ → Configuración**.
3. La URL ahora muestra:
   ```
   https://app.powerbi.com/groups/<WORKSPACE_ID>/settings/datasets/<DATASET_ID>
                                                                    ↑──────────↑
                                                                    DatasetId
   ```

---

## 3. Report ID (Informe)

1. En el workspace, haz clic sobre el informe `observatorio` para abrirlo.
2. La URL es:
   ```
   https://app.powerbi.com/groups/<WORKSPACE_ID>/reports/<REPORT_ID>/<página>
                                                          ↑─────────↑
                                                          ReportId
   ```

---

## 4. (Opcional) Cómo verificarlos rápido vía API

Si tienes curiosidad o quieres confirmarlos programáticamente, puedes usar el "playground" de Power BI:

1. Ve a **https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets-in-group**
2. Click en **Try it** → autentica con tu cuenta M365
3. En `groupId` pega tu Workspace ID
4. Ejecuta: te devolverá la lista de datasets con sus IDs.

Para informes la API es `Reports - Get Reports In Group` (mismo flujo).

---

## 📋 Guarda tus IDs aquí (no se versionará — está en `.gitignore`)

Crea un archivo local `power_automate/ids_powerbi.txt` (gitignored automáticamente porque está en `power_automate/` y no es `.md`/`.json`... wait — sí se versionaría. Mejor crea `ids_powerbi.local.txt` y agregamos esa extensión al gitignore).

Plantilla:
```
WorkspaceId  = d287f4ea-8862-4da2-8291-ba4168afd518
DatasetId    = <pegar aqui>
ReportId     = <pegar aqui>
```
