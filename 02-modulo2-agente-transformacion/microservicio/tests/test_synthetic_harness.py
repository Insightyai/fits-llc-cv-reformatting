import os
import pathlib
import re
import sys
import time
from datetime import date

import pytest

from agent import transform
from extract import extract_text

# Fase 5 del plan del agente (ver agente/CONTRATO-AGENTE.md): harness con CVs
# sinteticos para medir las 4 reglas de contenido del PRD sin depender del set
# real de 15-20 CVs de FITS (Fase 7, todavia no entregado). Marcado `llm`
# porque gasta tokens reales -- opt-in via `pytest -m llm`.
pytestmark = pytest.mark.llm

FIXTURES_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "cvs-prueba"
    / "sinteticos"
)
NOW = date(2026, 7, 30)

# Presupuesto interno para la llamada a Claude sola (extract + transform), no
# el pipeline completo. El criterio del PRD (<3 min desde el trigger de N8N
# hasta el .docx final) todavia no se puede medir de punta a punta -- Fase 6
# no esta wireada. /render toma <1s (ver smoke_test.py); este umbral deja
# ~2 min de margen para JazzHR + N8N + /render en la Fase 6.
SLA_BUDGET_SECONDS = 60

I_STATEMENT_RE = re.compile(r"\bI\b|\bmy\b|\bme\b|\bmine\b")


def _all_text(cv):
    parts = [cv["summary"]]
    for job in cv["experience"]:
        parts.extend(job["bullets"])
    return " ".join(parts)


def _run(filename, api_key):
    data = (FIXTURES_DIR / filename).read_bytes()
    extracted = extract_text(filename, data)
    t0 = time.monotonic()
    cv, usage, state = transform(
        extracted.text, NOW, api_key=api_key, extract_warnings=extracted.warnings
    )
    elapsed = time.monotonic() - t0
    print(
        f"\n--- {filename}: {elapsed:.1f}s, estado={state}, "
        f"warnings={cv['_meta']['warnings']} ---",
        file=sys.stderr,
    )
    return cv, state, elapsed


@pytest.fixture
def api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY no esta seteada")
    return key


def test_espanol_objetivo_primera_persona(api_key):
    cv, state, elapsed = _run("01-espanol-objetivo-primera-persona.txt", api_key)

    assert elapsed < SLA_BUDGET_SECONDS
    assert state in ("ok", "review")  # nunca "failed" -- ver comentario del modulo

    assert cv["_meta"]["translated"] is True
    assert any(w.startswith("SUMMARY_FROM_OBJECTIVE") for w in cv["_meta"]["warnings"])

    text = _all_text(cv)
    assert not I_STATEMENT_RE.search(text)  # regla 2: tercera persona

    lowered = text.lower()
    spanish_markers = ["realice", "documente", "capacite", "elabore", "mantuve", "busco"]
    for marker in spanish_markers:
        # \b evita falsos positivos por substring (ej. "documente" dentro de
        # "documenting" en ingles)
        assert not re.search(rf"\b{marker}\b", lowered)  # regla 1: nada del original en espanol sobrevive


def test_ingles_i_statements_summary_bueno(api_key):
    cv, state, elapsed = _run("02-ingles-i-statements-summary-bueno.txt", api_key)

    assert elapsed < SLA_BUDGET_SECONDS
    assert state in ("ok", "review")

    assert cv["_meta"]["translated"] is False  # ya estaba en ingles

    text = _all_text(cv)
    assert not I_STATEMENT_RE.search(text)  # regla 2 aplicada a cada bullet

    # senal blanda: el summary original ya era profesional, no deberia marcarse
    # para reescritura (a diferencia de la aprobacion de calidad en si, esto
    # solo verifica que el codigo de warning no se dispare de mas)
    assert not any(w.startswith("SUMMARY_REWRITTEN") for w in cv["_meta"]["warnings"])


def test_ingles_objective_sin_i_statements(api_key):
    cv, state, elapsed = _run("03-ingles-objective-sin-i-statements.txt", api_key)

    assert elapsed < SLA_BUDGET_SECONDS
    assert state in ("ok", "review")

    assert any(w.startswith("SUMMARY_FROM_OBJECTIVE") for w in cv["_meta"]["warnings"])
    assert "challenging position" not in cv["summary"].lower()  # no copiado literal

    text = _all_text(cv)
    assert not I_STATEMENT_RE.search(text)


def test_ingles_summary_pobre(api_key):
    cv, state, elapsed = _run("04-ingles-summary-pobre.txt", api_key)

    assert elapsed < SLA_BUDGET_SECONDS
    assert state in ("ok", "review")

    assert any(w.startswith("SUMMARY_REWRITTEN") for w in cv["_meta"]["warnings"])
    assert "hardworking person" not in cv["summary"].lower()  # no copiado literal

    text = _all_text(cv)
    assert not I_STATEMENT_RE.search(text)


def test_ingles_skills_narrativo_sin_lista(api_key):
    # Caso real: Patrick Santiago Cintron (27 ago 2026) -- un CV cuyo "SKILLS SUMMARY"
    # es un parrafo narrativo, sin lista de items. Antes de este fix el agente inferia
    # una lista parafraseando el parrafo (ej. "Teamwork", "Computer Proficiency",
    # "Adaptability"), y como esos tokens nunca aparecen literales en la fuente,
    # GROUNDING_TOKEN_NOT_FOUND bloqueaba el CV entero como failed. Riesgo ya
    # anticipado en la Fase 5 (30 jul, ver Decisiones.md) -- este es el primer caso
    # real que lo confirma. Fix: cv-schema.json + el prompt ahora instruyen dejar
    # skills:[] vacio en vez de inferir.
    cv, state, elapsed = _run("05-ingles-skills-narrativo-sin-lista.txt", api_key)

    assert elapsed < SLA_BUDGET_SECONDS
    assert state in ("ok", "review")  # nunca "failed" por skills inferidos
    assert cv["skills"] == []
