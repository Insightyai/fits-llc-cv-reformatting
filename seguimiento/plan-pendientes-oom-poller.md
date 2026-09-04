# Plan de pendientes — OOM y latencia del Convert Resume Poller

> Contexto completo de la investigación y el plan original: `/Users/santiagociurlo/.claude-trabajo/plans/investiguemos-a-fondo-quiero-majestic-crab.md`.
> Incidente que originó esto: `seguimiento/bitacora.md`, entrada "26 Ago 2026 (más tarde) — Crash simultáneo de 3 workflows por OOM".

## Ya aplicado (26 ago 2026)

**Capa 1 — cron de `Convert Resume Poller` (`6gxbJ87rfAsbcCOO`) cambiado de `7,22,37,52 * * * *` a `1,11,21,31,41,51 * * * *`**, para que cada ciclo arranque justo después de cada disparo de `AI Screening Poller` (cada 10 min exactos, intocable) en vez de solaparse con él. Guard anti-solapamiento interno bajado de 9 a 8 min. Verificado: `AI Screening Poller` sin ningún cambio, `active: true` sin tocar, 16 nodos intactos salvo los 2 modificados.

**Confirmado insuficiente (2 sep 2026):** el 2 sep hubo 2 crashes triples nuevos (`Convert Resume Poller` + `AI Screening Poller` + `AI CV Screening`), en el mismo minuto de offset que dejó la Capa 1 (`:X0:06` → `:X1:00`) — el margen de 1 minuto no alcanza para evitar el solapamiento de memoria. Motivó pasar directo a la Capa 2 (ver abajo, aplicada el mismo día).

## Capa 0 — RESUELTA (27 ago 2026)

Volumen real de jobs confirmado vía la misma API interna que usa el Poller (`api.jazz.co/job`, paginado completo con cookie de sesión, sin disparar `Trigger Manual`): **4873 jobs totales, 113 Open.** El total real cabe en 10 páginas de 500 — las 15 que pide hoy `Preparar Páginas` dejan 5 vacías cada ciclo. Detalle completo, desglose por status y por `workflowId` en `Volumen-JazzHR.md` (raíz del proyecto).

## Capa 2 — items 1 y 2 APLICADOS (2 sep 2026), item 3 pendiente

Cubre los ~3 crashes por OOM que fueron aislados (no por solapamiento de pollers) — causa probable: el propio consumo de memoria de `Convert Resume Poller` por ciclo.

1. **APLICADO.** Nuevo nodo `Reducir Payload Jobs` (Code) agregado entre `Listar Jobs` y `Filtrar Open y Mapear Formatos` en `Convert Resume Poller` — recorta cada job a `{id, status, workflowId, title}` antes de seguir el pipeline. Verificado por diff de `GET /workflows/6gxbJ87rfAsbcCOO` antes/después: único nodo nuevo, cron/settings intactos.
2. **APLICADO.** `pages` bajado de `15` a `12` en `Preparar Páginas` (con `per_page=500` en `Listar Jobs`, ahora hasta 6.000 registros por ciclo en vez de 7.500). Margen sobre las 10 páginas reales confirmadas en la Capa 0.
3. **Pendiente, sesión aparte.** Acotar `Leer Log Real` (hoy trae `Sheet1!B:H` completo sin límite). Antes de tocarlo, verificar con una llamada liviana de metadata (`spreadsheets.get`, sin `values`) cuántas filas tiene el Sheet hoy — si son pocas miles, no vale el riesgo; si son decenas de miles, acotar a las últimas ~5000 filas (mismo patrón que ya usa `AI Screening Poller` con su Sheet, rango `B2:C` + nodo `Parsear Log Sheet` dedicado).

**Verificación aplicada:** diff de nodos/conexiones/settings/cron antes-después del PUT (sin cambios fuera de lo esperado). Pendiente confirmar 1-2 ciclos reales sin crash tras el cambio (ver `bitacora.md`, entrada del 2 sep 2026).

## Diferido explícitamente (fuera de esta ronda, decisión de Santiago)

- Portar las mejoras de robustez de dedup que ya tiene `AI Screening Poller` y `Convert Resume Poller` no: límite de reintentos (`MAX_ATTEMPTS=3`, evita loops con candidatos "veneno"), comportamiento fail-closed explícito si falla la lectura del Sheet, recorte de columnas del Sheet apenas se lee.

## Opcional / sesión futura separada — Fase 2: migrar el polling al microservicio de Railway

Confirmado técnicamente viable (investigación 26 ago), pero es un cambio de arquitectura grande:
- Agregar `httpx` a `requirements.txt` del microservicio (`02-modulo2-agente-transformacion/microservicio/`).
- Agregar un disparador periódico — Railway Cron Job como servicio separado (recomendado, aísla memoria del proceso `web`) o `apscheduler` interno (más simple, mezcla responsabilidades).
- Portar la lógica de dedup (`staticData.processedPairs` + cruce contra el log de Sheets) a Python.
- Agregar la credencial `JazzHR Cookie` como variable de entorno en Railway (header de cookie/JWT de sesión — reutilizable tal cual, pero hereda el mismo riesgo de vencimiento manual ya documentado en `bitacora.md`).
- Eliminaría de raíz el problema de OOM (saca uno de los 2 procesos pesados de la instancia n8n compartida), pero no elimina el rate limit real de JazzHR (~1 req/10-11s) — la latencia mínima estructural del barrido seguiría existiendo.

## Recomendación de negocio (no técnica, a discutir con el cliente)

Reconsiderar con FITS el add-on de webhook nativo de JazzHR (Candidate Export Integration + Workflow Helper, ~$27-29 USD/mes) — ya rechazado una vez por costo, pero el costo operativo real del polling ya se demostró con 3 incidentes de producción y varias sesiones de investigación/fix.
