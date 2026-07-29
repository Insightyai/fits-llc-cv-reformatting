# Cliente: FITS LLC — CV Reformatting Automatizado
> Archivo de contexto para Claude Code. Cargado automáticamente en sesiones dentro de `fits-llc 2/cv-reformatting/`.
> Proyecto hermano: `../contract-renewal/` (mismo cliente, contrato firmado el mismo día, comparten equipo e infraestructura N8N).

## Perfil del Cliente

FITS LLC — outsourcing RRHH, industria farmacéutica, Puerto Rico. Contrato firmado 3 jul 2026 (USD 2,000). Cliente activo desde Fase 1 (ver `../../fits-llc/` — sistema de screening de CVs vía JazzHR, operativo en producción, incluye credencial Anthropic ya provisionada). Esta Fase 2 construye sobre la misma instancia de N8N (`fits.app.n8n.cloud`) y la misma cuenta de JazzHR ya integradas, sin costo de setup adicional.

## Estado del Proyecto

**Módulo 1 completo** (28 jul 2026): las etapas `Convert Resume - [Formato]` están activas y verificadas vía API en los 10 workflows de JazzHR.

**Módulo 2 — microservicio de render funcionando end-to-end en local (Fases 0–3 del plan revisado por Opus), sin tocar N8N todavía.** Arquitectura: microservicio Python (FastAPI + `docxtpl`) en `02-modulo2-agente-transformacion/microservicio-render/` genera el `.docx` final (N8N Cloud no puede hacerlo — bloquea `zlib`/`require()` en el Code node). Los 3 templates activos (New Format, Non Template, BD Format) están re-anotados según `templates/TAG-CONTRACT.md` y conectados al endpoint `POST /render` — probado con servidor real (auth `X-API-Key`, límites de tamaño, validación contra `cv-schema.json`, verificación de integridad del `.docx` de salida) contra 2 fixtures (`contrato-datos/fixtures/`). **Falta:** el agente de transformación AI (Claude) que lee el CV original y arma el JSON canónico — hoy se testea con JSONs armados a mano — y deploy a Railway. **Worksense Format descartado por FITS** (Paola, 21 jul 2026) y su archivo eliminado del repo. Detalle completo en `Decisiones.md`, `conocimiento/` y `seguimiento/bitacora.md`.

**Bloqueantes de negocio pendientes (FITS):** set de 15–20 CVs reales para pruebas de aceptación, CVs de ejemplo ya convertidos por formato, correo grupal del equipo para Módulo 3, decisión sobre revisión humana antes del envío grupal.

Yaritza es el punto de contacto principal de FITS para este proyecto y para `../contract-renewal/`.

## Módulos

1. Etapas "Convert Resume" en 10 workflows de JazzHR — **completo**
2. Agente de Transformación AI (Anthropic/Claude + microservicio de render — 4 reglas de contenido + generación de .docx con branding, 3 formatos activos)
3. Entrega al Equipo (.docx + email grupal, almacenamiento en SharePoint)

Detalle completo de alcance, criterios de aceptación y exclusiones en `PRD.md` y `00-contrato/Contrato.md`.

## Stack

- **ATS:** JazzHR — misma cuenta integrada en Fase 1
- **Orquestador:** N8N — instancia compartida con Fase 1 y con el proyecto hermano `contract-renewal`: `fits.app.n8n.cloud`
- **Agente AI:** Anthropic/Claude — reutiliza la credencial "Anthropic - FITS" de Fase 1 (`P3oMjAzU63IfOAff`, ver `../../fits-llc/CLAUDE.md`)
- **Render de .docx:** microservicio Python (FastAPI + `docxtpl`) — funcionando en local (`02-modulo2-agente-transformacion/microservicio-render/`), deploy a Railway pendiente
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
