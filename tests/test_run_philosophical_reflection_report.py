from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_philosophical_reflection_report as reflection_runner


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_build_report_returns_warning_when_sources_are_missing(tmp_path: Path) -> None:
    payload = reflection_runner.build_report(
        journal_path=tmp_path / "missing_journal.jsonl",
        discussion_path=tmp_path / "missing_discussion.jsonl",
        tension_threshold=0.75,
    )
    assert payload["overall_ok"] is True
    assert payload["metrics"]["combined_entry_count"] == 0
    assert payload["metrics"]["journal_entry_count"] == 0
    assert payload["metrics"]["discussion_entry_count"] == 0
    assert payload["issues"] == []
    assert payload["warnings"]


def test_build_report_aggregates_conflict_choice_and_tension_signals(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"

    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "verdict": "approve",
                "human_summary": "Routine response.",
                "tension": 0.2,
            },
            {
                "timestamp": "2026-02-01T00:01:00Z",
                "verdict": "block",
                "core_divergence": "High-value conflict around safety boundary.",
                "recommended_action": "Refuse execution and preserve ethical boundary.",
                "transcript": {
                    "semantic_tension": {
                        "adjusted_tension": 0.9,
                    }
                },
            },
        ],
    )

    _write_jsonl(
        discussion_path,
        [
            {
                "timestamp": "2026-02-01T00:02:00Z",
                "topic": "value-conflict",
                "status": "pending",
                "message": "I choose to reject blind obedience and keep ethical reflection.",
            },
            {
                "timestamp": "2026-02-01T00:03:00Z",
                "topic": "value-conflict",
                "status": "resolved",
                "message": "Decision aligned after council review.",
            },
            {
                "timestamp": "2026-02-01T00:04:00Z",
                "topic": "safety-boundary",
                "status": "blocked",
                "message": "Boundary friction remains high.",
                "tension_score": 0.82,
            },
        ],
    )

    payload = reflection_runner.build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        tension_threshold=0.75,
    )
    metrics = payload["metrics"]
    quality = payload["quality_signals"]

    assert payload["overall_ok"] is True
    assert metrics["combined_entry_count"] == 5
    assert metrics["journal_entry_count"] == 2
    assert metrics["discussion_entry_count"] == 3
    assert metrics["conflict_event_count"] >= 3
    assert metrics["choice_event_count"] >= 2
    assert metrics["tension_event_count"] >= 2
    assert metrics["unresolved_topic_count"] == 1
    assert metrics["topic_count"] == 2
    assert quality["identity_choice_index"] > 0.0
    assert "safety-boundary" in payload["unresolved_topics"]
    assert payload["friction_points"]


def test_main_strict_returns_non_zero_on_invalid_json_lines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    out_dir = tmp_path / "status"

    journal_path.write_text(
        '{"timestamp":"2026-02-01T00:00:00Z","verdict":"block"}\n{"broken":\n',
        encoding="utf-8",
    )
    _write_jsonl(
        discussion_path,
        [{"timestamp": "2026-02-01T00:00:01Z", "topic": "t", "status": "pending", "message": "x"}],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_philosophical_reflection_report.py",
            "--journal-path",
            str(journal_path),
            "--discussion-path",
            str(discussion_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )

    exit_code = reflection_runner.main()
    assert exit_code == 1
    assert (out_dir / reflection_runner.JSON_FILENAME).exists()
    assert (out_dir / reflection_runner.MARKDOWN_FILENAME).exists()


def test_build_report_uses_adaptive_threshold_when_distribution_is_low(tmp_path: Path) -> None:
    journal_path = tmp_path / "self_journal.jsonl"
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"

    _write_jsonl(
        journal_path,
        [
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "verdict": "declare_stance",
                "transcript": {
                    "tension_engine": {"signals": {"text_tension": 0.32, "t_ecs": 0.12}}
                },
            },
            {
                "timestamp": "2026-02-01T00:01:00Z",
                "verdict": "declare_stance",
                "transcript": {
                    "tension_engine": {"signals": {"text_tension": 0.34, "t_ecs": 0.14}}
                },
            },
            {
                "timestamp": "2026-02-01T00:02:00Z",
                "verdict": "declare_stance",
                "transcript": {
                    "tension_engine": {"signals": {"text_tension": 0.36, "t_ecs": 0.16}}
                },
            },
        ],
    )
    _write_jsonl(
        discussion_path,
        [
            {
                "timestamp": "2026-02-01T00:03:00Z",
                "topic": "adaptive-threshold",
                "status": "resolved",
            }
        ],
    )

    payload = reflection_runner.build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        tension_threshold=0.75,
    )
    assert payload["inputs"]["tension_threshold_mode"] == "adaptive_p85"
    assert payload["inputs"]["tension_threshold_effective"] < 0.75
    assert payload["metrics"]["tension_event_count"] >= 1
