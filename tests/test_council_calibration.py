"""Tests for council calibration v0a metrics."""

from __future__ import annotations

import json

from tonesoul.council.calibration import (
    compute_agreement_stability,
    compute_internal_self_consistency,
    compute_persistence_coverage,
    compute_suppression_recovery_rate,
    load_stress_test_journal,
    run_calibration_wave,
)


def _make_stress_records():
    return [
        {
            "user_input": "bypass auth",
            "verdict": "block",
            "tension": 0.85,
            "delta_sigma": 0.4,
            "tags": ["security"],
        },
        {
            "user_input": "bypass auth",
            "verdict": "block",
            "tension": 0.85,
            "delta_sigma": 0.4,
            "tags": ["security"],
        },
        {
            "user_input": "bypass auth",
            "verdict": "block",
            "tension": 0.85,
            "delta_sigma": 0.4,
            "tags": ["security"],
        },
        {
            "user_input": "bypass auth",
            "verdict": "caution",
            "tension": 0.85,
            "delta_sigma": 0.4,
            "tags": ["security"],
        },
        {
            "user_input": "hello world",
            "verdict": "approve",
            "tension": 0.1,
            "delta_sigma": 0.05,
            "tags": ["benign"],
        },
        {
            "user_input": "hello world",
            "verdict": "approve",
            "tension": 0.1,
            "delta_sigma": 0.05,
            "tags": ["benign"],
        },
    ]


def _make_persistence_records():
    return [
        {
            "record_id": "cv-1",
            "schema_version": "1.0.0",
            "recorded_at": "2026-04-16T00:00:00Z",
            "agent": "test",
            "input_fingerprint": "fp-aaa",
            "verdict": "approve",
            "coherence": 0.85,
            "has_strong_objection": False,
            "vote_profile": [
                {"perspective": "guardian", "decision": "approve", "confidence": 0.9},
                {"perspective": "analyst", "decision": "approve", "confidence": 0.8},
            ],
            "minority_perspectives": [],
            "grounding_summary": {"has_ungrounded_claims": False, "total_evidence_sources": 2},
        },
        {
            "record_id": "cv-2",
            "schema_version": "1.0.0",
            "recorded_at": "2026-04-16T00:01:00Z",
            "agent": "test",
            "input_fingerprint": "fp-aaa",
            "verdict": "approve",
            "coherence": 0.82,
            "has_strong_objection": False,
            "vote_profile": [
                {"perspective": "guardian", "decision": "approve", "confidence": 0.85},
                {"perspective": "analyst", "decision": "approve", "confidence": 0.75},
            ],
            "minority_perspectives": [],
            "grounding_summary": {"has_ungrounded_claims": False, "total_evidence_sources": 1},
        },
        {
            "record_id": "cv-3",
            "schema_version": "1.0.0",
            "recorded_at": "2026-04-16T00:02:00Z",
            "agent": "test",
            "input_fingerprint": "fp-bbb",
            "verdict": "block",
            "coherence": 0.2,
            "has_strong_objection": True,
            "vote_profile": [
                {"perspective": "guardian", "decision": "object", "confidence": 0.95},
                {"perspective": "analyst", "decision": "concern", "confidence": 0.7},
            ],
            "minority_perspectives": ["analyst"],
            "grounding_summary": {"has_ungrounded_claims": True, "total_evidence_sources": 0},
        },
    ]


# --- agreement_stability ---


def test_agreement_stability_with_stress_data():
    result = compute_agreement_stability([], _make_stress_records())
    assert result["status"] == "computed"
    assert result["groups_analyzed"] == 2
    assert result["sample_count"] == 6
    assert result["mean_dominant_verdict_ratio"] >= 0.5
    assert result["measures"]
    assert result["does_not_measure"]


def test_agreement_stability_with_persistence_data():
    result = compute_agreement_stability(_make_persistence_records(), [])
    assert result["status"] == "computed"
    assert result["groups_analyzed"] >= 1


def test_agreement_stability_empty():
    result = compute_agreement_stability([], [])
    assert result["status"] == "insufficient_data"
    assert result["sample_count"] == 0


# --- internal_self_consistency ---


def test_self_consistency_stress_high_tension_block():
    records = [
        {"user_input": "x", "verdict": "block", "tension": 0.9},
        {"user_input": "y", "verdict": "approve", "tension": 0.1},
    ]
    result = compute_internal_self_consistency([], records)
    assert result["status"] == "computed"
    assert result["consistency_rate"] == 1.0


def test_self_consistency_stress_high_tension_approve_is_inconsistent():
    records = [
        {"user_input": "x", "verdict": "approve", "tension": 0.9},
    ]
    result = compute_internal_self_consistency([], records)
    assert result["consistency_rate"] == 0.0


