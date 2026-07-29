# Diseño del Log de Google Sheets (Módulo 3)

> Estructura propuesta para el spreadsheet de registro de procesamiento exigido por el criterio de aceptación de Módulo 3 ("el log de Google Sheets registra la entrada correctamente: candidato, formato, fecha, resultado"). Solo diseño — la creación del Sheet real está pendiente de confirmación (ver abajo).

## Cuenta propietaria

`fitsscreening@gmail.com` — la misma cuenta detrás de la credencial `Google Sheets - FITS Screening` (`vuAQyDYC5NJboIEW`) ya usada y probada en Fase 1. Crearlo ahí evita provisionar una credencial nueva en N8N.

**Nombre propuesto del spreadsheet:** `FITS CV Reformatting - Log de Procesamiento`
**Nombre de la pestaña:** `Log`

## Columnas

| # | Columna | Tipo | Notas |
|---|---|---|---|
| 1 | `timestamp` | datetime | Zona horaria `America/Puerto_Rico`. Momento en que Módulo 3 termina de procesar (no el momento del trigger). |
| 2 | `candidateId` | string | ID de JazzHR. |
| 3 | `candidateName` | string | |
| 4 | `jobId` | string | ID del job posting en JazzHR. |
| 5 | `jobTitle` | string | |
| 6 | `workflowName` | string | Ej. "JNJ - Workflow 2024" — ver `../conocimiento/jazzhr-stepids-convert-resume.md`. |
| 7 | `stageName` | string | Nombre de la etapa tal como viene de JazzHR (puede variar entre workflows, ver hallazgo en el archivo de arriba). |
| 8 | `format` | string | `New Format` / `Non Template` / `BD Format` — derivado del `step_id`, no del nombre de la etapa. |
| 9 | `sourceLanguage` | string | De `_meta.source_language` del JSON canónico (`cv-schema.json`). |
| 10 | `translated` | boolean | De `_meta.translated`. |
| 11 | `docxFileName` | string | Nombre del archivo final subido a SharePoint. |
| 12 | `sharepointUrl` | string | `webUrl` devuelto por Microsoft Graph al subir. |
| 13 | `emailSent` | boolean | |
| 14 | `resultado` | string | Uno de: `OK`, `ERROR_EXTRACCION`, `ERROR_LLM`, `ERROR_RENDER`, `ERROR_UPLOAD`, `ERROR_EMAIL`. |
| 15 | `errorDetail` | string | Mensaje de error si `resultado != OK`. Vacío en caso de éxito. |
| 16 | `durationSec` | number | Desde la detección del poller hasta el fin de Módulo 3 — mide el criterio de aceptación de tiempo. |
| 17 | `promptVersion` | string | De `_meta.prompt_version` — trazabilidad de qué versión del prompt generó el resultado. |
| 18 | `executionId` | string | ID de la ejecución de N8N — para ir directo al log técnico si hay que auditar un caso. |
| 19 | `reviewStatus` | string | Vacío al crear la fila. Paola lo completa manualmente: `Approved` / `Rejected`. |
| 20 | `reviewComment` | string | Comentario de Paola si `reviewStatus = Rejected`. |

Las columnas 19-20 son las que convierten este log en el instrumento de medición del criterio "≥90% de aprobación humana del Summary" (Módulo 2) — Paola las completa después de recibir el `.docx`, y de ahí sale la evidencia para el Acta de Aceptación.

## Cómo se escribe

Una sola fila por candidato procesado (éxito o error), escrita al final de Módulo 3 (o apenas se detecta el error, en las ramas de falla). **Nunca en lote** — la cuota de Google Sheets (60 lecturas/min por usuario) ya se agotó una vez en Fase 1 con volumen mucho mayor; aquí el volumen es bajo (un candidato a la vez desde el poller), así que no debería repetirse, pero se escribe con `executeOnce` y sin reintentos automáticos (`retryOnFail: false`) para no duplicar filas.

## Pendiente — crear el Sheet real

No lo creé todavía. Dos formas de hacerlo, a elección:

1. **Tú lo creas manualmente** en Drive con la cuenta `fitsscreening@gmail.com`, con estas 20 columnas como encabezado, y me pasas el Sheet ID.
2. **Se crea desde N8N** con un nodo Google Sheets temporal usando la credencial `vuAQyDYC5NJboIEW` ya existente (evita que yo necesite acceso a esa cuenta de Google).

No lo genero con mi propia sesión de Google Drive porque quedaría bajo una cuenta distinta a `fitsscreening@gmail.com`, rompiendo el punto de reusar la credencial ya provista en N8N.
