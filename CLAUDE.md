# Cliente: FITS LLC — CV Reformatting Automatizado
> Archivo de contexto para Claude Code. Cargado automáticamente en sesiones dentro de `fits-llc 2/cv-reformatting/`.
> Proyecto hermano: `../contract-renewal/` (mismo cliente, contrato firmado el mismo día, comparten equipo e infraestructura N8N).

## Perfil del Cliente

FITS LLC — outsourcing RRHH, industria farmacéutica, Puerto Rico. Contrato firmado 3 jul 2026 (USD 2,000). Cliente activo desde Fase 1 (ver `../../fits-llc/` — sistema de screening de CVs vía JazzHR, operativo en producción, incluye credencial Anthropic ya provisionada). Esta Fase 2 construye sobre la misma instancia de N8N (`fits.app.n8n.cloud`) y la misma cuenta de JazzHR ya integradas, sin costo de setup adicional.

## Estado del Proyecto

**Módulo 1 completo** (28 jul 2026): las etapas `Convert Resume - [Formato]` están activas y verificadas vía API en los 10 workflows de JazzHR.

**Módulo 2 — microservicio de render + agente de transformación AI funcionando end-to-end en local (Fases 0–5 de 7 del plan del agente, auditado por Opus), sin tocar N8N todavía.** Arquitectura: microservicio Python (FastAPI + `docxtpl` + Anthropic SDK) en `02-modulo2-agente-transformacion/microservicio/` (renombrado el 30 jul desde `microservicio-render/`) hace las dos cosas — genera el `.docx` final (N8N Cloud no puede, bloquea `zlib`/`require()` en el Code node) y ahora también transforma el CV original a JSON canónico vía Claude. Los 3 templates activos (New Format, Non Template, BD Format) están re-anotados según `templates/TAG-CONTRACT.md` y conectados al endpoint `POST /render`. **Maquetación de los 3 formatos confirmada visualmente por Santiago (29 jul 2026)** con párrafos reales por bullet/encabezado (loops nativos de `docxtpl`, no `RichText`).

**Agente de transformación (30 jul 2026):** `extract.py` (PDF/DOCX/texto vía `pypdf`, fail-closed `NO_TEXT_LAYER`/`CORRUPT_FILE`), `agent.py` (Claude `claude-sonnet-5` con `strict: true`, sin `temperature`; prompt versionado en `prompt/transform-v1.md`), `dates.py` (`years_experience` calculado en Python, nunca por el LLM) y `grounding.py` (check anti-invención determinístico: empresa/años/métricas/I-statements bloquean como error, título/institución/summary como warning) — contrato completo en `agente/CONTRATO-AGENTE.md`. Bug de `"4++ YRS. OF EXP."` (doble `+` en el header de años) encontrado y corregido el mismo día, independiente del agente.

**Fase 4 completa (30 jul 2026):** endpoint `POST /transform` en `main.py` — body JSON `{filename, content_base64}` (mismo `X-API-Key` que `/render`), corre `extract_text` → `agent.transform` (esta última vía `run_in_threadpool` para no bloquear `/render` en el mismo proceso) y devuelve `{state, cv, usage}` o `422` con `{state:"failed", code, detail}`. Límite de tamaño de body ahora consciente de la ruta (`MAX_BODY_BYTES` 2MB para `/render`, `MAX_TRANSFORM_BODY_BYTES` 8MB default para `/transform`). `ANTHROPIC_API_KEY` ahora obligatoria al arranque, igual que `API_KEY`. De paso se cerró un gap: los warnings de `extract.py` (ej. `SOURCE_TRUNCATED`) antes se perdían y ahora `agent.transform()` los fusiona en `cv._meta.warnings` vía el nuevo parámetro `extract_warnings`.

