# 🚨 Flujo 2 — Alertas de Cambio en Skills (versión JSON)

> **Objetivo:** cuando el archivo `alertas_skills.json` se actualiza en OneDrive (lo genera el script Python `08_generar_alertas.py`), el flujo lo parsea con la acción nativa de Power Automate y envía un email HTML con la tabla de alertas.

**Trigger:** OneDrive — Cuando se modifica un archivo
**Destinatarios:** `bilbao990512@gmail.com`, `bilbao990512@hotmail.com`
**Salida:** 1 email por ejecución con tabla HTML estilizada

> **¿Por qué JSON en vez de CSV?** Power Automate parsea JSON nativamente con la acción **"Parse JSON"**. No requiere `split()`, ni manejar `\r\n`, ni `decodeUriComponent()`. **Mucho más confiable** que parsear CSV manualmente.

---

## 🔧 Prerequisitos

- [ ] `python/08_generar_alertas.py` ejecutado al menos una vez (genera `alertas_skills.json`)
- [ ] El archivo está en una carpeta visible para Power Automate (dentro de tu OneDrive sincronizado)

---

## 🏗️ Construcción paso a paso

### 1. Crear el flujo

1. **https://make.powerautomate.com → Crear → Flujo de nube automatizado**
2. Nombre: `Observatorio · Alertas de Skills (JSON)`
3. Trigger: **OneDrive for Business — Cuando se modifica un archivo**
4. Click en **Crear**.

### 2. Configurar el trigger

| Campo | Valor |
|---|---|
| Carpeta | Navega a `.../observatorio-mercado-laboral/data/outputs` dentro de tu OneDrive |
| Incluir subcarpetas | No |

### 3. Condición — solo procesar `alertas_skills.json`

**Acción → Condición (Control):**
- Lado izquierdo: `Nombre del archivo con extensión` (dynamic content del trigger)
- Operador: `es igual a`
- Lado derecho: `alertas_skills.json`

Si **NO** → terminar el flujo.
Si **SÍ** → continuar.

### 4. Obtener contenido del archivo

**OneDrive for Business → "Obtener contenido del archivo"**
- Archivo: `Identificador` del trigger (dynamic content)

### 5. **Parse JSON** — aquí está la magia ✨

**Acción → "Análisis JSON" / "Parse JSON"** (categoría Data Operations):

- **Contenido:** `Cuerpo` de la acción "Obtener contenido del archivo" (dynamic content)
- **Esquema:** copia y pega exactamente esto:

```json
{
  "type": "object",
  "properties": {
    "generated_at": { "type": "string" },
    "umbral_pct": { "type": "number" },
    "total_alertas": { "type": "integer" },
    "alertas": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "skill": { "type": "string" },
          "mes_actual": { "type": "string" },
          "mes_anterior": { "type": "string" },
          "ofertas_mes_actual": { "type": "integer" },
          "ofertas_mes_anterior": { "type": "integer" },
          "variacion_pct": { "type": "number" },
          "direccion": { "type": "string" },
          "severidad": { "type": "string" },
          "mensaje": { "type": "string" }
        },
        "required": ["skill", "variacion_pct", "direccion", "severidad", "mensaje"]
      }
    }
  }
}
```

> 💡 **Tip:** si tienes dudas con el esquema, en lugar de pegar el JSON arriba puedes hacer clic en **"Generar a partir de muestra"** y pegar el contenido completo de `alertas_skills.json` — Power Automate genera el esquema automáticamente.

### 6. Condición — solo continuar si hay alertas

**Acción → Condición:**
- Lado izquierdo: `total_alertas` (dynamic content del Parse JSON)
- Operador: `es mayor que`
- Lado derecho: `0` (escribir como número, no como texto)

Si **NO** → terminar (sin spam de emails vacíos).
Si **SÍ** → continuar dentro de la rama True.

### 7. Construir tabla HTML iterando las alertas

**Acción → "Inicializar variable":**
- Nombre: `TablaHTML`
- Tipo: `Cadena`
- Valor:
  ```html
  <table style="border-collapse:collapse;width:100%;font-family:Segoe UI,Arial,sans-serif;">
    <thead>
      <tr style="background-color:#1A1A2E;color:#00D4FF;">
        <th style="padding:8px;text-align:left;border-bottom:1px solid #7B2FBE;">Skill</th>
        <th style="padding:8px;border-bottom:1px solid #7B2FBE;">Dirección</th>
        <th style="padding:8px;text-align:right;border-bottom:1px solid #7B2FBE;">Variación</th>
        <th style="padding:8px;border-bottom:1px solid #7B2FBE;">Severidad</th>
      </tr>
    </thead>
    <tbody>
  ```

**Acción → "Aplicar a cada" (Apply to each):**
- Entrada: `alertas` (dynamic content del Parse JSON)

Dentro del Apply to each:

**Acción → "Anexar a la variable de cadena" (Append to string variable):**
- Nombre: `TablaHTML`
- Valor (en modo Expresión Avanzada cuando haga falta combinar):
  ```html
  <tr>
    <td style="padding:6px;border-bottom:1px solid #2A2A45;">@{items('Apply_to_each')?['skill']}</td>
    <td style="padding:6px;border-bottom:1px solid #2A2A45;color:@{if(equals(items('Apply_to_each')?['direccion'],'ALZA'),'#00E396','#FF4D6D')};">@{items('Apply_to_each')?['direccion']}</td>
    <td style="padding:6px;border-bottom:1px solid #2A2A45;text-align:right;">@{formatNumber(items('Apply_to_each')?['variacion_pct'],'0.0')}%</td>
    <td style="padding:6px;border-bottom:1px solid #2A2A45;font-weight:bold;">@{items('Apply_to_each')?['severidad']}</td>
  </tr>
  ```

