from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_subject_snapshot_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_subject_snapshot.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_subject_snapshot_writes_noncanonical_subject_surface(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_subject_snapshot.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--session-id",
            "sess-subject",
            "--summary",
            "Operate as a packet-first runtime steward with explicit boundaries.",
            "--vow",
            "do not commit personal memory data",
            "--boundary",
            "protected files stay human-managed",
            "--preference",
            "prefer packet before broad repo scan",
            "--routine",
            "leave compaction before release",
            "--thread",
            "subject-snapshot rollout",
            "--evidence-ref",
            "docs/AI_QUICKSTART.md",
            "--refresh-signal",
            "refresh when durable boundaries change",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["summary"].startswith("Operate as a packet-first runtime steward")

    saved = json.loads((tmp_path / ".aegis" / "subject_snapshots.json").read_text(encoding="utf-8"))
    assert saved[0]["durable_boundaries"] == ["protected files stay human-managed"]
    assert saved[0]["decision_preferences"] == ["prefer packet before broad repo scan"]


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root