**Fase 5 completa (30 jul 2026):** harness de evaluación con 4 CVs sintéticos (`cvs-prueba/sinteticos/`, uno por cada regla de contenido del PRD, sin datos de candidatos reales) — `tests/test_synthetic_harness.py`, marcado `llm`. Confirma SLA (<60s por transformación, presupuesto interno dentro del límite de 3 min punta a punta del PRD) y las 4 reglas de contenido (traducción, tercera persona, Objective→Summary, reescritura de summary pobre): 4/4 en verde, tiempos entre 10s y 25s. **Hallazgo real:** si el CV original no trae sección explícita de Skills, el modelo a veces infiere una lista parafraseando la experiencia, y el chequeo de token exacto de `grounding.py` la bloquea como no verificable (`GROUNDING_FAILED`) — riesgo anotado para medir con el set real de FITS en Fase 7 (ver `Decisiones.md` y `agente/CONTRATO-AGENTE.md`). 51 tests (`pytest`, más 6 marcados `llm` opt-in) verificados contra el único CV real disponible (Shirley Mercado) de punta a punta: PDF → Claude → `.docx`, sin datos armados a mano.

**Deploy a Railway completo (4 ago 2026):** microservicio activo en `https://fits-llc-cv-reformatting-production.up.railway.app` (trial de 5 USD/30 días). Requirió mover `contrato-datos/`, `templates/anotados/` y `prompt/` dentro de `microservicio/` (Railway con Root Directory acotado no incluye carpetas hermanas en el build). `/health` y `/render` verificados con curl real.

**Fase 6 + Módulo 3 construidos, validados de punta a punta con candidatos reales, y ACTIVADOS en producción (14 ago 2026):** poller (`JazzHR - Convert Resume Poller`) y worker (`JazzHR - Convert Resume Processor`) en `fits.app.n8n.cloud`. El Processor cubre Módulo 2 + Módulo 3 completos: detección → descarga → `/transform` → `/render` → subcarpeta por candidato en SharePoint (`Resumes/{Nombre} ({candidateId})/{Formato}.docx`) → notificación al reclutador asignado (`job.hiringLeadAccountId` → email, cambio de alcance pedido por FITS respecto al "correo grupal" del contrato firmado — ver `Decisiones.md`) → log en Google Sheets (`1EM7GeQ7AePoMyngzDsRgMgnjj85K_pIoqfa1u4ukAo4`). **Modo piloto activo:** la notificación al reclutador queda retenida (`Config Piloto` → `EMAIL_ENABLED: false`) hasta que Santiago revise varios CVs reales generados; SharePoint y el Sheet ya funcionan sin ese gate. Validado end-to-end con 2 candidatos reales de Convert Resume (Baxter Rains, Steven Palmer-Velazquez) — en el proceso se encontraron y corrigieron dos bugs reales de Módulo 2: `.doc` legacy mal detectado como texto plano en `extract.py` (causaba invenciones en vez de fallar cerrado) y un falso positivo de `GROUNDING_I_STATEMENT` con numeración romana de cursos ("Chemistry Laboratory I & II"). Mapeo completo de los 3 espacios de IDs de JazzHR en `conocimiento/jazzhr-stepids-convert-resume.md`. **Choque de scheduling corregido antes de reactivar (14 ago 2026):** Convert Resume Poller coincidía exactamente en el minuto :30 con AI Screening Poller (confirmado con el historial real de ejecuciones de n8n, no solo la config) — cron cambiado de `15,30,45 * * * *` a `7,22,37,52 * * * *`, sin tocar AI Screening Poller (activo en producción, fuera de alcance por decisión explícita de Santiago). Detalle completo en `seguimiento/bitacora.md` (4, 6, 11 y 14 ago).

**Calibración fina de layout — los 3 formatos completos, verificados con candidato real y con conversión real vía Microsoft Graph (11-14 ago 2026).** tras ~10 rondas de ajuste iterativo contra el canon real de Yanina, **New Format Resume Template.docx queda calibrado y confirmado por Santiago** — fuente/tamaño por defecto, bullets nativos (guion, no símbolo especial — Wingdings/Symbol se confirmaron invisibles en la conversión de Graph), fecha de cargo en columna derecha real (tab, no paréntesis ni espacios), fecha de subcargo omitida cuando duplica la de la empresa, 2-3 niveles de spacing calibrados con medición de PDF a nivel de glifo. Re-verificado en local el 14 ago con un candidato real (Luis Antonio García Sánchez, etapa real "9. CONVERT RESUME-NEW FORMAT") — encontró y corrigió un bug real de falso positivo en `grounding.py` (ver abajo), no del template.

