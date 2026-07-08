# Cliente: FITS LLC — CV Reformatting Automatizado
> Archivo de contexto para Claude Code. Cargado automáticamente en sesiones dentro de `fits-llc 2/cv-reformatting/`.
> Proyecto hermano: `../contract-renewal/` (mismo cliente, contrato firmado el mismo día, comparten equipo e infraestructura N8N).

## Perfil del Cliente

FITS LLC — outsourcing RRHH, industria farmacéutica, Puerto Rico. Contrato firmado 3 jul 2026 (USD 2,000). Cliente activo desde Fase 1 (ver `../../fits-llc/` — sistema de screening de CVs vía JazzHR, operativo en producción, incluye credencial Anthropic ya provisionada). Esta Fase 2 construye sobre la misma instancia de N8N (`fits.app.n8n.cloud`) y la misma cuenta de JazzHR ya integradas, sin costo de setup adicional.

## Estado del Proyecto

**No iniciado.** Contrato firmado, kickoff realizado el 7 jul 2026.

**Resuelto en el kickoff:** los 4 templates de branding ya están confirmados como definitivos (son los que Paola compartió). Paola además va a enviar un CV de ejemplo ya convertido por cada formato, como referencia inicial.

**Bloqueante activo:** sitio de SharePoint con Document Library propio de este proyecto — ya solicitado a Centeno, sin confirmación de que exista ni de su Azure AD App Registration. Este proyecto va más atrasado que su hermano `contract-renewal` en ese frente (que ya tiene sitio "Operaciones" creado, con el PU Balance cargado).

**Corrección de alcance importante (kickoff):** el Módulo 1 no es un job posting nuevo aislado — es agregar un stage "Resumes" a los 10-12 workflows de JazzHR que FITS ya tiene (los mismos de Fase 1), confirmado por Paola. Ver `PRD.md` y `01-modulo1-job-posting/README.md`.

**Ambigüedad sin resolver:** Google Drive vs. SharePoint como destino final de entrega de los CVs — quedó mencionado de las dos formas en el kickoff. Ver `Decisiones.md`.

Yaritza es el punto de contacto principal de FITS para este proyecto y para `../contract-renewal/`.

## Módulos

1. Job Posting Centralizado "Resumes" en JazzHR (4 stages: New Format, Non Template, BD Format, Worksense Format)
2. Agente de Transformación AI (Anthropic/Claude vía N8N — 4 reglas de contenido + generación de .docx con branding)
3. Entrega al Equipo (.docx + email grupal, almacenamiento en la nube)

Detalle completo de alcance, criterios de aceptación y exclusiones en `PRD.md` y `00-contrato/Contrato.md`.

## Stack

- **ATS:** JazzHR — misma cuenta integrada en Fase 1
- **Orquestador:** N8N — instancia compartida con Fase 1 y con el proyecto hermano `contract-renewal`: `fits.app.n8n.cloud`
- **Agente AI:** Anthropic/Claude — evaluar reutilizar la credencial "Anthropic - FITS" ya provisionada en Fase 1 (ver `../../fits-llc/CLAUDE.md`)
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
