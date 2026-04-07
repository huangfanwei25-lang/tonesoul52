from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_claude_entry_adapter_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_claude_entry_adapter.py"
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
                "last_updated": "2026-04-06T00:00:00+00:00",
                "soul_integral": 0.72,
                "tension_history": [{"topic": "claude-adapter", "severity": 0.31}],
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
                "session_id": "sess-claude-adapter",
                "agent": "codex",
                "timestamp": "2026-04-06T00:01:00+00:00",
                "topics": ["claude-entry-adapter"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["build claude adapter"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_run_claude_entry_adapter_emits_orientation_shell(
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
            "run_claude_entry_adapter.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--agent",
            "claude-shell",
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["bundle"] == "claude_entry_adapter"
    assert output["session_start_tier"] == 1
    assert output["adapter"]["shell"] == "claude_style_shell"
    assert output["adapter"]["first_hop_order"][:3] == [
        "readiness",
        "canonical_center",
        "closeout_attention",
    ]
    assert "closeout_focus" in output["adapter"]
    assert "priority_correction" in output["adapter"]
    assert output["adapter"]["priority_correction"]["receiver_rule"].startswith(
        "Recover the blocked assumption"
    )
    assert output["adapter"]["closeout_focus"]["status"] in {
        "complete",
        "partial",
        "blocked",
        "underdetermined",
    }
    assert output["adapter"]["bounded_pulls"]["observe_first"] is True
    assert output["underlying_commands"][0] == (
        "python scripts/start_agent_session.py --agent claude-shell --tier 1 --no-ack"
    )
