# Contrato del Agente de Transformación AI

> Fase 0 del plan de implementación (planner + auditoría de Opus, 30 jul 2026). Fija por escrito, antes de escribir código, los estados de salida, el catálogo de warnings, los campos que Python sobrescribe siempre y los criterios pendientes de confirmar con FITS. Reemplaza las menciones sueltas a "Fase 3.1/3.2/3.3" de `cv-schema.json` y `conocimiento/reglas-por-formato.md` (un plan anterior que nunca se escribió) — las fases correctas son las de este documento y de `Decisiones.md`.

## Arquitectura (decidido)

El agente corre como código Python nuevo dentro del mismo servicio que ya renderiza (`02-modulo2-agente-transformacion/microservicio/`, renombrado el 30 jul desde `microservicio-render/` para reflejar que aloja ambas responsabilidades), expuesto como `POST /transform`. N8N sigue orquestando: trigger, dedup, descarga del CV desde JazzHR, llamada a `/transform`, rama por estado, llamada a `/render`, entrega. Razón (ver `Decisiones.md`): la validación contra `cv-schema.json` y el grounding check necesitan tests reales (pytest); un Code node de N8N no puede correr esa suite. Detalle completo de la decisión y sus alternativas en `Decisiones.md`.

## Modelo y garantía de salida estructurada (decidido)

- **Modelo:** `claude-sonnet-5`, fijado explícitamente en `agent.py` (nunca un alias implícito heredado de Fase 1). Soporta `strict: true` en tool use.
- **`strict: true`** en la definición de la tool `emit_cv` — garantiza que `tool_use.input` valide contra el `input_schema` de la tool (no contra `cv-schema.json` directamente: ver más abajo). Con `strict`, el `jsonschema.validate` final y el retry de reparación quedan como red de seguridad, no como mecanismo principal.
- **No usar `temperature`/`top_p`/`top_k`** — eliminados en Sonnet 5/Opus 5/Fable 5; enviarlos devuelve 400.
- **No usar Sonnet 4.6** para este endpoint: no soporta `strict`.
- `tool_schema.py` deriva el `input_schema` de `cv-schema.json` en runtime (transformador, no copia): convierte `"type": ["string", "null"]` a `anyOf`, quita `$schema`/`$id`, y saca `prompt_version`/`years_experience` de `required` (Python los sobrescribe siempre — ver abajo). Un test falla si `cv-schema.json` gana un campo union-type nuevo sin pasar por el transformador.
- `stop_reason == "max_tokens"` se trata como fallo propio (`failed`, warning `OUTPUT_TRUNCATED`), no como error de schema — el retry de reparación no arregla una respuesta truncada. `max_tokens` con holgura (≥16000): en Opus 5/Sonnet 5 el thinking (activo por defecto) comparte presupuesto con la salida.

## Estados de salida

| Estado | Condición | Efecto en el pipeline |
|---|---|---|
| `ok` | Válido contra `cv-schema.json`, cero errores de grounding, cero warnings | Se renderiza y entrega sin marcar |
| `review` | Válido, cero errores, ≥1 warning en `_meta.warnings` | Gobernado por `REVIEW_BLOCKS_DELIVERY` (ver abajo) |
| `failed` | Schema inválido tras el retry de reparación, ≥1 error de grounding, `NO_TEXT_LAYER`, o `OUTPUT_TRUNCATED` | Nunca se renderiza ni se entrega. `POST /transform` responde 422 y **no** incluye `cv` en la respuesta |

## Flag `REVIEW_BLOCKS_DELIVERY`

**`false` — confirmado como definitivo (8 sep 2026).** El default original del plan (`true`, corregido el 30 jul 2026 tras el hallazgo de la auditoría de Opus sobre el fixture `shirley-mercado.json` — ver historial abajo) nunca se cableó como gate real en el `Convert Resume Processor` de N8N: en producción, un CV en estado `review` siempre se renderizó y entregó igual que uno `ok` — solo `failed` corta el pipeline (422, sin `cv` en la respuesta). Confirmado con múltiples candidatos reales entregados en `state=review` sin incidentes (Paola Maldonado Pereira, Miguel Rivera Palou, Daphne Rigual, entre otros — ver `seguimiento/bitacora.md`), y respaldado por el volumen ya acumulado de CVs reales de FITS procesados en producción (51 tests en el repo, más los casos reales caso-a-caso documentados en `bitacora.md`) — se documenta `false` para que el contrato refleje el comportamiento real medido, no un gate que nunca existió. Los datos realmente riesgosos (empresa/años/métricas inventados) siguen bloqueados como error duro (`state=failed`) por `grounding.py`, sin cambios.

