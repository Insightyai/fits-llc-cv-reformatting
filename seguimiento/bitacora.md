# Bitácora — CV Reformatting Automatizado

> Registro cronológico de avances, bloqueos y comunicaciones con FITS durante la ejecución.

### 3 Jul 2026
Contrato firmado. Reloj contractual sin arrancar — pendientes: templates de branding y sitio de SharePoint propio.

### 20 Jul 2026
Recibidos los 4 templates .docx definitivos (New Format, Non Template, BD Format, Worksense Format) — cargados en `02-modulo2-agente-transformacion/templates/`. También se recibió un CV de prueba (Shirley Mercado) — cargado en `02-modulo2-agente-transformacion/cvs-prueba/`. Confirmado el sitio de SharePoint propio (`Operaciones-RecursosHumanos`, carpeta `Resumes`) y recibidos Client ID / Tenant ID del Azure AD App Registration ("CV Reformatting"), guardados en `.env` local. Client Secret agregado por Santiago directo en `.env` local. Queda pendiente confirmar los permisos otorgados sobre el sitio (`Sites.Selected` vs. `Sites.ReadWrite.All`).

Revisados dos correos de Paola: uno del 18 jun 2026 (Alternativas A y B originales) y otro del 7 jul 2026 (mismo día del kickoff) con el mapeo definitivo de workflow → etapa(s) `Convert Resume - [Formato]` para 10 workflows de JazzHR. Se detectó una laguna: ningún workflow del mapeo incluye una etapa para Worksense Format (el template de J&J). Hipótesis de Santiago: para JNJ - Workflow 2024, la etapa "New Format" debe generar el template Worksense (no la etapa genérica New Format) — sin cambios en JazzHR. Se preparó mensaje para confirmar con Paola (correo y WhatsApp).

Se reutiliza la credencial Anthropic de Fase 1 (`P3oMjAzU63IfOAff`). Se verificó la conexión a SharePoint vía Microsoft Graph API: sitio, Document Library y carpeta `Resumes` accesibles, con lectura y escritura confirmadas. Credencial `SharePoint - CV Reformatting (Graph API)` creada y probada en N8N (`fits.app.n8n.cloud`) — responde correctamente. Falta construir el workflow completo de entrega (Módulo 3).
