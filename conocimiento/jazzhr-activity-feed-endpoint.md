# Feed de Actividad de JazzHR — Detección Rápida de Cambios de Etapa

> Endpoint interno no documentado, encontrado por Santiago inspeccionando con DevTools el widget "Latest Activity" del dashboard de JazzHR (11-12 sep 2026), mientras se evaluaban alternativas para bajar la latencia de detección de "Convert Resume" (el Poller por escaneo job+etapa tarda 50-70 min por barrido completo — ver `conocimiento/n8n-diagnostico-pollers.md` y `Decisiones.md`, entrada del 12 sep 2026).

## El endpoint

```
GET https://api.jazz.co/user/{userId}/action?expand=projob,projob.prospect,workflowStep&per_page=100&page=1
```

- Misma autenticación por cookie de sesión que ya usa el Poller (credencial n8n `JazzHR Cookie`, `T5hQiFoIQSHIvCMj`) — no requiere credencial nueva.
- `{userId}` se resuelve en cada corrida vía `GET https://api.jazz.co/user/me` con la misma cookie (no hardcodeado). Confirmado que la cuenta de esa cookie (`userId 874857`, "Fits AI", Super Administrator, `hasFullVisibility: true`) ve la actividad de toda la cuenta, no solo la propia — coincide con lo que ya se ve en el widget (movimientos de varios reclutadores distintos).
- `per_page` máximo real: **100** (confirmado empíricamente — pedir 500 devuelve `400 Bad Request`: "per_page should be less than or equal to 100").
- Paginación estándar vía header `Link` (`rel="first"|"next"|"last"`) + `X-Pagination-Total-Items`.
- **Ventana observada: 500 ítems** (`X-Pagination-Total-Items: 500`) — probablemente un techo de las últimas 500 acciones de toda la cuenta, no un historial completo. Si el poller estuviera caído más tiempo del que tarda en llenarse esa ventana, se pueden perder eventos de forma irrecuperable por esta vía — de ahí que el Poller original (`Convert Resume Poller`, escaneo exhaustivo job+etapa) se mantenga activo como red de reconciliación mientras dure la validación, no se retira.

## Forma de cada ítem (`actionType: "change_workflow_step"` es el relevante)

```json
{
  "id": 304405645,
  "userId": 884743,
  "user": { "firstName": "Elyzabeth", "lastName": "Padilla", "...": "..." },
  "jobId": 10848018,
  "projobId": 444841866,
  "projob": {
    "prospectId": 426881297,
    "prospect": { "id": 426881297, "firstName": "Elvin", "lastName": "Aviles", "resumeId": "resume_...", "...": "..." },
    "workflowStepId": 10727654
  },
  "prospectId": 426881297,
  "actionType": "change_workflow_step",
  "workflowStepId": 10727654,
  "workflowStep": { "id": 10727654, "workflowId": 653474, "name": "CONVERT RESUME-NON TEMPLATE", "category": "Active", "number": 10 },
  "createdAt": "2026-09-11 20:32:15"
}
```

- `id` es un contador **global ascendente en toda la cuenta** (no por usuario) — sirve como cursor: guardar el último `id` visto y en cada poll pedir solo lo que tenga un `id` mayor.
- `workflowStepId` viene directo en el ítem — **no hace falta resolver `/job` → `workflowId` interno → `step_id`** como hace el Poller viejo (`Filtrar Open y Mapear Formatos`). El mapeo `workflowStepId → formato` es el mismo diccionario `FORMAT_BY_STEP` ya embebido en el nodo `Extraer Pares` del Poller (`6gxbJ87rfAsbcCOO`) — copiado verbatim, no reinventado (tabla completa en `conocimiento/jazzhr-stepids-convert-resume.md`).
- `user`/`userId` pueden ser `null` — un auto-rechazo del sistema también es un `change_workflow_step` válido.
- El `expand` completo que usa la UI de JazzHR (`user,projob,projob.prospect,workflowStep,task,task.job,task.prospect,interviewResponse,interviewResponse.interview,interviewResponse.transientUser`) trae mucho peso muerto para este caso de uso — expandir `user` completo, en particular, trae `emailSignature` en HTML de varios KB por actor. **No expandir `user` en producción** (ver bug de sobre-consulta abajo).

## Bug real encontrado y corregido: sobre-consulta rompía la escritura al Sheet (12 sep 2026)

La primera versión del workflow `JazzHR - Convert Resume Activity Poller` traía siempre las 5 páginas completas (500 ítems) con el `expand` completo de arriba, en cada ciclo de 5 minutos, para siempre. Una ejecución real (`execution 29768`) generó ~2.9 MB de datos solo en el nodo de fetch, y la ejecución se cortó ahí (`resultData.lastNodeExecuted: "Procesar Ciclo"`, sin llegar a los nodos de Sheets) pese a marcar `status: success` — consistente con un límite de tamaño de datos de ejecución de n8n Cloud.

**Fix:** paginación perezosa (pedir solo página 1 por defecto; solo pedir páginas 2-5 si el `id` mínimo de la página 1 todavía no cubre el cursor guardado, tope duro de 5 páginas, con `gapDetected` si ni así se cubre) + `expand` recortado a `projob,projob.prospect,workflowStep` (se sacó `user`, `task*`, `interviewResponse*` — ninguno se usa en la lógica de filtrado/mapeo). Con esto, `actorUserName` queda vacío en el log (salvo `SYSTEM` en auto-rechazos) — trade-off deliberado de peso vs. completitud del campo, pendiente de decidir si se recupera con una llamada aparte solo para los ítems que sí matchean formato.

Verificado con 3 ejecuciones reales post-fix (`29778`, `29779`, `29780`): tamaño total de `runData` bajó de ~2.9 MB a ~206 KB (~14x menos), las tres llegaron hasta el último nodo (`Append Meta Row`) sin error.

## Dónde vive esto

Workflow n8n `JazzHR - Convert Resume Activity Poller` (`ioKEvVylitg7MHil`, `fits.app.n8n.cloud`), cron cada 5 min (`3,8,13,...,58 * * * *`), corriendo en **modo sombra** (detecta y registra en `Activity Shadow Log`/`Activity Shadow Meta` del spreadsheet de producción, no dispara el Processor todavía). Contexto completo de la decisión en `Decisiones.md`, bitácora de la sesión en `seguimiento/bitacora.md` (12 sep 2026).

## Pendiente

- Ventana de validación de 5-7 días hábiles corridos contra el log real de producción (criterios numéricos en `Decisiones.md`).
- Confirmar el primer caso real con datos de candidato en `Activity Shadow Log` (hasta ahora solo se probó con `matchedCount: 0`).
- Agregar la fila de encabezados a las 2 pestañas del Sheet (quedó bloqueado por permisos durante la construcción, es manual y cosmético).
- Decidir si vale la pena recuperar `actorUserName`.
- Plan de corte a producción (agregar `LIVE_MODE`, dedup contra el log real, conexión al webhook del Processor, downgrade del cron del Poller viejo a reconciliación) — diseñado en el plan de la sesión, pendiente de ejecutar una vez cumplida la validación.
