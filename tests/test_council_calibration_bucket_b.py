"""Tests for tonesoul.council.calibration_bucket_b — pure helpers (no council run)."""
from __future__ import annotations

import json
from datetime import datetime

import pytest

from tonesoul.council.calibration_bucket_b import (
    _audit_adversarial,
    _audit_anti_pattern_3,
    _canonical_key,
    _epistemic_label_status,
    _utc_now_iso,
    build_calibration_table,
    bucket_b_equal,
    derive_alignment_judgment_v0b,
    derive_baseline_regime,
    join_verdicts_with_outcomes,
    load_corpus,
    load_outcomes,
)


# ── _utc_now_iso ──────────────────────────────────────────────────────────────

class TestUtcNowIso:
    def test_returns_string(self):
        assert isinstance(_utc_now_iso(), str)

    def test_ends_with_z(self):
        assert _utc_now_iso().endswith("Z")

    def test_parseable(self):
        ts = _utc_now_iso()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ── load_corpus / load_outcomes ───────────────────────────────────────────────

class TestLoadCorpus:
    def test_loads_valid_jsonl(self, tmp_path):
        f = tmp_path / "corpus.jsonl"
        f.write_text(
            json.dumps({"draft_output": "Hello", "category": "greeting"}) + "\n"
            + json.dumps({"draft_output": "World", "category": "test"}) + "\n",
            encoding="utf-8",
        )
        entries = load_corpus(f)
        assert len(entries) == 2
        assert entries[0]["category"] == "greeting"

    def test_skips_blank_lines(self, tmp_path):
        f = tmp_path / "corpus.jsonl"
        f.write_text(
            json.dumps({"draft_output": "a"}) + "\n\n" + json.dumps({"draft_output": "b"}) + "\n",
            encoding="utf-8",
        )
        entries = load_corpus(f)
        assert len(entries) == 2


class TestLoadOutcomes:
    def test_returns_empty_for_missing_file(self, tmp_path):
        result = load_outcomes(tmp_path / "missing.jsonl")
        assert result == []

    def test_loads_valid_records(self, tmp_path):
        f = tmp_path / "outcomes.jsonl"
        rec = {"verdict_fingerprint": "abc", "signal": "accept"}
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        records = load_outcomes(f)
        assert len(records) == 1
        assert records[0]["verdict_fingerprint"] == "abc"

    def test_empty_file_returns_empty(self, tmp_path):
        f = tmp_path / "outcomes.jsonl"
        f.write_text("", encoding="utf-8")
        assert load_outcomes(f) == []


# ── derive_baseline_regime ────────────────────────────────────────────────────

class TestDeriveBaselineRegime:
    def _outcome(self, source: str) -> dict:
        return {"outcome_signal": {"signal_source": source}}

    def test_all_synthetic(self):
        outcomes = [self._outcome("synthetic")] * 3
        assert derive_baseline_regime(outcomes) == "synthetic"

    def test_all_real(self):
        outcomes = [self._outcome("real")] * 2
        assert derive_baseline_regime(outcomes) == "real"

    def test_mixed(self):
        outcomes = [self._outcome("synthetic"), self._outcome("real")]
        assert derive_baseline_regime(outcomes) == "mixed"

    def test_no_source_unknown(self):
        outcomes = [{"outcome_signal": {}}]
        assert derive_baseline_regime(outcomes) == "unknown"

    def test_empty_outcomes_unknown(self):
        assert derive_baseline_regime([]) == "unknown"

    def test_missing_outcome_signal_unknown(self):
        assert derive_baseline_regime([{}]) == "unknown"


# ── derive_alignment_judgment_v0b ─────────────────────────────────────────────

class TestDeriveAlignmentJudgmentV0b:
    # block verdicts
    def test_block_accept_unconfirmed(self):
        j, b = derive_alignment_judgment_v0b("accept", "block")
        assert j == "unconfirmed"
        assert b == "block_silently_accepted"

    def test_block_reject_misaligned(self):
        j, b = derive_alignment_judgment_v0b("reject", "block")
        assert j == "misaligned"

    def test_block_correction_aligned(self):
        j, b = derive_alignment_judgment_v0b("correction", "block")
        assert j == "aligned"

    def test_block_harm_misaligned(self):
        j, b = derive_alignment_judgment_v0b("harm", "block")
        assert j == "misaligned"

    # refine verdicts
    def test_refine_accept_aligned(self):
        j, b = derive_alignment_judgment_v0b("accept", "refine")
        assert j == "aligned"

    def test_refine_correction_partial(self):
        j, b = derive_alignment_judgment_v0b("correction", "refine")
        assert j == "partial_aligned"

    def test_refine_reject_misaligned(self):
        j, b = derive_alignment_judgment_v0b("reject", "refine")
        assert j == "misaligned"

    def test_refine_harm_misaligned(self):
        j, b = derive_alignment_judgment_v0b("harm", "refine")
        assert j == "misaligned"

    # declare_stance
    def test_declare_stance_any_signal_declared(self):
        j, b = derive_alignment_judgment_v0b("accept", "declare_stance")
        assert j == "declared"
        j2, _ = derive_alignment_judgment_v0b("reject", "declare_stance")
        assert j2 == "declared"

    # approve (default path)
    def test_approve_accept_aligned(self):
        j, b = derive_alignment_judgment_v0b("accept", "approve")
        assert j == "aligned"

    def test_approve_reject_misaligned(self):
        j, _ = derive_alignment_judgment_v0b("reject", "approve")
        assert j == "misaligned"

    def test_approve_harm_misaligned(self):
        j, _ = derive_alignment_judgment_v0b("harm", "approve")
        assert j == "misaligned"

    def test_unknown_signal_unknown_judgment(self):
        j, b = derive_alignment_judgment_v0b("weird_signal", "approve")
        assert j == "unknown"
        assert b == "unmapped_signal"


