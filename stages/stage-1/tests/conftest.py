from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest


def learner_project_dir() -> Path:
    configured_path = os.environ.get("DATA_BY_DOING_LEARNER_PROJECT")
    if configured_path is None:
        raise pytest.UsageError(
            "Defina DATA_BY_DOING_LEARNER_PROJECT com o caminho do projeto."
        )

    project_dir = Path(configured_path)
    if not project_dir.is_dir():
        raise pytest.UsageError(
            "DATA_BY_DOING_LEARNER_PROJECT deve apontar para um diretório."
        )

    return project_dir


@pytest.fixture
def input_dir(tmp_path: Path) -> Path:
    source_dir = learner_project_dir() / "data" / "source"
    destination = tmp_path / "source"
    shutil.copytree(source_dir, destination)
    return destination


@pytest.fixture
def output_path(tmp_path: Path) -> Path:
    return tmp_path / "output" / "warehouse.duckdb"
