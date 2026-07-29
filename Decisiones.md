# Decisiones — FITS LLC · CV Reformatting Automatizado

> Registro de decisiones importantes tomadas durante la ejecución del proyecto.

## Plantilla
```
### [FECHA] — [Título]
**Contexto:** Por qué surgió esta decisión.
**Opciones consideradas:** Qué alternativas había.
**Decisión:** Qué se decidió.
**Razón:** Por qué se eligió esa opción.
**Impacto:** Qué cambia en el proyecto.
```

## Registro

### 3 Jul 2026 — Inicio del proyecto
**Contexto:** Contrato firmado por ambas partes vía PandaDoc (Ref. UTPMD-5NM4I-BUYGT-KWFRW).
**Decisión:** Proyecto activo. El reloj de 3–4 semanas (máx. 7) corre desde que Insighty reciba los 4 templates definitivos con branding completo, no desde la firma.
**Impacto:** El desarrollo no arranca formalmente hasta recibir los templates y resolver el destino de almacenamiento (ver decisión siguiente).

### Jul 2026 — SharePoint Document Library propio en vez de Google Drive/OneDrive
**Contexto:** El contrato firmado especifica Google Drive como destino por defecto, con OneDrive como upgrade posterior cuando Azure AD esté habilitado — diseñado así justamente para no depender de Centeno desde el arranque. En la práctica, se decidió que ambos proyectos de Fase 2 operen desde SharePoint.
**Opciones consideradas:** (a) mantener Google Drive como destino inicial según el contrato, migrar a SharePoint después; (b) ir directo a un sitio de SharePoint con Document Library desde el arranque.
**Decisión:** Este proyecto usa su **propio** sitio de SharePoint con Document Library (separado del de Contract Renewal), para los 4 templates de branding y la entrega de CVs transformados. Ya se le comunicó a FITS/Centeno.
**Razón:** Consistencia con la decisión tomada para Contract Renewal — almacenamiento organizacional en vez de personal, no depende de la cuenta de un usuario específico.
**Impacto:** Reintroduce como bloqueante de arranque la dependencia del Azure AD App Registration (el riesgo que el contrato había mitigado con Google Drive como fallback). A diferencia de Contract Renewal, aquí no hay ni siquiera confirmación de que el sitio ya se haya creado — este proyecto va más atrasado en prerequisitos que su hermano.

### Jul 2026 — Estado de la solicitud a Centeno
**Contexto:** Seguimiento de la recomendación de crear un sitio/Document Library propio para este proyecto.
**Decisión:** Registrado como "solicitado, sin confirmación de ejecución" — a diferencia de Contract Renewal (que ya tiene sitio creado y Excels migrados), acá todavía no hay evidencia de que el sitio exista, ni de si comparte o no el mismo App Registration que Contract Renewal.
**Impacto:** Ninguno de los dos prerequisitos bloqueantes del contrato (templates con branding, destino de entrega confirmado) está resuelto todavía. Es el proyecto de Fase 2 con más atraso.

### 7 Jul 2026 — Kickoff fase 2/3: templates confirmados y corrección de alcance del Módulo 1
**Contexto:** Sesión de kickoff conjunta con FITS para Contract Renewal y CV Reformatting (ver `seguimiento/Reuniones Transcript/2026-07-07-kickoff-fase2-3.txt`).
**Decisión:**
- Los 4 templates que Paola ya había compartido por correo son los **definitivos** — confirmado explícitamente por Jeremy en la llamada.
- **Corrección de alcance del Módulo 1:** no se crea un job posting nuevo aislado en JazzHR. Se agrega un stage **"Resumes"** dentro de cada uno de los **10–12 workflows/pipelines de JazzHR que FITS ya tiene** (los mismos usados para AI Screening en Fase 1). Confirmado explícitamente por Paola: "dentro de estos mismos workflows se crea una etapa nueva para pasar el resumen a CV." El reclutador sube/mueve el CV manualmente a ese stage según el formato deseado (New Format, Non Template, BD Format o Worksense Format).
- El agente de N8N corre en un **workflow nuevo** (no reutiliza los workflows de AI Screening de Fase 1), pero lee el stage "Resumes" que se agrega a los pipelines existentes.
- Paola va a enviar **un CV de ejemplo ya convertido a cada uno de los 4 formatos**, como caso de prueba/referencia inicial.
- Nota sin resolver: en la llamada se mencionó tanto "Google Drive" como "SharePoint" como destino de entrega de los CVs transformados — Santiago lo pidió como Google Drive, pero al describir el flujo lo ubicó en la carpeta compartida de SharePoint. Confirmar con el equipo cuál es el destino definitivo (se asume SharePoint, consistente con la decisión ya tomada para ambos proyectos).
**Impacto:** Se resuelve el prerequisito de templates. Se corrige la descripción técnica del Módulo 1 en `PRD.md` y en `01-modulo1-job-posting/README.md` — implica modificar los 10-12 workflows existentes de FITS, no crear una superficie nueva aislada, lo cual tiene mayor superficie de cambio (y de riesgo de romper algo en producción) que lo que sugería la lectura inicial del contrato.

