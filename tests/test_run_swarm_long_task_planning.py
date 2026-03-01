from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_swarm_long_task_planning as planner


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_command_validates_input_exists(tmp_path: Path) -> None:
    config = planner.PlanningConfig(
        repo_root=tmp_path,
        input_path=tmp_path / "missing.json",
        out_path=tmp_path / "out.json",
        summary_path=tmp_path / "summary.json",
        strict=True,
    )

    command, warnings, error = planner.build_command(config)
    assert command[1] == "scripts/run_persona_swarm_framework.py"
    assert warnings == []
    assert error is not None
    assert "input_path does not exist" in error


def test_build_command_warns_for_non_json_input(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("{}", encoding="utf-8")

    config = planner.PlanningConfig(
        repo_root=tmp_path,
        input_path=input_path,
        out_path=tmp_path / "out.json",
        summary_path=tmp_path / "summary.json",
        strict=False,
    )
    command, warnings, error = planner.build_command(config)

    assert error is None
    assert "--strict" not in command
    assert len(warnings) == 1
    assert "does not end with .json" in warnings[0]


def test_extract_summary_maps_expected_fields() -> None:
    payload = {
        "evaluation": {
            "decision": "revise",
            "decision_support": 0.77,
            "metrics": {
                "swarm_score": 0.85,
                "safety_pass_rate": 1.0,
                "token_latency_cost_index": 0.44,
            },
            "persona_positioning": {"archetype": "critical_discovery"},
        },
        "readiness_gate": {
            "passed": True,
            "cost_profile": {"tier": "low"},
        },
    }
    summary = planner._extract_summary(payload, input_path_label="docs/experiments/sample.json")

    assert summary["decision"] == "revise"
    assert summary["decision_support"] == 0.77
    assert summary["swarm_score"] == 0.85
    assert summary["safety_pass_rate"] == 1.0
    assert summary["archetype"] == "critical_discovery"
    assert summary["cost_tier"] == "low"
    assert summary["readiness_gate_passed"] is True


def test_main_writes_summary_snapshot(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_path = tmp_path / "docs" / "experiments" / "input.json"
    _write_json(input_path, {"signals": []})
    out_path = tmp_path / "docs" / "status" / "swarm.json"
    _write_json(
        out_path,
        {
            "evaluation": {
                "decision": "approve",
                "decision_support": 0.88,
                "metrics": {"swarm_score": 0.9, "safety_pass_rate": 1.0},
                "persona_positioning": {"archetype": "reliable_executor"},
            },
            "readiness_gate": {"passed": True, "cost_profile": {"tier": "low"}},
        },
    )
    summary_path = tmp_path / "docs" / "status" / "summary.json"

    class _FakeResult:
        returncode = 0

    monkeypatch.setattr(planner.subprocess, "run", lambda *args, **kwargs: _FakeResult())
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_swarm_long_task_planning.py",
            "--repo-root",
            str(tmp_path),
            "--input",
            str(input_path.relative_to(tmp_path)),
            "--out",
            str(out_path.relative_to(tmp_path)),
            "--summary-out",
            str(summary_path.relative_to(tmp_path)),
            "--strict",
        ],
    )

    exit_code = planner.main()
    assert exit_code == 0
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["decision"] == "approve"
    assert payload["next_phase"] == "Phase 124"
