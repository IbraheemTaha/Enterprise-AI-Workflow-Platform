"""Tests for the Gradio service app.py — no real HTTP calls are issued."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SERVICE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVICE_ROOT))


def test_load_readme_existing_file(tmp_path):
    from app import load_readme

    target = tmp_path / "sample.md"
    target.write_text("# Hello", encoding="utf-8")
    assert load_readme(str(target)) == "# Hello"


def test_load_readme_missing_file_returns_error_string():
    from app import load_readme

    result = load_readme("/does/not/exist.md")
    assert "Error loading documentation" in result


def test_chat_fn_requires_model():
    from app import chat_fn

    message = chat_fn("hi", [], "openai", None)
    assert "No model selected" in message


@patch("app.requests.post")
def test_chat_fn_returns_assistant_content(mock_post):
    from app import chat_fn

    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"choices": [{"message": {"content": "pong"}}]},
    )

    result = chat_fn("hi", [], "openai", "gpt-4o")
    assert result == "pong"


@patch("app.requests.post")
def test_chat_fn_surfaces_http_errors(mock_post):
    from app import chat_fn

    mock_post.return_value = MagicMock(status_code=503, text="down")
    result = chat_fn("hi", [], "openai", "gpt-4o")
    assert "Error 503" in result


@patch("app.requests.get")
def test_check_health_returns_api_json(mock_get):
    from app import check_health

    mock_get.return_value = MagicMock(json=lambda: {"status": "healthy"})
    assert check_health() == {"status": "healthy"}


@patch("app.requests.get", side_effect=Exception("boom"))
def test_check_health_handles_network_failure(_mock_get):
    from app import check_health

    result = check_health()
    assert result["status"] == "API not available"
    assert "boom" in result["error"]
