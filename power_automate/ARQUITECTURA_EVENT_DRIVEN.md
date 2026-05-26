# 🏗️ Arquitectura Event-Driven del Observatorio

> **Decisión arquitectónica clave:** las tres capas del sistema (datos, notificaciones, dashboard) se mantienen **desacopladas** y operan en horizontes temporales distintos. Esta separación de responsabilidades es deliberada y refleja patrones modernos de analytics (lambda architecture, event-driven design).

---

## 🎯 Las 3 capas

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                    │
│   CAPA 1 · DATOS                                                   │
│   ⏰ Task Scheduler ejecuta python/99_pipeline.py cada N horas    │
│   🐍 Produce CSVs frescos: clusters, predicciones, alertas        │
│   📁 Output: data/outputs/ (sincronizado por OneDrive)            │
│                                                                    │
│   Latencia hasta datos frescos: configurable (1h-24h)             │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
                                ↓ trigger por cambio de archivo
┌───────────────────────────────────────────────────────────────────┐
│                                                                    │
│   CAPA 2 · NOTIFICACIONES (Power Automate cloud flows)             │
│   ⚡ Flujo 2 — Alertas de skills (event-driven)                    │
│       Trigger: OneDrive detecta cambio en alertas_skills.csv      │
│       Acción: parseo + email HTML con tabla de alertas             │
│   📅 Flujo 1 — Reporte semanal (scheduled)                         │
│       Trigger: lunes 8:00 AM                                       │
│       Acción: export PDF de Power BI + email                       │
│                                                                    │
│   Latencia notificación crítica: < 1 minuto                       │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
                                ↓ (decoupled)
┌───────────────────────────────────────────────────────────────────┐
│                                                                    │
│   CAPA 3 · DASHBOARD (Power BI Service)                            │
│   📊 Modelo estrella publicado con datos embebidos                 │
│   🎨 6 páginas: Resumen, Skills, Salarios, Mapa, Predicciones,    │
│      Clusters                                                      │
│   🔄 Refresh on-demand: Power BI Desktop → Publicar                │
│                                                                    │
│   Razón del on-demand: exploración interactiva no requiere refresh│
│   continuo. Se evita consumo de capacity y costo innecesario.     │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Lo que es TIEMPO REAL (demostrable en vivo)

| Capacidad | Latencia | Cómo se demuestra |
|---|---|---|
| Pipeline ML completo | Cada N horas configurable | `Get-ScheduledTaskInfo BilbaoAnalytics_Observatorio` muestra última ejecución |
| Detección de cambios críticos en skills | Inmediata al correr el pipeline | Log de `08_generar_alertas.py` con timestamp |
| Email de alerta a stakeholders | **< 1 minuto** desde que aparece la alerta | EN VIVO: edita un valor en alertas_skills.csv → en menos de 60s llega el email |
| Reporte ejecutivo semanal | Lunes 8:00 AM puntual | Llega email con PDF en bandeja de entrada cada lunes |

---

## 🟡 Lo que es ON-DEMAND (cómo se posiciona)

| Capacidad | Frecuencia |
|---|---|
| Refresh del modelo en Power BI Service | Manual cuando hay cambios estructurales del pipeline |

**Lenguaje para CV/portfolio:**

> *"Arquitectura event-driven con desacoplamiento explícito entre las capas de datos, notificación y visualización. La capa de notificación opera en tiempo real (latencia <1 min) usando triggers por cambio de archivo. La capa de visualización se refresca on-demand para optimizar consumo de capacity, en línea con buenas prácticas de FinOps en Power BI."*

**Lenguaje para entrevista técnica:**

> *"Tres capas, tres horizontes temporales distintos. Los CSVs se regeneran cada N horas mediante un orquestador Python invocado por Task Scheduler. Cuando el script de alertas detecta cambios significativos, genera un archivo de eventos que Power Automate consume vía OneDrive trigger — eso da latencia de notificación bajo el minuto. El dashboard publicado es un snapshot que se refresca on-demand: las exploraciones interactivas no requieren refresh continuo. Esto es un patrón lambda-style aplicado al stack de Microsoft."*

---

## 🎬 Demo de 90 segundos para reclutadores

```
0:00 - 0:15  Abre el repo en GitHub. Muestra:
              · Badges del README (Python, PBI, Prophet, etc.)
              · Visual del clustering K-means
              · Forecast Prophet con bandas

0:15 - 0:30  Abre Power BI Service. Navega por las 6 páginas:
              · Resumen ejecutivo (KPIs)
              · Skills (top 10 + heatmap)
              · Mapa geográfico
              · Predicciones (banda de confianza Prophet)

0:30 - 0:50  Abre la terminal. Ejecuta:
              `Start-ScheduledTask -TaskName BilbaoAnalytics_Observatorio`
              Muestra los logs streaming.

0:50 - 1:00  El pipeline detecta cambios → alertas_skills.csv se
              actualiza → OneDrive sync.

1:00 - 1:30  Aparece en Gmail el email con tabla HTML
              de alertas — IN VIVO durante la demo.

1:30         Cierre: "Esto es event-driven analytics — datos frescos
              cada 6 horas, notificaciones críticas en < 1 minuto,
              dashboard exploratorio on-demand. Stack 100% Microsoft."
```

---

## 🔁 Roadmap para subir a la siguiente liga

Cuando quieras evolucionar la arquitectura:

| # | Mejora | Beneficio |
|---|---|---|
| 1 | Resolver credenciales del Gateway → activar auto-refresh del dataset | Dashboard 100% sincronizado sin intervención manual |
| 2 | Migrar CSVs a Azure Data Lake Storage Gen2 (o SharePoint Online) + conector OAuth | Elimina el Gateway por completo, todo cloud-native |
| 3 | Reemplazar Task Scheduler local por Azure Function programada | Alta disponibilidad, sin dependencia de PC encendido |
| 4 | Sustituir CSVs por base de datos relacional (Azure SQL / Postgres) | Soporte real-time queries desde PBI Direct Query |
| 5 | Power Automate enterprise flows con manejo de errores y reintentos | Production-grade reliability |
| 6 | Capa de observabilidad: Application Insights + Log Analytics | Detección automática de pipelines fallidos |
| 7 | Modelo ML servido como API REST (Flask/FastAPI + Azure Container Apps) | Endpoint público para calcular salarios |

---

## 📚 Referencias para profundizar

- [Lambda architecture (Wikipedia)](https://en.wikipedia.org/wiki/Lambda_architecture)
- [Event-driven design (Microsoft docs)](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven)
- [Power BI capacity FinOps](https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-what-is)