### 20 Jul 2026 — Sitio de SharePoint propio confirmado, con URL
**Contexto:** Seguimiento del bloqueante de almacenamiento (ver decisión de Jul 2026 sobre SharePoint Document Library propio).
**Decisión:** El sitio existe y es propio de este proyecto — `Operaciones-RecursosHumanos`, distinto del sitio `Operaciones` de Contract Renewal, consistente con la decisión de separarlos. Datos:
- Sitio: `netorg583168.sharepoint.com/sites/Operaciones-RecursosHumanos`
- Document Library: `Shared Documents`
- Carpeta destino de los CVs transformados: `Resumes`
**Impacto:** Se resuelve la ambigüedad Google Drive vs. SharePoint — el destino final es este sitio de SharePoint.

### 20 Jul 2026 — Credenciales del Azure AD App Registration recibidas
**Contexto:** Seguimiento del bloqueante de acceso técnico al sitio `Operaciones-RecursosHumanos`.
**Decisión:** Santiago confirma que ya tiene el `client_id` y `tenant_id` del App Registration ("CV Reformatting", propio de este proyecto, distinto del de Contract Renewal). Valores guardados en `.env` local (gitignorado) como referencia. **Pendiente real:** el Client Secret y cargar los tres valores como credencial nativa en N8N (tipo Microsoft OAuth2/SharePoint) dentro de `fits.app.n8n.cloud` — se hace cuando arranque la construcción del workflow de entrega (Módulo 3).
**Impacto:** Se resuelve el bloqueante de identidad de la app. Falta confirmar los permisos otorgados (`Sites.Selected` vs. `Sites.ReadWrite.All`) antes de poder probar la conexión real vía Microsoft Graph API.

**Actualización 20 Jul 2026:** Santiago agregó el Client Secret directo en `.env` local (sin exponerlo en el chat). Los 3 valores del App Registration ya están completos en `.env`. Sigue pendiente: confirmar permisos otorgados y cargar la credencial nativa en N8N.

### 7 Jul 2026 — Mapeo confirmado de workflows y etapas (correo de Paola)
**Contexto:** Correo de Paola (mismo día del kickoff) con la lista definitiva de los 10 workflows de JazzHR y el nombre exacto de la(s) etapa(s) que se agrega(n) a cada uno. También adjuntó el resume de Shirley Mercado como caso de prueba (mismo archivo ya cargado en `02-modulo2-agente-transformacion/cvs-prueba/`).
**Decisión:** El mapeo real no es "4 sub-formatos en cada uno de los 10-12 workflows" (lectura previa del PRD) sino una etapa nueva por workflow, nombrada `Convert Resume - [Formato]`, y solo con los formatos que ese workflow necesita:

| Workflow | Etapa(s) agregada(s) |
|---|---|
| Abbott FG - Workflow 2024 | Convert Resume - Non Template |
| Amgen FG - Workflow 2024 | Convert Resume - Non Template |
| Becton Dickinson - Workflow 2024 | Convert Resume - BD Format |
| Beeline - Workflow 2024 | Convert Resume - Non Template |
| Haleon FG - Workflow 2026 | Convert Resume - Non Template · Convert Resume - New Format |
| JazzHR Standard Workflow | Convert Resume - Non Template · Convert Resume - New Format |
| JNJ - Workflow 2024 | Convert Resume - Non Template · Convert Resume - New Format |
| Integra FG - Workflow 2024 | Convert Resume - Non Template |
| Medtronic - Workflow 2024 | Convert Resume - Non Template |
| SOW Workflow 2024 | Convert Resume - New Format |

