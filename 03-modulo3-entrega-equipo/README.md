# Módulo 3 — Entrega al Equipo

**Estado:** Construido e integrado al Processor de Fase 6 (11 ago 2026), en modo piloto — la notificación al reclutador queda retenida hasta que Santiago revise 3–5 CVs reales generados. Detalle completo en `../Decisiones.md` (11 ago 2026) y `../seguimiento/bitacora.md`.

## Alcance

- Generación del CV transformado en .docx editable, para que el reclutador pueda hacer ajustes finales antes de enviarlo al cliente
- Almacenamiento automático en el sitio de SharePoint del proyecto
- **Cambio de alcance (11 ago 2026, pedido por FITS):** en vez de un correo grupal, notificación automática al reclutador asignado del candidato en JazzHR (vía `job.hiringLeadAccountId` → email), con fallback a `reclutamiento@fitspr.com` si no se puede resolver. El email incluye el link a SharePoint, no el .docx adjunto (ver justificación en `../Decisiones.md`). El contrato firmado todavía dice "correo grupal" — queda anotado como desviación de alcance, no gestionada como adenda formal.
- **Estructura de carpetas en SharePoint:** una subcarpeta por candidato dentro de `Resumes/`, nombrada `{NombreCandidato} ({candidateId})` — el `candidateId` evita colisiones entre candidatos con el mismo nombre. Dentro de cada carpeta, un archivo por formato (`New Format.docx`, etc.). La carpeta se crea automáticamente si no existe antes de subir el archivo.

## Nota sobre el destino de almacenamiento

El contrato firmado especifica Google Drive como destino por defecto, con OneDrive como upgrade posterior sin costo cuando Azure AD esté habilitado. En la práctica se decidió usar un sitio de SharePoint desde el arranque — ver `../Decisiones.md`. Esto reintroduce como bloqueante la dependencia del Azure AD App Registration que el contrato había evitado a propósito.

## Criterio de Aceptación

- El .docx se almacena en la carpeta designada dentro de 5 minutos del trigger
- El correo grupal recibe el email con el CV adjunto y un enlace funcional
- El log de procesamiento en Google Sheets registra la entrada correctamente (candidato, formato, fecha, resultado)

## No incluido

Entrega final del CV al cliente de FITS — sigue siendo tarea del reclutador; este sistema entrega únicamente al equipo interno.

## Pendientes para arrancar

~~Confirmación de que el sitio/Document Library de SharePoint de este proyecto existe, y acceso vía Azure AD App Registration~~ — resuelto y verificado 20 Jul 2026 (lectura/escritura OK vía Microsoft Graph API, ver `../Decisiones.md`).

~~Falta cargar la credencial nativa Microsoft OAuth2/SharePoint en N8N~~ — resuelto 20 Jul 2026: credencial `SharePoint - CV Reformatting (Graph API)` creada y probada en `fits.app.n8n.cloud`, responde correctamente vía HTTP Request node.

Falta construir el workflow completo de entrega.

Diseño de columnas del log de Google Sheets: ver `log-sheets-diseno.md`. Falta crear el spreadsheet real (pendiente de tu confirmación, ver ese archivo).
