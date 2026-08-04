import hashlib
import json
import pathlib

import anthropic
import jsonschema

import dates
import grounding
from tool_schema import TOOL_NAME, build_tool_definition

BASE_DIR = pathlib.Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompt" / "transform-v1.md"
CV_SCHEMA_PATH = BASE_DIR / "contrato-datos" / "cv-schema.json"

MODEL = "claude-sonnet-5"
MAX_TOKENS = 16000


class TransformError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _prompt_version():
    digest = hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()[:12]
    return f"{PROMPT_PATH.stem}-{digest}"


def _system_prompt(now):
    return PROMPT_PATH.read_text(encoding="utf-8").replace("{{now}}", now.isoformat())


def _load_cv_schema():
    return json.loads(CV_SCHEMA_PATH.read_text(encoding="utf-8"))


def _call_claude(client, system, cv_text, repair_note=None):
    tool = build_tool_definition()
    user_content = f"CV original:\n\n{cv_text}"
    if repair_note:
        user_content += (
            "\n\n---\nTu respuesta anterior no cumplio el schema:\n"
            f"{repair_note}\nCorregi y volve a invocar la tool completa."
        )

    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=[{"role": "user", "content": user_content}],
    )

    if resp.stop_reason == "max_tokens":
        raise TransformError(
            "OUTPUT_TRUNCATED", "la respuesta del modelo se corto antes de completar el JSON"
        )

    for block in resp.content:
        if block.type == "tool_use" and block.name == TOOL_NAME:
            return block.input, resp.usage

    raise TransformError("NO_TOOL_USE", f"stop_reason={resp.stop_reason}, no vino tool_use")


def _drop_unknown_top_level_fields(cv, schema):
    known = set(schema["properties"].keys())
    extra = [k for k in cv if k not in known]
    warnings = []
    for key in extra:
        del cv[key]
        warnings.append(f"UNKNOWN_FIELD_DROPPED: campo no reconocido descartado: {key!r}")
    return warnings


def _postprocess(cv, now, schema):
    """Inserta los campos que Python siempre sobrescribe (ver CONTRATO-AGENTE.md)
    ANTES de validar -- cv-schema.json exige _meta.prompt_version, que el LLM nunca
    declara, asi que validar contra el objeto crudo del modelo fallaria siempre."""
    extra_field_warnings = _drop_unknown_top_level_fields(cv, schema)
    warnings = list(cv.get("_meta", {}).get("warnings", [])) + extra_field_warnings

    years_value, years_warnings = dates.calculate_years_experience(
        cv.get("experience", []), now
    )
    cv["years_experience"] = years_value
    warnings.extend(years_warnings)

    cv.setdefault("_meta", {})["prompt_version"] = _prompt_version()
    cv["_meta"]["warnings"] = warnings
    return cv


def transform(cv_text, now, api_key=None, client=None, extract_warnings=None):
    """Devuelve (cv: dict, usage, state) con un objeto ya valido contra cv-schema.json
    y el estado del contrato (ver agente/CONTRATO-AGENTE.md): 'ok' o 'review'.
    Lanza TransformError (nunca devuelve `failed`) si: el schema no valida tras el
    retry, el grounding encuentra >=1 error, o la respuesta se trunco."""
    schema = _load_cv_schema()
    client = client or anthropic.Anthropic(api_key=api_key)
    system = _system_prompt(now)

    cv, usage = _call_claude(client, system, cv_text)
    cv = _postprocess(cv, now, schema)

    try:
        jsonschema.validate(cv, schema)
    except jsonschema.ValidationError as exc:
        cv, usage = _call_claude(client, system, cv_text, repair_note=str(exc))
        cv = _postprocess(cv, now, schema)
        try:
            jsonschema.validate(cv, schema)
        except jsonschema.ValidationError as exc2:
            raise TransformError("SCHEMA_INVALID", str(exc2)) from exc2

    report = grounding.evaluate(cv, cv_text)
    if report.errors:
        raise TransformError("GROUNDING_FAILED", "; ".join(report.errors))

    cv["_meta"]["warnings"].extend(report.warnings)
    if extract_warnings:
        cv["_meta"]["warnings"].extend(extract_warnings)
    state = "review" if cv["_meta"]["warnings"] else "ok"
    return cv, usage, state
