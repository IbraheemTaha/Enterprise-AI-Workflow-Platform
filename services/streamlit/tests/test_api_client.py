"""Tests for the Streamlit utils.api_client helpers.

No real HTTP traffic — requests and sockets are mocked.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

SERVICE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVICE_ROOT))

from utils import api_client  # noqa: E402


@patch("utils.api_client.requests.get")
def test_get_fastapi_returns_json(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"ok": True},
        raise_for_status=lambda: None,
    )
    assert api_client.get_fastapi("/health") == {"ok": True}


@patch(
    "utils.api_client.requests.get",
    side_effect=requests.exceptions.ConnectionError,
)
def test_get_fastapi_wraps_connection_error(_mock_get):
    with pytest.raises(Exception, match="Could not connect"):
        api_client.get_fastapi("/health")


@patch("utils.api_client.requests.post")
def test_call_fastapi_posts_json(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"output": "hi"},
        raise_for_status=lambda: None,
    )
    result = api_client.call_fastapi("/v1/chat/completions", {"messages": []})
    assert result == {"output": "hi"}
    mock_post.assert_called_once()


@patch(
    "utils.api_client.requests.post",
    side_effect=requests.exceptions.Timeout,
)
def test_call_langchain_timeout(_mock_post):
    with pytest.raises(Exception, match="timeout"):
        api_client.call_langchain("/chat/dynamic", {})


@patch("utils.api_client.requests.get")
def test_check_service_health_healthy(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"status": "healthy"},
    )
    out = api_client.check_service_health("http://svc")
    assert out["status"] == "healthy"
    assert out["data"] == {"status": "healthy"}


@patch(
    "utils.api_client.requests.get",
    side_effect=requests.exceptions.ConnectionError,
)
def test_check_service_health_unreachable(_mock_get):
    assert api_client.check_service_health("http://x")["status"] == "unreachable"


@patch("utils.api_client.socket.socket")
def test_check_tcp_health_open(mock_sock_cls):
    sock = MagicMock()
    sock.connect_ex.return_value = 0
    mock_sock_cls.return_value = sock
    assert api_client.check_tcp_health("host", 5432)["status"] == "healthy"


@patch("utils.api_client.socket.socket")
def test_check_tcp_health_closed(mock_sock_cls):
    sock = MagicMock()
    sock.connect_ex.return_value = 111
    mock_sock_cls.return_value = sock
    assert api_client.check_tcp_health("host", 5432)["status"] == "unreachable"


@patch("utils.api_client.requests.get")
def test_get_service_info_returns_none_on_error(mock_get):
    mock_get.return_value = MagicMock(status_code=500)
    assert api_client.get_service_info("http://x") is None
