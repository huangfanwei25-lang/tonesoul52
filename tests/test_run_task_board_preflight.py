from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_task_board_preflight_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_task_board_preflight.py"
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
                "tension_history": [{"topic": "task-board-preflight", "severity": 0.31}],
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
                "session_id": "sess-task-board-preflight",
                "agent": "codex",
                "timestamp": "2026-04-02T00:01:00+00:00",
                "topics": ["task-board-preflight"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["check task-board parking discipline"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_run_task_board_preflight_emits_docs_plans_first(
    capsys,
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"

    _write_state(state_path)
    _write_traces(traces_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_task_board_preflight.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "observer-task-board-preflight",
            "--proposal-kind",
            "external_idea",
            "--target-path",
            "task.md",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["bundle"] == "task_board_preflight"
    assert output["agent"] == "observer-task-board-preflight"
    assert output["proposal_kind"] == "external_idea"
    assert output["target_path"] == "task.md"
    assert output["preflight"]["classification"] == "docs_plans_first"
    assert output["preflight"]["suggested_destination"] == "docs/plans/"
