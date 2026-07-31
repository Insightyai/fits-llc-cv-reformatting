# Microservicio de Render + Agente de Transformación — CV Reformatting

Aloja dos responsabilidades: `POST /render` recibe el JSON canónico (`cv-schema.json`) y genera el `.docx` final con `docxtpl`; `POST /transform` recibe el CV original (PDF/DOCX/texto) y lo transforma a ese mismo JSON canónico vía Claude (`agent.py`). Corre en Railway; N8N no puede generar `.docx` ni correr la suite de validación/grounding (bloquea `zlib`/`require()` y no tiene pytest).

**Estado: Fase 4.** `/render` completo desde Fase 3 (los 3 templates renderizan contenido real vía HTTP, con bullets separados y sangría francesa). `/transform` agregado en Fase 4: extrae texto (`extract.py`), llama a Claude con tool use estricto (`agent.py`), corre el grounding check (`grounding.py`) y devuelve `{state, cv, usage}` o un error 422 con `{state: "failed", code, detail}`. Corre la llamada a Claude en un threadpool (`run_in_threadpool`) para no bloquear `/render` en el mismo proceso. Límite de tamaño de body propio por ruta (`MAX_BODY_BYTES` para `/render`, `MAX_TRANSFORM_BODY_BYTES` para `/transform`). **Pendiente, no de código:** confirmación visual de FITS/Paola sobre `summary_skills_block` de BD Format y sobre la sangría en general; deploy a Railway; wiring en N8N (Fase 6) — ver `seguimiento/bitacora.md`.

## Correr localmente

```bash
cd 02-modulo2-agente-transformacion/microservicio
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar API_KEY y ANTHROPIC_API_KEY
export $(cat .env | xargs)
uvicorn main:app --reload
```

## Endpoints

- `GET /health` — sin auth, para el healthcheck de Railway.
- `POST /render` — requiere header `X-API-Key`. Body:
  ```json
  { "template": "new_format" | "non_template" | "bd_format", "cv": { ...cv-schema.json... } }
  ```
  Devuelve el `.docx` (bytes) o un error JSON:
  - `400` — `template` inválido, body no es JSON, o falta `cv`.
  - `401` — `X-API-Key` ausente o incorrecta.
  - `413` — body excede `MAX_BODY_BYTES` (default 2 MB).
  - `422` — `cv` no cumple `cv-schema.json` (incluye el path del campo que falló).
  - `500` — falla al renderizar o el `.docx` generado no pasó la verificación de integridad (se reabre con `python-docx` antes de responder).
- `POST /transform` — requiere header `X-API-Key`. Body:
  ```json
  { "filename": "cv.pdf", "content_base64": "..." }
  ```
  Devuelve `{ "state": "ok" | "review", "cv": {...cv-schema.json...}, "usage": {"input_tokens": N, "output_tokens": N} }` o un error JSON:
  - `400` — body no es JSON, faltan `filename`/`content_base64`, o `content_base64` no es base64 válido.
  - `401` — `X-API-Key` ausente o incorrecta.
  - `413` — body excede `MAX_TRANSFORM_BODY_BYTES` (default 8 MB).
  - `422` — `{"state": "failed", "code": ..., "detail": ...}`. `code` es uno de los de `ExtractionError` (`NO_TEXT_LAYER`, `CORRUPT_FILE`) o de `TransformError` (`SCHEMA_INVALID`, `GROUNDING_FAILED`, `OUTPUT_TRUNCATED`, `NO_TOOL_USE`) — ver `agente/CONTRATO-AGENTE.md`. Nunca incluye `cv`.

## Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `API_KEY` | (obligatoria, sin default) | El servicio no arranca si falta. |
| `ANTHROPIC_API_KEY` | (obligatoria, sin default) | El servicio no arranca si falta — usada por `/transform` para llamar a Claude. |
| `MAX_BODY_BYTES` | `2000000` | Límite de tamaño del body de `/render`. |
| `MAX_TRANSFORM_BODY_BYTES` | `8000000` | Límite de tamaño del body de `/transform` (más alto: incluye el CV en base64, ~33% más pesado que el archivo original). |
| `PORT` | (la fija Railway) | Puerto de `uvicorn`, ver `Procfile`. |

## Fixtures de prueba

`../contrato-datos/fixtures/shirley-mercado.json` y `adversarial.json` — ver `TAG-CONTRACT.md` para el contrato de tags y la evidencia del spike de indentación de bullets.
