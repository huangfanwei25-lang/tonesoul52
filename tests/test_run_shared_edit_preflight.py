from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_shared_edit_preflight_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_shared_edit_preflight.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_state(state_path: Path) -> None:
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-04-02T00:00:00+00:00",
                "soul_integral": 0.72,
                "tension_history": [{"topic": "shared-preflight", "severity": 0.31}],
                "active_vows": [{"id": "v1", "content": "leave explicit handoff state"}],
                "aegis_vetoes": [],
                "baseline_drift": {
                    "caution_bias": 0.52,
                    "innovation_bias": 0.58,
                    "autonomy_level": 0.34,
                },
                "session_count": 7,
            }
        ),
        encoding="utf-8",
    )


def _write_traces(traces_path: Path) -> None:
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-preflight",
                "agent": "codex",
                "timestamp": "2026-04-02T00:01:00+00:00",
                "topics": ["shared-preflight"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["check shared path overlap"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_run_shared_edit_preflight_emits_coordinate_decision(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    claims_path = tmp_path / ".aegis" / "task_claims.json"

    _write_state(state_path)
    _write_traces(traces_path)
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "other-agent",
                    "summary": "hold runtime lane",
                    "paths": ["tonesoul/runtime_adapter.py"],
                    "source": "cli",
                    "created_at": "2026-04-02T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_shared_edit_preflight.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-shared-preflight",
            "--path",
            "tonesoul/runtime_adapter.py",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["bundle"] == "shared_edit_preflight"
    assert output["agent"] == "observer-shared-preflight"
    assert output["readiness"] == "needs_clarification"
    assert output["task_track"] == "feature_track"
    assert output["preflight"]["decision"] == "coordinate"
    assert output["preflight"]["decision_basis"] == "other_agent_overlap"
    assert output["preflight"]["other_overlap_paths"] == ["tonesoul/runtime_adapter.py"]
    assert output["preflight"]["overlaps"][0]["task_id"] == "task-1"
    assert output["underlying_commands"][0] == "python scripts/run_task_claim.py list"
