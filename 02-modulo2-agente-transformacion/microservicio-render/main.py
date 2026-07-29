import io
import json
import os
from email.utils import encode_rfc2231
from pathlib import Path

import jsonschema
from docxtpl import DocxTemplate
from docx import Document
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from blocks import CONTEXT_BUILDERS, strip_empty_paragraphs

BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR.parent

SCHEMA_PATH = MODULE_DIR / "contrato-datos" / "cv-schema.json"
TEMPLATES_DIR = MODULE_DIR / "templates" / "anotados"

TEMPLATES = {
    "new_format": TEMPLATES_DIR / "New Format Resume Template.docx",
    "non_template": TEMPLATES_DIR / "Non Template Resume.docx",
    "bd_format": TEMPLATES_DIR / "BD - Resume Template.docx",
}

API_KEY = os.environ.get("API_KEY")
MAX_BODY_BYTES = int(os.environ.get("MAX_BODY_BYTES", 2_000_000))

app = FastAPI(title="CV Reformatting — Microservicio de Render")


@app.on_event("startup")
def load_schema_and_check_templates():
    if not API_KEY:
        raise RuntimeError("API_KEY no está configurada — obligatoria para arrancar el servicio.")
    if not SCHEMA_PATH.exists():
        raise RuntimeError(f"No se encontró cv-schema.json en {SCHEMA_PATH}")
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        app.state.cv_schema = json.load(f)
    missing = [name for name, path in TEMPLATES.items() if not path.exists()]
    if missing:
        raise RuntimeError(f"Templates configurados pero no encontrados en disco: {missing}")


@app.middleware("http")
async def enforce_max_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None and int(content_length) > MAX_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"error": f"Cuerpo del request excede el límite de {MAX_BODY_BYTES} bytes."},
        )
    return await call_next(request)


def check_api_key(x_api_key: str = Header(default=None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="X-API-Key inválida o ausente.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/render")
async def render(request: Request, x_api_key: str = Header(default=None)):
    check_api_key(x_api_key)

    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Body no es JSON válido.")

    template_id = body.get("template")
    cv = body.get("cv")

    if template_id not in TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"template debe ser uno de: {sorted(TEMPLATES.keys())}",
        )
    if not isinstance(cv, dict):
        raise HTTPException(status_code=400, detail="Falta el campo 'cv' (objeto JSON).")

    try:
        jsonschema.validate(cv, app.state.cv_schema)
    except jsonschema.ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"cv no cumple cv-schema.json en '{'.'.join(str(p) for p in e.path)}': {e.message}",
        )

    template_path = TEMPLATES[template_id]
    try:
        context = CONTEXT_BUILDERS[template_id](cv)
        tpl = DocxTemplate(str(template_path))
        tpl.render(context, autoescape=True)
        buffer = io.BytesIO()
        tpl.save(buffer)
        buffer.seek(0)
        rendered_doc = Document(buffer)
        strip_empty_paragraphs(rendered_doc)
        buffer = io.BytesIO()
        rendered_doc.save(buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Fallo al renderizar el .docx.")

    buffer.seek(0)
    output_bytes = buffer.read()

    try:
        Document(io.BytesIO(output_bytes))
    except Exception:
        raise HTTPException(status_code=500, detail="El .docx generado no pasó la verificación de integridad.")

    filename = f"{cv.get('full_name', 'resume')}.docx"
    ascii_fallback = filename.encode("ascii", errors="replace").decode("ascii")
    encoded = encode_rfc2231(filename, charset="utf-8")
    content_disposition = f'attachment; filename="{ascii_fallback}"; filename*={encoded}'

    return Response(
        content=output_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": content_disposition},
    )
