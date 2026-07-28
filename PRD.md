# PRD — FITS LLC · CV Reformatting Automatizado

> Generado a partir de Brief.md y del Anexo 1 del contrato firmado. Documento técnico de referencia para ejecución.
> **Última actualización:** Julio 2026

---

## 1. Objetivo

Automatizar la transformación del CV original de un candidato al formato de presentación que FITS usa con cada cliente farmacéutico. El agente toma el CV tal como llega, aplica las reglas de contenido de FITS y genera el documento final — sin que ningún miembro del equipo tenga que abrirlo, copiarlo ni reformatearlo.

---

## 2. Usuarios

| Usuario | Rol | Necesidad |
|---|---|---|
| Reclutadores FITS | Operadores | Mover el candidato al stage del formato correcto y recibir el .docx listo |
| Paola Guirado | Validadora de calidad / operación | Confirmar que la reescritura del Summary cumple el estándar acordado |
| Jeremy Rivera | Coordinador | Acceso a los CVs transformados en la carpeta de entrega |
| Centeno | IT | Habilitar el sitio de SharePoint y el acceso vía Azure AD |
| Yaritza Cordero | Decisora / representante legal | Visibilidad y aprobación de entregables |

---

## 3. Módulos

### Módulo 1 — Etapas "Convert Resume" en los Workflows de JazzHR

**Corrección de alcance (kickoff 7 jul 2026):** no es un job posting nuevo aislado. Es agregar etapa(s) nuevas dentro de cada uno de los **workflows de JazzHR que FITS ya tiene** (los mismos de Fase 1) — confirmado explícitamente por Paola. Mapeo exacto confirmado por correo el mismo día (ver `Decisiones.md`). Ver también `01-modulo1-job-posting/README.md`.

**Alcance:**
- Agregar la(s) etapa(s) `Convert Resume - [Formato]` a 10 workflows/pipelines existentes de JazzHR, solo con los formatos que cada uno necesita (no los 4 en todos):

| Workflow | Etapa(s) agregada(s) |
|---|---|
| Abbott FG - Workflow 2024 | Convert Resume - Non Template |
| Amgen FG - Workflow 2024 | Convert Resume - Non Template |
| Becton Dickinson - Workflow 2024 | Convert Resume - BD Format |
| Beeline - Workflow 2024 | Convert Resume - Non Template |
| Haleon FG - Workflow 2026 | Non Template · New Format |
| JazzHR Standard Workflow | Non Template · New Format |
| JNJ - Workflow 2024 | Convert Resume - Non Template · Convert Resume - New Format |
| Integra FG - Workflow 2024 | Convert Resume - Non Template |
| Medtronic - Workflow 2024 | Convert Resume - Non Template |
| SOW Workflow 2024 | Convert Resume - New Format |

- Acceso habilitado para todos los reclutadores
- El reclutador mueve manualmente el CV a la etapa del formato deseado — el sistema hace el resto

**Worksense Format descartado (confirmado por Paola, 21 jul 2026):** FITS decidió no integrar el formato Worksense en JazzHR — no es de uso regular en sus operaciones. JNJ - Workflow 2024 mantiene únicamente sus dos etapas (Non Template y New Format), ambas con los templates genéricos estándar, sin lógica especial de selección por workflow. Ver `Decisiones.md`.

**Criterio de aceptación:** las etapas están activas y correctamente configuradas en los 10 workflows de JazzHR, y todos los reclutadores tienen acceso confirmado por el representante designado de FITS.

**No incluido:** modificación de otras etapas en los workflows existentes — solo se agregan las etapas `Convert Resume - [Formato]`, sin tocar la lógica de AI Screening de Fase 1 que ya está en producción sobre esos mismos workflows.

---

### Módulo 2 — Agente de Transformación AI

**Alcance:**
- Detección automática cuando un candidato llega a cualquier stage del job posting "Resumes"
- Extracción del CV (PDF o DOCX) desde JazzHR
- Transformación del contenido vía agente AI (Anthropic/Claude):
  - Traducción al inglés si el CV está en otro idioma
  - Conversión a tercera persona (eliminación de I-statements)
  - Sustitución de Objectives por Summary profesional
  - Reescritura de summaries pobres o incompletos
- Generación programática del .docx final con los 4 templates (logo, estilos de fuente, orden de secciones por formato — incluyendo pueblo de residencia en Summary of Skills para BD Format)
- Aplicación del template correspondiente al stage seleccionado

**Criterio de aceptación:** el agente procesa un CV de prueba en menos de 3 minutos desde el trigger hasta el .docx final; las reglas de formato se aplican en el 100% del set de prueba acordado (15–20 CVs reales); la calidad de reescritura del Summary es aprobada por FITS en ≥90% del set de prueba; el template correcto se aplica para cada uno de los 4 formatos.

