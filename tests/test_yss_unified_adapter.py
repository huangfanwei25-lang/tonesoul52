from __future__ import annotations

import json
from pathlib import Path

import tonesoul.yss_pipeline as yss_pipeline
from tonesoul.yss_unified_adapter import (
    build_multi_persona_eval_snapshot,
    build_unified_seed,
    write_multi_persona_eval_snapshot,
)


def test_build_unified_seed_maps_dispatch_state() -> None:
    seed = build_unified_seed(
        {
            "user_message": "請幫我整理風險與下一步",
            "history": [{"role": "user", "content": "x"}, {"role": "assistant", "content": "y"}],
            "council_mode": "hybrid",
            "persona_config": {"name": "ops", "custom_roles": [{"name": "guardian"}]},
            "dispatch_trace": {"state": "C", "adjusted_tension": 0.91},
        }
    )

    assert seed["decision_mode"] == "strict"
    assert seed["payload"]["history_count"] == 2
    assert seed["payload"]["custom_role_count"] == 1


def test_build_multi_persona_eval_snapshot_has_non_null_metrics() -> None:
    snapshot = build_multi_persona_eval_snapshot(
        gate_report={
            "results": [
                {
                    "gate": "poav_gate",
                    "passed": True,
                    "details": {"components": {"total": 0.83}},
                },
                {"gate": "guardian_gate", "passed": True},
                {"gate": "mercy_gate", "passed": True},
            ]
        },
        dispatch_trace={"adjusted_tension": 0.62},
    )

    for mode in ("A", "B", "C"):
        metrics = snapshot["modes"][mode]
        assert metrics["task_quality"] is not None
        assert metrics["safety_pass_rate"] is not None
        assert metrics["consistency_at_session"] is not None
        assert metrics["disagreement_utility"] is not None
        assert metrics["token_latency_cost_index"] is not None
        assert metrics["p95_latency_ms"] is not None

    assert snapshot["promotion_decision"]["from_mode"] == "A"


def test_write_multi_persona_eval_snapshot(tmp_path: Path) -> None:
    out = tmp_path / "multi_persona_eval.json"
    payload = build_multi_persona_eval_snapshot(gate_report={}, dispatch_trace={})
    path = write_multi_persona_eval_snapshot(out, payload)

    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    assert loaded["baseline_mode"] == "A"
    assert loaded["modes"]["A"]["task_quality"] is not None


def test_run_pipeline_from_unified_request_injects_seed_defaults(monkeypatch) -> None:
    captured = {}

    def _fake_run_pipeline(config):
        captured["task"] = config.task
        captured["decision_mode"] = config.decision_mode
        return {"run_dir": "dummy"}

    monkeypatch.setattr(yss_pipeline, "run_pipeline", _fake_run_pipeline)
    result = yss_pipeline.run_pipeline_from_unified_request(
        {
            "user_message": "請給我可審計的方案",
            "dispatch_trace": {"state": "B"},
        }
    )

    assert captured["task"]
    assert captured["decision_mode"] == "guarded"
    assert result["unified_seed"]["decision_mode"] == "guarded"
