"""DAG integrity tests for the Airflow service.

Verifies DAG modules parse without import errors, that each file defines
at least one DAG, and that the shipped example DAG has the expected
structure.
"""

import os
import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parent.parent
DAGS_DIR = SERVICE_ROOT / "dags"

# Make `dags/` importable for bare module loads.
sys.path.insert(0, str(DAGS_DIR))

# Airflow requires some environment variables during DAG parsing.
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")


def _collect_dag_files():
    return sorted(
        p for p in DAGS_DIR.glob("*.py") if p.name != "__init__.py"
    )


def test_dags_directory_exists():
    assert DAGS_DIR.is_dir(), f"Expected DAG directory at {DAGS_DIR}"


@pytest.mark.parametrize("dag_file", _collect_dag_files(), ids=lambda p: p.name)
def test_dag_file_imports_cleanly(dag_file):
    from airflow.models import DagBag

    dag_bag = DagBag(dag_folder=str(dag_file), include_examples=False)
    assert not dag_bag.import_errors, (
        f"DAG import errors in {dag_file.name}: {dag_bag.import_errors}"
    )
    assert len(dag_bag.dags) >= 1, f"{dag_file.name} produced no DAGs"


def test_example_dag_has_expected_tasks():
    from airflow.models import DagBag

    dag_bag = DagBag(dag_folder=str(DAGS_DIR / "example_dag.py"), include_examples=False)
    dag = dag_bag.dags.get("example_ml_pipeline")
    assert dag is not None, "example_ml_pipeline DAG not found"
    task_ids = {t.task_id for t in dag.tasks}
    assert {"extract_data", "process_data", "train_model"}.issubset(task_ids)
