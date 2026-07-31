import copy
import json
import pathlib

import pytest

import grounding
from extract import extract_text

CV_PDF_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "cvs-prueba"
    / "Resume- Shirley Mercado.pdf"
)
FIXTURE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "contrato-datos"
    / "fixtures"
    / "shirley-mercado.json"
)


@pytest.fixture(scope="module")
def source_text():
    data = CV_PDF_PATH.read_bytes()
    return extract_text(CV_PDF_PATH.name, data).text


@pytest.fixture
def clean_cv():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_clean_fixture_has_zero_findings(clean_cv, source_text):
    report = grounding.evaluate(clean_cv, source_text)
    assert report.errors == []
    assert report.warnings == []


def test_invented_company_is_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][0]["company"] = "Pfizer Inc"
    report = grounding.evaluate(cv, source_text)
    assert any(e.startswith("GROUNDING_TOKEN_NOT_FOUND") for e in report.errors)


def test_short_acronym_company_is_warning_not_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][0]["company"] = "J&J"
    report = grounding.evaluate(cv, source_text)
    assert report.errors == []
    assert any(w.startswith("COMPANY_NOT_VERIFIABLE") for w in report.warnings)


def test_changed_year_is_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][1]["period"] = "April 2018 - May 2024"
    report = grounding.evaluate(cv, source_text)
    assert any("GROUNDING_YEAR_NOT_FOUND" in e and "2018" in e for e in report.errors)


def test_i_statement_bullet_is_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][0]["bullets"][0] = "I managed environmental compliance reporting."
    report = grounding.evaluate(cv, source_text)
    assert any(e.startswith("GROUNDING_I_STATEMENT") for e in report.errors)


def test_domain_exception_phase_i_is_not_flagged(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][0]["bullets"][0] = "Led a Phase I environmental site assessment."
    report = grounding.evaluate(cv, source_text)
    assert report.errors == []


def test_invented_metric_is_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"][0]["bullets"][0] = "Reduced costs by 37% through process optimization."
    report = grounding.evaluate(cv, source_text)
    assert any("GROUNDING_METRIC_NOT_FOUND" in e and "37" in e for e in report.errors)


def test_translated_metric_mismatch_is_warning_not_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["_meta"]["translated"] = True
    cv["experience"][0]["bullets"][0] = "Reduced costs by 37% through process optimization."
    report = grounding.evaluate(cv, source_text)
    assert report.errors == []
    assert any(w.startswith("METRIC_NOT_VERIFIED") for w in report.warnings)


def test_invented_town_is_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["town"] = "Bayamon"
    report = grounding.evaluate(cv, source_text)
    assert any(e.startswith("GROUNDING_TOWN_NOT_FOUND") for e in report.errors)


def test_town_matching_employer_city_is_warning_not_error(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["town"] = "Cidra"
    report = grounding.evaluate(cv, source_text)
    assert report.errors == []
    assert any(w.startswith("TOWN_MAY_BE_EMPLOYER_CITY") for w in report.warnings)


def test_summary_invented_word_is_warning(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["summary"] = cv["summary"].replace(
        "food manufacturing", "food and beverage manufacturing"
    )
    report = grounding.evaluate(cv, source_text)
    assert report.errors == []
    assert any("beverage" in w for w in report.warnings if w.startswith("SUMMARY_CLAIM_NOT_VERIFIED"))


def test_kerned_source_name_does_not_false_positive(clean_cv, source_text):
    # reproduce el bug real que encontro la auditoria: un espacio fantasma por kerning
    # tipografico ("SHIRLEY M. MERC ADO") no debe marcar failed al propio ground truth
    kerned_source = source_text.replace("SHIRLEY M. MERCADO", "SHIRLEY M. MERC ADO")
    report = grounding.evaluate(clean_cv, kerned_source)
    assert report.errors == []


def test_omitted_job_is_section_coverage_warning(clean_cv, source_text):
    cv = copy.deepcopy(clean_cv)
    cv["experience"] = [cv["experience"][0]]
    report = grounding.evaluate(cv, source_text)
    assert any(w.startswith("SECTION_COVERAGE_LOW") for w in report.warnings)