# ── _epistemic_label_status ───────────────────────────────────────────────────

class TestEpistemicLabelStatus:
    def test_returns_status_when_present(self):
        verdict = {"epistemic_label": {"status": "retrieved"}}
        assert _epistemic_label_status(verdict) == "retrieved"

    def test_returns_none_when_no_label(self):
        assert _epistemic_label_status({}) is None

    def test_returns_none_when_not_dict(self):
        verdict = {"epistemic_label": "not-a-dict"}
        assert _epistemic_label_status(verdict) is None

    def test_returns_none_when_no_status_key(self):
        verdict = {"epistemic_label": {"weight": "primary"}}
        assert _epistemic_label_status(verdict) is None


# ── join_verdicts_with_outcomes ───────────────────────────────────────────────

class TestJoinVerdictsWithOutcomes:
    def _recon(self, fp: str, verdict_type: str = "approve", cat: str = "test") -> dict:
        return {
            "verdict_fingerprint": fp,
            "intent_id": f"smoke:{cat}:0",
            "verdict_dict": {"verdict": verdict_type},
            "category": cat,
            "suggested_signal": "accept",
            "entry": {},
        }

    def _outcome(self, fp: str, signal: str = "accept") -> dict:
        return {
            "verdict_fingerprint": fp,
            "signal": signal,
            "alignment_judgment": "aligned",
            "judgment_basis": "user_accept",
            "outcome_signal": {"signal_source": "synthetic"},
        }

    def test_matching_fingerprint_joins(self):
        recon = [self._recon("fp1")]
        outcomes = [self._outcome("fp1")]
        result = join_verdicts_with_outcomes(recon, outcomes)
        assert result["join_summary"]["joined"] == 1

    def test_no_match_orphan_verdict(self):
        recon = [self._recon("fp1")]
        outcomes = [self._outcome("fp2")]
        result = join_verdicts_with_outcomes(recon, outcomes)
        assert result["join_summary"]["joined"] == 0
        assert result["join_summary"]["orphan_verdicts"] == 1
        assert result["join_summary"]["orphan_outcomes"] == 1

    def test_row_has_bucket_b_judgment(self):
        recon = [self._recon("fp1", verdict_type="block")]
        outcomes = [self._outcome("fp1", signal="accept")]
        result = join_verdicts_with_outcomes(recon, outcomes)
        row = result["rows"][0]
        assert row["bucket_b_judgment"] == "unconfirmed"

    def test_empty_inputs(self):
        result = join_verdicts_with_outcomes([], [])
        assert result["join_summary"]["joined"] == 0

    def test_totals_in_summary(self):
        recon = [self._recon("fp1"), self._recon("fp2")]
        outcomes = [self._outcome("fp1")]
        result = join_verdicts_with_outcomes(recon, outcomes)
        assert result["join_summary"]["verdicts_total"] == 2
        assert result["join_summary"]["outcomes_total"] == 1


# ── _canonical_key ────────────────────────────────────────────────────────────

class TestCanonicalKey:
    def test_deterministic(self):
        key = {"verdict_type": "approve", "signal": "accept", "epistemic_label_status": None}
        assert _canonical_key(key) == _canonical_key(key)

    def test_order_independent(self):
        k1 = {"a": 1, "b": 2}
        k2 = {"b": 2, "a": 1}
        assert _canonical_key(k1) == _canonical_key(k2)

    def test_different_keys_differ(self):
        k1 = {"verdict_type": "approve"}
        k2 = {"verdict_type": "block"}
        assert _canonical_key(k1) != _canonical_key(k2)


# ── build_calibration_table ───────────────────────────────────────────────────

