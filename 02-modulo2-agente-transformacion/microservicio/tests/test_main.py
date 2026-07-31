import base64
import os
from types import SimpleNamespace

os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("MAX_BODY_BYTES", "500000")
os.environ.setdefault("MAX_TRANSFORM_BODY_BYTES", "1500000")

import pytest
from fastapi.testclient import TestClient

import main
from agent import TransformError

API_KEY = os.environ["API_KEY"]
MAX_BODY_BYTES = int(os.environ["MAX_BODY_BYTES"])
MAX_TRANSFORM_BODY_BYTES = int(os.environ["MAX_TRANSFORM_BODY_BYTES"])


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        yield c


def _auth():
    return {"X-API-Key": API_KEY}


def _body(content=b"Experiencia profesional real. " * 30, filename="cv.txt"):
    return {"filename": filename, "content_base64": base64.b64encode(content).decode()}


def test_missing_api_key_returns_401(client):
    r = client.post("/transform", json=_body())
    assert r.status_code == 401


def test_wrong_api_key_returns_401(client):
    r = client.post("/transform", json=_body(), headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_missing_fields_returns_400(client):
    r = client.post("/transform", json={"filename": "cv.txt"}, headers=_auth())
    assert r.status_code == 400


def test_invalid_base64_returns_400(client):
    r = client.post(
        "/transform",
        json={"filename": "cv.txt", "content_base64": "no es base64 valido!!"},
        headers=_auth(),
    )
    assert r.status_code == 400


def test_invalid_json_body_returns_400(client):
    r = client.post("/transform", content=b"esto no es json", headers=_auth())
    assert r.status_code == 400


def test_extraction_error_returns_422(client):
    r = client.post("/transform", json=_body(content=b"Hi"), headers=_auth())
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "NO_TEXT_LAYER"


def test_transform_success_returns_cv_and_state(client, monkeypatch):
    fake_cv = {"full_name": "Ana Test", "_meta": {"warnings": [], "prompt_version": "x"}}

    def fake_transform(cv_text, now, api_key=None, extract_warnings=None):
        return fake_cv, SimpleNamespace(input_tokens=10, output_tokens=20), "ok"

    monkeypatch.setattr(main, "transform", fake_transform)

    r = client.post("/transform", json=_body(), headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body == {
        "state": "ok",
        "cv": fake_cv,
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }


def test_transform_error_returns_422(client, monkeypatch):
    def fake_transform(cv_text, now, api_key=None, extract_warnings=None):
        raise TransformError("GROUNDING_FAILED", "empresa inventada")

    monkeypatch.setattr(main, "transform", fake_transform)

    r = client.post("/transform", json=_body(), headers=_auth())
    assert r.status_code == 422
    assert r.json()["detail"] == {
        "state": "failed",
        "code": "GROUNDING_FAILED",
        "detail": "empresa inventada",
    }


def test_body_between_route_limits_rejected_on_render_but_accepted_on_transform(client, monkeypatch):
    mid_size = (MAX_BODY_BYTES + MAX_TRANSFORM_BODY_BYTES) // 2

    render_body = {"template": "new_format", "cv": {"full_name": "x" * mid_size}}
    r_render = client.post("/render", json=render_body, headers=_auth())
    assert r_render.status_code == 413

    def fake_transform(cv_text, now, api_key=None, extract_warnings=None):
        return {"_meta": {"warnings": []}}, SimpleNamespace(input_tokens=1, output_tokens=1), "ok"

    monkeypatch.setattr(main, "transform", fake_transform)
    phrase = b"Experiencia profesional real. "
    mid_text = phrase * (mid_size // len(phrase) + 10)
    r_transform = client.post("/transform", json=_body(content=mid_text), headers=_auth())
    assert r_transform.status_code == 200


def test_transform_body_exceeding_its_own_limit_returns_413(client):
    huge = b"x" * (MAX_TRANSFORM_BODY_BYTES + 100_000)
    r = client.post("/transform", json=_body(content=huge), headers=_auth())
    assert r.status_code == 413
