"""Basic tests for the FastAPI service (main.py).

These tests run without external dependencies (no OpenAI/Anthropic/etc.).
They validate:
  - app metadata
  - root and health endpoints
  - /v1/models rejects unsupported providers
  - /v1/chat/completions validates input
  - /v1/models returns 503 when the provider is unconfigured
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVICE_ROOT))

from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_provider_env(monkeypatch):
    for var in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture()
def client():
    return TestClient(app)


def test_app_metadata():
    assert app.title == "Enterprise AI API"
    assert app.version == "1.0.0"


def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Enterprise AI Workflow Platform API"
    assert body["version"] == "1.0.0"


def test_health_endpoint_structure(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert set(body["services"].keys()) == {
        "api",
        "openai_configured",
        "anthropic_configured",
        "gemini_configured",
        "amazon_nova_configured",
    }
    assert body["services"]["api"] is True


def test_health_reflects_env(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    body = client.get("/health").json()
    assert body["services"]["openai_configured"] is True
    assert body["services"]["anthropic_configured"] is False


def test_models_unsupported_provider(client):
    resp = client.get("/v1/models", params={"provider": "bogus"})
    assert resp.status_code == 400
    assert "Unsupported provider" in resp.json()["detail"]


def test_models_missing_key_returns_503(client):
    resp = client.get("/v1/models", params={"provider": "openai"})
    assert resp.status_code == 503
    assert "OPENAI_API_KEY" in resp.json()["detail"]


def test_chat_requires_messages(client):
    resp = client.post("/v1/chat/completions", json={"provider": "openai"})
    assert resp.status_code == 400
    assert "messages" in resp.json()["detail"]


def test_chat_unsupported_provider(client):
    resp = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}], "provider": "bogus"},
    )
    assert resp.status_code == 400


def test_chat_missing_key_returns_503(client):
    resp = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}], "provider": "anthropic"},
    )
    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]
