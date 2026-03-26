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
