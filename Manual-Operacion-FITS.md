# Manual de Operación — Sistema de Reformateo de CV (FITS LLC)

> Cierre del proyecto **CV Reformatting Automatizado** (contrato firmado 3 jul 2026, `00-contrato/Contrato.md`). Este documento cumple el compromiso de "documentación" de la cláusula Décima del contrato y del cronograma de referencia (Anexo 1, Semana 3: "Entrega y documentación"). No reemplaza el contrato ni el PRD — donde haya diferencia, manda el contrato firmado.
>
> Última actualización: 8 sep 2026.

---

# Parte 1 — Manual para el equipo de FITS

## 1. Qué hace el sistema

Cuando un reclutador mueve un candidato a la etapa **"Convert Resume - [Formato]"** correspondiente en JazzHR, el sistema:

1. Detecta el movimiento automáticamente (sin acción manual adicional).
2. Descarga el CV original del candidato (PDF o DOCX).
3. Lo transforma con un agente de IA (Anthropic/Claude) aplicando las 4 reglas de contenido de FITS (ver §4).
4. Genera el `.docx` final con el formato de branding correcto (logo, fuente, orden de secciones).
5. Lo sube a una subcarpeta del candidato en SharePoint.
6. Notifica por correo al reclutador asignado del candidato.
7. Registra el resultado en un Google Sheet de control.

Todo esto ocurre en **menos de 5 minutos** desde que el candidato llega a la etapa (criterio de aceptación del contrato, Módulo 3).

## 2. Cómo usarlo — el único paso manual

El reclutador **mueve el candidato a la etapa que corresponde al formato que necesita**, dentro del workflow de JazzHR del cliente farmacéutico correspondiente. No hay ninguna otra acción manual: no hay que subir el CV a otro lado, ni pedirle nada a Insighty.

| Formato | Cuándo se usa | Etapa en JazzHR |
|---|---|---|
| **New Format** | SOW, Haleon FG, JNJ | `CONVERT RESUME-NEW FORMAT` (el nombre exacto puede variar levemente entre workflows) |
| **Non Template** | Medtronic, Integra FG, Haleon FG, Beeline, Amgen FG, Abbott FG, JNJ | `CONVERT RESUME-NON TEMPLATE` |
| **BD Format** | Becton Dickinson | `CONVERT RESUME-BD FORMAT` |

> El formato **Worksense** (Johnson & Johnson) fue descartado por FITS (confirmado por Paola, 21 jul 2026) y no está integrado — no existe una etapa para él en JazzHR.

El mapeo completo de las 13 etapas en los 10 workflows está en `conocimiento/jazzhr-stepids-convert-resume.md` (referencia técnica, no hace falta para el uso diario).

## 3. Dónde llega el resultado

- **Archivo:** `.docx` editable, en SharePoint — sitio `Operaciones-RecursosHumanos`, biblioteca `Shared Documents`, carpeta `Resumes/{Nombre del candidato} ({ID de candidato})/{Formato}.docx`. Cada candidato tiene su propia subcarpeta.
- **Notificación por correo:** al reclutador asignado al candidato en JazzHR (el "hiring lead" del job), con el CV adjunto/enlace. Si por algún motivo no se puede identificar al reclutador asignado, el correo cae a `reclutamiento@fitspr.com` como respaldo.
- **Horario de envío de la notificación:** Lunes a Viernes 7:00am–8:00pm y Sábado 7:00am–4:00pm, hora de Puerto Rico. Si un candidato se procesa fuera de ese horario (de noche, domingo), el correo **no se pierde** — queda en cola y se envía automáticamente al inicio del siguiente ciclo laboral. El `.docx` en SharePoint y el registro en el Sheet ocurren igual, sin depender del horario.
- **Editable, no entrega final:** el `.docx` está pensado para que el reclutador lo revise y ajuste antes de mandarlo al cliente final de FITS. El sistema **no envía nada al cliente externo** — esa entrega sigue siendo tarea del reclutador (fuera del alcance contratado).

## 4. Reglas de contenido que aplica el agente de IA

En este orden, sobre los 3 formatos activos (New Format, Non Template, BD Format):

1. **Traducción al inglés** si el CV original está en otro idioma. El resultado final siempre queda en inglés.
2. **Conversión a tercera persona** — elimina frases en primera persona ("I managed...") y las reescribe en tercera persona.
3. **Objective → Summary** — si el CV trae una sección "Objective" (típico de CVs poco profesionales), se reemplaza por un "Summary" en tono profesional de reclutamiento.
4. **Reescritura de summaries pobres o incompletos** — si ya hay un Summary pero es muy corto o genérico, se reescribe. Este es el único punto que requiere revisión de calidad por parte de FITS (ver §6) porque depende de criterio editorial, no de una regla binaria.

