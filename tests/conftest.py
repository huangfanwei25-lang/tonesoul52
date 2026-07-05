import shutil
import uuid
from pathlib import Path

import pytest


def pytest_ignore_collect(collection_path, config):
    """Ignore files named test_output*.txt during collection."""
    return collection_path.name.startswith("test_output")


@pytest.fixture(autouse=True)
def _isolate_soul_db(tmp_path, monkeypatch):
    """Redirect all SoulDB writes to a temp directory during tests.

    Without this, tests that trigger council runtime / self_journal writes
    pollute the real memory/self_journal.jsonl with thousands of test entries.
    """
    import tonesoul.memory.soul_db as soul_db_mod

    monkeypatch.setattr(soul_db_mod, "_default_memory_root", lambda: tmp_path / "memory")
    (tmp_path / "memory").mkdir(exist_ok=True)


@pytest.fixture(autouse=True)
def _isolate_aegis_chain_head(tmp_path, monkeypatch):
    """Redirect Aegis chain-head persistence to a temp directory during tests.

    Without this, any test that reaches AegisShield.save() (real commit()
    paths) advances the repo-global .aegis/chain_head.txt while its trace log
    stays test-isolated — reopening the recurring benign head/tail gap that
    diagnose reports as 'compromised' (the alarm word must not depreciate).
    Root cause + adjudicated fix shape (monkeypatch over env override):
    docs/plans/aegis_chain_head_test_pollution_2026-07-05.md.
    _KEYS_DIR is intentionally NOT redirected: signing keys are read-only in
    tests and live keys must keep working.
    """
    import tonesoul.aegis_shield as aegis_shield_mod

    monkeypatch.setattr(aegis_shield_mod, "_AEGIS_DIR", tmp_path / ".aegis")


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


@pytest.fixture
def qa_sandbox(monkeypatch, tmp_path):
    """
    QA Sandbox (D4 Environment Test)
    Creates a completely isolated environment root and mocks necessary vars/paths
    to ensure AI testing scripts cannot touch real memory or configurations.
    """
    sandbox_root = tmp_path / "qa_sandbox"
    sandbox_root.mkdir()

    # Mock HOME and APPDATA to ensure no global config leaks
    monkeypatch.setenv("HOME", str(sandbox_root))
    monkeypatch.setenv("APPDATA", str(sandbox_root))

    return sandbox_root
