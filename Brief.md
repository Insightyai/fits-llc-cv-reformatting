# Brief — FITS LLC · CV Reformatting Automatizado

> Contexto inicial del proyecto. Fase 2 de FITS (ver también `../contract-renewal/`, proyecto hermano firmado el mismo día). Fuente de verdad antes de convertirse en PRD.

## Datos del Cliente

| Campo | Detalle |
|---|---|
| **Empresa** | FITS LLC |
| **Sector** | HR Outsourcing — Industria Farmacéutica |
| **País** | Puerto Rico |
| **Contactos** | Yaritza Cordero Nieves (representante legal) · Jeremy Rivera · Paola Guirado (operación/entrega) · Agustín · Centeno (IT) |
| **Contrato firmado** | 3 de julio de 2026 |
| **Valor** | USD 2,000 |

## Problema Central

Hoy, cuando un candidato pasa el screening inicial (Fase 1), un miembro del equipo de FITS tiene que abrir el CV original, traducirlo si está en otro idioma, convertirlo a tercera persona, reescribir el resumen, y darle el formato de branding correspondiente al cliente final (4 formatos distintos según el cliente farmacéutico). Es trabajo manual y repetitivo por cada candidato.

## Qué Nos Contrató a Hacer

1. **Módulo 1 — Job Posting Centralizado "Resumes" en JazzHR** (4 stages, uno por formato)
2. **Módulo 2 — Agente de Transformación AI** (Anthropic/Claude vía N8N — 4 reglas de contenido + generación de .docx con branding)
3. **Módulo 3 — Entrega al Equipo** (.docx + email grupal, almacenamiento en la nube)

## Stack Involucrado

- **ATS:** JazzHR (job posting centralizado "Resumes", reutiliza la cuenta ya integrada en Fase 1)
- **Orquestador:** N8N (misma instancia `fits.app.n8n.cloud` provisionada en Fase 1 — sin costo de setup)
- **Agente AI:** Anthropic/Claude (posible reutilización de la credencial "Anthropic - FITS" ya provisionada en Fase 1, a confirmar con el equipo)
- **Almacenamiento/entrega:** sitio de SharePoint con Document Library propio de este proyecto (ver Notas de Contexto)
- **Generación de documentos:** .docx programático con los 4 templates de branding

## Notas de Contexto

- **Cambio de arquitectura de almacenamiento (post-firma):** el contrato firmado especifica Google Drive como destino por defecto, con OneDrive como upgrade posterior. En la práctica, Insighty recomendó a Centeno usar un **sitio de SharePoint con Document Library propio** para este proyecto (separado del de Contract Renewal). Ver `Decisiones.md`.
- **Templates — resuelto en el kickoff del 7 jul 2026:** los 4 templates que Paola ya había compartido son los **definitivos**, confirmado explícitamente por Jeremy. Ya no está pendiente.
- **Corrección de alcance del Módulo 1 (kickoff 7 jul 2026):** no es un job posting nuevo aislado. Es agregar un stage "Resumes" a los 10-12 workflows de JazzHR que FITS ya tiene (los mismos de Fase 1) — confirmado por Paola. Implica más superficie de cambio que la lectura inicial del contrato.
- **Estado del sitio de SharePoint propio (al kickoff):** ya se le comunicó a FITS/Centeno que cree su propio sitio/Document Library. Todavía sin confirmación de que exista, ni del estado del Azure AD App Registration para este sitio.
- **Ambigüedad sin resolver:** en el kickoff se mencionó tanto Google Drive como SharePoint como destino de entrega de los CVs transformados. Confirmar con el equipo cuál es el definitivo.
- El reloj del proyecto (3–4 semanas, máx. 7) corre desde que Insighty reciba los 4 templates definitivos — ya cumplido, pero el sitio de almacenamiento sigue sin confirmarse.
- CVs escaneados/imagen sin texto seleccionable están fuera de alcance.
- Ajustes de prompt por nuevos tipos de CV no cubiertos en el set de prueba de aceptación se cotizan aparte (no son bugs).
- **Punto de contacto principal de FITS para ambos proyectos de Fase 2:** Yaritza Cordero.

## Próximo Paso

- [ ] Confirmar con Centeno el estado del sitio/Document Library propio de este proyecto
- [ ] Confirmar si reutiliza el App Registration de Contract Renewal (con grant adicional) o necesita uno nuevo
- [x] Recibir los 4 templates definitivos en .docx con branding completo — completado, son los de Paola
- [ ] Recibir de Paola un CV de ejemplo ya convertido a cada uno de los 4 formatos
- [ ] Acordar con FITS el set de 15–20 CVs reales para las pruebas de aceptación
- [ ] Confirmar si se reutiliza la credencial Anthropic de Fase 1 o se provisiona una nueva
- [ ] Resolver la ambigüedad Google Drive vs. SharePoint como destino final
- [ ] Convertir este Brief en `PRD.md` una vez confirmados los accesos (ya iniciado)

---

## Ver también

[[CLAUDE|CLAUDE]] · [[PRD|PRD]] · [[Decisiones|Decisiones]] · [[00-contrato/Contrato|Contrato firmado]] · [[../../Depto AI/Knowledge/Lecciones/fits-llc|Lecciones Fase 1]]
