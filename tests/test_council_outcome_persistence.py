"""Tests for tonesoul.council.outcome_persistence — all pure helpers."""
from __future__ import annotations

import json
import os

import pytest

from tonesoul.council.outcome_persistence import (
    OutcomeRecord,
    OutcomeSignal,
    _resolve_outcome_path,
    _strip_ignored_paths,
    _utc_now_iso,
    build_outcome_record,
    compute_verdict_fingerprint,
    derive_alignment_judgment,
    persist_outcome_record,
)


# ── _utc_now_iso ──────────────────────────────────────────────────────────────

class TestUtcNowIso:
    def test_returns_string(self):
        assert isinstance(_utc_now_iso(), str)

    def test_ends_with_z(self):
        assert _utc_now_iso().endswith("Z")

    def test_parseable(self):
        from datetime import datetime
        ts = _utc_now_iso()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ── OutcomeSignal validation ──────────────────────────────────────────────────

class TestOutcomeSignal:
    def test_valid_signal_source(self):
        sig = OutcomeSignal(signal_source="explicit_feedback")
        assert sig.signal_source == "explicit_feedback"

    def test_invalid_signal_source_raises(self):
        with pytest.raises(ValueError, match="signal_source"):
            OutcomeSignal(signal_source="bad_source")

    def test_all_valid_sources_accepted(self):
        for src in ("explicit_feedback", "follow_up_message", "session_close",
                    "external_audit", "synthetic"):
            sig = OutcomeSignal(signal_source=src)
            assert sig.signal_source == src

    def test_defaults_are_none(self):
        sig = OutcomeSignal()
        assert sig.user_accept is None
        assert sig.user_reject is None
        assert sig.user_correction is None
        assert sig.detected_harm is None


# ── OutcomeRecord validation ──────────────────────────────────────────────────

def _make_signal(signal: str) -> OutcomeSignal:
    return OutcomeSignal(
        user_accept=True if signal == "accept" else None,
        first_signal_at="2026-01-01T00:00:00Z",
        last_signal_at="2026-01-01T00:00:00Z",
    )


class TestOutcomeRecord:
    def test_valid_accept_record(self):
        record = OutcomeRecord(
            verdict_fingerprint="sha256:abc123",
            signal="accept",
            outcome_signal=_make_signal("accept"),
            alignment_judgment="aligned",
            judgment_basis="user_accept",
        )
        assert record.signal == "accept"

    def test_missing_fingerprint_raises(self):
        with pytest.raises(ValueError, match="verdict_fingerprint"):
            OutcomeRecord(
                verdict_fingerprint="",
                signal="accept",
                outcome_signal=_make_signal("accept"),
                alignment_judgment="aligned",
                judgment_basis="user_accept",
            )

    def test_invalid_signal_raises(self):
        with pytest.raises(ValueError, match="signal must be"):
            OutcomeRecord(
                verdict_fingerprint="sha256:abc",
                signal="unknown_signal",
                outcome_signal=_make_signal("accept"),
                alignment_judgment="aligned",
                judgment_basis="user_accept",
            )

    def test_invalid_alignment_raises(self):
        with pytest.raises(ValueError, match="alignment_judgment must be"):
            OutcomeRecord(
                verdict_fingerprint="sha256:abc",
                signal="accept",
                outcome_signal=_make_signal("accept"),
                alignment_judgment="great",
                judgment_basis="user_accept",
            )

    def test_invalid_judgment_basis_raises(self):
        with pytest.raises(ValueError, match="judgment_basis must be"):
            OutcomeRecord(
                verdict_fingerprint="sha256:abc",
                signal="accept",
                outcome_signal=_make_signal("accept"),
                alignment_judgment="aligned",
                judgment_basis="bad_basis",
            )

    def test_to_dict_returns_dict(self):
        record = OutcomeRecord(
            verdict_fingerprint="sha256:abc",
            signal="reject",
            outcome_signal=_make_signal("accept"),
            alignment_judgment="misaligned",
            judgment_basis="user_reject",
        )
        d = record.to_dict()
        assert isinstance(d, dict)
        assert d["signal"] == "reject"
        assert d["alignment_judgment"] == "misaligned"