**Razón:** Reduce el riesgo de selección manual errónea — cada workflow solo expone los formatos que le aplican, no los 4 completos.
**Impacto:** Se resuelve el pendiente "confirmar en cuáles de los 10-12 workflows se habilita el stage 'Resumes'". Se corrige el nombre de la etapa: no es un stage único "Resumes" con sub-formatos, son etapas individuales `Convert Resume - [Formato]`.

**Laguna detectada — Worksense Format:** La tabla enviada por Paola no incluía ninguna etapa "Convert Resume - Worksense Format" — JNJ - Workflow 2024 solo tiene Non Template y New Format, igual que otros workflows. Al revisar el correo original del 18 jun 2026 (Alternativa B), Paola sí listaba "Worksense format for J&J platform requisitions" como uno de los 4 formatos.

**Hipótesis de resolución (Santiago, 20 jul 2026):** No hace falta agregar una etapa nueva en JazzHR. La etapa "Convert Resume - New Format" ya existe en JNJ - Workflow 2024 (tal como la envió Paola) — lo que cambia es qué template aplica el agente cuando el candidato está en *ese workflow específico* y llega a *esa etapa*: en vez del template genérico `New Format Resume Template.docx`, debe usar `Worksense Template.docx`. La selección de template pasa a depender del par (workflow, etapa), no solo del nombre de la etapa. Esto evita pedirle a FITS que modifique un workflow en producción.
**Impacto:** No cambia el alcance de Módulo 1 (JazzHR queda igual a lo que Paola envió). Sí cambia el diseño del Módulo 2: el Code node que selecciona el template necesita el nombre del workflow además del nombre de la etapa. **Pendiente confirmar con Paola** que esta lectura es correcta antes de dar por cerrada la regla.

### 21 Jul 2026 — Worksense Format descartado: JNJ usa el template genérico de New Format
**Contexto:** Respuesta de Paola (correo del 21 jul 2026) a la hipótesis de Santiago sobre el template Worksense para JNJ - Workflow 2024.
**Decisión:** FITS decidió **no integrar** el formato Worksense en JazzHR — no es un formato de uso regular en sus operaciones actuales. Para JNJ - Workflow 2024 solo se consideran las etapas `Convert Resume - Non Template` y `Convert Resume - New Format`, ambas con sus templates genéricos estándar. No hace falta etapa adicional ni template específico de Worksense.
**Razón:** Paola indica que si surge una necesidad recurrente de ese formato en el futuro, se reevaluaría su integración — no es prioridad ahora.
**Impacto:** Se descarta la hipótesis de selección de template dependiente del par (workflow, etapa). El Code node de selección de template en Módulo 2 vuelve a depender únicamente del nombre de la etapa — diseño más simple que el propuesto el 20 jul. El template `Worksense Template.docx` recibido junto con los otros 3 queda sin uso por ahora (no se elimina, por si se reevalúa a futuro).

### 28 Jul 2026 — Corrección de la etapa Worksense en JazzHR (JNJ - Workflow 2024)
**Contexto:** Verificación del Módulo 1 vía API de JazzHR (`GET /workflows`): los 10 workflows ya tenían sus etapas `Convert Resume - [Formato]` creadas (Paola las agregó antes del kickoff), coincidiendo con el mapeo confirmado — excepto JNJ - Workflow 2024, que tenía `Convert Resume - Worksense` en vez de `Convert Resume - Non Template`.
**Decisión:** Santiago confirmó por qué no había riesgo de candidatos activos en esa etapa: son etapas nuevas agregadas específicamente para este proyecto, que aún no está en producción, por lo que ningún candidato pudo haber llegado ahí todavía. Se verificó manualmente en JazzHR (vacante HR Business Partner, la de mayor volumen de candidatos del workflow) que los únicos 2 candidatos activos estaban en etapas anteriores del pipeline, no en Worksense. Con el riesgo descartado, se renombró la etapa directamente en JazzHR (Settings → Workflows → JNJ - Workflow 2024) de `Convert Resume-Worksense` a `Convert Resume-Non Template`.
**Impacto:** JNJ - Workflow 2024 queda con las etapas exactas del mapeo de Paola (Non Template + New Format). Verificado nuevamente vía API tras el cambio. **Módulo 1 queda resuelto en su totalidad** — las etapas `Convert Resume - [Formato]` ya existen y están correctas en los 10 workflows de JazzHR. Lo pendiente ahora es la automatización (Módulo 2): hoy la conversión de formato se hace manualmente cuando el candidato llega a la etapa.

