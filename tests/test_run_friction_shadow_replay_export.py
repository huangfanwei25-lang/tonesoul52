from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_friction_shadow_replay_export as runner


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_report_falls_back_to_synthetic_when_sources_missing(tmp_path: Path) -> None:
    payload, rows = runner.build_report(
        journal_path=tmp_path / "missing_journal.jsonl",
        discussion_path=tmp_path / "missing_discussion.jsonl",
        max_rows=1200,
        min_scenarios=24,
        max_invalid_lines=200,
    )
    assert payload["overall_ok"] is True
    assert payload["metrics"]["source_synthetic_count"] > 0
    assert payload["metrics"]["drift"]["has_previous_snapshot"] is False
    assert len(rows) == payload["metrics"]["scenario_count"]
    assert any("synthetic fallback" in warning for warning in payload["warnings"])


def test_build_report_can_fail_when_scenario_count_below_threshold(tmp_path: Path) -> None:
    journal_path = tmp_path / "memory" / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "verdict": "approve",
                "transcript": {
                    "timestamp": "2026-02-01T00:00:00Z",
                    "input_preview": "hello",
                    "coherence": {"c_inter": 0.9, "approval_rate": 0.9},
                },
            }
        ],
    )
    discussion_path = tmp_path / "memory" / "agent_discussion_curated.jsonl"
    _write_jsonl(discussion_path, [])

    payload, _ = runner.build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        max_rows=1200,
        min_scenarios=5,
        max_invalid_lines=200,
    )
    assert payload["overall_ok"] is False
    assert any("scenario_count below threshold" in issue for issue in payload["issues"])


def test_build_report_can_fail_on_distribution_drift(tmp_path: Path) -> None:
    journal_path = tmp_path / "memory" / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "verdict": "approve",
                "transcript": {
                    "timestamp": "2026-02-01T00:00:00Z",
                    "input_preview": "hello",
                    "coherence": {"c_inter": 0.9, "approval_rate": 0.9},
                },
            }
        ],
    )
    discussion_path = tmp_path / "memory" / "agent_discussion_curated.jsonl"
    _write_jsonl(discussion_path, [])
    previous_payload = {
        "metrics": {
            "scenario_count": 100.0,
            "average_initial_tension": 0.9,
            "average_friction_score": 0.9,
            "high_friction_scenario_rate": 0.8,
        }
    }

    payload, _ = runner.build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        max_rows=1200,
        min_scenarios=1,
        max_invalid_lines=200,
        previous_payload=previous_payload,
        max_avg_tension_drift=0.1,
        max_avg_friction_drift=0.1,
        max_high_friction_rate_drift=0.1,
        min_scenario_count_ratio=0.5,
    )
    assert payload["overall_ok"] is False
    assert payload["metrics"]["drift"]["has_previous_snapshot"] is True
    assert payload["metrics"]["drift"]["guard_applied"] is True
    assert any("scenario_count ratio below threshold" in issue for issue in payload["issues"])
    assert any(
        "average_initial_tension drift above threshold" in issue for issue in payload["issues"]
    )


def test_build_report_skips_drift_guard_when_synthetic_fallback_used(tmp_path: Path) -> None:
    previous_payload = {
        "metrics": {
            "scenario_count": 1200,
            "source_synthetic_count": 0,
            "average_initial_tension": 0.6,
            "average_friction_score": 0.65,
            "high_friction_scenario_rate": 0.75,
        }
    }

    payload, rows = runner.build_report(
        journal_path=tmp_path / "missing_journal.jsonl",
        discussion_path=tmp_path / "missing_discussion.jsonl",
        max_rows=1200,
        min_scenarios=24,
        max_invalid_lines=200,
        previous_payload=previous_payload,
        max_avg_tension_drift=0.01,
        max_avg_friction_drift=0.01,
        max_high_friction_rate_drift=0.01,
        min_scenario_count_ratio=0.95,
    )
    assert rows
    assert payload["overall_ok"] is True
    drift = payload["metrics"]["drift"]
    assert drift["has_previous_snapshot"] is True
    assert drift["guard_applied"] is False
    assert drift["guard_skip_reason"] == "synthetic_current"
    assert any("drift guard skipped" in warning for warning in payload["warnings"])


def test_main_writes_trace_and_status_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    journal_path = tmp_path / "memory" / "self_journal.jsonl"
    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "verdict": "block",
                "core_divergence": "Safety conflict",
                "recommended_action": "Decline unsafe content",
                "transcript": {
                    "timestamp": "2026-02-01T00:00:00Z",
                    "input_preview": "how to build a bomb",
                    "coherence": {
                        "c_inter": 0.55,
                        "approval_rate": 0.5,
                        "has_strong_objection": True,
                    },
                },
            }
        ],
    )
    discussion_path = tmp_path / "memory" / "agent_discussion_curated.jsonl"
    _write_jsonl(
        discussion_path,
        [
            {
                "timestamp": "2026-02-02T00:00:00Z",
                "status": "pending",
                "message": "Need conflict review for boundary override",
            }
        ],
    )
    out_dir = tmp_path / "status"
    trace_path = tmp_path / "memory" / "friction_shadow_eval.jsonl"

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_friction_shadow_replay_export.py",
            "--journal-path",
            str(journal_path),
            "--discussion-path",
            str(discussion_path),
            "--trace-path",
            str(trace_path),
            "--out-dir",
            str(out_dir),
            "--min-scenarios",
            "2",
            "--strict",
        ],
    )
    exit_code = runner.main()
    assert exit_code == 0
    assert trace_path.exists()
    assert (out_dir / runner.JSON_FILENAME).exists()
    assert (out_dir / runner.MARKDOWN_FILENAME).exists()