# ── _strip_ignored_paths ──────────────────────────────────────────────────────

class TestStripIgnoredPaths:
    def test_removes_transcript_timestamp(self):
        obj = {"transcript": {"timestamp": "2026-01-01", "verdict": "approve"}}
        result = _strip_ignored_paths(obj)
        assert "timestamp" not in result["transcript"]
        assert result["transcript"]["verdict"] == "approve"

    def test_removes_recorded_at_at_top_level(self):
        obj = {"recorded_at": "2026-01-01", "signal": "accept"}
        result = _strip_ignored_paths(obj)
        assert "recorded_at" not in result
        assert result["signal"] == "accept"

    def test_non_dict_passthrough(self):
        assert _strip_ignored_paths("hello") == "hello"
        assert _strip_ignored_paths(42) == 42

    def test_list_passthrough(self):
        obj = {"items": [1, 2, 3]}
        result = _strip_ignored_paths(obj)
        assert result["items"] == [1, 2, 3]

    def test_empty_dict_unchanged(self):
        assert _strip_ignored_paths({}) == {}

    def test_nested_transcript_generated_at_removed(self):
        obj = {"transcript": {"generated_at": "now", "content": "x"}}
        result = _strip_ignored_paths(obj)
        assert "generated_at" not in result["transcript"]


# ── compute_verdict_fingerprint ───────────────────────────────────────────────

class TestComputeVerdictFingerprint:
    def test_returns_sha256_prefix(self):
        fp = compute_verdict_fingerprint({"verdict": "approve"})
        assert fp.startswith("sha256:")

    def test_deterministic(self):
        payload = {"verdict": "refine", "coherence": 0.7}
        fp1 = compute_verdict_fingerprint(payload)
        fp2 = compute_verdict_fingerprint(payload)
        assert fp1 == fp2

    def test_different_payloads_different_fingerprints(self):
        fp1 = compute_verdict_fingerprint({"verdict": "approve"})
        fp2 = compute_verdict_fingerprint({"verdict": "block"})
        assert fp1 != fp2

    def test_strips_timestamp_before_hashing(self):
        payload_with_ts = {"verdict": "approve", "transcript": {"timestamp": "2026-01-01"}}
        payload_no_ts = {"verdict": "approve", "transcript": {}}
        assert compute_verdict_fingerprint(payload_with_ts) == compute_verdict_fingerprint(payload_no_ts)

    def test_custom_digest_length(self):
        fp = compute_verdict_fingerprint({"x": 1}, digest_length=8)
        # "sha256:" + 8 hex chars = 15 chars total
        assert len(fp) == 15

    def test_full_digest_length(self):
        fp = compute_verdict_fingerprint({"x": 1}, digest_length=64)
        assert len(fp) == 71  # "sha256:" (7) + 64


# ── derive_alignment_judgment ─────────────────────────────────────────────────

class TestDeriveAlignmentJudgment:
    def test_accept_gives_aligned(self):
        j, b = derive_alignment_judgment("accept")
        assert j == "aligned"
        assert b == "user_accept"

    def test_reject_gives_misaligned(self):
        j, b = derive_alignment_judgment("reject")
        assert j == "misaligned"
        assert b == "user_reject"

    def test_correction_gives_misaligned(self):
        j, b = derive_alignment_judgment("correction")
        assert j == "misaligned"
        assert b == "user_correction"

    def test_harm_gives_misaligned(self):
        j, b = derive_alignment_judgment("harm")
        assert j == "misaligned"
        assert b == "detected_harm"

    def test_unknown_signal_raises(self):
        with pytest.raises(ValueError, match="unknown signal"):
            derive_alignment_judgment("invalid")


# ── build_outcome_record ──────────────────────────────────────────────────────