**Principio de no invención:** el agente nunca agrega experiencia, empresas, fechas, títulos o skills que no estén en el CV original. Si no puede verificar un dato con certeza contra el CV fuente, prefiere dejarlo en blanco o bloquear el caso (ver §7) antes que inventarlo. Por ejemplo: si el CV no trae una lista de Skills explícita, el sistema deja esa sección vacía en vez de inferir skills a partir de la experiencia narrada.

**Particularidad de BD Format:** no tiene sección "Skills" separada — el pueblo de residencia del candidato se incluye dentro de "Summary of Skills".

## 5. Qué NO hace el sistema (fuera de alcance contractual)

- **CVs escaneados o en imagen** (PDF sin texto seleccionable) — el agente necesita texto legible por máquina. Si llega uno de estos, el caso queda bloqueado (no se genera un `.docx` con datos inventados).
- **Evaluación de idoneidad del candidato** — eso lo hace el sistema de AI Screening de Fase 1, es un proyecto distinto.
- **Entrega final al cliente farmacéutico de FITS** — el sistema entrega solo al equipo interno.
- **Templates adicionales** a los 4 definidos, o ajustes de prompt para tipos de CV muy distintos a los del set de prueba — esto es nuevo alcance, se cotiza aparte.
- **Modificación de otras etapas** de los workflows de JazzHR — el sistema solo interactúa con las etapas `Convert Resume - [Formato]`.

## 6. Cómo revisar la calidad y el historial de procesamiento

Todo candidato procesado (con éxito o con error) queda registrado en el Google Sheet:

**"FITS CV Reformatting - Log de Procesamiento"**
`https://docs.google.com/spreadsheets/d/1EM7GeQ7AePoMyngzDsRgMgnjj85K_pIoqfa1u4ukAo4/edit`

Tiene 3 pestañas:

| Pestaña | Para qué sirve |
|---|---|
| **Sheet1** (log principal) | Una fila por candidato procesado: nombre, formato, resultado, enlace de SharePoint, si se envió el correo, etc. Las columnas `reviewStatus` / `reviewComment` las completa Paola manualmente después de revisar el `.docx` — sirven como evidencia del criterio de aceptación de calidad del Summary (≥90% de aprobación). |
| **Errores de Procesamiento** | Candidatos que quedaron bloqueados de forma permanente (ej. CV escaneado, dato no verificable) — con el motivo exacto. Estos **no se reintentan solos**; requieren revisión (ver §7). |
| **Notificaciones Pendientes** | Correos que se generaron fuera del horario laboral y están en cola para despacharse en el próximo ciclo hábil. Es normal ver filas acá durante la noche o el domingo — se vacían automáticamente en horario laboral. |

## 7. Qué hacer si un candidato no llega o parece un error

1. **Buscar al candidato en la pestaña "Sheet1"** por nombre o `candidateId`. Si aparece con `resultado: OK`, revisar la carpeta de SharePoint — puede ser que el correo esté en la pestaña "Notificaciones Pendientes" esperando el horario laboral.
2. **Si aparece en "Errores de Procesamiento"**, el motivo (columna `motivo`) explica por qué quedó bloqueado. Casos conocidos:
   - CV escaneado o sin texto legible → fuera de alcance, requiere que el reclutador consiga una versión con texto seleccionable.
   - Un dato del CV no se pudo verificar con certeza (ej. una fecha o skill "pegada" sin espacio en el PDF original) → puede resolverse pidiendo a Insighty que reprocese el caso.
3. **Si no aparece en ninguna pestaña** y ya pasaron más de 15-20 minutos desde que se movió a la etapa, contactar a Insighty con el `candidateId` y el nombre del candidato.
4. **No mover el candidato de etapa repetidamente** intentando "forzar" el reproceso — puede generar duplicados. Ante una duda, escribir a Insighty primero.

## 8. Garantía y soporte

- **Garantía:** 30 días calendario desde la Fecha de Go-Live Final, sobre defectos reproducibles dentro del alcance de los 3 módulos contratados. No cubre infraestructura ni cambios de API de terceros (Anthropic/Claude, JazzHR, Microsoft Graph). **Fecha de Go-Live Final acordada: 26 de agosto de 2026** (fecha de la capacitación al equipo de FITS) → garantía vigente hasta el **25 de septiembre de 2026**.
- **Mantenimiento correctivo:** hasta 5 horas en el primer mes, para defectos de producción y ajustes a configuraciones/variables existentes. No cubre nuevos templates, cambios a la lógica de transformación, ajustes de prompt por tipos de CV no cubiertos en el set de prueba, ni errores de terceros — eso se cotiza como orden de cambio separada.
- **Contacto de soporte:** Santiago Ciurlo — santiago@insightyai.com.

## 9. Contactos del proyecto

