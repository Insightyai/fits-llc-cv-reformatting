import json
import os
import pathlib
from datetime import date

import jsonschema
import pytest

from agent import transform
from extract import extract_text

CV_PDF_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "cvs-prueba"
    / "Resume- Shirley Mercado.pdf"
)
CV_SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "contrato-datos"
    / "cv-schema.json"
)

pytestmark = pytest.mark.llm


@pytest.fixture
def cv_result():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY no esta seteada")
    data = CV_PDF_PATH.read_bytes()
    extracted = extract_text(CV_PDF_PATH.name, data)
    cv, _usage, state = transform(extracted.text, date(2026, 7, 30), api_key=api_key)
    return cv, state


def test_output_validates_against_schema(cv_result):
    cv, _state = cv_result
    schema = json.loads(CV_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(cv, schema)  # no debe lanzar


def test_structural_equivalence_with_shirley_mercado(cv_result):
    # nunca aserciones exactas sobre el texto del summary -- es el campo que
    # aprueba FITS a mano, no un valor determinístico a comparar por igualdad
    cv, state = cv_result
    assert state in ("ok", "review")  # nunca "failed" para el ground truth conocido
    assert cv["full_name"] == "Shirley M. Mercado"
    assert cv["years_experience"] == "4"
    assert cv.get("town") is None

    companies = {job["company"] for job in cv["experience"]}
    assert any("Caribbean Refrescos" in c for c in companies)
    assert any("Baxter" in c for c in companies)

    institutions = {edu["institution"] for edu in cv["education"]}
    assert any("Polytechnic" in i for i in institutions)

    assert "TOWN_NOT_DECLARED" in cv["_meta"]["warnings"]
    assert cv["_meta"]["prompt_version"].startswith("transform-v1-")