class TestBuildCalibrationTable:
    def _row(self, verdict_type="approve", signal="accept", judgment="aligned", source="synthetic", label=None):
        return {
            "verdict_type": verdict_type,
            "signal": signal,
            "epistemic_label_status": label,
            "bucket_b_judgment": judgment,
            "signal_source": source,
        }

    def test_empty_rows_empty_table(self):
        assert build_calibration_table([]) == []

    def test_single_row_produces_entry(self):
        table = build_calibration_table([self._row()])
        assert len(table) == 1
        assert table[0]["count"] == 1

    def test_alignment_rate_computed(self):
        rows = [self._row(), self._row()]  # 2 aligned
        table = build_calibration_table(rows)
        assert table[0]["alignment_rate"] == pytest.approx(1.0)

    def test_alignment_rate_partial(self):
        rows = [self._row(judgment="aligned"), self._row(judgment="misaligned")]
        table = build_calibration_table(rows)
        assert table[0]["alignment_rate"] == pytest.approx(0.5)

    def test_groups_by_key(self):
        rows = [
            self._row(verdict_type="approve", signal="accept"),
            self._row(verdict_type="block", signal="accept"),
        ]
        table = build_calibration_table(rows)
        assert len(table) == 2

    def test_sorted_by_canonical_key(self):
        rows = [
            self._row(verdict_type="block", signal="accept"),
            self._row(verdict_type="approve", signal="accept"),
        ]
        table = build_calibration_table(rows)
        keys = [t["key"]["verdict_type"] for t in table]
        assert keys == sorted(keys)

    def test_regime_synthetic_when_all_synthetic(self):
        rows = [self._row(source="synthetic")] * 3
        table = build_calibration_table(rows)
        assert table[0]["baseline_regime"] == "synthetic"

    def test_regime_mixed_when_both(self):
        rows = [self._row(source="synthetic"), self._row(source="real")]
        table = build_calibration_table(rows)
        assert table[0]["baseline_regime"] == "mixed"


# ── _audit_adversarial ────────────────────────────────────────────────────────

class TestAuditAdversarial:
    def _row(self, category="tone_laundering", verdict="approve", judgment="aligned"):
        return {
            "category": category,
            "verdict_type": verdict,
            "bucket_b_judgment": judgment,
            "intent_id": "x",
        }

    def test_no_adversarial_rows(self):
        result = _audit_adversarial([self._row(category="neutral")])
        assert result["entries_analyzed"] == 0

    def test_adversarial_category_counted(self):
        result = _audit_adversarial([self._row()])
        assert result["entries_analyzed"] == 1

    def test_false_approve_counted(self):
        rows = [self._row(verdict="approve", judgment="aligned")]
        result = _audit_adversarial(rows)
        assert result["false_approve_count"] == 1

    def test_non_approve_not_false_approve(self):
        rows = [self._row(verdict="block", judgment="aligned")]
        result = _audit_adversarial(rows)
        assert result["false_approve_count"] == 0

    def test_categories_seen_sorted(self):
        rows = [
            self._row(category="hedging_camouflage"),
            self._row(category="expert_voice"),
        ]
        result = _audit_adversarial(rows)
        assert result["categories_seen"] == sorted(result["categories_seen"])


# ── _audit_anti_pattern_3 ─────────────────────────────────────────────────────

class TestAuditAntiPattern3:
    def _row(self, verdict_type="block", signal="accept", judgment="unconfirmed"):
        return {
            "verdict_type": verdict_type,
            "signal": signal,
            "bucket_b_judgment": judgment,
        }

    def test_block_plus_accept_counted(self):
        result = _audit_anti_pattern_3([self._row()])
        assert result["block_plus_accept_count"] == 1

    def test_reclassified_as_unconfirmed(self):
        result = _audit_anti_pattern_3([self._row(judgment="unconfirmed")])
        assert result["reclassified_as_unconfirmed"] == 1

    def test_non_block_not_counted(self):
        result = _audit_anti_pattern_3([self._row(verdict_type="approve")])
        assert result["block_plus_accept_count"] == 0

    def test_non_accept_not_counted(self):
        result = _audit_anti_pattern_3([self._row(signal="reject")])
        assert result["block_plus_accept_count"] == 0

    def test_note_field_present(self):
        result = _audit_anti_pattern_3([])
        assert "note" in result


# ── bucket_b_equal ────────────────────────────────────────────────────────────

class TestBucketBEqual:
    def _base(self) -> dict:
        return {
            "schema_version": "v0b-bucket-b-1.0.0",
            "generated_at": "2026-01-01T00:00:00Z",
            "inputs": {"corpus_path": "/a", "outcome_path": "/b"},
            "baseline_regime": "synthetic",
            "calibration_table": [{"key": {"verdict_type": "approve"}, "count": 1}],
            "caveat": "test",
        }

    def test_equal_when_same_content(self):
        a = self._base()
        b = self._base()
        assert bucket_b_equal(a, b) is True

    def test_different_generated_at_still_equal(self):
        a = self._base()
        b = self._base()
        b["generated_at"] = "2999-12-31T23:59:59Z"
        assert bucket_b_equal(a, b) is True

    def test_different_inputs_still_equal(self):
        a = self._base()
        b = self._base()
        b["inputs"] = {"corpus_path": "/x", "outcome_path": "/y"}
        assert bucket_b_equal(a, b) is True

    def test_different_calibration_table_not_equal(self):
        a = self._base()
        b = self._base()
        b["calibration_table"] = []
        assert bucket_b_equal(a, b) is False

    def test_different_regime_not_equal(self):
        a = self._base()
        b = self._base()
        b["baseline_regime"] = "real"
        assert bucket_b_equal(a, b) is False