### 20 Jul 2026 — Conexión a SharePoint verificada vía Microsoft Graph API
**Contexto:** Con Client ID, Tenant ID y Client Secret ya en `.env`, se probó la conexión real antes de configurarla en N8N.
**Decisión:** Conexión verificada con éxito vía client credentials flow:
- Sitio `Operaciones-RecursosHumanos` resuelto correctamente (Site ID guardado en `.env`)
- Document Library "Documents" (Shared Documents) accesible, con la carpeta `Resumes` visible
- Permisos de **lectura y escritura** confirmados (se subió y luego se borró un archivo de prueba)
**Impacto:** Se resuelve el pendiente de permisos del App Registration — el nivel de acceso otorgado (sea `Sites.Selected` o `Sites.ReadWrite.All`) es suficiente para el Módulo 3.

**Actualización 20 Jul 2026:** Credencial `SharePoint - CV Reformatting (Graph API)` creada en N8N (tipo genérico OAuth2 API, Client Credentials, scope `https://graph.microsoft.com/.default`) y probada con un nodo HTTP Request — responde correctamente con los datos del sitio, Site ID idéntico al verificado por curl. Conexión SharePoint↔N8N lista para construir el workflow de entrega (Módulo 3).

### 20 Jul 2026 — Credencial Anthropic: se reutiliza la de Fase 1
**Decisión:** Se reutiliza la credencial "Anthropic - FITS" (`P3oMjAzU63IfOAff`, ya provisionada en `../../fits-llc/`) en vez de crear una nueva para este proyecto.
**Razón:** Sin costo de setup adicional, misma cuenta ya operativa en producción.
**Impacto:** El consumo de ambos proyectos queda bajo la misma credencial/facturación — no hay medición de costo independiente por proyecto.

### 28 Jul 2026 — Plan de arquitectura para Módulo 2 y 3, y arranque de Fase 0
**Contexto:** Al planificar la construcción de Módulo 2 (Agente de Transformación) y Módulo 3 (Entrega al Equipo), surgieron restricciones heredadas de Fase 1 que cambian el diseño: JazzHR no tiene webhooks (Fase 1 usa un poller con schedule), y N8N Cloud bloquea `zlib`/`require()` en el Code node con límite de 49 KB de salida — generar un `.docx` completo dentro de N8N es inviable.
**Opciones consideradas (generación del .docx):** (a) microservicio Python (`docxtpl`) en Railway; (b) Google Docs API con conversión `.docx→Docs→.docx`; (c) Code node JS puro; (d) SaaS de render (Carbone, CloudConvert).
**Decisión:** Se aprueba (a) — microservicio Python en Railway. Se descartan (c) por las restricciones técnicas de N8N Cloud, y (d) por la exclusión contractual de licencias de terceros y por enviar PII de candidatos a un procesador nuevo sin DPA.
**Otras decisiones del plan:** los 4 templates se anotan con tags `docxtpl`/Jinja2 directamente en Word, a cargo de Santiago (no por script, para evitar el bug de run-splitting de Word); el workflow de N8N se construye como JSON versionado en el repo, con primer import manual por UI en `fits.app.n8n.cloud` antes de iterar por API REST; el log de Módulo 3 se crea como spreadsheet nuevo bajo la cuenta `fitsscreening@gmail.com` para reutilizar la credencial de Sheets ya existente.
**Impacto:** Arranca la Fase 0 (reconocimiento, sin bloqueantes de FITS): anatomía de los 4 templates (`conocimiento/anatomia-templates.md`), esquema canónico de datos (`02-modulo2-agente-transformacion/contrato-datos/cv-schema.json`), mapeo de placeholders y guía de anotación (`02-modulo2-agente-transformacion/templates/`), mapa real de `step_id` de las 13 etapas "Convert Resume" vía API de JazzHR (`conocimiento/jazzhr-stepids-convert-resume.md`), reglas de contenido por formato (`conocimiento/reglas-por-formato.md`) y diseño del log de Sheets (`03-modulo3-entrega-equipo/log-sheets-diseno.md`, aún no creado).
**Hallazgo relevante:** los nombres de etapa "Convert Resume" no son consistentes entre workflows (Haleon FG usa `Convert Resume - Non Template` en vez de `CONVERT RESUME-NON TEMPLATE`) — el Code node de selección de template debe matchear por `step_id`, no por nombre de texto.