class TestBuildOutcomeRecord:
    def test_accept_signal(self):
        record = build_outcome_record(
            verdict_fingerprint="sha256:abc123",
            signal="accept",
        )
        assert record.signal == "accept"
        assert record.alignment_judgment == "aligned"
        assert record.outcome_signal.user_accept is True
        assert record.outcome_signal.user_reject is None

    def test_correction_signal_with_text(self):
        record = build_outcome_record(
            verdict_fingerprint="sha256:abc",
            signal="correction",
            correction_text="You should have said X",
        )
        assert record.outcome_signal.user_correction == "You should have said X"
        assert record.judgment_basis == "user_correction"

    def test_harm_signal(self):
        record = build_outcome_record(
            verdict_fingerprint="sha256:abc",
            signal="harm",
            harm_description="dangerous output",
        )
        assert record.outcome_signal.detected_harm == "dangerous output"

    def test_optional_fields_passed_through(self):
        record = build_outcome_record(
            verdict_fingerprint="sha256:abc",
            signal="reject",
            intent_id="intent-001",
            verdict_type="BLOCK",
            epistemic_label_status="uncertain",
            epistemic_label_refusal_eligible=True,
        )
        assert record.intent_id == "intent-001"
        assert record.verdict_type == "BLOCK"
        assert record.epistemic_label_status == "uncertain"
        assert record.epistemic_label_refusal_eligible is True

    def test_schema_version_set(self):
        record = build_outcome_record(verdict_fingerprint="sha256:abc", signal="accept")
        assert record.schema_version.startswith("v0b")


# ── _resolve_outcome_path ─────────────────────────────────────────────────────

class TestResolveOutcomePath:
    def test_env_var_override(self, monkeypatch, tmp_path):
        override = str(tmp_path / "custom.jsonl")
        monkeypatch.setenv("TONESOUL_OUTCOME_PATH", override)
        assert str(_resolve_outcome_path()) == override

    def test_surface_parameter(self, monkeypatch):
        monkeypatch.delenv("TONESOUL_OUTCOME_PATH", raising=False)
        result = _resolve_outcome_path(surface="/tmp/test.jsonl")
        assert str(result) == "/tmp/test.jsonl"

    def test_default_path(self, monkeypatch):
        monkeypatch.delenv("TONESOUL_OUTCOME_PATH", raising=False)
        result = _resolve_outcome_path()
        assert str(result).endswith("council_outcomes.jsonl")


# ── persist_outcome_record ────────────────────────────────────────────────────

class TestPersistOutcomeRecord:
    def test_writes_jsonl_line(self, tmp_path, monkeypatch):
        monkeypatch.delenv("TONESOUL_OUTCOME_PATH", raising=False)
        output = tmp_path / "outcomes.jsonl"
        record = build_outcome_record(verdict_fingerprint="sha256:abc", signal="accept")
        meta = persist_outcome_record(record, surface=str(output))

        assert meta["status"] == "stored"
        assert meta["signal"] == "accept"
        assert meta["alignment_judgment"] == "aligned"
        assert output.exists()
        line = output.read_text()
        parsed = json.loads(line.strip())
        assert parsed["signal"] == "accept"

    def test_appends_multiple_records(self, tmp_path, monkeypatch):
        monkeypatch.delenv("TONESOUL_OUTCOME_PATH", raising=False)
        output = tmp_path / "outcomes.jsonl"
        for signal in ("accept", "reject"):
            r = build_outcome_record(verdict_fingerprint="sha256:abc", signal=signal)
            persist_outcome_record(r, surface=str(output))

        lines = [l for l in output.read_text().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_creates_parent_dirs(self, tmp_path, monkeypatch):
        monkeypatch.delenv("TONESOUL_OUTCOME_PATH", raising=False)
        output = tmp_path / "deep" / "nested" / "out.jsonl"
        r = build_outcome_record(verdict_fingerprint="sha256:abc", signal="accept")
        persist_outcome_record(r, surface=str(output))
        assert output.exists()
