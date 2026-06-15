from __future__ import annotations

import pytest

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource
from tonesoul.memory.subjectivity_shadow import (
    _classified_count,
    _normalize_profile,
    _rate,
    _reviewed_vow_count,
    _score_candidate,
    _subjectivity_distribution,
    build_subjectivity_shadow_pressure_report,
    build_subjectivity_shadow_report,
)


def _build_db(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    return db, source


def test_shadow_report_tension_profile_promotes_tension_candidate(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    baseline_id = db.append(
        source,
        {
            "title": "Governance note",
            "summary": "governance memory without subjectivity tag",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    tension_id = db.append(
        source,
        {
            "title": "Governance conflict",
            "summary": "governance tension record with unresolved friction",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "source_record_ids": ["stim-001"],
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )

    report = build_subjectivity_shadow_report(
        db,
        query="governance",
        source=source,
        profile="tension_first",
        limit=2,
        candidate_limit=5,
    )

    assert report["baseline_results"][0]["record_id"] == baseline_id
    assert report["shadow_results"][0]["record_id"] == tension_id
    assert report["shadow_results"][0]["shadow_reasons"] == [
        "tension_match",
        "unresolved_tension",
        "linked_source_trace",
    ]
    assert report["metrics"]["shadow_by_subjectivity_layer"]["tension"] == 1


def test_shadow_report_reviewed_vow_profile_promotes_reviewed_vow(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    baseline_id = db.append(
        source,
        {
            "title": "Provenance note",
            "summary": "provenance reminder without review metadata",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    vow_id = db.append(
        source,
        {
            "title": "Provenance commitment",
            "summary": "provenance vow reviewed through operator lane",
            "subjectivity_layer": "vow",
            "layer": "factual",
            "promotion_gate": {
                "status": "approved",
                "reviewed_by": "operator",
                "review_basis": "Repeated reviewed tension.",
            },
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )

    report = build_subjectivity_shadow_report(
        db,
        query="provenance",
        source=source,
        profile="reviewed_vow_first",
        limit=2,
        candidate_limit=5,
    )

    assert report["baseline_results"][0]["record_id"] == baseline_id
    assert report["shadow_results"][0]["record_id"] == vow_id
    assert report["shadow_results"][0]["shadow_reasons"] == [
        "vow_match",
        "reviewed_memory",
        "factual_layer",
    ]
    assert report["delta"]["promoted_ids"] == []


def test_shadow_report_rejects_unknown_profile(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "title": "Memory note",
            "summary": "memory note",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )

    with pytest.raises(ValueError):
        build_subjectivity_shadow_report(db, query="memory", profile="identity_first")


def test_shadow_pressure_report_aggregates_query_level_pressure_metrics(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "title": "Governance note",
            "summary": "governance baseline record",
            "timestamp": "2026-03-10T03:00:00Z",
        },
    )
    db.append(
        source,
        {
            "title": "Governance conflict",
            "summary": "governance unresolved tension",
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
            "source_record_ids": ["stim-003"],
            "timestamp": "2026-03-10T02:00:00Z",
        },
    )
    db.append(
        source,
        {
            "title": "Provenance note",
            "summary": "provenance baseline record",
            "timestamp": "2026-03-10T03:10:00Z",
        },
    )
    db.append(
        source,
        {
            "title": "Provenance commitment",
            "summary": "provenance vow reviewed through operator lane",
            "subjectivity_layer": "vow",
            "layer": "factual",
            "promotion_gate": {
                "status": "approved",
                "reviewed_by": "operator",
                "review_basis": "Repeated reviewed tension.",
            },
            "timestamp": "2026-03-10T02:10:00Z",
        },
    )

    report = build_subjectivity_shadow_pressure_report(
        db,
        queries=["governance", "provenance", "absent"],
        source=source,
        profile="classified_first",
        limit=1,
        candidate_limit=5,
    )

    assert report["metrics"]["query_count"] == 3
    assert report["metrics"]["changed_query_count"] == 2
    assert report["metrics"]["changed_query_rate"] == 0.6667
    assert report["metrics"]["top1_changed_count"] == 2
    assert report["metrics"]["pressure_query_count"] == 2
    assert report["metrics"]["avg_classified_lift"] == 0.6667
    assert report["no_hit_queries"] == ["absent"]
    assert report["queries"][0]["query"] == "governance"


# ── Private helpers ───────────────────────────────────────────────────────────


def test_normalize_profile_accepts_valid_profiles() -> None:
    assert _normalize_profile("classified_first") == "classified_first"
    assert _normalize_profile("TENSION_FIRST") == "tension_first"
    assert _normalize_profile("  reviewed_vow_first  ") == "reviewed_vow_first"


def test_normalize_profile_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="shadow profile"):
        _normalize_profile("identity_first")


def test_subjectivity_distribution_counts_by_layer() -> None:
    rows = [
        {"subjectivity_layer": "tension"},
        {"subjectivity_layer": "vow"},
        {"subjectivity_layer": "tension"},
        {},  # → unclassified
    ]
    dist = _subjectivity_distribution(rows)
    assert dist["tension"] == 2
    assert dist["vow"] == 1
    assert dist["unclassified"] == 1


def test_classified_count_excludes_unclassified() -> None:
    rows = [
        {"subjectivity_layer": "tension"},
        {"subjectivity_layer": "vow"},
        {},  # unclassified
        {"subjectivity_layer": "unclassified"},
    ]
    assert _classified_count(rows) == 2


def test_reviewed_vow_count_only_approved_vows() -> None:
    rows = [
        {"subjectivity_layer": "vow", "promotion_status": "approved"},
        {"subjectivity_layer": "vow", "promotion_status": "candidate"},
        {"subjectivity_layer": "tension", "promotion_status": "approved"},
    ]
    assert _reviewed_vow_count(rows) == 1


def test_rate_zero_denominator_returns_zero() -> None:
    assert _rate(5, 0) == 0.0
    assert _rate(0, 0) == 0.0


def test_rate_normal_calculation() -> None:
    assert _rate(1, 4) == 0.25
    assert _rate(3, 3) == 1.0


def test_score_candidate_classified_first_boosts_classified() -> None:
    row = {"subjectivity_layer": "vow", "promotion_status": "approved"}
    boost, reasons = _score_candidate(row, profile="classified_first")
    assert boost > 0
    assert "classified_subjectivity" in reasons
    assert "reviewed_memory" in reasons


def test_score_candidate_tension_first_boosts_tension_with_source() -> None:
    row = {
        "subjectivity_layer": "tension",
        "unresolved_tension": True,
        "source_record_ids": ["stim-1"],
    }
    boost, reasons = _score_candidate(row, profile="tension_first")
    assert "tension_match" in reasons
    assert "unresolved_tension" in reasons
    assert "linked_source_trace" in reasons


def test_score_candidate_reviewed_vow_first_boosts_reviewed_vow() -> None:
    row = {
        "subjectivity_layer": "vow",
        "promotion_status": "approved",
        "layer": "factual",
    }
    boost, reasons = _score_candidate(row, profile="reviewed_vow_first")
    assert "vow_match" in reasons
    assert "reviewed_memory" in reasons
    assert "factual_layer" in reasons


def test_shadow_report_empty_db_returns_empty_results(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    report = build_subjectivity_shadow_report(
        db, query="nothing", source=source, profile="classified_first"
    )
    assert report["baseline_results"] == []
    assert report["shadow_results"] == []
    assert report["candidate_count"] == 0


def test_shadow_pressure_report_empty_queries(tmp_path) -> None:
    db, source = _build_db(tmp_path)
    report = build_subjectivity_shadow_pressure_report(
        db, queries=[], source=source, profile="classified_first"
    )
    assert report["metrics"]["query_count"] == 0
    assert report["queries"] == []
