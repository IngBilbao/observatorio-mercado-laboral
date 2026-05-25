# 🚨 Flujo 2 — Alertas de Cambio en Skills

> **Objetivo:** cuando el archivo `alertas_skills.csv` se actualiza en OneDrive (lo genera el script Python `08_generar_alertas.py`), el flujo lee las skills críticas y envía un email destacando los cambios significativos.

**Trigger:** OneDrive — Cuando se modifica un archivo
**Destinatarios:** `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`
**Salida:** 1 email por ejecución, con tabla HTML de skills en alerta

---

## 🔧 Prerequisitos

- [ ] Carpeta `/Bilbao Analytics/Observatorio/outputs/` en OneDrive (donde se sube `alertas_skills.csv`)
- [ ] Script `python/08_generar_alertas.py` ejecutándose periódicamente (manualmente, vía Tarea Programada de Windows, o vía Desktop Flow)

> 💡 Como `data/outputs/` ya está dentro de tu carpeta OneDrive sincronizada (tu proyecto vive en `OneDrive - Bilbao Analytics`), el archivo automáticamente se sube. Solo necesitas la ruta correcta en OneDrive for Business.

---

## 🏗️ Construcción paso a paso

### 1. Crear el flujo

1. **https://make.powerautomate.com → Crear → Flujo de nube automatizado**
2. Nombre: `Observatorio · Alertas de Skills`
3. Buscar trigger: **"OneDrive for Business — Cuando se modifica un archivo"**
4. Click en **Crear**.

### 2. Configurar el trigger

| Campo                 | Valor                                                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------------------------------------|
| Carpeta               | Navega a la carpeta donde está `alertas_skills.csv` (la ruta dentro de tu OneDrive personal del proyecto)              |
| Incluir subcarpetas   | No                                                                                                                     |

> ⚠️ La ruta en OneDrive depende de cómo aparezca el folder del proyecto en tu OneDrive. Algo como:
> `/Bilbao Analitycs/Proyectos/Proyecto analista de datos/observatorio-mercado-laboral/data/outputs/`

### 3. Paso — Condición: solo procesar `alertas_skills.csv`

**Acción → Condición (Control):**
- `Nombre del archivo` `es igual a` `alertas_skills.csv`

Si **NO**: terminar. Si **SÍ**: continuar.

### 4. Paso — Obtener el contenido del archivo

**OneDrive for Business → "Obtener contenido del archivo":**
- Archivo: `Identificador` del trigger

### 5. Paso — Parsear el CSV

Power Automate no tiene parser CSV nativo, pero hay dos opciones:

#### Opción A (más simple) — Acción "Crear tabla CSV"
> No existe nativa. Se usa el truco de leer como texto y splitear.

#### Opción B (recomendada) — Usar `Office Scripts` o función `split()`

**Inicializar variable** `Filas`:
- Tipo: Matriz
- Valor:
  ```
  skip(split(decodeBase64(body('Obtener_contenido_del_archivo')['$content']), '\r\n'), 1)
  ```

> 💡 `skip(..., 1)` salta la cabecera. Si el CSV usa `\n` solo (Linux line endings), cambiar a `'\n'`.

### 6. Paso — Iterar las filas y enviar 1 email consolidado

**Inicializar variable** `TablaHTML`:
- Tipo: Cadena
- Valor:
  ```
  <table style="border-collapse:collapse; width:100%;">
    <thead>
      <tr style="background-color:#1A1A2E; color:#00D4FF;">
        <th style="padding:8px; text-align:left;">Skill</th>
        <th style="padding:8px;">Dirección</th>
        <th style="padding:8px;">Variación</th>
        <th style="padding:8px;">Severidad</th>
      </tr>
    </thead>
    <tbody>
  ```

**Acción → Aplicar a cada (Apply to each):**
- Entrada: `variables('Filas')`
- Dentro:
  - **Condición:** la fila no está vacía → `length(items('Apply_to_each'))` `mayor que` `0`
  - **Inicializar variables temporales** (en cada iteración usar `Componer` para sacar campos):

    Crear acción **Componer** para `Campos`:
    ```
    split(items('Apply_to_each'), ',')
    ```

    Luego acceder con `outputs('Componer')?[index]`:
    - skill            → `outputs('Componer')?[0]`
    - mes_actual       → `outputs('Componer')?[1]`
    - mes_anterior     → `outputs('Componer')?[2]`
    - ofertas_act      → `outputs('Componer')?[3]`
    - ofertas_ant      → `outputs('Componer')?[4]`
    - variacion_pct    → `outputs('Componer')?[5]`
    - direccion        → `outputs('Componer')?[6]`
    - severidad        → `outputs('Componer')?[7]`
    - mensaje          → `outputs('Componer')?[8]`

  - **Anexar a variable de cadena** `TablaHTML`:
    ```
    <tr>
      <td style="padding:6px; border-bottom:1px solid #7B2FBE;">@{outputs('Componer')?[0]}</td>
      <td style="padding:6px; border-bottom:1px solid #7B2FBE; color:@{if(equals(outputs('Componer')?[6], 'ALZA'), '#00E396', '#FF4D6D')};">@{outputs('Componer')?[6]}</td>
      <td style="padding:6px; border-bottom:1px solid #7B2FBE;">@{outputs('Componer')?[5]}%</td>
      <td style="padding:6px; border-bottom:1px solid #7B2FBE; font-weight:bold;">@{outputs('Componer')?[7]}</td>
    </tr>
    ```