**BD Format — calibración fina completa (12 ago 2026), mismo método (medición glyph-box con `pymupdf` contra canon de Edgeliz/Edward):** color de texto corregido (gris → negro), spacing roto corregido (mismo modelo de 2 niveles de New Format, sin el 3er nivel intermedio — el canon de BD no lo tiene), summary/bullets justificados, `role.header` con negrita/indent/período entre paréntesis (patrón de Edgeliz, elegido por Santiago tras contradicción real con el canon de Edward), educación separada de certificaciones (antes mezcladas en una lista con viñeta), nombre/localidad en mayúsculas (`|upper`, mismo fix ya usado en New Format), bullets con tab real entre el guion y el texto (antes espacio literal, rompía la sangría en la primera línea de bullets de 2+ líneas). Verificado con una candidata real encontrada directamente en `api.jazz.co` sin pasar por N8N (Ruth Sotomayor Clavell, etapa real "8. CONVERT RESUME-BD FORMAT") — encontró y corrigió de paso un bug real de `town` ausente (ningún canon lo cubre).

**Non Template — calibración fina completa (14 ago 2026), mismo método contra canon de Andrea I. Arzola Torres y Aneira Palmer Berrios:** el hallazgo principal fue que el template no tenía ningún `spacing before` explícito en ningún párrafo (título pegado al contenido, empresas pegadas entre sí) — corregido con el mismo modelo de 2 niveles de New Format/BD. También: bullets sin sangría colgante real ni justificar (mismo fix ya aplicado en BD), `role.header` sin tab stop, y el header con años de experiencia quitado (decisión de Santiago — ningún canon de Non Template lo muestra, a diferencia de New Format). Verificado con una candidata real (Yajaira Ortiz Ruiz, etapa real "8. CONVERT RESUME-NON TEMPLATE", 20 años de experiencia en 5 empresas) — encontró y corrigió un bug real de espaciado doble cuando una sección con lista (`skills`/`certifications`) queda vacía (Word suma `spacing after`+`before` entre 2 títulos consecutivos en vez de colapsarlo). El mismo bug se portó y corrigió también en New Format el mismo día.

**Verificación vía Microsoft Graph completada para los 3 formatos (14 ago 2026):** BD Format y Non Template convertidos a PDF real (`GET .../content?format=pdf`, mismo método ya usado para New Format) subiendo temporalmente los renders de prueba a SharePoint (borrados al cerrar, no era entrega real). Confirmado en el PDF real de producción: fuente Arial sin fallback en ambos, spacing de certificaciones de BD correcto (~240 twips por bloque), y el fix de spacing doble de Non Template funcionando (gap único, no doble, cuando `certifications: []`).

**Dos bugs reales de falso positivo en `grounding.py` encontrados y corregidos con candidatos reales ya en producción (14 ago 2026):** (1) `GROUNDING_TOKEN_NOT_FOUND` bloqueaba skills de una sola palabra (`JMP`, `SolidWorks`, `Matlab`, `Excel`) que sí estaban en la fuente — el chequeo tokenizaba el texto solo por espacios en blanco, así que una skill pegada a una coma sin espacio (o dos skills pegadas entre sí) nunca matcheaba el valor limpio del agente; corregido tokenizando con split por regex. (2) `GROUNDING_METRIC_NOT_FOUND` bloqueaba un número real (`'14001'` de "ISO 14001") partido en dos por un espacio fantasma de kerning tipográfico en la extracción de `pypdf` ("ISO 14 001") — corregido reusando `despace()` (mismo mecanismo ya usado para `full_name`) en el chequeo de métricas. Ambos afectan a los 3 formatos por igual (son del agente, no de una plantilla). Deploy automático a Railway confirmado (push a GitHub dispara el deploy solo, ~1 min).

**Notificaciones al reclutador activadas con gate de horario laboral (14 ago 2026):** `EMAIL_ENABLED: true` en producción. Nueva regla de negocio: los correos solo se envían Lun-Vie 8am-5pm hora PR — si un candidato se procesa fuera de ese horario, el correo se encola (pestaña nueva "Notificaciones Pendientes" en el mismo Sheet de log) y un workflow nuevo (`JazzHR - Convert Resume Notification Queue Flusher`, cron cada 15 min en horario laboral) lo despacha en el próximo ciclo laboral — nunca se omite, solo se pospone. Verificado de punta a punta con un correo de prueba real antes de dejarlo activo. Detalle completo (incluido un bug real de configuración de Google Sheets encontrado en el camino) en `seguimiento/bitacora.md`.

