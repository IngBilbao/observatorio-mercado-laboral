# 📅 Flujo 1 — Reporte Semanal Automático

> **Objetivo:** cada lunes a las 8:00 AM (hora de Madrid), refrescar el dataset de Power BI, exportar el dashboard como PDF y enviarlo por email a los stakeholders.

**Trigger:** Recurrencia (programado)
**Destinatarios:** `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`
**Salidas:** Email con PDF adjunto + log en OneDrive

---

## 🔧 Prerequisitos

- [x] `.pbix` publicado al workspace `d287f4ea-8862-4da2-8291-ba4168afd518`
- [ ] Personal Gateway instalado y configurado (ver `CONFIGURAR_REFRESH.md`)
- [ ] DatasetId y ReportId anotados (ver `COMO_OBTENER_IDS.md`)
- [ ] Refresh manual del dataset funciona desde Power BI Service

---

## 🏗️ Construcción paso a paso

### 1. Crear el flujo

1. Abre **https://make.powerautomate.com**
2. **Crear → Flujo de nube programado**
3. Configuración inicial:
   - Nombre: `Observatorio · Reporte Semanal`
   - Iniciar el: próximo lunes a las **08:00**
   - Repetir cada: **1 Semana**
   - Días: **Lunes**
   - Zona horaria: **(UTC+01:00) Bruselas, Copenhague, Madrid, París**
4. Click en **Crear**.

### 2. Paso — Inicializar variables

Agrega 3 acciones **Inicializar variable**:

| Nombre        | Tipo   | Valor                                                       |
|---------------|--------|-------------------------------------------------------------|
| `WorkspaceId` | Cadena | `d287f4ea-8862-4da2-8291-ba4168afd518`                      |
| `DatasetId`   | Cadena | `<pega tu Dataset ID aquí>`                                  |
| `ReportId`    | Cadena | `<pega tu Report ID aquí>`                                   |

### 3. Paso — Refrescar el dataset

**Nueva acción → Buscar "Power BI" → "Actualizar un conjunto de datos"**

Campos:
- **Workspace:** `Personalizado` → expresión: `variables('WorkspaceId')`
- **Conjunto de datos:** `Personalizado` → expresión: `variables('DatasetId')`

### 4. Paso — Esperar a que termine el refresh (polling)

El refresh es asíncrono — hay que esperar. Patrón "Until":

**Nueva acción → Inicializar variable**:
- Nombre: `EstadoRefresh`
- Tipo: Cadena
- Valor: `Unknown`

**Nueva acción → Hasta (Control)**:
- Condición: `EstadoRefresh` `es igual a` `Completed`
- Cambiar límites (⋯): Contador = 60, Tiempo de espera = `PT30M` (max 30 min)

Dentro del **Hasta**:

**Acción → Retraso (Schedule → Delay):**
- Contar: 30
- Unidad: Segundo

**Acción → Power BI → "Obtener el historial de actualización":**
- Workspace: `variables('WorkspaceId')`
- Conjunto de datos: `variables('DatasetId')`
- Top: `1`

**Acción → Establecer variable:**
- Nombre: `EstadoRefresh`
- Valor (expresión):
  ```
  first(body('Obtener_el_historial_de_actualización')?['value'])?['status']
  ```

> ⚠️ El nombre exacto de la acción puede tener tildes en español. Usa el botón "Agregar contenido dinámico" para evitar errores.

### 5. Paso — Validar que terminó OK

**Después del bucle Hasta → Condición:**
- `EstadoRefresh` `es igual a` `Completed`
  - **Si NO**: enviar email de error (ver paso 9) y terminar
  - **Si SÍ**: continuar

### 6. Paso — Exportar el reporte a PDF

**Power BI → "Exportar a archivo para informes de Power BI":**
- Workspace: `variables('WorkspaceId')`
- Informe: `variables('ReportId')`
- **Formato de exportación:** `PDF`
- *(Opcional)* Páginas: dejar vacío para todo el informe, o especificar `ReportSection,ReportSection1` para páginas concretas.

> 💡 Esta acción es **asíncrona**. Power Automate la maneja transparentemente — bloquea hasta que el PDF esté listo y te devuelve el `Cuerpo` con los bytes.

