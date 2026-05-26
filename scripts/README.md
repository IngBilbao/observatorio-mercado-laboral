# 🔧 Scripts de automatización

Scripts de PowerShell que automatizan tareas operativas del Observatorio en Windows.

## 📋 Inventario

| Script | Propósito |
|---|---|
| `programar_pipeline.ps1` | Registra/elimina una tarea de Windows Task Scheduler que ejecuta `python/99_pipeline.py` cada N horas. Es el **componente real-time del data layer**. |

---

## 🚀 Uso de `programar_pipeline.ps1`

Abre PowerShell **como usuario normal** (no Admin — el script registra la tarea bajo tu propio usuario) en la raíz del proyecto.

### Programar pipeline cada 6 horas (default)

```powershell
.\scripts\programar_pipeline.ps1
```

### Programar cada 4 horas, modo rápido (sin Prophet)

```powershell
.\scripts\programar_pipeline.ps1 -IntervaloHoras 4 -Rapido
```

### Programar pipeline completo + Adzuna una vez al día

```powershell
.\scripts\programar_pipeline.ps1 -ConAdzuna -IntervaloHoras 24
```

> ⚠️ Con `-ConAdzuna` cada ejecución consume ~20 llamadas API (de tu cuota mensual de 1000). Cada 24h = ~600 llamadas/mes — dentro del límite.

### Ver estado y últimas ejecuciones

```powershell
.\scripts\programar_pipeline.ps1 -Estado
```

Muestra:
- Estado actual (Ready / Running / Disabled)
- Última ejecución con resultado
- Próxima ejecución programada
- Comando exacto que ejecuta

### Ejecutar manualmente para probar

```powershell
Start-ScheduledTask -TaskName 'BilbaoAnalytics_Observatorio'
# Seguir el log en vivo:
Get-Content .\logs\pipeline_$(Get-Date -Format yyyyMMdd).log -Tail 30 -Wait
```

### Eliminar la tarea programada

```powershell
.\scripts\programar_pipeline.ps1 -Eliminar
```

---

## 🏗️ Cómo encaja en la arquitectura event-driven

```
┌─────────────────────────────────────────────────────────────────┐
│  ⏰ Task Scheduler (este script)                                  │
│      ↓ cada 6h                                                    │
│  🐍 python/99_pipeline.py                                          │
│      ↓ produce CSVs frescos en data/outputs/                      │
│  ☁️  OneDrive sync (segundos)                                     │
│      ↓                                                            │
│  ⚡ Power Automate (trigger por cambio de archivo)                │
│      ↓ < 1 minuto                                                 │
│  📨 Email a Gmail/Hotmail con alertas y reporte                   │
└─────────────────────────────────────────────────────────────────┘
```

El pipeline corre desacoplado del dashboard. Cuando se detectan cambios significativos (≥30% MoM), el script `08_generar_alertas.py` produce `alertas_skills.csv` → OneDrive lo sincroniza → Power Automate dispara el email en **menos de 1 minuto desde que el evento ocurrió**.

---

## 🪵 Logs

Los logs se guardan en `logs/pipeline_YYYYMMDD.log` (rotación diaria automática). Están en `.gitignore` para no versionarlos.

Para revisar errores históricos:

```powershell
Get-ChildItem .\logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5
Get-Content .\logs\pipeline_20260525.log -Tail 50
```

---

## 🛑 Limitaciones

- **Necesita que tu PC esté encendido** para que la tarea se ejecute. Si está apagado durante el horario programado, la tarea se ejecuta cuando enciendes (gracias a `-StartWhenAvailable`).
- **No corre en sesiones bloqueadas con políticas estrictas.** La tarea está registrada en modo "Interactivo" — funciona normalmente en estaciones de trabajo, no en servidores headless.
- **No es alta disponibilidad.** Para producción real, migrar a Azure Logic Apps + función serverless (próximo paso del roadmap).