**Falta:** revisar algunos correos reales que empiecen a salir con `EMAIL_ENABLED` activo; set de 15–20 CVs reales de FITS para medir falsos positivos del grounding y ajuste fino (Fase 7); confirmación visual de FITS/Paola sobre los 3 formatos (paso de negocio, no bloquea el uso del microservicio). **Worksense Format descartado por FITS** (Paola, 21 jul 2026) y su archivo eliminado del repo. Detalle completo en `Decisiones.md`, `agente/CONTRATO-AGENTE.md`, `conocimiento/` y `seguimiento/bitacora.md`.

**Bloqueantes de negocio pendientes (FITS):** set de 15–20 CVs reales para pruebas de aceptación (Fase 7). El "correo grupal" y "revisión humana antes del envío" ya no son bloqueantes — resueltos el 11 ago (correo grupal reemplazado por notificación al reclutador asignado, decisión de FITS; revisión humana resuelta con el gate manual `EMAIL_ENABLED` del modo piloto, hoy ya desactivado, ver `Decisiones.md`).

Yaritza es el punto de contacto principal de FITS para este proyecto y para `../contract-renewal/`.

## Módulos

1. Etapas "Convert Resume" en 10 workflows de JazzHR — **completo**
2. Agente de Transformación AI (Anthropic/Claude + microservicio de render — 4 reglas de contenido + generación de .docx con branding, 3 formatos activos) — **desplegado en Railway, wiring en N8N (poller+worker) construido, validado con candidatos reales y ACTIVO en producción**
3. Entrega al Equipo (.docx en SharePoint por candidato + notificación al reclutador asignado + log en Sheets) — **construido e integrado al Processor, validado con candidatos reales, modo piloto (email retenido) hasta revisar más CVs**

Detalle completo de alcance, criterios de aceptación y exclusiones en `PRD.md` y `00-contrato/Contrato.md`.

## Stack

- **ATS:** JazzHR — misma cuenta integrada en Fase 1
- **Orquestador:** N8N — instancia compartida con Fase 1 y con el proyecto hermano `contract-renewal`: `fits.app.n8n.cloud`
- **Agente AI:** Anthropic/Claude (`claude-sonnet-5`, `strict: true`) — mismo valor de la credencial "Anthropic - FITS" de Fase 1 (`P3oMjAzU63IfOAff`, ver `../../fits-llc/CLAUDE.md`), pero corre dentro del microservicio Python (`ANTHROPIC_API_KEY` en su `.env`/Railway), no como credencial de N8N — la decisión de arquitectura (por qué no un nodo nativo de N8N) está en `Decisiones.md`, 30 jul 2026
- **Render de .docx + Agente de Transformación AI:** microservicio Python (FastAPI + `docxtpl` + Anthropic SDK) — funcionando en local (`02-modulo2-agente-transformacion/microservicio/`), deploy a Railway pendiente
- **Almacenamiento/entrega:** SharePoint Document Library propio (Microsoft Graph API, Azure AD app-only auth)

## Contactos FITS

| Nombre | Rol |
|---|---|
| Yaritza Cordero Nieves | Representante legal / firma |
| Jeremy Rivera | Coordinador |
| Paola Guirado | Operación / validación de calidad — ya trabajó con el equipo de Insighty en el UAT de Fase 1 |
| Agustín | — |
| Centeno | IT — Azure AD, SharePoint |

## Comandos disponibles

| Comando | Uso |
|---|---|
| `/plan` | Plan de implementación por fases (invoca `planner`) |
| `/n8n-review` | Revisión de workflows N8N (error handling, idempotencia, credenciales) |
| `/prompt-review` | Optimización del prompt del agente de transformación AI |
| `/code-review` | Revisión de código/lógica de N8N Code nodes |
| `/verify` | Pipeline de verificación completo |

## Ver también

[[Brief|Brief]] · [[PRD|PRD]] · [[Decisiones|Decisiones]] · [[00-contrato/Contrato|Contrato firmado]] · [[../contract-renewal/CLAUDE|Proyecto hermano: Contract Renewal]] · [[../../fits-llc/CLAUDE|Fase 1: Screening de CVs]]