| Nombre | Rol |
|---|---|
| Yaritza Cordero Nieves | Representante legal / firma (FITS) |
| Jeremy Rivera | Coordinador (FITS) |
| Paola Guirado | Operación / validación de calidad (FITS) |
| Centeno | IT — Azure AD, SharePoint (FITS) |
| Santiago Ciurlo (santiago@insightyai.com) | Ejecución y soporte (Insighty AI) |

---

# Parte 2 — Anexo técnico / Runbook de soporte 

## 1. Arquitectura

```
JazzHR (candidato movido a etapa "Convert Resume - [Formato]")
   │
   ▼
n8n: JazzHR - Convert Resume Poller  (6gxbJ87rfAsbcCOO)   ← detecta el candidato (polling, cron)
   │  dispara vía webhook interno
   ▼
n8n: JazzHR - Convert Resume Processor  (mp3U5XDSxLCAX9kI)
   │  descarga CV → POST /transform → POST /render → sube a SharePoint → notifica/encola → registra en Sheet
   ▼
Microservicio Railway (FastAPI, 02-modulo2-agente-transformacion/microservicio/)
   - POST /transform  → extract.py + agent.py (Claude) + grounding.py → JSON canónico (cv-schema.json)
   - POST /render      → docxtpl sobre los 3 templates activos → .docx final

n8n: JazzHR - Convert Resume Notification Queue Flusher  (A2fusycYaExIdZ4R)
   - despacha correos que quedaron en cola fuera de horario laboral
```

Todos los workflows viven en la instancia compartida `fits.app.n8n.cloud` (misma instancia de Fase 1 / AI Screening y del proyecto hermano `contract-renewal`).

## 2. Componentes y estado operativo

| Componente | ID / URL | Cron actual | Notas |
|---|---|---|---|
| `JazzHR - Convert Resume Poller` | `6gxbJ87rfAsbcCOO` | `1,11,21,31,41,51 * * * *` | Sincronizado ~54s después de cada disparo de `AI Screening Poller` (cron fijo cada 10 min, intocable) para evitar el solapamiento de memoria que causó varios crashes OOM (ver §6). `saveDataSuccessExecution: "none"` — **una ejecución exitosa no deja rastro en `/executions`**, ver §6. |
| `JazzHR - Convert Resume Processor` | `mp3U5XDSxLCAX9kI` | (webhook, disparado por el Poller) | Cubre Módulo 2 + Módulo 3 completos. |
| `JazzHR - Convert Resume Notification Queue Flusher` | `A2fusycYaExIdZ4R` | `5,20,35,50 7-19 * * 1-5` y `5,20,35,50 7-15 * * 6` | Despacha la pestaña "Notificaciones Pendientes"; sin IF de horario propio, confía en su propio cron. |
| Microservicio (Railway) | `https://fits-llc-cv-reformatting-production-12c6.up.railway.app` | — | Cuenta `fitsscreening@gmail.com` (trial 30 días / 5 USD — **ver riesgo recurrente en §7**). Deploy automático al hacer push a GitHub (~1 min). Root Directory: `02-modulo2-agente-transformacion/microservicio`. |
| Google Sheet de log | `1EM7GeQ7AePoMyngzDsRgMgnjj85K_pIoqfa1u4ukAo4` | — | Cuenta `fitsscreening@gmail.com`, credencial `vuAQyDYC5NJboIEW` en n8n. 3 pestañas: `Sheet1`, `Errores de Procesamiento` (gid `1493500949`), `Notificaciones Pendientes` (gid `483100955`). |
| SharePoint | `netorg583168.sharepoint.com/sites/Operaciones-RecursosHumanos` | — | Document Library `Shared Documents`, carpeta raíz `Resumes/`. Auth: Azure AD App Registration (Microsoft Graph API), `.env` local del microservicio en Railway. |

## 3. Endpoints del microservicio

- `GET /health` — sin auth.
- `POST /transform` (header `X-API-Key`) — `{filename, content_base64}` → `{state: "ok"|"review", cv, usage}` o `422 {state:"failed", code, detail}`.
- `POST /render` (header `X-API-Key`) — `{template, cv}` → bytes del `.docx` o error JSON.

Variables de entorno obligatorias: `API_KEY`, `ANTHROPIC_API_KEY` (el servicio no arranca sin ellas). Detalle completo, límites de body y códigos de error en `02-modulo2-agente-transformacion/microservicio/README.md`.

## 4. Códigos de error conocidos y cómo se clasifican

