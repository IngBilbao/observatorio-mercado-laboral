# ⚡ Power Automate — Flujos del Observatorio

Esta carpeta contiene las guías paso a paso para construir los flujos que automatizan el ciclo de vida del Observatorio.

---

## 📋 Índice de guías

| Archivo                          | Propósito                                                        |
|----------------------------------|------------------------------------------------------------------|
| `CONFIGURAR_REFRESH.md`          | **Empieza aquí.** Instalar Personal Gateway para que PBI Service refresque los CSVs locales. |
| `COMO_OBTENER_IDS.md`             | Cómo encontrar Dataset ID y Report ID desde Power BI Service.    |
| `flujo_01_reporte_semanal.md`     | Construcción del Flujo 1 (reporte semanal con PDF por email).    |
| `flujo_02_alertas_skills.md`      | Construcción del Flujo 2 (alertas MoM ≥30% en skills).            |

---

## 🗺️ Orden de implementación recomendado

```
1. Instalar Personal Gateway          → CONFIGURAR_REFRESH.md
2. Obtener Dataset ID y Report ID      → COMO_OBTENER_IDS.md
3. Probar refresh manual desde PBI Service
4. Construir Flujo 1 (Reporte Semanal) → flujo_01_reporte_semanal.md
5. Probar Flujo 1 manualmente
6. Construir Flujo 2 (Alertas Skills)  → flujo_02_alertas_skills.md
7. (Futuro) Construir Flujo 3 — pipeline Python automatizado
8. (Futuro) Construir Flujo 4 — ingesta Adzuna diaria
```

---

## 🎯 IDs y datos del proyecto

| Concepto         | Valor                                                          |
|------------------|----------------------------------------------------------------|
| Workspace ID     | `d287f4ea-8862-4da2-8291-ba4168afd518`                          |
| Dataset ID       | *(pendiente — ver `COMO_OBTENER_IDS.md`)*                       |
| Report ID        | *(pendiente — ver `COMO_OBTENER_IDS.md`)*                       |
| Destinatarios    | `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`            |
| Host de archivos | OneDrive (project root: `OneDrive - Bilbao Analytics/...`)      |
| Zona horaria     | Europe/Madrid                                                   |

---

## 📦 Exportar / importar flujos

**Para guardar copia versionada de un flujo:**

1. Power Automate → Mis flujos → seleccionar
2. `⋯ → Exportar → Paquete (.zip)`
3. Descomprimir → copiar `Microsoft.Flow/flows/<id>/definition.json` a esta carpeta como:
   - `flujo_01_reporte_semanal.json`
   - `flujo_02_alertas_skills.json`

**Para importar (en otra máquina o tenant):**

1. Power Automate → Mis flujos → Importar → Paquete
2. Mapear conexiones (Outlook, OneDrive, Power BI) a las tuyas

---

## 🔐 Manejo de secretos

- ❌ **Nunca** subir `kaggle.json`, `adzuna_credentials.json`, App IDs, API keys a GitHub. El `.gitignore` ya los cubre.
- ✅ En Power Automate usar **Conexiones** (no hardcodear keys en pasos HTTP).
- ✅ Para credenciales sensibles considerar **Azure Key Vault** + conector dedicado.

---

## ✅ Estado de implementación

| Flujo                          | Diseñado | Construido | Probado | En producción |
|--------------------------------|----------|------------|---------|---------------|
| 1 · Reporte semanal             | ✅        | ⏳          | ⏳       | ⏳             |
| 2 · Alertas de skills           | ✅        | ⏳          | ⏳       | ⏳             |
| 3 · Pipeline Python automatizado | ⏳        | ⏳          | ⏳       | ⏳             |
| 4 · Ingesta Adzuna diaria       | ⏳        | ⏳          | ⏳       | ⏳             |