**Historial:** el default `true` inicial (30 jul 2026) respondió a que el propio fixture de referencia `shirley-mercado.json` contenía una inferencia no verificada del LLM — "food **and beverage** manufacturing" no estaba en el CV original — que el diseño de grounding original no atrapaba como error; corregido ese mismo día tanto en el fixture como con el check de grounding suave de `summary` (ver Fase 3 más abajo).

## Catálogo cerrado de códigos de warning

Formato en `_meta.warnings`: `"CODIGO: detalle en español"`. No se agregan códigos nuevos sin actualizar esta tabla.

| Código | Cuándo se emite |
|---|---|
| `YEARS_EXPERIENCE_UNKNOWN` | `dates.py` no pudo calcular `years_experience` con confianza (fechas ambiguas, faltantes, o solapamiento irresoluble) |
| `AMBIGUOUS_DATES` | Un período parsea con más de una interpretación razonable (ej. formato de fecha ambiguo) |
| `NO_EDUCATION_SECTION` | El CV original no trae sección de educación |
| `TOWN_NOT_DECLARED` | El CV no declara pueblo/ciudad de residencia (`town: null` es el valor correcto, no un error) |
| `TOWN_MAY_BE_EMPLOYER_CITY` | `town` coincide con algún `experience[].location` — puede ser la ciudad de un empleador, no la residencia declarada (ver nota en `TAG-CONTRACT.md` y en `reglas-por-formato.md`) |
| `SUMMARY_FROM_OBJECTIVE` | Se aplicó la regla 3 (Objective → Summary profesional) |
| `SUMMARY_REWRITTEN` | Se aplicó la regla 4 (reescritura de summary pobre) |
| `SOURCE_TRUNCATED` | El texto extraído del CV se cortó por exceder el tope de caracteres |
| `LOW_TEXT_QUALITY` | El texto extraído se ve fragmentado (posible PDF con columnas/tablas mal ordenado) |
| `TITLE_NOT_LITERAL_IN_SOURCE` | `experience[].title` no matchea léxicamente la fuente (puede ser traducción legítima) |
| `INSTITUTION_NOT_LITERAL_IN_SOURCE` | `education[].institution` no matchea léxicamente la fuente (mismo motivo — ej. nombres de universidades traducidos) |
| `COMPANY_NOT_VERIFIABLE` | El nombre de la empresa quedó con cero tokens significativos tras normalizar (siglas cortas: 3M, BD, J&J) — no se pudo verificar ni refutar, se marca en vez de darlo por bueno |
| `UNKNOWN_FIELD_DROPPED` | El LLM devolvió una clave de nivel superior no reconocida y se descartó antes de validar |
| `EMPTY_PERIOD` | `experience[].period` o `education[].period` llegó vacío o solo espacios |
| `SECTION_COVERAGE_LOW` | El conteo heurístico de empleos en la fuente es mayor al de `experience[]` — posible omisión del LLM |
| `OUTPUT_TRUNCATED` | `stop_reason == "max_tokens"` — la respuesta del modelo se cortó antes de completar el JSON |
| `YEARS_NOT_VERIFIABLE_IN_SOURCE` | La fuente no tiene ningún año de 4 dígitos en formato `19xx`/`20xx` — el check de años de `grounding.py` no es aplicable, se marca en vez de omitirse en silencio |
| `SUMMARY_CLAIM_NOT_VERIFIED` | Un sustantivo propio o término de industria del `summary` no aparece en la fuente (grounding suave, no bloquea — ver Fase 3) |
| `METRIC_NOT_VERIFIED` | Un número/porcentaje/monto de un bullet no aparece en la fuente, pero `_meta.translated == true` — degradado de error a warning porque la Regla 1 puede convertir numerales escritos en palabras a dígitos |

