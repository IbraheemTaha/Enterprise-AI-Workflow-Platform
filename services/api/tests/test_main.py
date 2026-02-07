from fastapi.testclient import TestClient

from services.api.main import app


client = TestClient(app)


def _clear_llm_env(monkeypatch):
    for key in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_root_returns_message_and_version():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Enterprise AI Workflow Platform API",
        "version": "1.0.0",
    }


def test_health_defaults_to_unconfigured(monkeypatch):
    _clear_llm_env(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "services": {
            "api": True,
            "openai_configured": False,
            "anthropic_configured": False,
            "gemini_configured": False,
            "amazon_nova_configured": False,
        },
    }


def test_health_reflects_configured_env(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setenv("GOOGLE_API_KEY", "test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["services"] == {
        "api": True,
        "openai_configured": True,
        "anthropic_configured": True,
        "gemini_configured": True,
        "amazon_nova_configured": True,
    }
