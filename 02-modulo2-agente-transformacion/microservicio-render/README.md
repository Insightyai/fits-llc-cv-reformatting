# Microservicio de Render — CV Reformatting

Recibe el JSON canónico del agente de transformación (`cv-schema.json`) y genera el `.docx` final con `docxtpl`. Corre en Railway; N8N no puede generar `.docx` (bloquea `zlib`/`require()` en el Code node).

**Estado: Fase 3.** Auth, límites de tamaño, validación de schema, manejo de errores y verificación de integridad del `.docx` de salida (Fase 1); los 3 templates re-anotados según `TAG-CONTRACT.md` (Fase 2); `blocks.py` (builders de `RichText` por template) conectado al endpoint `/render` vía `CONTEXT_BUILDERS` (Fase 3) — los 3 templates (`new_format`, `non_template`, `bd_format`) renderizan contenido real vía HTTP, con bullets separados y sangría francesa. **Pendiente, no de código:** confirmación visual de FITS/Paola sobre `summary_skills_block` de BD Format (mezcla texto corrido + lista con viñeta en un mismo párrafo, ver nota abierta en `TAG-CONTRACT.md`) y sobre la sangría en general — ver `seguimiento/bitacora.md`.

## Correr localmente

```bash
cd 02-modulo2-agente-transformacion/microservicio-render
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar API_KEY
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

## Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `API_KEY` | (obligatoria, sin default) | El servicio no arranca si falta. |
| `MAX_BODY_BYTES` | `2000000` | Límite de tamaño del body de `/render`. |
| `PORT` | (la fija Railway) | Puerto de `uvicorn`, ver `Procfile`. |

## Fixtures de prueba

`../contrato-datos/fixtures/shirley-mercado.json` y `adversarial.json` — ver `TAG-CONTRACT.md` para el contrato de tags y la evidencia del spike de indentación de bullets.
