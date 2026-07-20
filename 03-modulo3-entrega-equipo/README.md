# Módulo 3 — Entrega al Equipo

**Estado:** No iniciado — bloqueado por el sitio de SharePoint

## Alcance

- Generación del CV transformado en .docx editable, para que el reclutador pueda hacer ajustes finales antes de enviarlo al cliente
- Almacenamiento automático en el sitio de SharePoint del proyecto
- Email automático al correo grupal del equipo con el CV adjunto y enlace directo al archivo

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

Falta cargar la credencial nativa Microsoft OAuth2/SharePoint en N8N (`fits.app.n8n.cloud`) y construir el workflow de entrega.
