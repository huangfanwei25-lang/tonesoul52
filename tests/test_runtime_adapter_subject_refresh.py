from __future__ import annotations

from datetime import datetime

from tonesoul.runtime_adapter_subject_refresh import (
    build_subject_refresh_summary,
    entries_newer_than,
)


def test_entries_newer_than_filters_against_snapshot_marker() -> None:
    marker = datetime.fromisoformat("2026-04-14T12:00:00+00:00")
    entries = [
        {"updated_at": "2026-04-14T11:00:00+00:00", "id": "old"},
        {"updated_at": "2026-04-14T13:00:00+00:00", "id": "new"},
    ]

    fresh = entries_newer_than(
        entries,
        marker_dt=marker,
        parse_dt=datetime.fromisoformat,
    )

    assert [entry["id"] for entry in fresh] == ["new"]


def test_build_subject_refresh_summary_recommends_seed_snapshot() -> None:
    summary = build_subject_refresh_summary(
        subject_snapshots=[],
        checkpoints=[],
        compactions=[
            {
                "updated_at": "2026-04-14T13:00:00+00:00",
                "carry_forward": ["keep packet-first cadence stable"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
            }
        ],
        claims=[],
        routing_summary={"total_events": 1, "dominant_surface": "compaction"},
        project_memory_summary={"focus_topics": ["runtime_adapter", "redis"]},
        risk_posture={"level": "stable"},
        parse_dt=datetime.fromisoformat,
    )

    active_threads = next(
        item for item in summary["field_guidance"] if item["field"] == "active_threads"
    )

    assert summary["status"] == "seed_snapshot"
    assert summary["refresh_recommended"] is True
    assert active_threads["action"] == "may_refresh_directly"
    assert active_threads["candidate_values"] == ["runtime_adapter", "redis"]
    assert "apply_subject_refresh.py" in summary["recommended_command"]


def test_build_subject_refresh_summary_surfaces_manual_review_hazards() -> None:
    summary = build_subject_refresh_summary(
        subject_snapshots=[
            {
                "snapshot_id": "snap-1",
                "updated_at": "2026-04-14T12:00:00+00:00",
                "active_threads": ["runtime_adapter"],
            }
        ],
        checkpoints=[
            {"updated_at": "2026-04-14T13:00:00+00:00"},
        ],
        compactions=[],
        claims=[{"task_id": "shared-lane"}],
        routing_summary={"misroute_signal_count": 1},
        project_memory_summary={"focus_topics": ["runtime_adapter", "redis"]},
        risk_posture={"level": "elevated"},
        parse_dt=datetime.fromisoformat,
    )

    assert summary["status"] == "manual_review"
    assert summary["refresh_recommended"] is False
    assert summary["active_claim_count"] == 1
    assert summary["routing_misroute_signal_count"] == 1
    assert any("active claims" in hazard for hazard in summary["promotion_hazards"])
    assert any("routing ambiguity" in hazard for hazard in summary["promotion_hazards"])
    assert any("Checkpoint-only evidence" in hazard for hazard in summary["promotion_hazards"])
