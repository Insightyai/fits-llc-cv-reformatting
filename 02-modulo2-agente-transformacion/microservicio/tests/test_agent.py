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
