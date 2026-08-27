# Volumen real de jobs en JazzHR (FITS)

> Referencia de consulta rápida, a la par de `Decisiones.md`. Mide el volumen real de jobs en la cuenta de JazzHR de FITS — dato necesario para calibrar el Poller (`Convert Resume Poller`, ver `seguimiento/plan-pendientes-oom-poller.md`, Capa 0/Capa 2) sin adivinar. Detalle completo de la investigación en `seguimiento/bitacora.md`, 27 ago 2026.

## Medición del 27 ago 2026

**Método:** paginación completa de `GET https://api.jazz.co/job?per_page=500&page=N` (la misma API interna que usa el nodo `Listar Jobs` del Poller en producción), con cookie de sesión de Santiago. No se usó la API pública (`api.resumatorapi.com`) porque su parámetro `page` no funciona — devuelve siempre el mismo conjunto de 100 registros sin importar la página pedida (confirmado empíricamente: overlap total de IDs entre página 1 y página 80).

**Resultado — jobs totales en la cuenta (histórico completo, desde 2018):**

| Métrica | Valor |
|---|---|
| Jobs totales (todos los `status`) | **4873** |
| Jobs actualmente **Open** | **113** |
| `workflowId` (plantillas de proceso) con al menos 1 job Open | 12 de ~24 totales |
| Páginas de 500 necesarias para cubrir todo el histórico | **10** (la página 10 devuelve 373, la 11 en adelante estaría vacía) |

**Desglose completo por `status`:**

| Status | Cantidad |
|---|---|
| Closed | 2286 |
| Filled | 1222 |
| Cancelled | 1027 |
| On Hold | 170 |
| Open | 113 |
| Drafting | 54 |
| Not Approved | 1 |

**Desglose de los 113 jobs Open por `workflowId` (top 10, de 12 con al menos 1 Open):**

| `workflowId` | Jobs Open |
|---|---|
| 655764 | 57 |
| 653512 | 17 |
| 653474 | 17 |
| 653470 | 8 |
| 653513 | 4 |
| 499366 | 3 |
| 534058 | 2 |
| 653543 | 1 |
| 547224 | 1 |
| 660931 | 1 |

## Implicación directa para el Poller (Capa 2, pendiente)

El nodo `Preparar Páginas` del `Convert Resume Poller` pide `pages = 15` (hasta 7500 registros por ciclo, `per_page=500`). El volumen real (4873 jobs) cabe en **10 páginas** — las páginas 11 a 15 siempre devuelven vacío. Esto significa que **5 de las 15 páginas que pide cada ciclo del Poller son trabajo desperdiciado** (llamadas HTTP y memoria gastadas en resultados vacíos), consistente con la sospecha ya anotada en `seguimiento/plan-pendientes-oom-poller.md` de que `pages=15` está sobredimensionado.

**Sin aplicar todavía** — pendiente decidir con Santiago si bajar `pages` a un valor con margen de crecimiento (ej. 11-12, no exactamente 10) antes de tocar el nodo.

## Nota de vigencia

Esta es una foto puntual del 27 ago 2026, no un valor fijo. El total de jobs (4873) solo crece con el tiempo; los Open (113) varían día a día según el ritmo de contratación de FITS. Si pasan varios meses o se nota un cambio grande en el comportamiento del Poller, vale la pena remedir en vez de asumir que estos números siguen vigentes.