### 7. Paso — Guardar copia en OneDrive (log histórico)

**OneDrive for Business → "Crear archivo":**
- Ruta: `/Bilbao Analytics/Observatorio/Reportes/`
- Nombre del archivo (expresión):
  ```
  concat('observatorio_', formatDateTime(utcNow(), 'yyyy-MM-dd'), '.pdf')
  ```
- Contenido del archivo: `Cuerpo` (output de la acción "Exportar a archivo")

### 8. Paso — Enviar email con el PDF

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
  <p style="color:#9090A8; margin-top:-8px;">Resumen semanal — Bilbao Analytics</p>
  <hr style="border:0; border-top:1px solid #7B2FBE; margin:16px 0;">

  <p>Hola,</p>
  <p>Adjunto encontrarás el reporte de esta semana del Observatorio del Mercado Laboral en Datos & Tecnología. Incluye:</p>
  <ul>
    <li>📈 KPIs principales: ofertas totales, salario mediano, % remoto</li>
    <li>🏆 Top skills más demandadas del periodo</li>
    <li>🌍 Distribución geográfica de las ofertas</li>
    <li>🔮 Forecast de demanda para los próximos 12 meses</li>
    <li>👥 Arquetipos profesionales identificados (clustering)</li>
  </ul>

  <p style="margin-top:24px;">
    <a href="https://app.powerbi.com/groups/d287f4ea-8862-4da2-8291-ba4168afd518/reports/@{variables('ReportId')}"
       style="background-color:#00D4FF; color:#0D0D1A; padding:10px 20px; text-decoration:none; border-radius:6px; font-weight:bold;">
      Abrir dashboard en Power BI →
    </a>
  </p>

  <p style="color:#9090A8; font-size:12px; margin-top:32px;">
    Generado automáticamente el @{formatDateTime(utcNow(),'dd/MM/yyyy HH:mm')} UTC.<br>
    Bilbao Analytics · <a href="https://github.com/IngBilbao/observatorio-mercado-laboral" style="color:#00D4FF;">repositorio en GitHub</a>
  </p>
</div>
```

### 9. Paso (rama "error") — Email de fallo

Si el refresh falló, dentro de la rama "Si NO" del paso 5:

**Outlook → Enviar correo:**
- Para: `bilbao990512@gmail.com`
- Asunto: `⚠️ Observatorio — Fallo en refresh del @{utcNow()}`
- Cuerpo:
  ```
  El refresh programado del dataset falló con estado: @{variables('EstadoRefresh')}.

  Revisar el historial en:
  https://app.powerbi.com/groups/@{variables('WorkspaceId')}/settings/datasets/@{variables('DatasetId')}
  ```

---

## ✅ Probar el flujo

1. **Guardar** el flujo.
2. **Probar → Manualmente → Probar**.
3. Verifica que:
   - El dataset arranque su refresh.
   - El bucle "Hasta" haga polling hasta ver `Completed`.
   - Llegue el PDF a OneDrive.
   - Llegue el email con el PDF adjunto.

---

## 📐 Diagrama final del flujo

```
Recurrencia (Lun 8:00)
    │
    ▼
Inicializar variables (3)
    │
    ▼
Refrescar dataset PBI
    │
    ▼
┌── Hasta (EstadoRefresh = Completed) ──┐
│   Retraso 30s                           │
│   Obtener historial de actualización    │
│   Establecer EstadoRefresh              │
└─────────────────────────────────────────┘
    │
    ▼
¿Completed?
    ├── NO → Email de error → FIN
    └── SÍ ↓
Exportar PDF
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

## 🚀 Mejoras futuras (v2)

- [ ] Inyectar KPIs reales en el cuerpo del email (Var MoM, Top Skill del Mes) usando una consulta DAX previa vía conector "Ejecutar una consulta contra un conjunto de datos".
- [ ] Adjuntar también el CSV de alertas si hay skills críticas.
- [ ] Publicar el PDF en un canal de Teams en lugar de email (audiencia más amplia).
- [ ] Manejar reintentos con backoff exponencial si el refresh falla por timeout.