`NO_TEXT_LAYER` y `CORRUPT_FILE` no son warnings: son condiciones de `failed` que se detectan en `extract.py` **antes** de llamar al LLM — nunca se gasta una llamada a Claude sobre un archivo vacío o corrupto. `NO_TEXT_LAYER`: CV escaneado/imagen sin capa de texto (fuera de alcance contractual, ver PRD §4). `CORRUPT_FILE`: el archivo no se pudo parsear como PDF/DOCX (truncado, dañado), o es un formato no soportado (ej. `.doc` legacy, binario pre-2007 — detectado por firma OLE2/CFB desde el 11 ago 2026, ver `seguimiento/bitacora.md`).

## Fase 3 — Grounding check (`grounding.py`)

Checks determinísticos sobre el texto fuente ya extraído (nunca sobre datos externos). Normalización compartida (`grounding.normalize`): casefold, NFKD sin diacríticos, `&`→`and`, guiones/comillas unificados, colapso de espacios — aplicada por igual a la fuente y a los valores a verificar. Para el chequeo de `full_name` se usa además una vista **sin espacios** (`grounding.despace`): un CV real (Shirley Mercado, extraído con `pypdf`) tiene un espacio fantasma por kerning tipográfico que separa "Merc" de "ado" — comparar contra la fuente con todos los espacios colapsados es la única forma de no marcar `failed` al propio ground truth del proyecto.

**Errores (bloquean, producen `failed`):**

| Código | Chequeo |
|---|---|
| `GROUNDING_NAME_NOT_FOUND` | Algún token (≥3 chars) de `full_name` no aparece en la fuente (vista sin espacios) |
| `GROUNDING_TOKEN_NOT_FOUND` | `experience[].company` (o `certifications[]`/`skills[]`, mismo chequeo) tiene ≥1 token significativo (≥3 chars, sin sufijos legales ni stopwords) y ninguno aparece en la fuente. Se probó exigir que **todos** aparecieran (26 ago 2026) pero se revirtió el 27 ago — ver nota abajo. Si el conjunto de tokens significativos queda vacío (siglas cortas: 3M, BD, J&J) **no** es error — pasa a warning `COMPANY_NOT_VERIFIABLE` |
| `GROUNDING_YEAR_NOT_FOUND` | Un año de 4 dígitos (`19xx`/`20xx`) en `experience[].period` o `education[].period` no está en el multiset de años de la fuente (que excluye dígitos de teléfonos) |
| `GROUNDING_METRIC_NOT_FOUND` | Un número/porcentaje/monto en un bullet no aparece en la fuente, **solo si `_meta.translated == false`** (si es `true`, la Regla 1 de traducción puede convertir números escritos en palabras a dígitos — ahí es warning, no error) |
| `GROUNDING_I_STATEMENT` | `\bI\b`/`\bmy\b`/`\bme\b`/`\bmine\b` en `summary` o algún bullet, **excepto** la lista de excepciones de dominio (`Phase I`, `Level I`, `Class I`, `Type I`, `Operator I`, `Part I`, `I/O`) y `ME` en mayúsculas (Maine/Mechanical Engineering) |
| `GROUNDING_TOWN_NOT_FOUND` | `town` no nulo y no aparece en la fuente |

**Warnings nuevos que agrega `grounding.py`** (todos en la tabla del catálogo, arriba): `COMPANY_NOT_VERIFIABLE`, `TOWN_MAY_BE_EMPLOYER_CITY`, `TITLE_NOT_LITERAL_IN_SOURCE`, `INSTITUTION_NOT_LITERAL_IN_SOURCE`, `SECTION_COVERAGE_LOW`, `EMPTY_PERIOD`, `YEARS_NOT_VERIFIABLE_IN_SOURCE`, `SUMMARY_CLAIM_NOT_VERIFIED`, `METRIC_NOT_VERIFIED`.

`certifications[]` y `skills[]` usan el mismo chequeo de tokens que `company` (error si hay tokens significativos y ninguno aparece; warning `COMPANY_NOT_VERIFIABLE` — mismo código, reutilizado — si el conjunto queda vacío).

