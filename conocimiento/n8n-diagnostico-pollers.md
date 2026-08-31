# Cómo diagnosticar si un Poller está corriendo (y la trampa que ya cayó 3 veces)

> Origen: caída en la misma trampa en 3 sesiones distintas (20 ago, y dos veces el 31 ago — una casi con `AI Screening Poller`, corregida por Santiago antes de tocar nada; otra con `Convert Resume Poller`, corregida después de hacer 2 toggles y un PUT completo innecesarios en producción). Este archivo existe para que la próxima sesión lea esto ANTES de concluir "el poller está caído" a partir de `GET /executions`.

## La trampa

`Convert Resume Poller` y `AI Screening Poller` tienen `settings.saveDataSuccessExecution: "none"` (fix del 19 ago 2026, para evitar el OOM de guardar ~49.5 MB por ejecución exitosa — ver `CLAUDE.md`, 19 ago). Con ese valor, **una ejecución exitosa no deja ningún registro en `GET /api/v1/executions`** — ni siquiera una entrada con datos vacíos. Solo quedan visibles las ejecuciones `crashed`/`error`.

Consecuencia directa: si consultás `/executions?workflowId=<poller>` y el último registro es un crash de hace días, **eso NO prueba que el poller lleve días sin correr.** Puede llevar corriendo con total normalidad todo ese tiempo — el silencio es el comportamiento esperado, no una señal de falla.

Esta misma confusión ya causó una falsa alarma documentada el 20 ago 2026 (ver `CLAUDE.md`): una alerta de "Poller crasheado hace 19 minutos" resultó ser un aviso real pero con ~17 horas de retraso, porque n8n solo corre el error-workflow cuando el estado final es `crashed`, y las ejecuciones exitosas intermedias eran invisibles por este mismo motivo.

## Cómo confirmar de verdad si un Poller está corriendo (en este orden)

1. **Evidencia downstream primero, sin tocar nada.** Los Pollers no procesan directo — disparan al Processor correspondiente (`JazzHR - Convert Resume Processor` / la cadena de AI Screening) vía webhook interno, y ESE workflow sí guarda sus ejecuciones normalmente (`saveDataSuccessExecution` no está en `none` ahí). Revisar:
   - `GET /executions?workflowId=<processor>&limit=10` — buscar ejecuciones recientes en modo `webhook` con timestamps que coincidan con los ticks del cron del Poller.
   - El Google Sheet de log real (`1EM7GeQ7AePoMyngzDsRgMgnjj85K_pIoqfa1u4ukAo4` para Convert Resume; el sheet "FITS - AI Screening Log" para AI Screening) — filas nuevas con timestamp reciente son la prueba más directa de que el ciclo completo funciona.
   - Si hay evidencia downstream reciente (procesó un candidato real hace poco), **el Poller está sano — no hace falta tocar nada más.**

2. **Solo si no hay evidencia downstream reciente y necesitás confirmar en vivo**, hacer el test controlado:
   - Traer el workflow completo (`GET /workflows/{id}`), cambiar únicamente `settings.saveDataSuccessExecution` a `"all"`, y hacer `PUT /workflows/{id}` con el objeto completo (`name`, `nodes`, `connections`, `settings`, `staticData` — el PUT exige el workflow entero, no un patch parcial).
   - Revisar el cron real del nodo Schedule Trigger (`GET /workflows/{id}`, buscar el nodo `scheduleTrigger`) para saber los minutos exactos en que debería disparar.
   - Esperar a que pase **al menos un tick completo del cron desde el momento del cambio**, más el tiempo de ejecución típico del ciclo (~4-5 min para Convert Resume Poller) — no cortar la espera antes de que la ejecución termine, o quedará invisible igual.
   - Confirmar con `GET /executions?workflowId=<poller>&limit=3` que aparece una ejecución nueva (`success` o `crashed`, cualquiera de las dos confirma que el trigger está vivo).
   - **Revertir `saveDataSuccessExecution` a `"none"` apenas se confirme** — no dejarlo en `"all"` en producción, es el mismo riesgo de OOM que motivó el fix del 19 ago.

3. **Nunca concluir "está caído" solo por ausencia de entradas en `/executions`.** Si hace falta reactivar (toggle `deactivate`/`activate`) porque de verdad no hay evidencia downstream reciente y el test del punto 2 confirma silencio total, ahí sí es una señal real — pero llegar a esa conclusión sin pasar por los pasos 1 y 2 es exactamente el error que ya se cometió 3 veces.

## Nota sobre AI Screening Poller

Nunca fue parte del alcance de este proyecto (`Fits-LLC — CV Reformatting`) — es de la Fase 1 (`../../fits-llc/`). No tocar su configuración ni sus toggles salvo pedido explícito, aunque haya crasheado junto con `Convert Resume Poller` en el pasado (ver `Decisiones.md`, 26 ago 2026, crash triple simultáneo). Confirmado el 31 ago 2026: Santiago corrigió en el momento un intento de tocarlo sin que lo hubiera pedido.
