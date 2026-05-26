# 📅 Flujo 1 — Reporte Semanal Automático

> **Objetivo:** cada lunes a las 8:00 AM (hora de Madrid), exportar el dashboard de Power BI como PDF y enviarlo por email a los stakeholders con un resumen ejecutivo.

**Trigger:** Recurrencia (programado)
**Cuenta ejecutora:** `cristian.garcia@bilbaoanalytics.com` (M365)
**Destinatarios:** `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`
**Salidas:** Email con PDF adjunto + log en OneDrive

---

## 📐 Posicionamiento arquitectónico

Este flujo opera en la **capa de notificaciones** de la arquitectura event-driven. **No refresca el dataset** — el dataset publicado se actualiza on-demand desde Power BI Desktop cuando hay cambios estructurales del modelo. Los datos del dashboard reflejan el estado más reciente publicado.

Para mantener los datos frescos hay dos componentes complementarios:
- **`scripts/programar_pipeline.ps1`** (Task Scheduler): genera CSVs frescos en `data/outputs/` cada N horas.
- **Flujo 2 — Alertas de Skills**: notifica EN TIEMPO REAL cualquier cambio crítico detectado por el pipeline (latencia < 1 min).

Este Flujo 1 es entonces **el resumen ejecutivo periódico**, mientras que el Flujo 2 es **el sistema de alertas reactivas**.

---

## 🔧 Prerequisitos

- [x] `.pbix` publicado al workspace `d287f4ea-8862-4da2-8291-ba4168afd518`
- [x] Cuenta M365 con licencia Power BI Pro
- [ ] **Report ID** anotado (ver [`COMO_OBTENER_IDS.md`](COMO_OBTENER_IDS.md))
- [ ] El dataset publicado contiene datos refrescados (publicaste desde Power BI Desktop tras correr el pipeline)

---

## 🏗️ Construcción paso a paso

### 1. Crear el flujo

1. Abre **https://make.powerautomate.com** logueado como `cristian.garcia@bilbaoanalytics.com`
2. **Crear → Flujo de nube programado**
3. Configuración inicial:
   - Nombre: `Observatorio · Reporte Semanal`
   - Iniciar el: próximo lunes a las **08:00**
   - Repetir cada: **1 Semana**
   - Días: **Lunes**
   - Zona horaria: **(UTC+01:00) Bruselas, Copenhague, Madrid, París**
4. Click en **Crear**.

### 2. Paso — Inicializar variables

Agrega 2 acciones **Inicializar variable**:

| Nombre        | Tipo   | Valor                                                       |
|---------------|--------|-------------------------------------------------------------|
| `WorkspaceId` | Cadena | `d287f4ea-8862-4da2-8291-ba4168afd518`                      |
| `ReportId`    | Cadena | `<pega tu Report ID aquí>`                                   |

### 3. Paso — Exportar el reporte a PDF

**Nueva acción → Power BI → "Exportar a archivo para informes de Power BI"**

Campos:
- **Workspace:** `Personalizado` → expresión: `variables('WorkspaceId')`
- **Informe:** `Personalizado` → expresión: `variables('ReportId')`
- **Formato de exportación:** `PDF`
- *(Opcional)* Páginas: dejar vacío para todo el informe, o especificar `ReportSection,ReportSection1` para páginas concretas.

> 💡 Esta acción es **asíncrona pero Power Automate la maneja transparentemente** — bloquea hasta que el PDF esté listo y te devuelve el `Cuerpo` con los bytes binarios.

### 4. Paso — Guardar copia en OneDrive (archivo histórico)

**OneDrive for Business → "Crear archivo":**
- Carpeta: `/Bilbao Analytics/Observatorio/Reportes/`
- Nombre del archivo (expresión):
  ```
  concat('observatorio_', formatDateTime(utcNow(), 'yyyy-MM-dd'), '.pdf')
  ```
- Contenido del archivo: dynamic content → `Cuerpo` de la acción "Exportar a archivo"

### 5. Paso — Enviar email con el PDF adjunto

**Office 365 Outlook → "Enviar un correo electrónico (V2)":**

| Campo        | Valor                                                                 |
|--------------|-----------------------------------------------------------------------|
| Para         | `bilbao990512@gmail.com;bilbao990512@hotmail.com`                     |
| Asunto       | `📊 Observatorio Datos & Tech — Resumen semanal @{formatDateTime(utcNow(),'dd/MM/yyyy')}` |
| Cuerpo       | (Ver HTML abajo. Cambiar a modo HTML con el botón `</>`)              |
| Importancia  | Normal                                                                |
| Mostrar opciones avanzadas → **Datos adjuntos**:                                       |
|   Nombre     | `observatorio_semanal.pdf`                                            |
|   Contenido  | `Cuerpo` de la acción "Exportar a archivo"                            |