**Riesgo encontrado por el harness de la Fase 5 (30 jul 2026), resuelto con un caso real el 27 ago 2026:** si el CV original no trae una sección de Skills explícita, el modelo a veces infería una lista parafraseando la experiencia — y como el chequeo de `skills[]` exige token exacto (sin stemming ni tolerancia a paráfrasis, a diferencia del tratamiento "soft" de `title`/`institution`), esa lista inferida se marcaba `failed`. Confirmado con un candidato real (Patrick Santiago Cintrón, 27 ago) y resuelto por instrucción explícita en `cv-schema.json`/`prompt/transform-v1.md`: el agente ahora deja `skills: []` vacío en vez de inferir. Detalle completo, incluida la opción descartada (tolerancia "soft" en `grounding.py`) y por qué, en `Decisiones.md`, 30 jul y 27 ago 2026.

**Bug real encontrado y corregido (14 ago 2026, candidato real de FITS — Luis Antonio García Sánchez, New Format):** `GROUNDING_TOKEN_NOT_FOUND` bloqueaba skills de una sola palabra (`Excel`, `Matlab`, `JMP`, `SolidWorks`) que sí estaban literalmente en la fuente. Causa: `significant_tokens()`/`source_words` tokenizaban el texto fuente con `.split()` (solo espacios en blanco), así que la puntuación pegada a una palabra sin espacio ("Excel," al final de una lista, o incluso dos skills pegadas entre sí sin ningún espacio — "JMP,SolidWorks", como vino este CV real) quedaba dentro del mismo token y nunca matcheaba el valor limpio que devuelve el agente. Como estas 4 skills eran de una sola palabra, no tenían ningún token alternativo de respaldo (a diferencia de `company`/`certifications` con varias palabras, donde basta que UNA coincida) y el chequeo las rechazaba como si no aparecieran en la fuente. Corregido tokenizando con un split por regex (`[^\w]+`, no solo espacios) tanto en `significant_tokens()` como en la construcción de `source_words` y en `_check_summary_claims()` — separa cualquier palabra de la puntuación que tenga pegada, sea al borde o en el medio. Test de regresión con el patrón exacto del CV real en `tests/test_grounding.py`. 75 tests en verde tras el fix.

**Segundo bug real, mismo día, encontrado con un candidato real ya en producción (14 ago 2026, etapa BD Format):** `GROUNDING_METRIC_NOT_FOUND` bloqueaba el número `'14001'` de un bullet sobre certificación ISO, aunque el dato es real. Causa: `pypdf` extrajo el texto fuente como "ISO 14 001" (espacio fantasma en medio del número, mismo tipo de artefacto de kerning tipográfico ya conocido en este documento para nombres — ver la nota de `full_name`/`Merc·ado` de Shirley Mercado más arriba, sección "Chequeos determinísticos"). `extract_metrics()` corta el número en `"14"` y `"001"` como dos valores separados, así que el `"14001"` limpio que escribe el agente nunca matchea contra el set de métricas de la fuente. Corregido reusando el mismo mecanismo ya existente para `full_name` (`despace()`, la fuente sin ningún espacio): `_check_metrics()` ahora acepta el match si el número aparece en el set exacto **o** como substring de la fuente despaciada. Diagnosticado comparando el CV real (`api.jazz.co`) contra el texto que efectivamente extrae `extract.py` — confirmó que el número sí está en el original, solo mal segmentado por la extracción. Test de regresión con el patrón exacto en `tests/test_grounding.py`. 76 tests en verde tras el fix. **De paso se confirmó un rechazo legítimo, no un bug:** el mismo día, otro candidato real (Ruth Sotomayor Clavell, re-procesada en etapa New Format) fue bloqueada por `GROUNDING_TOKEN_NOT_FOUND: skill='Competitive drive'` — se verificó contra su CV real que esa frase no aparece en ningún lado; el agente la inventó/parafraseó, y el chequeo funcionó como debía (mismo riesgo ya documentado arriba, harness de Fase 5).

