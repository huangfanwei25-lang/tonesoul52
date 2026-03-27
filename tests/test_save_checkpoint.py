from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_checkpoint_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_checkpoint.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_checkpoint_writes_noncanonical_checkpoint(
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
            "save_checkpoint.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--checkpoint-id",
            "cp-20260327",
            "--agent",
            "codex",
            "--session-id",
            "sess-ops",
            "--summary",
            "Pause before commit and leave a resumable checkpoint.",
            "--path",
            "tonesoul/unified_pipeline.py",
            "--next-action",
            "Resume packet-first observer hardening",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["checkpoint_id"] == "cp-20260327"
    assert output["agent"] == "codex"
    saved = json.loads((tmp_path / ".aegis" / "checkpoints.json").read_text(encoding="utf-8"))
    assert saved["cp-20260327"]["pending_paths"] == ["tonesoul/unified_pipeline.py"]


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root