**Después del Apply to each:**

**Anexar a variable de cadena** `TablaHTML`:
```
    </tbody>
  </table>
```

### 7. Paso — Enviar email solo si hay alertas

**Condición:** `length(variables('Filas'))` `mayor que` `0`

Si **SÍ**:

**Outlook → Enviar correo (V2):**

| Campo   | Valor                                                                                  |
|---------|----------------------------------------------------------------------------------------|
| Para    | `bilbao990512@gmail.com;bilbao990512@hotmail.com`                                       |
| Asunto  | `🚨 Observatorio — @{length(variables('Filas'))} skills en alerta`                       |
| Cuerpo  | (ver HTML completo abajo)                                                              |

#### Cuerpo HTML del email

```html
<div style="font-family: 'Segoe UI', Arial, sans-serif; background-color:#0D0D1A; color:#E8E8F0; padding:24px; max-width:720px; border-radius:8px;">
  <h2 style="color:#FF4D6D; margin-top:0;">🚨 Alerta del Observatorio</h2>
  <p style="color:#9090A8;">Detectados cambios significativos (±30% MoM) en la demanda de skills.</p>
  <hr style="border:0; border-top:1px solid #7B2FBE; margin:16px 0;">

  @{variables('TablaHTML')}

  <p style="margin-top:24px; color:#9090A8; font-size:13px;">
    Severidad: <strong style="color:#FF4D6D;">CRITICA</strong> (>60%) ·
    <strong style="color:#FFB020;">ALTA</strong> (45-60%) ·
    <strong style="color:#9090A8;">MEDIA</strong> (30-45%)
  </p>

  <p style="margin-top:24px;">
    <a href="https://app.powerbi.com/groups/d287f4ea-8862-4da2-8291-ba4168afd518"
       style="background-color:#00D4FF; color:#0D0D1A; padding:10px 20px; text-decoration:none; border-radius:6px; font-weight:bold;">
      Ver detalle en Power BI →
    </a>
  </p>

  <p style="color:#9090A8; font-size:12px; margin-top:32px;">
    Generado automáticamente el @{formatDateTime(utcNow(),'dd/MM/yyyy HH:mm')} UTC.<br>
    Bilbao Analytics · Observatorio Mercado Laboral
  </p>
</div>
```

Si **NO** (cero alertas): no hacer nada. El flujo termina silencioso.

---

## 🧪 Probar el flujo

1. Asegúrate de que `alertas_skills.csv` existe en la carpeta correcta de OneDrive (ya lo generamos: 8 alertas detectadas).
2. **Guardar** el flujo.
3. Trigger manual: edita ligeramente el CSV (abrir y guardar) → el trigger debería dispararse en ~1 minuto.
4. Verifica que llegue el email con la tabla.

> ⚠️ El trigger de OneDrive puede tardar **hasta 1 minuto** en detectar el cambio — es asíncrono por diseño.

---

## 📐 Diagrama del flujo

```
Trigger: Archivo modificado en /outputs/
    │
    ▼
¿Nombre = alertas_skills.csv?
    │ NO → FIN
    │ SÍ ↓
Obtener contenido del archivo
    │
    ▼
Parsear CSV → variable Filas
    │
    ▼
Inicializar TablaHTML con cabecera
    │
    ▼
┌── Aplicar a cada (fila) ────────────┐
│   Componer Campos = split(fila,',')  │
│   Anexar fila HTML a TablaHTML        │
└──────────────────────────────────────┘
    │
    ▼
Cerrar TablaHTML
    │
    ▼
¿Hay filas?
    │ NO → FIN silencioso
    │ SÍ ↓
Enviar email con TablaHTML
    │
    ▼
FIN
```

---

## 🚀 Mejoras futuras (v2)

- [ ] Agrupar por severidad y enviar email separado por severidad CRITICA.
- [ ] Enviar también notificación push a Teams del workspace de Bilbao Analytics.
- [ ] Llamar a una API de noticias para enriquecer el email con artículos relacionados con la skill (ej. "Snowflake +60%: artículos recientes").
- [ ] Si la skill `Python` cae >30% — eso es probablemente un error del pipeline, no del mercado. Filtrar skills "fundamentales" (Python, SQL, Excel) para excluirlas del trigger normal.
