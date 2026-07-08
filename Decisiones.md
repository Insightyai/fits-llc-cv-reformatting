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

---

## Decisiones Pendientes
- [ ] Google Drive vs. SharePoint como destino final de entrega de CVs transformados — resolver la ambigüedad que quedó en el kickoff
- [ ] Sitio de SharePoint propio con App Registration nuevo, vs. reutilizar el App Registration de Contract Renewal con un grant adicional (`Sites.Selected`) sobre este segundo sitio
- [ ] Reutilizar la credencial Anthropic de Fase 1 (`P3oMjAzU63IfOAff` en `../../fits-llc/`) o provisionar una nueva para este proyecto
- [ ] Set de 15–20 CVs reales para las pruebas de aceptación del Módulo 2 (más allá de los 4 ejemplos de referencia que envía Paola)
- [ ] Paso de revisión humana antes del envío grupal — confirmar con Paola/Jeremy si se quiere o si la entrega automática es aceptable
- [ ] Confirmar en cuáles de los 10-12 workflows de JazzHR se habilita el nuevo stage "Resumes" (¿todos, o un subconjunto?)
