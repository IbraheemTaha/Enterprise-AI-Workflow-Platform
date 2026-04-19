"""Structural tests for the dbt project.

We validate the project layout and configuration without requiring a live
Postgres connection. A `dbt parse` invocation is used separately in CI for
deeper validation.
"""

from pathlib import Path

import yaml

SERVICE_ROOT = Path(__file__).resolve().parent.parent


def test_dbt_project_file_is_valid_yaml():
    with (SERVICE_ROOT / "dbt_project.yml").open() as fh:
        project = yaml.safe_load(fh)
    assert project["name"] == "enterprise_ai_platform"
    assert project["profile"] == "enterprise_ai_platform"
    assert "staging" in project["models"]["enterprise_ai_platform"]
    assert "marts" in project["models"]["enterprise_ai_platform"]


def test_profiles_file_is_valid_yaml():
    with (SERVICE_ROOT / "profiles.yml").open() as fh:
        profiles = yaml.safe_load(fh)
    assert "enterprise_ai_platform" in profiles
    outputs = profiles["enterprise_ai_platform"]["outputs"]
    assert "dev" in outputs
    assert outputs["dev"]["type"] == "postgres"


def test_expected_directories_exist():
    for sub in ("models", "seeds", "analyses", "snapshots", "tests"):
        assert (SERVICE_ROOT / sub).is_dir(), f"Missing dbt directory: {sub}"


def test_models_directory_has_staging_and_marts():
    models_dir = SERVICE_ROOT / "models"
    assert (models_dir / "staging").is_dir()
    assert (models_dir / "marts").is_dir()
    assert (models_dir / "sources.yml").is_file()


def test_sources_file_parses():
    with (SERVICE_ROOT / "models" / "sources.yml").open() as fh:
        data = yaml.safe_load(fh)
    assert "sources" in data
    assert isinstance(data["sources"], list) and data["sources"]