**Batch de fixes de la auditoría de Codex del 24 ago, aplicado el 26 ago 2026 (sin candidato real involucrado, TDD puro contra el fixture de Shirley Mercado):** de los 21 hallazgos de la auditoría (ver `seguimiento/bitacora.md`, 24 ago), se aplicaron 5, en orden de prioridad:
1. **`_check_source_backed` (mecanismo de `GROUNDING_TOKEN_NOT_FOUND`) usaba `any()` sobre los tokens significativos** — bastaba que UNO de los tokens de una empresa/certificación/skill de varias palabras coincidiera con la fuente para pasar, aunque el resto fuera inventado (ej. compañía real + "Analytics" agregado por el LLM pasaba sin error). Cambiado a `all()` el 26 ago. **Revertido a `any()` el 27 ago 2026** — ver la nota completa más abajo, "Fix revertido en menos de 24h".
2. **`_check_metrics` contra `source_despaced` era un substring sin límites** (efecto colateral del fix de ISO 14001 del 14 ago) — una métrica inventada que casualmente fuera substring de un número más largo y contiguo de la fuente (ej. "500" dentro de "1500") pasaba sin error. Acotado con `(?<!\d)...(?!\d)` para que el número no quede pegado a otro dígito, sin romper el caso ISO 14001 original (que sigue con test de regresión).
3. **`dates.combine_periods` podía combinar el inicio de un rol con fin no interpretable con el fin de un rol completamente distinto** — start y end de un mismo período ahora deben parsear juntos antes de que ese período contribuya al rango combinado (antes, un período con inicio válido pero fin basura igual prestaba su inicio a la combinación).
4. **`agent.py` pisaba el `usage` de la primera llamada con el del retry de reparación de schema** — subreportaba tokens reales exactamente en el caso más caro (dos llamadas completas al modelo). Ahora se suman.
5. **Batch de `main.py` sin riesgo de regresión:** JSON válido pero no-objeto (array/null) devuelve 400 en vez de 500; `Content-Length` no numérico ya no crashea el middleware; comparación de `X-API-Key` con `hmac.compare_digest` (constant-time); `full_name` sanitizado (sin `\r\n`/caracteres de control) antes de ir al header `Content-Disposition`.

**No aplicado en este batch, decisión explícita de Santiago:** degradar `GROUNDING_METRIC_NOT_FOUND` a error incluso en CVs traducidos (línea `translated`) — se deja como está (documentado arriba) hasta medir con el set real de FITS (Fase 7) si el LLM abusa de esa regla para colar números inventados; no hay evidencia real todavía. Tampoco se tocó `extract.py` (tablas ignoradas en `_extract_docx`) — pendiente de confirmar con un CV real de FITS que use tablas de layout antes de invertir tiempo. 86 tests en verde tras el batch (más 6 marcados `llm`, opt-in, sin correr).

**Fix del punto 1 revertido en menos de 24h — el "riesgo teórico" anotado arriba resultó real, confirmado con 3 candidatos reales (27 ago 2026):** al revisar el log real de producción (`seguimiento/bitacora.md`, ver entrada del 27 ago) se encontraron 3 fallos permanentes de `GROUNDING_FAILED` sin investigar (candidatos Deanceshka Rivera, Eric Alemán Marrero, Miguel Rivera Palou). Se descargaron los 3 CVs reales vía `api.jazz.co` y se corrió el pipeline completo en local (llamada real a Claude) tanto con `all()` como, tras el hallazgo, con `any()` revertido. Con `all()`, los 3 candidatos fallaban con muchos más motivos que los registrados originalmente en el Sheet, y al menos 2 de ellos eran **parafraseo legítimo del LLM, no alucinación**: la fuente de Deanceshka dice literalmente *"Validation Life Cycle (URS, DS, IQ, OQ, PQ pro[tocol]..."* pero el LLM escribió la skill como `"URS, DS, IQ, OQ, PQ Protocol Development"` — "development" no aparece exactamente así, y con `all()` eso solo bastaba para bloquear todo el CV. Mismo patrón con Miguel Rivera Palou: `"Electrical Installations Oversight"` vs. fuente que solo dice "electrical" (substation, rooms) — sin "installations" ni "oversight" en esa forma. **Revertido a `any()` el mismo día.** El boquete original que motivó el cambio (alucinación parcial en nombres de varias palabras) sigue sin evidencia real de haber ocurrido nunca en producción — se prioriza el daño real y confirmado (falsos positivos que bloquean el envío) sobre el riesgo teórico.

