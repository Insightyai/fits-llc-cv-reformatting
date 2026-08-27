# Plan de pendientes — OOM y latencia del Convert Resume Poller

> Contexto completo de la investigación y el plan original: `/Users/santiagociurlo/.claude-trabajo/plans/investiguemos-a-fondo-quiero-majestic-crab.md`.
> Incidente que originó esto: `seguimiento/bitacora.md`, entrada "26 Ago 2026 (más tarde) — Crash simultáneo de 3 workflows por OOM".

## Ya aplicado (26 ago 2026)

**Capa 1 — cron de `Convert Resume Poller` (`6gxbJ87rfAsbcCOO`) cambiado de `7,22,37,52 * * * *` a `1,11,21,31,41,51 * * * *`**, para que cada ciclo arranque justo después de cada disparo de `AI Screening Poller` (cada 10 min exactos, intocable) en vez de solaparse con él. Guard anti-solapamiento interno bajado de 9 a 8 min. Verificado: `AI Screening Poller` sin ningún cambio, `active: true` sin tocar, 16 nodos intactos salvo los 2 modificados.

**Pendiente de confirmar (arrancar la próxima sesión por acá):** revisar el resultado del monitoreo de 1-2h programado el mismo día del cambio — confirmar vía `GET /executions?status=crashed` que no hubo crashes nuevos desde el cambio, y que los timestamps reales de ejecución de `Convert Resume Poller` nunca coincidieron con los de `AI Screening Poller` (`:X0:06`). Si el monitoreo automático no llegó a completarse o no quedó documentado en `bitacora.md`, repetirlo antes de dar la Capa 1 por cerrada.

## Capa 0 — RESUELTA (27 ago 2026)

Volumen real de jobs confirmado vía la misma API interna que usa el Poller (`api.jazz.co/job`, paginado completo con cookie de sesión, sin disparar `Trigger Manual`): **4873 jobs totales, 113 Open.** El total real cabe en 10 páginas de 500 — las 15 que pide hoy `Preparar Páginas` dejan 5 vacías cada ciclo. Detalle completo, desglose por status y por `workflowId` en `Volumen-JazzHR.md` (raíz del proyecto).

## Pendiente — Capa 2: reducir memoria por ciclo

Cubre los ~3 crashes por OOM que fueron aislados (no por solapamiento de pollers) — causa probable: el propio consumo de memoria de `Convert Resume Poller` por ciclo.

1. **Portar el nodo `Reducir Payload Jobs`** de `AI Screening Poller` (patrón ya probado en producción, no se toca ese workflow, solo se copia el patrón): agregar un nodo `Set` entre `Listar Jobs` y `Filtrar Open y Mapear Formatos` en `Convert Resume Poller`, recortando cada job a `id`, `status`, `workflowId` antes de seguir el pipeline.
2. **Ajustar `pages`** en el nodo `Preparar Páginas` (hoy `15` hardcodeado, con `per_page=500` en `Listar Jobs` — hasta 7.500 registros por ciclo) según el resultado de la Capa 0.
3. **Acotar `Leer Log Real`** (opcional): hoy trae `Sheet1!B:H` completo sin límite, crece indefinidamente desde que el sistema está en producción. Antes de acotarlo, verificar con una llamada liviana de metadata (`spreadsheets.get`, sin `values`) cuántas filas tiene el Sheet hoy — si son pocas miles, no vale el riesgo; si son decenas de miles, acotar a las últimas ~5000 filas (mismo patrón que ya usa `AI Screening Poller` con su Sheet, rango `B2:C` + nodo `Parsear Log Sheet` dedicado).

**Verificación:** disparar `Trigger Manual` una vez después de cada cambio para confirmar que el conteo de jobs/candidatos detectados no cambia (solo debe bajar memoria/duración), y monitorear 2-3 ciclos reales.

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
