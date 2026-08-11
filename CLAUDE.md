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

**Fase 6 + Módulo 3 construidos y validados de punta a punta con candidatos reales (11 ago 2026), DESACTIVADOS a la espera de decisión de Santiago sobre reactivar:** poller (`JazzHR - Convert Resume Poller`) y worker (`JazzHR - Convert Resume Processor`) en `fits.app.n8n.cloud`. El Processor ahora cubre Módulo 2 + Módulo 3 completos: detección → descarga → `/transform` → `/render` → subcarpeta por candidato en SharePoint (`Resumes/{Nombre} ({candidateId})/{Formato}.docx`) → notificación al reclutador asignado (`job.hiringLeadAccountId` → email, cambio de alcance pedido por FITS respecto al "correo grupal" del contrato firmado — ver `Decisiones.md`) → log en Google Sheets (`1EM7GeQ7AePoMyngzDsRgMgnjj85K_pIoqfa1u4ukAo4`). **Modo piloto activo:** la notificación al reclutador queda retenida (`Config Piloto` → `EMAIL_ENABLED: false`) hasta que Santiago revise varios CVs reales generados; SharePoint y el Sheet ya funcionan sin ese gate. Validado end-to-end con 2 candidatos reales de Convert Resume (Baxter Rains, Steven Palmer-Velazquez) — en el proceso se encontraron y corrigieron dos bugs reales de Módulo 2: `.doc` legacy mal detectado como texto plano en `extract.py` (causaba invenciones en vez de fallar cerrado) y un falso positivo de `GROUNDING_I_STATEMENT` con numeración romana de cursos ("Chemistry Laboratory I & II"). Mapeo completo de los 3 espacios de IDs de JazzHR en `conocimiento/jazzhr-stepids-convert-resume.md`. Detalle completo en `seguimiento/bitacora.md` (4, 6 y 11 ago).

**Falta:** decisión de Santiago sobre reactivar Poller+Processor ahora (con modo piloto) vs. seguir con pruebas manuales candidato por candidato; habilitar `EMAIL_ENABLED` tras revisar 3-5 CVs reales; set de 15–20 CVs reales de FITS para medir falsos positivos del grounding y ajuste fino (Fase 7); confirmación visual de FITS/Paola sobre los 3 formatos (paso de negocio, no bloquea el uso del microservicio). **Worksense Format descartado por FITS** (Paola, 21 jul 2026) y su archivo eliminado del repo. Detalle completo en `Decisiones.md`, `agente/CONTRATO-AGENTE.md`, `conocimiento/` y `seguimiento/bitacora.md`.

**Bloqueantes de negocio pendientes (FITS):** set de 15–20 CVs reales para pruebas de aceptación, CVs de ejemplo ya convertidos por formato, correo grupal del equipo para Módulo 3, decisión sobre revisión humana antes del envío grupal.

Yaritza es el punto de contacto principal de FITS para este proyecto y para `../contract-renewal/`.

## Módulos

1. Etapas "Convert Resume" en 10 workflows de JazzHR — **completo**
2. Agente de Transformación AI (Anthropic/Claude + microservicio de render — 4 reglas de contenido + generación de .docx con branding, 3 formatos activos) — **desplegado en Railway, wiring en N8N (poller+worker) construido y validado con candidatos reales, desactivado a la espera de decisión de Santiago sobre reactivar**
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
