# Bitácora — CV Reformatting Automatizado

> Registro cronológico de avances, bloqueos y comunicaciones con FITS durante la ejecución.

### 3 Jul 2026
Contrato firmado. Reloj contractual sin arrancar — pendientes: templates de branding y sitio de SharePoint propio.

### 20 Jul 2026
Recibidos los 4 templates .docx definitivos (New Format, Non Template, BD Format, Worksense Format) — cargados en `02-modulo2-agente-transformacion/templates/`. También se recibió un CV de prueba (Shirley Mercado) — cargado en `02-modulo2-agente-transformacion/cvs-prueba/`. Confirmado el sitio de SharePoint propio (`Operaciones-RecursosHumanos`, carpeta `Resumes`) y recibidos Client ID / Tenant ID del Azure AD App Registration ("CV Reformatting"), guardados en `.env` local. Client Secret agregado por Santiago directo en `.env` local. Queda pendiente confirmar los permisos otorgados sobre el sitio (`Sites.Selected` vs. `Sites.ReadWrite.All`).

Revisados dos correos de Paola: uno del 18 jun 2026 (Alternativas A y B originales) y otro del 7 jul 2026 (mismo día del kickoff) con el mapeo definitivo de workflow → etapa(s) `Convert Resume - [Formato]` para 10 workflows de JazzHR. Se detectó una laguna: ningún workflow del mapeo incluye una etapa para Worksense Format (el template de J&J). Hipótesis de Santiago: para JNJ - Workflow 2024, la etapa "New Format" debe generar el template Worksense (no la etapa genérica New Format) — sin cambios en JazzHR. Se preparó mensaje para confirmar con Paola (correo y WhatsApp).

Se reutiliza la credencial Anthropic de Fase 1 (`P3oMjAzU63IfOAff`). Se verificó la conexión a SharePoint vía Microsoft Graph API: sitio, Document Library y carpeta `Resumes` accesibles, con lectura y escritura confirmadas. Credencial `SharePoint - CV Reformatting (Graph API)` creada y probada en N8N (`fits.app.n8n.cloud`) — responde correctamente. Falta construir el workflow completo de entrega (Módulo 3).

### 21 Jul 2026
Respuesta de Paola a la duda sobre Worksense Format: FITS decidió no integrarlo en JazzHR, no es un formato de uso regular. Para JNJ - Workflow 2024 quedan solo las etapas Non Template y New Format, ambas con templates genéricos — sin lógica especial por workflow. Se descarta la hipótesis de selección de template por (workflow, etapa) planteada el 20 jul.

### 28 Jul 2026
Verificación del Módulo 1 vía API de JazzHR: las etapas `Convert Resume - [Formato]` ya estaban creadas en los 10 workflows (las agregó Paola antes del kickoff), coincidiendo con el mapeo confirmado — excepto JNJ - Workflow 2024, que tenía por error una etapa `Convert Resume - Worksense` en vez de `Convert Resume - Non Template`. Confirmado que no había riesgo de candidatos activos en esa etapa (proyecto aún sin automatizar). Santiago corrigió el nombre de la etapa directamente en JazzHR (Settings → Workflows). Verificado por API tras el cambio: JNJ queda con Non Template + New Format, igual al resto. **Módulo 1 resuelto por completo.** Se copiaron al `.env` de este repo las credenciales de JazzHR (API key, usuario, password) y el N8N API key de FITS, reutilizando la integración de Fase 1.
