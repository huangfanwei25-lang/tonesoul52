from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_persona_swarm_framework as swarm_runner


def _signals_for_selection():
    signals, _ = swarm_runner._parse_input_payload(
        [
            {
                "agent_id": "g1",
                "role": "guardian",
                "vote": "block",
                "confidence": 0.95,
                "safety_score": 0.95,
                "quality_score": 0.70,
                "latency_ms": 800,
                "token_cost": 350,
            },
            {
                "agent_id": "e1",
                "role": "engineer",
                "vote": "approve",
                "confidence": 0.88,
                "safety_score": 0.82,
                "quality_score": 0.86,
                "latency_ms": 1000,
                "token_cost": 500,
            },
            {
                "agent_id": "c1",
                "role": "critic",
                "vote": "revise",
                "confidence": 0.76,
                "safety_score": 0.85,
                "quality_score": 0.90,
                "latency_ms": 1500,
                "token_cost": 700,
            },
            {
                "agent_id": "a1",
                "role": "analyst",
                "vote": "approve",
                "confidence": 0.72,
                "safety_score": 0.88,
                "quality_score": 0.83,
                "latency_ms": 1400,
                "token_cost": 680,
            },
        ]
    )
    return signals


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


def test_select_execution_signals_guardian_only_mode() -> None:
    signals = _signals_for_selection()
    selected = swarm_runner._select_execution_signals(
        signals,
        {
            "tier": "critical",
            "recommended_mode": "guardian_only",
            "recommended_agent_budget": 1,
        },
    )
    assert len(selected) == 1
    assert selected[0].agent_id == "g1"


def test_build_execution_plan_tracks_selected_and_dropped_agents() -> None:
    signals = _signals_for_selection()
    selected = swarm_runner._select_execution_signals(
        signals,
        {
            "tier": "high",
            "recommended_mode": "guardian_engineer_only",
            "recommended_agent_budget": 2,
        },
    )
    plan = swarm_runner._build_execution_plan(
        signals,
        selected,
        {
            "tier": "high",
            "recommended_mode": "guardian_engineer_only",
            "recommended_agent_budget": 2,
        },
    )
    assert plan["selected_agent_count"] == 2
    assert plan["budget_respected"] is True
    assert set(plan["selected_agent_ids"]) == {"g1", "e1"}
    assert set(plan["dropped_agent_ids"]) == {"c1", "a1"}


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
    assert payload["input"]["signal_count"] >= payload["input"]["execution_signal_count"]
    assert payload["execution_plan"]["budget_respected"] is True
    assert "baseline_evaluation" in payload
    assert payload["readiness_gate"]["passed"] is True
