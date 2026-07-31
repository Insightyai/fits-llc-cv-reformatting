import json
import pathlib

CV_SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "contrato-datos" / "cv-schema.json"
)

TOOL_NAME = "emit_cv"


def _union_to_anyof(node):
    """La API de tool use no soporta 'type': [...] (union). cv-schema.json lo usa en
    los 4 campos nullable (town, years_experience, experience[].location,
    education[].period) -- se convierte a anyOf, recursivamente en todo el schema."""
    if isinstance(node, dict):
        if isinstance(node.get("type"), list):
            types = node.pop("type")
            node["anyOf"] = [{"type": t} for t in types]
        for value in node.values():
            _union_to_anyof(value)
    elif isinstance(node, list):
        for item in node:
            _union_to_anyof(item)


def build_input_schema():
    """Deriva el input_schema de la tool `emit_cv` a partir de cv-schema.json.
    Transformador, no copia (ver agente/CONTRATO-AGENTE.md): cv-schema.json sigue
    siendo la unica fuente de verdad -- un test (test_tool_schema.py) falla si el
    schema gana un campo union-type nuevo sin pasar por aca."""
    schema = json.loads(CV_SCHEMA_PATH.read_text(encoding="utf-8"))
    schema.pop("$schema", None)
    schema.pop("$id", None)
    schema.pop("title", None)

    # _meta.prompt_version lo sobrescribe siempre Python (nunca lo declara el LLM) --
    # se saca de required, pero el campo se mantiene en properties: el LLM debe
    # seguir devolviendolo, forzado a null (ver descripcion de la tool).
    meta = schema["properties"]["_meta"]
    meta["required"] = [f for f in meta["required"] if f != "prompt_version"]

    _union_to_anyof(schema)
    return schema


def build_tool_definition():
    return {
        "name": TOOL_NAME,
        "description": (
            "Emite el CV transformado como JSON canonico segun cv-schema.json. "
            "years_experience y _meta.prompt_version se calculan/sobrescriben "
            "siempre en Python despues -- devuelve ambos como null, nunca inventes "
            "un valor para ninguno de los dos."
        ),
        "input_schema": build_input_schema(),
        "strict": True,
    }