| Código | Origen | Clasificación | Acción |
|---|---|---|---|
| `NO_TEXT_LAYER`, `CORRUPT_FILE` | `extract.py` | Permanente | Se marca en "Errores de Procesamiento", no se reintenta solo. |
| `GROUNDING_FAILED` (+ subtipos: `GROUNDING_TOKEN_NOT_FOUND`, `GROUNDING_METRIC_NOT_FOUND`, `GROUNDING_YEAR_NOT_FOUND`, `GROUNDING_I_STATEMENT`, `GROUNDING_NAME_NOT_FOUND`) | `grounding.py` | Permanente (pero puede no repetirse en un reproceso manual — la llamada a Claude no es determinística) | Revisar el CV real contra el motivo antes de descartarlo como bug; varios falsos positivos reales ya fueron corregidos (ver `Decisiones.md`). |
| `NO_RESUME_FILE` | Processor (n8n) | Permanente | Se marca, visible en el Sheet. |
| `SCHEMA_INVALID`, `OUTPUT_TRUNCATED`, `NO_TOOL_USE` | `agent.py` | Permanente | Indica problema con la respuesta del LLM, no con el CV en sí — revisar `prompt/transform-v1.md` y límite de tokens. |
| `RENDER_FAILED` | Processor / `/render` | Transitorio | No se marca, se reintenta en el siguiente ciclo del Poller. |

## 5. Trampa de diagnóstico — leer antes de tocar los Pollers

`Convert Resume Poller` (y `AI Screening Poller`) tienen `saveDataSuccessExecution: "none"` — una ejecución exitosa **no deja ningún rastro** en `GET /executions`. Un historial silencioso **no significa que el Poller esté caído**. Antes de concluir eso, seguir el procedimiento completo en `conocimiento/n8n-diagnostico-pollers.md` (evidencia downstream primero: Processor + Sheet real; test controlado con `saveDataSuccessExecution: "all"` solo si hace falta confirmar en vivo, revertido después). Esta trampa ya causó intervenciones innecesarias en producción 3 veces documentadas.

## 6. Riesgos operativos conocidos

- **Railway trial recurrente:** el microservicio corre con trial de 30 días / 5 USD. El 7 sep 2026 se migró a un proyecto nuevo en la cuenta de FITS (`fitsscreening@gmail.com`) — estado al 8 sep 2026: **29 días o USD 4.96 restantes** (vence ~7 oct 2026). **Revisar el estado de facturación de Railway (`fitsscreening@gmail.com`) proactivamente antes de esa fecha**, o migrar a un plan pago antes del cierre de garantía — de lo contrario se repite el mismo corte que ya ocurrió dos veces.
- **Solapamiento de memoria (OOM) entre Pollers:** `Convert Resume Poller` comparte instancia de n8n con `AI Screening Poller` (cron fijo cada 10 min, fuera de alcance de este proyecto). Ya causó 6 crashes OOM documentados; mitigado (no eliminado) sincronizando el cron. Pendiente de fondo: reducir `pages=15` en `Listar Jobs` y acotar la lectura de `Leer Log Real` (bloqueado por confirmar volumen real de jobs — ver `Volumen-JazzHR.md`, 113 jobs Open de 4873 totales).
- **Rate limit real de JazzHR:** ~1 request exitosa cada 10-11s en `/job/{jobId}/projob`, no documentado por JazzHR — el Poller trocea el escaneo en bloques de 20 con offset rotativo para respetarlo.
- **`AI Screening Poller` está fuera de alcance** de este proyecto (es de Fase 1) — no tocar su configuración salvo pedido explícito, aunque comparta instancia e historial de crashes.

## 7. Reproceso manual de un candidato

No hay un botón de "reprocesar" — mover al candidato de etapa y de vuelta a `Convert Resume - [Formato]` en JazzHR dispara el ciclo completo de nuevo en el siguiente tick del Poller (hasta ~10 min de espera según el cron). Antes de reprocesar un caso que fue a "Errores de Procesamiento", confirmar que la causa ya fue corregida (o que es un caso no determinístico que puede no repetirse) — reprocesar sin diagnóstico solo genera otra fila de error idéntica.

## 8. Dónde está todo

- Repo: este directorio (`fits-llc 2/cv-reformatting/`).
- Contrato firmado: `00-contrato/Contrato.md` (transcripción) + PDF original.
- Historial completo de decisiones técnicas: `Decisiones.md`.
- Bitácora sesión a sesión (más granular, con IDs de ejecución y diffs): `seguimiento/bitacora.md`.
- Conocimiento de dominio: `conocimiento/` (mapeo de IDs de JazzHR, reglas por formato, anatomía de templates, trampa de diagnóstico de Pollers).
- Microservicio: `02-modulo2-agente-transformacion/microservicio/` (código, tests, `.env.example`).

## 9. Pendientes abiertos no bloqueantes al cierre

- Reducir consumo de memoria propio del `Convert Resume Poller` (§6).
- Auditar si candidatos recurrentes de años anteriores recibieron un CV desactualizado antes del fix de selección de CV por `createdAt` (20 ago 2026).
