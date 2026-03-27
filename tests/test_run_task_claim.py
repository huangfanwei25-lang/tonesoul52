from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_task_claim_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_task_claim.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_run_task_claim_list_emits_json(capsys, monkeypatch) -> None:
    module = _load_script_module()
    monkeypatch.setattr(sys, "argv", ["run_task_claim.py", "list"])
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.list_active_claims",
        lambda: [{"task_id": "task-1", "agent": "codex"}],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)
    assert output["claims"][0]["task_id"] == "task-1"


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root


def test_run_task_claim_claim_list_release_round_trip(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_task_claim.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "claim",
            "task-1",
            "--agent",
            "codex",
            "--summary",
            "stabilize shared handoff",
            "--path",
            "scripts/save_checkpoint.py",
        ],
    )
    module.main()
    claim_output = json.loads(capsys.readouterr().out)
    assert claim_output["ok"] is True
    assert claim_output["claim"]["task_id"] == "task-1"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_task_claim.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "list",
        ],
    )
    module.main()
    list_output = json.loads(capsys.readouterr().out)
    assert list_output["claims"][0]["agent"] == "codex"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_task_claim.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "release",
            "task-1",
            "--agent",
            "codex",
        ],
    )
    module.main()
    release_output = json.loads(capsys.readouterr().out)
    assert release_output["ok"] is True

    claims_path = tmp_path / ".aegis" / "task_claims.json"
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    assert claims == {}