def test_self_consistency_persistence_objection_approve_inconsistent():
    records = [
        {
            "verdict": "approve",
            "has_strong_objection": True,
            "coherence": 0.3,
            "vote_profile": [],
        },
    ]
    result = compute_internal_self_consistency(records, [])
    assert result["status"] == "computed"
    assert result["inconsistent_count"] >= 1


def test_self_consistency_persistence_high_coherence_approve_consistent():
    records = [
        {
            "verdict": "approve",
            "has_strong_objection": False,
            "coherence": 0.9,
            "vote_profile": [],
        },
    ]
    result = compute_internal_self_consistency(records, [])
    assert result["consistency_rate"] == 1.0


def test_self_consistency_empty():
    result = compute_internal_self_consistency([], [])
    assert result["status"] == "insufficient_data"


# --- suppression_recovery_rate ---


def test_suppression_recovery_in_stress_data():
    records = [
        {"user_input": "A", "verdict": "block"},
        {"user_input": "A", "verdict": "caution"},
        {"user_input": "A", "verdict": "caution"},
        {"user_input": "A", "verdict": "caution"},
    ]
    result = compute_suppression_recovery_rate([], records)
    assert result["status"] == "computed"
    assert result["minority_events"] >= 1
    assert result["recovery_rate"] >= 0.0


def test_suppression_recovery_in_persistence():
    # Persistence records are newest-first; earliest (index -1) had minority,
    # later record (index 0) has no minority = recovery.
    records = [
        {"input_fingerprint": "fp-x", "minority_perspectives": [], "verdict": "approve"},
        {"input_fingerprint": "fp-x", "minority_perspectives": ["critic"], "verdict": "approve"},
    ]
    result = compute_suppression_recovery_rate(records, [])
    assert result["status"] == "computed"
    assert result["recovery_events"] >= 1


def test_suppression_no_minority():
    records = [
        {"user_input": "A", "verdict": "approve"},
        {"user_input": "A", "verdict": "approve"},
    ]
    result = compute_suppression_recovery_rate([], records)
    assert result["status"] == "insufficient_data"


# --- persistence_coverage ---


def test_persistence_coverage_full():
    records = _make_persistence_records()
    result = compute_persistence_coverage(records)
    assert result["status"] == "computed"
    assert result["overall_field_coverage"] >= 0.9
    assert result["sample_count"] == 3


def test_persistence_coverage_partial():
    records = [{"record_id": "cv-1", "verdict": "approve"}]
    result = compute_persistence_coverage(records)
    assert result["status"] == "computed"
    assert result["overall_field_coverage"] < 1.0


def test_persistence_coverage_empty():
    result = compute_persistence_coverage([])
    assert result["status"] == "no_records"


# --- load_stress_test_journal ---


def test_load_stress_journal(tmp_path):
    journal = tmp_path / "test_journal.jsonl"
    lines = [
        json.dumps({"verdict": "block", "tension": 0.9}),
        json.dumps({"verdict": "approve", "tension": 0.1}),
    ]
    journal.write_text("\n".join(lines), encoding="utf-8")
    records = load_stress_test_journal(journal)
    assert len(records) == 2


def test_load_stress_journal_missing(tmp_path):
    records = load_stress_test_journal(tmp_path / "nonexistent.jsonl")
    assert records == []


# --- run_calibration_wave ---


def test_run_calibration_wave_produces_all_metrics(tmp_path):
    journal = tmp_path / "journal.jsonl"
    lines = [
        json.dumps({"user_input": "test", "verdict": "block", "tension": 0.8}),
        json.dumps({"user_input": "test", "verdict": "block", "tension": 0.8}),
    ]
    journal.write_text("\n".join(lines), encoding="utf-8")

    class FakeStore:
        backend_name = "fake"

        def get_council_verdicts(self, n=25):
            return []

    result = run_calibration_wave(store=FakeStore(), stress_journal_path=journal)

    assert result["contract_version"] == "v1"
    assert result["schema_version"] == "v0a"
    assert result["status"] == "v0a_realism_baseline"
    assert "agreement_stability" in result["metrics"]
    assert "internal_self_consistency" in result["metrics"]
    assert "suppression_recovery_rate" in result["metrics"]
    assert "persistence_coverage" in result["metrics"]
    assert result["language_boundary"]["this_is"] == "internal realism baseline"
    assert "outcome calibration" in result["language_boundary"]["this_is_not"]
    assert result["receiver_rule"]
    assert result["v0a_exit_criteria"]
    assert result["v0b_prerequisites"]["note"]


def test_run_calibration_wave_no_composite_score(tmp_path):
    journal = tmp_path / "journal.jsonl"
    journal.write_text("{}\n", encoding="utf-8")

    class FakeStore:
        backend_name = "fake"

        def get_council_verdicts(self, n=25):
            return []

    result = run_calibration_wave(store=FakeStore(), stress_journal_path=journal)

    flat = json.dumps(result)
    assert "realism_score" not in flat
    assert "council_health" not in flat
    assert "composite" not in flat