**Hallazgos incidentales de esta misma revisión, ambos confirmados como falsos positivos reales (no alucinaciones) en una segunda pasada, sin resolver, anotados para Fase 7 o una sesión dedicada:**
- **Bug de tokenización nuevo, distinto al ya corregido el 14 ago:** en el CV de Eric Alemán Marrero, `pypdf` extrajo `"JD EdwardsMAX MRP II system"` sin ningún espacio entre "Edwards" y "MAX" (dos palabras alfabéticas reales pegadas, sin puntuación de por medio) — el split por regex `[^\w]+` no las separa porque no hay ningún caracter no-alfanumérico entre ellas. `GROUNDING_TOKEN_NOT_FOUND: skill='JD Edwards'` es un rechazo **incorrecto** de un dato real, con `any()` y con `all()` por igual (no relacionado al fix de este día). Sin investigar la causa (¿layout de columnas del PDF, fuente/kerning específico?) ni corregir.
- **`company='Latitud Perfecta, LLC'` del mismo candidato — no es alucinación, confirmado con búsqueda exhaustiva:** la fuente real dice `"LATITUD PRFECTA, LLC"` (falta la "E" — typo real del propio candidato en el nombre de su empleador). El LLM transcribió el nombre corregido ortográficamente, y el chequeo de token exacto lo bloqueó como si fuera inventado. Familia de falso positivo distinta a las ya conocidas (kerning fantasma, palabras pegadas): un error tipográfico real del documento fuente que el LLM corrige razonablemente. Sin fix, sin evidencia todavía de qué tan frecuente es este patrón.

## Campos que Python sobrescribe siempre, ignorando lo que devuelva el LLM

- **`_meta.prompt_version`** — derivado del nombre + hash del archivo `prompt/transform-v1.md`, nunca declarado por el modelo (que no debe poder auditarse a sí mismo).
- **`years_experience`** — el tool schema fuerza al LLM a devolver siempre `null` en este campo; `dates.py` lo calcula de forma determinística en Python a partir de `experience[]` ya extraído.

## Criterio v1 de `years_experience`

Suma de los períodos de `experience[]` sin solapamiento, a partir de fechas explícitas. "Present"/"Current"/"Actualidad"/"a la fecha" se resuelve contra una fecha de ejecución **inyectable** (parámetro `now` en toda la cadena de `dates.py`; nunca `datetime.now()` embebido — necesario porque el propio fixture de Shirley Mercado solo da `"4"` entre abril 2026 y marzo 2027; fuera de esa ventana el resultado cambia y un test sin `now` congelado se rompería solo con el paso del calendario). Redondeo hacia abajo. **Formato: solo el número en string (ej. `"4"`), sin el sufijo `+`** — el `.docx` ya agrega el `"+ YRS. OF EXP."` de forma literal (ver `templates/TAG-CONTRACT.md`; bug de doble `+` corregido el 30 jul 2026, ver `Decisiones.md`). Si algún período no parsea o hay ambigüedad irresoluble → `null` + `YEARS_EXPERIENCE_UNKNOWN`, nunca un número inventado.

**Confirmado (8 sep 2026):** el criterio real es la suma de todos los períodos de `experience[]` (sin distinción de campo/industria), calculada por Python — nunca lo que el candidato declara como total en el CV original. Coincide con lo que ya implementa `dates.py`, sin cambio de código.

## Estilo de tercera persona (confirmado, 8 sep 2026)

Impersonal, sin pronombres, verbo primero — "Managed a team of 5", no "He/She managed a team of 5". Es el estilo que ya usa `fixtures/shirley-mercado.json` (ground truth validado) y queda como definitivo: ya cumple el requisito de FITS de tercera persona (sin "I", primera persona) sin el riesgo de inferir mal el género del candidato con "He/She" — dato no siempre explícito en el CV fuente. Sin cambio de código.

## Qué NO cubre este documento

Los umbrales numéricos exactos de cada check de grounding (ej. cobertura ≥80% para empresas, longitud mínima de token) viven como constantes documentadas en `grounding.py`, no acá — este contrato fija la severidad (error vs. warning) y el código de cada uno, no el umbral fino.