#### Cuerpo HTML del email

```html
<div style="font-family: 'Segoe UI', Arial, sans-serif; background-color:#0D0D1A; color:#E8E8F0; padding:24px; max-width:640px; border-radius:8px;">
  <h2 style="color:#00D4FF; margin-top:0;">🌌 Observatorio del Mercado Laboral</h2>
  <p style="color:#9090A8; margin-top:-8px;">Resumen semanal · Bilbao Analytics</p>
  <hr style="border:0; border-top:1px solid #7B2FBE; margin:16px 0;">

  <p>Hola,</p>
  <p>Adjunto encontrarás el reporte de esta semana del Observatorio del Mercado Laboral en Datos & Tecnología. Incluye:</p>
  <ul>
    <li>📈 KPIs principales: ofertas totales, salario mediano, % remoto</li>
    <li>🏆 Top skills más demandadas del periodo</li>
    <li>🌍 Distribución geográfica de las ofertas</li>
    <li>🔮 Forecast Prophet de demanda para los próximos 12 meses</li>
    <li>👥 Arquetipos profesionales identificados via K-means clustering</li>
  </ul>

  <p style="margin-top:24px;">
    <a href="https://app.powerbi.com/groups/d287f4ea-8862-4da2-8291-ba4168afd518/reports/@{variables('ReportId')}"
       style="background-color:#00D4FF; color:#0D0D1A; padding:10px 20px; text-decoration:none; border-radius:6px; font-weight:bold;">
      Abrir dashboard en Power BI →
    </a>
  </p>

  <p style="color:#9090A8; font-size:12px; margin-top:32px;">
    Generado automáticamente el @{formatDateTime(utcNow(),'dd/MM/yyyy HH:mm')} UTC.<br>
    Las alertas de cambios significativos en skills llegan en tiempo real vía un flujo separado.<br>
    Bilbao Analytics · <a href="https://github.com/IngBilbao/observatorio-mercado-laboral" style="color:#00D4FF;">repositorio en GitHub</a>
  </p>
</div>
```

---

## ✅ Probar el flujo

1. **Guardar** el flujo.
2. **Probar → Manualmente → Probar**.
3. Verifica:
   - ✅ La exportación a PDF se completa (Power BI tarda 30s-2min según tamaño del informe)
   - ✅ El PDF aparece en `OneDrive/Bilbao Analytics/Observatorio/Reportes/observatorio_<fecha>.pdf`
   - ✅ Llega el email con el PDF adjunto a ambas direcciones (Gmail y Hotmail)

---

## 📐 Diagrama del flujo

```
Recurrencia (Lun 8:00 Madrid)
    │
    ▼
Inicializar variables (WorkspaceId, ReportId)
    │
    ▼
Exportar reporte a PDF
    │
    ▼
Guardar copia en OneDrive
    │
    ▼
Enviar email con PDF adjunto
    │
    ▼
FIN
```

---

## 🚀 Mejoras futuras

- [ ] Refrescar el dataset antes de exportar (requiere resolver credenciales de Gateway). Una vez resuelto, agregar al inicio: acción `Power BI → Actualizar conjunto de datos` + bucle Hasta para esperar a `status = Completed`.
- [ ] Inyectar KPIs reales en el cuerpo del email (Var MoM, Top Skill) usando una consulta DAX previa vía conector "Ejecutar una consulta contra un conjunto de datos".
- [ ] Publicar el PDF también en un canal de Teams (audiencia más amplia).
- [ ] Generar mini-resumen HTML con los 3 cambios más relevantes de la semana usando el script `08_generar_alertas.py`.

---

## 💡 Sobre el refresh del dataset

El refresh automático del dataset desde Power BI Service **requiere configurar credenciales válidas en el Gateway local** (ver [`CONFIGURAR_REFRESH.md`](CONFIGURAR_REFRESH.md) si quieres volver a esa ruta).

**Cómo se mantienen frescos los datos del dashboard en la arquitectura actual:**

| Capa | Mecanismo | Latencia |
|---|---|---|
| Datos (CSVs en disco) | Task Scheduler ejecuta `99_pipeline.py` cada N horas | Cuasi-real-time |
| Notificaciones de cambios críticos | Flujo 2 dispara emails en cambio de archivo | < 1 min |
| Dataset publicado en PBI Service | Refresh manual cuando se quiere actualizar visualizaciones | On-demand |
| Reportes ejecutivos semanales | Este Flujo 1 (sin refresh) | Semanal |

Esta separación de responsabilidades por capa es un patrón estándar en arquitecturas modernas de analytics — y se vende muy bien en entrevistas.