> 💡 Nota cómo accedo a los campos: `items('Apply_to_each')?['skill']` — el `?` evita errores si el campo está vacío. Esto es **mucho más limpio** que `outputs('Componer')?[index]` que tenías antes.

**Después del Apply to each:**

**Acción → "Anexar a la variable de cadena":**
- Nombre: `TablaHTML`
- Valor:
  ```html
    </tbody>
  </table>
  ```

### 8. Enviar email

**Office 365 Outlook → "Enviar un correo electrónico (V2)":**

| Campo | Valor |
|---|---|
| Para | `bilbao990512@gmail.com;bilbao990512@hotmail.com` |
| Asunto | `🚨 Observatorio — @{triggerOutputs()?['body/Name']} con @{outputs('Analizar_JSON')?['body/total_alertas']} alertas activas` |
| Cuerpo | (HTML abajo — activar modo `</>`) |

#### Cuerpo HTML del email

```html
<div style="font-family:'Segoe UI',Arial,sans-serif;background-color:#0D0D1A;color:#E8E8F0;padding:24px;max-width:720px;border-radius:8px;">
  <h2 style="color:#FF4D6D;margin-top:0;">🚨 Alerta del Observatorio</h2>
  <p style="color:#9090A8;">
    Detectados <b>@{outputs('Analizar_JSON')?['body/total_alertas']}</b> cambios significativos (umbral ±@{outputs('Analizar_JSON')?['body/umbral_pct']}% MoM) en la demanda de skills.
  </p>
  <hr style="border:0;border-top:1px solid #7B2FBE;margin:16px 0;">

  @{variables('TablaHTML')}

  <p style="margin-top:24px;color:#9090A8;font-size:13px;">
    Severidad: <strong style="color:#FF4D6D;">CRITICA</strong> (>60%) ·
    <strong style="color:#FFB020;">ALTA</strong> (45-60%) ·
    <strong style="color:#9090A8;">MEDIA</strong> (30-45%)
  </p>

  <p style="margin-top:24px;">
    <a href="https://app.powerbi.com/groups/d287f4ea-8862-4da2-8291-ba4168afd518"
       style="background-color:#00D4FF;color:#0D0D1A;padding:10px 20px;text-decoration:none;border-radius:6px;font-weight:bold;">
      Ver detalle en Power BI →
    </a>
  </p>

  <p style="color:#9090A8;font-size:12px;margin-top:32px;">
    Generado automáticamente · @{outputs('Analizar_JSON')?['body/generated_at']} <br>
    Bilbao Analytics · <a href="https://github.com/IngBilbao/observatorio-mercado-laboral" style="color:#00D4FF;">repositorio en GitHub</a>
  </p>
</div>
```

> ⚠️ Si el nombre exacto de tu acción Parse JSON es "Analizar JSON" en español, las expresiones usan `outputs('Analizar_JSON')`. Si es "Parse_JSON", ajusta. **El truco**: en lugar de escribir la expresión, usa el botón **"Agregar contenido dinámico"** que muestra los campos con clic — evita typos.

---

## 📐 Diagrama del flujo

```
Trigger: Archivo modificado en /outputs/
    │
    ▼
¿Nombre = alertas_skills.json?
    │ NO → FIN
    │ SÍ ↓
Obtener contenido del archivo
    │
    ▼
Analizar JSON (Parse JSON)  ← AQUÍ ESTÁ LA MAGIA
    │
    ▼
¿total_alertas > 0?
    │ NO → FIN silencioso
    │ SÍ ↓
Inicializar TablaHTML (con cabecera)
    │
    ▼
┌── Aplicar a cada (alertas) ────────────┐
│   Anexar fila HTML a TablaHTML          │
│   (acceso directo: items()?['skill'])   │
└─────────────────────────────────────────┘
    │
    ▼
Anexar cierre de tabla a TablaHTML
    │
    ▼
Enviar email con TablaHTML
    │
    ▼
FIN
```

---

## 🧪 Probar el flujo

1. Asegúrate de que `alertas_skills.json` existe en OneDrive (ejecuta `py python/08_generar_alertas.py` localmente).
2. **Guardar** el flujo.
3. Ejecuta el script otra vez (o edita y guarda el JSON manualmente) → el trigger se dispara en ~1 minuto.
4. Verifica que llegue el email con la tabla HTML correcta.

> 💡 **Trigger de prueba manual:** desde la página del flujo, click en **Probar → Manualmente** → modifica el archivo en OneDrive → debería dispararse.

---

## 🆚 Comparativa: JSON vs CSV

| Aspecto | JSON (esta guía) | CSV (versión anterior) |
|---|---|---|
| Parsing | Nativo (`Parse JSON`) | Manual (`split`, `decodeUriComponent`) |
| Acceso a campos | `items()?['skill']` | `outputs('Componer')?[0]` |
| Tipos de dato | Preservados (int, float, string) | Todos string → requiere `float()` |
| Manejo de `\r\n` | No aplica | Crítico, fuente de bugs |
| Reordenar columnas | No afecta | Romper índices |
| Errores típicos | Raros | "String/Integer don't match" |

**Resultado:** menos código, más robusto, más fácil de mantener.

---

## 🚀 Mejoras futuras

- [ ] Filtrar alertas por severidad: una acción `Filter array` antes del Apply to each para enviar solo CRITICA.
- [ ] Agrupar alertas por categoría de skill (Cloud, ML/AI, BI...) y enviar 1 email por categoría.
- [ ] Notificación push a Teams en lugar de email para alertas CRITICAS.
- [ ] Adjuntar el CSV original al email para análisis manual.
