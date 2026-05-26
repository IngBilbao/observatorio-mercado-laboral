# ⚡ Power Automate — Flujos del Observatorio

Esta carpeta contiene las guías paso a paso para construir los flujos que automatizan el ciclo de vida del Observatorio bajo una arquitectura **event-driven**.

---

## 🏗️ Arquitectura del sistema

📖 **[ARQUITECTURA_EVENT_DRIVEN.md](ARQUITECTURA_EVENT_DRIVEN.md)** — leer **antes** de construir los flujos. Define las 3 capas, las latencias de cada una, y el discurso de portfolio.

---

## 📋 Índice de guías

| Archivo | Propósito |
|---|---|
| **[`ARQUITECTURA_EVENT_DRIVEN.md`](ARQUITECTURA_EVENT_DRIVEN.md)** | **Empieza aquí.** Arquitectura completa de las 3 capas. Demo de 90s. |
| [`COMO_OBTENER_IDS.md`](COMO_OBTENER_IDS.md) | Cómo encontrar Workspace/Dataset/Report IDs desde Power BI Service. |
| [`flujo_01_reporte_semanal.md`](flujo_01_reporte_semanal.md) | Flujo 1: PDF semanal por email los lunes 8:00 AM. |
| [`flujo_02_alertas_skills.md`](flujo_02_alertas_skills.md) | Flujo 2: alertas en tiempo real al cambiar `alertas_skills.csv`. |
| [`CONFIGURAR_REFRESH.md`](CONFIGURAR_REFRESH.md) | *(Opcional)* cómo activar auto-refresh del dataset si se resuelven credenciales del Gateway. |

---

## 🗺️ Orden de implementación recomendado

```
1. Leer ARQUITECTURA_EVENT_DRIVEN.md — entender las 3 capas
2. Programar Task Scheduler (capa DATOS):
   .\scripts\programar_pipeline.ps1
3. Obtener Report ID (COMO_OBTENER_IDS.md)
4. Construir Flujo 1 — Reporte semanal
5. Probar Flujo 1 manualmente
6. Construir Flujo 2 — Alertas skills
7. Probar Flujo 2 editando alertas_skills.csv
8. (Opcional) Activar auto-refresh del dataset (CONFIGURAR_REFRESH.md)
```

---

## 🎯 IDs y datos del proyecto

| Concepto         | Valor                                                          |
|------------------|----------------------------------------------------------------|
| Workspace ID     | `d287f4ea-8862-4da2-8291-ba4168afd518`                          |
| Dataset ID       | *(opcional — solo necesario si activas refresh automático)*    |
| Report ID        | *(necesario para Flujo 1 — ver `COMO_OBTENER_IDS.md`)*          |
| Destinatarios    | `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`            |
| Cuenta ejecutora | `cristian.garcia@bilbaoanalytics.com` (M365)                    |
| Host de archivos | OneDrive sincronizado (carpeta del proyecto)                    |
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
| 3 · Pipeline scheduled (Task Scheduler) | ✅ | ✅ (`scripts/programar_pipeline.ps1`) | ⏳ | ⏳ |
| 4 · Ingesta Adzuna diaria       | ✅ (vía Task Scheduler) | ⏳ | ⏳ | ⏳ |
