from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_perspective_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_perspective.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_perspective_writes_noncanonical_perspective(
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
            "save_perspective.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "codex",
            "--session-id",
            "sess-perspective",
            "--summary",
            "Runtime shell is stable enough for packet-first handoff.",
            "--stance",
            "divergent_but_productive",
            "--tension",
            "redis live surfaces remain unavailable",
            "--drift",
            "caution_bias=0.58",
            "--vow",
            "Prefer packet-first handoff before broad repo scans.",
            "--evidence-ref",
            "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["proposed_drift"]["caution_bias"] == 0.58
    saved = json.loads((tmp_path / ".aegis" / "perspectives.json").read_text(encoding="utf-8"))
    assert saved["codex"]["stance"] == "divergent_but_productive"
    assert saved["codex"]["tensions"] == ["redis live surfaces remain unavailable"]


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root