**No incluido:** templates adicionales a los 4 definidos · evaluación de idoneidad del candidato (eso lo hace el agente de screening de Fase 1) · ajustes de prompt para nuevos tipos/formatos de CV no cubiertos en el set de prueba (se cotizan aparte).

**Riesgo abierto:** el criterio del 95% original del borrador se reformuló para separar reglas binarias (100% medibles) de calidad editorial (aprobación humana ≥90%) — evita exponer a Insighty a rechazos por preferencia subjetiva durante la garantía.

---

### Módulo 3 — Entrega al Equipo

**Alcance:**
- Generación del CV transformado en .docx editable, para que el reclutador pueda hacer ajustes finales antes de enviarlo al cliente
- Almacenamiento automático en el sitio de SharePoint del proyecto (ver `Decisiones.md` — el contrato dice Google Drive por defecto con OneDrive como upgrade; en la práctica se usa SharePoint desde el arranque)
- Email automático al correo grupal del equipo con el CV adjunto y enlace directo al archivo

**Criterio de aceptación:** el .docx se almacena en la carpeta designada dentro de 5 minutos del trigger; el correo grupal recibe el email con el CV adjunto y un enlace funcional; el log de procesamiento en Google Sheets registra la entrada correctamente (candidato, formato, fecha, resultado).

**No incluido:** entrega final del CV al cliente de FITS (eso sigue siendo tarea del reclutador; este sistema entrega únicamente al equipo interno).

---

## 4. Fuera de Alcance (explícito en el contrato)

- CVs escaneados o en formato de imagen (sin texto seleccionable)
- Templates adicionales a los 4 definidos
- Evaluación de idoneidad del candidato (cubierta por Fase 1)
- Entrega final al cliente de FITS
- Ajustes de prompt de AI para nuevos tipos/formatos de CV no representados en el set de prueba
- Migración de datos históricos, auditorías de seguridad, licencias de terceros

## Lagunas a confirmar con FITS antes del kick-off (no requieren cambio de contrato)

- Si llegan CVs escaneados/imagen y con qué frecuencia
- Si el equipo quiere un paso de revisión humana antes del envío grupal, o si la entrega automática es aceptable
- Si las 4 reglas de contenido listadas son todas las reglas por formato, o hay reglas adicionales específicas de cada template

---

## 5. Dependencias del Cliente

| Dependencia | Estado | Responsable |
|---|---|---|
| Sitio/Document Library de SharePoint propio del proyecto | ✅ Confirmado — `Operaciones-RecursosHumanos`, carpeta `Resumes` (ver `Decisiones.md`) | Centeno |
| Azure AD App Registration para este sitio | ✅ Completo (`.env` local) — falta confirmar permisos otorgados | Centeno |
| Los 4 templates definitivos en .docx con branding completo | ✅ Completado — recibidos y cargados en `02-modulo2-agente-transformacion/templates/` | Jeremy / Paola |
| Un CV de ejemplo por formato (referencia inicial) | ⏳ Pendiente — Paola se comprometió a enviarlos | Paola |
| Set de 15–20 CVs reales para pruebas de aceptación | ⏳ Pendiente | Paola / Jeremy |
| Acceso a JazzHR para agregar el stage "Resumes" a los workflows existentes | ✅ Completo — etapas ya creadas en los 10 workflows, verificado vía API el 28 jul 2026 | Jeremy |
| Confirmación Google Drive vs. SharePoint como destino final de entrega | ✅ Resuelto — SharePoint, sitio `Operaciones-RecursosHumanos` | Insighty (interno) |

---

## 6. Timeline

| Fase | Duración estimada |
|---|---|
| Semana 1 | Configuración job posting · Construcción de los 4 templates con branding real · Setup del workflow en N8N |
| Semana 2 | Desarrollo del agente AI de transformación · Setup de entrega · Pruebas con CVs reales |
| Semana 3 | Ajustes según feedback · Pruebas finales de ciclo completo · Entrega y documentación |
| **Total** | **3–4 semanas desde recepción de los 4 templates definitivos (máx. 7 semanas)** |

El reloj no ha arrancado formalmente — corre desde que Insighty reciba los 4 templates con branding completo, no desde la firma del 3 de julio.

---

## 7. Decisiones Pendientes

- [x] Sitio de SharePoint propio vs. compartido con Contract Renewal — resuelto: sitio propio `Operaciones-RecursosHumanos`
- [x] Registrar Tenant ID / Client ID / Client Secret del Azure AD App Registration — recibidos, en `.env` local
- [ ] Confirmar permisos otorgados sobre el sitio (`Sites.Selected` vs. `Sites.ReadWrite.All`)
- [ ] Reutilizar credencial Anthropic de Fase 1 o provisionar una nueva
- [ ] Set de CVs reales para pruebas de aceptación
- [ ] Paso de revisión humana antes del envío grupal — sí/no
