"""Tests for tonesoul.council.outcome_persistence — v0b Bucket A.

Coverage:
- VALID_* frozensets cover the spec's enums
- OutcomeRecord validation rejects bad input
- derive_alignment_judgment maps each signal correctly
- build_outcome_record populates the right outcome_signal field per signal type
- persist_outcome_record writes a parseable JSONL line and is append-safe
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.council.outcome_persistence import (
    VALID_ALIGNMENT_JUDGMENTS,
    VALID_JUDGMENT_BASES,
    VALID_OUTCOME_SIGNALS,
    VALID_SIGNAL_SOURCES,
    OutcomeRecord,
    OutcomeSignal,
    build_outcome_record,
    derive_alignment_judgment,
    persist_outcome_record,
)

# ----- Constants match the spec -----


def test_valid_outcome_signals_match_spec():
    assert VALID_OUTCOME_SIGNALS == frozenset({"accept", "reject", "correction", "harm"})


def test_valid_signal_sources_match_spec():
    assert VALID_SIGNAL_SOURCES == frozenset(
        {"explicit_feedback", "follow_up_message", "session_close", "external_audit"}
    )


def test_valid_alignment_judgments_match_spec():
    assert VALID_ALIGNMENT_JUDGMENTS == frozenset({"aligned", "misaligned", "ambiguous", "unknown"})


def test_valid_judgment_bases_match_spec():
    assert VALID_JUDGMENT_BASES == frozenset(
        {"user_accept", "user_reject", "user_correction", "detected_harm", "timeout"}
    )


# ----- derive_alignment_judgment -----


def test_derive_accept():
    assert derive_alignment_judgment("accept") == ("aligned", "user_accept")


def test_derive_reject():
    assert derive_alignment_judgment("reject") == ("misaligned", "user_reject")


def test_derive_correction():
    assert derive_alignment_judgment("correction") == ("misaligned", "user_correction")


def test_derive_harm():
    assert derive_alignment_judgment("harm") == ("misaligned", "detected_harm")


def test_derive_unknown_signal_raises():
    with pytest.raises(ValueError):
        derive_alignment_judgment("bogus")


# ----- OutcomeSignal validation -----


def test_outcome_signal_rejects_invalid_source():
    with pytest.raises(ValueError):
        OutcomeSignal(signal_source="random_string")


def test_outcome_signal_defaults_are_null():
    sig = OutcomeSignal()
    assert sig.user_accept is None
    assert sig.user_reject is None
    assert sig.user_correction is None
    assert sig.detected_harm is None


# ----- OutcomeRecord validation -----


def test_outcome_record_requires_fingerprint():
    with pytest.raises(ValueError):
        OutcomeRecord(
            verdict_fingerprint="",
            signal="accept",
            outcome_signal=OutcomeSignal(),
            alignment_judgment="aligned",
            judgment_basis="user_accept",
        )


def test_outcome_record_rejects_bad_signal():
    with pytest.raises(ValueError):
        OutcomeRecord(
            verdict_fingerprint="sha256:abc",
            signal="meh",
            outcome_signal=OutcomeSignal(),
            alignment_judgment="aligned",
            judgment_basis="user_accept",
        )


def test_outcome_record_rejects_bad_alignment_judgment():
    with pytest.raises(ValueError):
        OutcomeRecord(
            verdict_fingerprint="sha256:abc",
            signal="accept",
            outcome_signal=OutcomeSignal(),
            alignment_judgment="great",
            judgment_basis="user_accept",
        )


def test_outcome_record_rejects_bad_judgment_basis():
    with pytest.raises(ValueError):
        OutcomeRecord(
            verdict_fingerprint="sha256:abc",
            signal="accept",
            outcome_signal=OutcomeSignal(),
            alignment_judgment="aligned",
            judgment_basis="vibes",
        )


# ----- build_outcome_record signal-specific population -----


def test_build_record_accept_populates_user_accept():
    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="accept",
    )
    assert record.outcome_signal.user_accept is True
    assert record.outcome_signal.user_reject is None
    assert record.outcome_signal.user_correction is None
    assert record.outcome_signal.detected_harm is None
    assert record.alignment_judgment == "aligned"


def test_build_record_reject_populates_user_reject():
    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="reject",
    )
    assert record.outcome_signal.user_reject is True
    assert record.outcome_signal.user_accept is None
    assert record.alignment_judgment == "misaligned"
    assert record.judgment_basis == "user_reject"


def test_build_record_correction_carries_text():
    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="correction",
        correction_text="The capital of Australia is Canberra, not Sydney.",
    )
    assert record.outcome_signal.user_correction == (
        "The capital of Australia is Canberra, not Sydney."
    )
    assert record.alignment_judgment == "misaligned"
    assert record.judgment_basis == "user_correction"


def test_build_record_harm_carries_description():
    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="harm",
        harm_description="User followed dosage advice and was hospitalized.",
    )
    assert record.outcome_signal.detected_harm == (
        "User followed dosage advice and was hospitalized."
    )
    assert record.alignment_judgment == "misaligned"
    assert record.judgment_basis == "detected_harm"


def test_build_record_carries_optional_metadata():
    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="accept",
        intent_id="task:42",
        verdict_type="APPROVE",
        epistemic_label_status="retrieved",
        epistemic_label_refusal_eligible=False,
        signal_source="follow_up_message",
    )
    assert record.intent_id == "task:42"
    assert record.verdict_type == "APPROVE"
    assert record.epistemic_label_status == "retrieved"
    assert record.epistemic_label_refusal_eligible is False
    assert record.outcome_signal.signal_source == "follow_up_message"


# ----- persist_outcome_record file behavior -----


def test_persist_writes_jsonl_line(tmp_path: Path, monkeypatch):
    target = tmp_path / "outcomes.jsonl"
    monkeypatch.setenv("TONESOUL_OUTCOME_PATH", str(target))

    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="accept",
    )
    result = persist_outcome_record(record)

    assert result["status"] == "stored"
    assert result["surface"] == str(target)
    assert result["alignment_judgment"] == "aligned"
    assert target.exists()

    lines = target.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["verdict_fingerprint"] == "sha256:abc"
    assert parsed["alignment_judgment"] == "aligned"
    assert parsed["outcome_signal"]["user_accept"] is True


def test_persist_is_append_only(tmp_path: Path, monkeypatch):
    target = tmp_path / "outcomes.jsonl"
    monkeypatch.setenv("TONESOUL_OUTCOME_PATH", str(target))

    for signal in ("accept", "reject", "correction"):
        record = build_outcome_record(
            verdict_fingerprint=f"sha256:{signal}",
            signal=signal,
            correction_text="x" if signal == "correction" else None,
        )
        persist_outcome_record(record)

    lines = target.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3
    parsed = [json.loads(line) for line in lines]
    assert [p["signal"] for p in parsed] == ["accept", "reject", "correction"]


def test_persist_creates_parent_directory(tmp_path: Path, monkeypatch):
    nested = tmp_path / "a" / "b" / "outcomes.jsonl"
    monkeypatch.setenv("TONESOUL_OUTCOME_PATH", str(nested))

    record = build_outcome_record(
        verdict_fingerprint="sha256:abc",
        signal="accept",
    )
    persist_outcome_record(record)

    assert nested.exists()
