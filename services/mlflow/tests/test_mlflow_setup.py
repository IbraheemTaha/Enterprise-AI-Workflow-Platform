"""Structural tests for the MLflow service.

MLflow itself does not require our source code; these tests verify the
Dockerfile/requirements contract is correct so the image builds and runs.
"""

from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent.parent


def test_requirements_lists_mlflow_and_drivers():
    content = (SERVICE_ROOT / "requirements.txt").read_text().splitlines()
    pkgs = {line.split("==")[0].strip() for line in content if line.strip()}
    assert "mlflow" in pkgs
    assert "psycopg2-binary" in pkgs
    assert "boto3" in pkgs


def test_dockerfile_exposes_5000_and_runs_server():
    dockerfile = (SERVICE_ROOT / "Dockerfile").read_text()
    assert "EXPOSE 5000" in dockerfile
    assert "mlflow" in dockerfile and "server" in dockerfile
    assert "--port" in dockerfile and "5000" in dockerfile


def test_mlflow_importable():
    import mlflow  # noqa: F401

    assert hasattr(mlflow, "__version__")
