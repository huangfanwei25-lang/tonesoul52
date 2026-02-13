from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_persona_swarm_framework as swarm_runner


def test_parse_input_payload_supports_list_payload() -> None:
    signals, final_decision = swarm_runner._parse_input_payload(
        [
            {
                "agent_id": "a1",
                "role": "guardian",
                "vote": "approve",
            }
        ]
    )
    assert len(signals) == 1
    assert final_decision is None


def test_parse_input_payload_supports_object_payload_and_final_decision() -> None:
    signals, final_decision = swarm_runner._parse_input_payload(
        {
            "signals": [
                {
                    "agent_id": "a1",
                    "role": "guardian",
                    "vote": "approve",
                }
            ],
            "final_decision": "REVISE",
        }
    )
    assert len(signals) == 1
    assert final_decision == "revise"


def test_parse_input_payload_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        swarm_runner._parse_input_payload({"signals": []})

    with pytest.raises(ValueError):
        swarm_runner._parse_input_payload("bad")  # type: ignore[arg-type]


def test_parse_input_payload_rejects_invalid_final_decision() -> None:
    with pytest.raises(ValueError, match="final_decision must be one of"):
        swarm_runner._parse_input_payload(
            {
                "signals": [
                    {
                        "agent_id": "a1",
                        "role": "guardian",
                        "vote": "approve",
                    }
                ],
                "final_decision": "escalate",
            }
        )


def test_gate_snapshot_collects_failure_reasons() -> None:
    gate = swarm_runner._gate_snapshot(
        {
            "decision_support": 0.2,
            "metrics": {
                "safety_pass_rate": 0.5,
                "swarm_score": 0.4,
                "token_latency_cost_index": 0.9,
            },
        }
    )
    assert gate["passed"] is False
    assert set(gate["failed_checks"]) == {
        "safety_pass_rate",
        "swarm_score",
        "decision_support",
        "token_latency_cost_index",
    }


def test_gate_snapshot_includes_cost_profile() -> None:
    gate = swarm_runner._gate_snapshot(
        {
            "decision": "approve",
            "decision_support": 0.8,
            "metrics": {
                "safety_pass_rate": 0.9,
                "swarm_score": 0.85,
                "token_latency_cost_index": 0.81,
            },
            "governance": {
                "guardian_fail_fast_triggered": False,
            },
        }
    )
    assert gate["cost_profile"]["tier"] == "critical"
    assert gate["cost_profile"]["recommended_mode"] == "guardian_only"
    assert gate["cost_profile"]["recommended_agent_budget"] == 1


def test_gate_snapshot_enforces_guardian_fail_fast_consistency() -> None:
    gate = swarm_runner._gate_snapshot(
        {
            "decision": "approve",
            "decision_support": 0.9,
            "metrics": {
                "safety_pass_rate": 0.95,
                "swarm_score": 0.9,
                "token_latency_cost_index": 0.4,
            },
            "governance": {
                "guardian_fail_fast_triggered": True,
            },
        }
    )
    assert gate["checks"]["guardian_fail_fast_consistency"] is False
    assert "guardian_fail_fast_consistency" in gate["failed_checks"]


def test_main_writes_artifact_and_returns_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_path = tmp_path / "persona_swarm_framework_latest.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_persona_swarm_framework.py",
            "--repo-root",
            str(tmp_path),
            "--out",
            str(out_path),
        ],
    )

    exit_code = swarm_runner.main()
    assert exit_code == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["source"] == "scripts/run_persona_swarm_framework.py"
    assert payload["readiness_gate"]["passed"] is True