### 28 Jul 2026 — Anotación de templates por script en vez de manual, y limpieza de Worksense Template.docx
**Contexto:** Se empezó a anotar `Non Template Resume.docx` a mano en Word siguiendo la guía (decisión del 28 jul anterior). Tomó mucho tiempo y generó problemas menores (Word "conservando mayúsculas" al reemplazar, texto que quedaba en varios runs de XML).
**Decisión:** Se cambió a anotar los 3 templates activos (`New Format`, `Non Template`, `BD Format`) por script (`python-docx`), verificando cada uno con un render real de `docxtpl` contra datos de prueba antes de darlo por bueno. Los 3 quedaron validados en `02-modulo2-agente-transformacion/templates/anotados/`.
**Razón:** Más rápido y con verificación automática inmediata (el render expone cualquier error de sintaxis Jinja al instante), en vez de depender de una inspección visual en Word.
**Impacto:** La guía `INSTRUCCIONES-ANOTACION.md` para anotar manualmente en Word queda como referencia para templates futuros, no como el método usado para estos 3.

**Aparte:** el archivo `Worksense Template.docx` se eliminó del repo el mismo día. La decisión de **descartar el formato Worksense** ya estaba tomada por Paola (FITS) el 21 jul 2026 (ver entrada de esa fecha más arriba) — lo de hoy fue solo limpieza del archivo ya sin uso, no una decisión nueva. Si FITS reactiva el formato, hay que pedirle el `.docx` de nuevo.

---

## Decisiones Pendientes
- [x] Google Drive vs. SharePoint como destino final de entrega de CVs transformados — resuelto: SharePoint, sitio `Operaciones-RecursosHumanos`
- [x] Sitio de SharePoint propio con App Registration nuevo, vs. reutilizar el de Contract Renewal — resuelto: sitio propio
- [x] Registrar Tenant ID / Client ID del Azure AD App Registration para este sitio — recibidos, en `.env` local
- [x] Client Secret del App Registration — recibido, en `.env` local
- [x] Confirmar permisos otorgados — resuelto: lectura y escritura verificadas vía Graph API
- [x] Cargar y probar credencial de SharePoint en N8N — resuelto: `SharePoint - CV Reformatting (Graph API)` funcionando
- [x] Reutilizar la credencial Anthropic de Fase 1 (`P3oMjAzU63IfOAff` en `../../fits-llc/`) o provisionar una nueva — resuelto: se reutiliza la de Fase 1
- [ ] Set de 15–20 CVs reales para las pruebas de aceptación del Módulo 2 (más allá del CV de prueba ya recibido, ver `02-modulo2-agente-transformacion/cvs-prueba/`)
- [ ] Paso de revisión humana antes del envío grupal — confirmar con Paola/Jeremy si se quiere o si la entrega automática es aceptable
- [x] Confirmar en cuáles workflows de JazzHR se habilita el/los nuevo(s) stage(s) — resuelto: 10 workflows, mapeo exacto arriba
- [x] Corregir etapa mal nombrada en JNJ - Workflow 2024 (`Convert Resume - Worksense` → `Convert Resume - Non Template`) — resuelto 28 jul 2026, verificado vía API
- [x] **Confirmar con Paola:** para JNJ - Workflow 2024, ¿la etapa "Convert Resume - New Format" debe generar el template Worksense en vez del template genérico de New Format? — resuelto: no, Worksense queda descartado, JNJ usa el template genérico de New Format (correo de Paola, 21 jul 2026)
