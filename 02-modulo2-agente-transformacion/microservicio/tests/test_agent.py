import copy
import json
import pathlib
from datetime import date
from types import SimpleNamespace

import pytest

from agent import transform
from extract import extract_text

CV_PDF_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "cvs-prueba"
    / "Resume- Shirley Mercado.pdf"
)
FIXTURE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "contrato-datos"
    / "fixtures"
    / "shirley-mercado.json"
)


@pytest.fixture(scope="module")
def source_text():
    data = CV_PDF_PATH.read_bytes()
    return extract_text(CV_PDF_PATH.name, data).text


@pytest.fixture
def tool_output():
    """Fixture ground-truth (cero errores/warnings de grounding) sin warnings
    autodeclarados por el LLM, para aislar el efecto de extract_warnings."""
    cv = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    cv["_meta"]["warnings"] = []
    return cv


class _FakeClient:
    def __init__(self, cv_input):
        self._cv_input = cv_input
        tool_block = SimpleNamespace(type="tool_use", name="emit_cv", input=cv_input)
        self._response = SimpleNamespace(
            stop_reason="tool_use",
            content=[tool_block],
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        )
        self.messages = SimpleNamespace(create=lambda **kwargs: self._response)


def test_extract_warnings_merge_into_meta_warnings(tool_output, source_text):
    client = _FakeClient(copy.deepcopy(tool_output))

    cv, _usage, state = transform(
        source_text,
        date(2026, 7, 30),
        client=client,
        extract_warnings=["SOURCE_TRUNCATED: texto cortado a 20000 caracteres"],
    )

    assert "SOURCE_TRUNCATED: texto cortado a 20000 caracteres" in cv["_meta"]["warnings"]
    assert state == "review"


def test_no_extract_warnings_defaults_to_empty_list(tool_output, source_text):
    client = _FakeClient(copy.deepcopy(tool_output))

    cv, _usage, state = transform(source_text, date(2026, 7, 30), client=client)

    assert cv["_meta"]["warnings"] == []
    assert state == "ok"


class _FakeRetryClient:
    """Primera respuesta invalida contra el schema (fuerza el repair-retry de
    transform()); segunda respuesta valida. Cada llamada reporta su propio usage."""

    def __init__(self, invalid_cv, valid_cv):
        self._responses = [
            SimpleNamespace(
                stop_reason="tool_use",
                content=[SimpleNamespace(type="tool_use", name="emit_cv", input=invalid_cv)],
                usage=SimpleNamespace(input_tokens=100, output_tokens=50),
            ),
            SimpleNamespace(
                stop_reason="tool_use",
                content=[SimpleNamespace(type="tool_use", name="emit_cv", input=valid_cv)],
                usage=SimpleNamespace(input_tokens=120, output_tokens=60),
            ),
        ]
        self._call_count = 0

        def _create(**kwargs):
            resp = self._responses[self._call_count]
            self._call_count += 1
            return resp

        self.messages = SimpleNamespace(create=_create)


def test_usage_accumulates_across_schema_repair_retry(tool_output, source_text):
    # hallazgo Codex 24 ago: agent.py:107/113 pisaba el usage de la primera llamada
    # (la que fallo el schema) con el de la segunda (el retry) -- subreportaba tokens
    # reales cuando el repair-retry se dispara, que es exactamente el caso mas caro
    # en tokens (dos llamadas completas al modelo).
    invalid_cv = {"full_name": "Ana Test"}  # falta campos requeridos por el schema
    valid_cv = copy.deepcopy(tool_output)
    client = _FakeRetryClient(invalid_cv, valid_cv)

    _cv, usage, _state = transform(source_text, date(2026, 7, 30), client=client)

    assert usage.input_tokens == 100 + 120
    assert usage.output_tokens == 50 + 60
