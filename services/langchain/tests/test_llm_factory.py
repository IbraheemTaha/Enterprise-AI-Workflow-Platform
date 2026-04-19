"""Tests for langchain service llm_factory utilities.

Tests only the availability / validation logic — no network calls and
no actual model instantiation is performed.
"""

import pytest


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


def test_get_available_providers_all_absent():
    from utils.llm_factory import get_available_providers

    providers = get_available_providers()
    assert providers == {
        "openai": False,
        "anthropic": False,
        "google": False,
        "aws": False,
    }


def test_get_available_providers_partial(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")

    from utils.llm_factory import get_available_providers

    providers = get_available_providers()
    assert providers["openai"] is True
    assert providers["aws"] is True
    assert providers["anthropic"] is False
    assert providers["google"] is False


def test_get_llm_auto_with_no_providers_raises():
    from utils.llm_factory import get_llm

    with pytest.raises(ValueError, match="No LLM provider available"):
        get_llm(provider="auto")


def test_get_llm_missing_api_key_raises(monkeypatch):
    from utils.llm_factory import get_llm

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        get_llm(provider="openai")

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        get_llm(provider="anthropic")
