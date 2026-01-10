import shutil
import uuid
from pathlib import Path

import pytest


def pytest_ignore_collect(collection_path, config):
    """Ignore files named test_output*.txt during collection."""
    return collection_path.name.startswith("test_output")


@pytest.fixture
def workspace_tmpdir():
    """Provide a temporary directory rooted inside the repo workspace."""
    base = Path.cwd() / "temp" / "pytest"
    base.mkdir(parents=True, exist_ok=True)
    tmpdir = base / f"tmp{uuid.uuid4().hex}"
    tmpdir.mkdir(parents=True, exist_ok=True)
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
