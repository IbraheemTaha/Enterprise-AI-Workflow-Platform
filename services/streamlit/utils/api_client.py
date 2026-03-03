import requests
import socket
import os
from typing import Dict, Any, Optional


API_URL = os.getenv("API_URL", "http://api:8000")
LANGCHAIN_URL = os.getenv("LANGCHAIN_URL", "http://langchain:8001")


def get_fastapi(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Make a GET request to a FastAPI endpoint.

    Args:
        endpoint: API endpoint path
        params: Query parameters
        timeout: Request timeout in seconds

    Returns:
        Response JSON

    Raises:
        Exception: If request fails
    """
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(f"Request timeout after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to API at {API_URL}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


def call_fastapi(endpoint: str, data: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Call FastAPI endpoint.

    Args:
        endpoint: API endpoint path
        data: Request data
        timeout: Request timeout in seconds

    Returns:
        Response JSON

    Raises:
        Exception: If request fails
    """
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(f"Request timeout after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to API at {API_URL}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


def call_langchain(endpoint: str, data: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Call LangChain service endpoint.

    Args:
        endpoint: LangChain endpoint path
        data: Request data
        timeout: Request timeout in seconds

    Returns:
        Response JSON

    Raises:
        Exception: If request fails
    """
    try:
        url = f"{LANGCHAIN_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(f"Request timeout after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to LangChain service at {LANGCHAIN_URL}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


def check_service_health(url: str, timeout: int = 10, health_path: str = "/health") -> Dict[str, Any]:
    """
    Check service health.

    Args:
        url: Service base URL
        health_path: Health check endpoint path
        timeout: Request timeout in seconds

    Returns:
        Health check response or error dict
    """
    try:
        response = requests.get(f"{url}{health_path}", timeout=timeout)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = response.text or "OK"
            return {"status": "healthy", "data": data}
        else:
            return {"status": "unhealthy", "code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"status": "unreachable", "error": "Connection failed"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_tcp_health(host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
    """
    Check service health via TCP connection (for non-HTTP services like Postgres, Redis).

    Args:
        host: Hostname to connect to
        port: TCP port number
        timeout: Connection timeout in seconds

    Returns:
        Health check result dict
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return {"status": "healthy", "data": f"TCP port {port} reachable"}
        else:
            return {"status": "unreachable", "error": f"Port {port} is closed (code {result})"}
    except socket.timeout:
        return {"status": "timeout", "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_service_info(url: str, timeout: int = 10, info_path: str = "/info") -> Optional[Dict[str, Any]]:
    """
    Get service information.

    Args:
        url: Service URL
        info_path: Info endpoint path
        timeout: Request timeout in seconds

    Returns:
        Service info or None if request fails
    """
    try:
        response = requests.get(f"{url}{info_path}", timeout=timeout)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None
