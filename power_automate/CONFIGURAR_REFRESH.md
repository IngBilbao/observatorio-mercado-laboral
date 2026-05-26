# 🔄 Configurar el refresh automático del dataset *(opcional)*

> ⚠️ **Estado actual del proyecto:** el sistema funciona con **refresh on-demand** del dataset en Power BI Service. Esta es una decisión arquitectónica deliberada — ver [`ARQUITECTURA_EVENT_DRIVEN.md`](ARQUITECTURA_EVENT_DRIVEN.md).
>
> Esta guía documenta cómo activar el refresh automático **si en algún momento quieres dar ese paso**.

---

## ¿Cuándo te interesa activarlo?

| Cuando... | ¿Conviene activarlo? |
|---|---|
| Compartes el dashboard con stakeholders que necesitan ver datos frescos sin que tú toques nada | ✅ Sí |
| Es solo para tu portfolio o uso personal | ❌ No — el on-demand actual es suficiente |
| Quieres demostrar dominio del Gateway en entrevistas técnicas | ✅ Sí |
| Tienes el ancho de banda / capacity de Power BI Pro o Premium | ✅ Sí |

---

## Estrategia A — On-premises Data Gateway (Standard)

Es lo que ya tienes instalado ("Observatorio"). El bloqueo actual: faltan **credenciales válidas de Windows** para el conector File.

### Pasos para desbloquear

1. **Recuperar tu contraseña de Windows.** Si entras con PIN/cara/huella, esa NO es la contraseña que la gateway necesita.
   - Si tu Windows está vinculado a una cuenta Microsoft: resetear en https://account.microsoft.com/security
   - Si es cuenta local: `Configuración → Cuentas → Opciones de inicio de sesión → Contraseña → Cambiar`

2. **Averiguar el nombre de usuario correcto** ejecutando en PowerShell:
   ```powershell
   whoami
   ```
   Devuelve algo como `equipo\usuario`. Eso (con la barra invertida) es lo que va en "Nombre de usuario de Windows" en la gateway.

3. **Editar las conexiones de la gateway** en Power BI Service:
   - **⚙️ → Administrar conexiones y puertas de enlace → Conexiones**
   - Para las 2 conexiones tipo Carpeta que creaste:
     - Click en `⋯ → Editar`
     - Pega usuario (`EQUIPO\bilba` o el que devolvió `whoami`) y contraseña real de Windows
     - Desmarca "Omitir conexión de prueba"
     - Guarda — debe mostrar "Conexión correcta" en verde

4. **Asignar dataset a Gateway:**
   - Workspace → Dataset → `⋯ → Configuración`
   - Sección "Conexiones de puerta de enlace y nube" → selecciona **Gateway connection** = Observatorio
   - Mapea cada origen detectado a las conexiones de carpeta
   - Aplicar

5. **Probar refresh manual:**
   - `⋯ → Actualizar ahora`
   - Verificar en "Historial de actualización" que termine en `Completo`

6. **Programar refresh:**
   - En la misma configuración: sección "Actualizar" → activar
   - Frecuencia: diaria (recomendado), 6 AM (antes del horario laboral)
   - Cuenta de notificación de errores: `cristian.garcia@bilbaoanalytics.com`

7. **Agregar el paso de refresh al Flujo 1 de Power Automate:**
   - Antes del paso "Exportar PDF", añadir acción **Power BI → "Actualizar un conjunto de datos"**
   - Después: bucle **Until** verificando `status = Completed` con polling cada 30s

---

## Estrategia B — Migrar a cloud-native (elimina el Gateway)

Si quieres deshacerte del Gateway por completo:

1. **Subir CSVs a OneDrive cloud** (no la carpeta sincronizada local) o **SharePoint Online**.
2. **Reescribir los Power Query M** usando el conector `OneDrive.Files` o `SharePoint.Files` (OAuth, sin password).
3. **Modificar `99_pipeline.py`** para que tras generar los CSVs locales, los suba automáticamente al destino cloud vía Microsoft Graph API.
4. **Eliminar la gateway** (deja de ser necesaria).

**Pros:** sin dependencia de PC encendido, refresh totalmente cloud.
**Contras:** ~45 min de reescritura inicial. Requiere registrar una app en Azure AD para Graph API.

---

## Estrategia C — Migrar a base de datos cloud

La opción más "enterprise":

1. Provisionar **Azure SQL Database** (tier basic, ~5 USD/mes) o **Postgres en Supabase free tier**.
2. Modificar el pipeline para que escriba a la BD en lugar de CSVs.
3. Power BI conecta vía conector SQL Server o Postgres con OAuth.
4. Soporta **DirectQuery** — Power BI no almacena los datos, consulta en vivo.

**Pros:** arquitectura production-grade, soporte multi-usuario, queries DirectQuery en tiempo real.
**Contras:** ~3 horas de migración. Costo nominal mensual.

---

## 🚦 Recomendación

| Si tu prioridad es... | Camino |
|---|---|
| Tener el portfolio listo YA | Quédate con on-demand (status actual) — funciona perfecto |
| Activar auto-refresh sin reescribir nada | Estrategia A (resolver credenciales) |
| Solución limpia para el largo plazo | Estrategia B (cloud + OAuth) |
| Demostrar arquitectura enterprise | Estrategia C (BD cloud) |

Hoy el sistema está en on-demand y eso **NO es un problema** — al contrario, es una decisión defendible que vendes como "event-driven con refresh on-demand para FinOps". Ver [`ARQUITECTURA_EVENT_DRIVEN.md`](ARQUITECTURA_EVENT_DRIVEN.md) para el discurso completo.
