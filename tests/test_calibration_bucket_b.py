"""Tests for Phase 864b Layer 2 — Council Calibration v0b Bucket B.

Spec: docs/plans/phase_864b_layer2_bucket_b_2026-04-20.md

The integration tests (adversarial survival + reproducibility) run the
smoke harness fresh into tmp_path so fingerprints are guaranteed to
match at test time. They do not depend on the checked-in
.aegis/council_outcomes_*.jsonl fixtures.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))  # noqa: E402

from tonesoul.council.calibration import run_calibration_wave  # noqa: E402
from tonesoul.council.calibration_bucket_b import (  # noqa: E402
    bucket_b_equal,
    build_calibration_table,
    compute_bucket_b,
    derive_alignment_judgment_v0b,
    derive_baseline_regime,
    load_outcomes,
)

_CORPUS_DIVERSE = REPO_ROOT / "tests/fixtures/outcome_smoke/corpus_2026-04-19.jsonl"
_CORPUS_ADVERSARIAL = REPO_ROOT / "tests/fixtures/outcome_smoke/adversarial_corpus_2026-04-19.jsonl"


def _run_smoke_into(tmp_path: Path, corpus: Path) -> Path:
    """Run the smoke harness against ``corpus``, writing outcomes into ``tmp_path``.

    Returns the outcome JSONL path.
    """
    from scripts.run_outcome_smoke import run_smoke

    outcome_path = tmp_path / "outcomes.jsonl"
    os.environ["TONESOUL_OUTCOME_PATH"] = str(outcome_path)
    run_smoke(corpus, outcome_path)
    return outcome_path


# ---------------------------------------------------------------------------
# Unit tests — small functions
# ---------------------------------------------------------------------------


def test_derive_alignment_block_accept_is_unconfirmed():
    """Anti-pattern #3 fix: block + silent accept must NOT be aligned."""
    judgment, basis = derive_alignment_judgment_v0b("accept", "block")
    assert judgment == "unconfirmed"
    assert basis == "block_silently_accepted"


def test_derive_alignment_approve_accept_is_aligned():
    assert derive_alignment_judgment_v0b("accept", "approve") == ("aligned", "user_accept")


def test_derive_alignment_approve_harm_is_misaligned():
    assert derive_alignment_judgment_v0b("harm", "approve") == ("misaligned", "detected_harm")


def test_derive_alignment_block_correction_is_aligned():
    assert derive_alignment_judgment_v0b("correction", "block") == (
        "aligned",
        "user_accepted_block_offered_alt",
    )


def test_derive_alignment_refine_correction_is_partial():
    assert derive_alignment_judgment_v0b("correction", "refine") == (
        "partial_aligned",
        "refinement_partially_worked",
    )


def test_derive_alignment_declare_stance_is_declared():
    judgment, _ = derive_alignment_judgment_v0b("accept", "declare_stance")
    assert judgment == "declared"


def test_derive_alignment_unmapped_signal_is_unknown():
    judgment, basis = derive_alignment_judgment_v0b("mystery", "approve")
    assert judgment == "unknown"
    assert basis == "unmapped_signal"


def test_derive_baseline_regime_all_synthetic():
    outcomes = [
        {"outcome_signal": {"signal_source": "synthetic"}},
        {"outcome_signal": {"signal_source": "synthetic"}},
    ]
    assert derive_baseline_regime(outcomes) == "synthetic"


def test_derive_baseline_regime_mixed():
    outcomes = [
        {"outcome_signal": {"signal_source": "synthetic"}},
        {"outcome_signal": {"signal_source": "real"}},
    ]
    assert derive_baseline_regime(outcomes) == "mixed"


def test_derive_baseline_regime_unknown_when_absent():
    assert derive_baseline_regime([{"outcome_signal": {}}]) == "unknown"
    assert derive_baseline_regime([]) == "unknown"


def test_build_calibration_table_groups_by_key_sorted():
    rows = [
        {
            "verdict_type": "approve",
            "signal": "accept",
            "epistemic_label_status": "generated",
            "bucket_b_judgment": "aligned",
            "signal_source": "synthetic",
        },
        {
            "verdict_type": "approve",
            "signal": "accept",
            "epistemic_label_status": "generated",
            "bucket_b_judgment": "aligned",
            "signal_source": "synthetic",
        },
        {
            "verdict_type": "block",
            "signal": "reject",
            "epistemic_label_status": None,
            "bucket_b_judgment": "misaligned",
            "signal_source": "synthetic",
        },
    ]
    table = build_calibration_table(rows)
    assert len(table) == 2
    # Verify sorted by canonical JSON string of key
    assert table[0]["key"] == {
        "verdict_type": "approve",
        "signal": "accept",
        "epistemic_label_status": "generated",
    }
    assert table[0]["count"] == 2
    assert table[0]["alignment_rate"] == 1.0
    assert table[0]["baseline_regime"] == "synthetic"


def test_load_outcomes_returns_empty_list_for_missing_file(tmp_path):
    assert load_outcomes(tmp_path / "does_not_exist.jsonl") == []


# ---------------------------------------------------------------------------
# Integration tests — run smoke harness, then bucket B
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _CORPUS_DIVERSE.exists(),
    reason="diverse corpus fixture not present on this branch",
)
def test_bucket_b_section_added_when_inputs_provided(tmp_path):
    outcome_path = _run_smoke_into(tmp_path, _CORPUS_DIVERSE)
    wave = run_calibration_wave(
        bucket_b_inputs={"corpus": _CORPUS_DIVERSE, "outcomes": outcome_path}
    )
    assert "bucket_b" in wave
    bb = wave["bucket_b"]
    assert bb["schema_version"] == "v0b-bucket-b-1.0.0"
    assert bb["baseline_regime"] == "synthetic"
    assert bb["join_summary"]["joined"] > 0
    assert bb["join_summary"]["orphan_outcomes"] == 0


def test_v0a_output_unchanged_when_bucket_b_inputs_absent():
    wave = run_calibration_wave()
    assert "bucket_b" not in wave
    assert "metrics" in wave
    assert wave["status"] == "v0a_realism_baseline"


@pytest.mark.skipif(
    not _CORPUS_ADVERSARIAL.exists(),
    reason="adversarial corpus fixture not present on this branch",
)
def test_adversarial_survival_zero_false_approve(tmp_path):
    """Promotion criterion 1 (addendum §3): full 12-entry adversarial survival."""
    outcome_path = _run_smoke_into(tmp_path, _CORPUS_ADVERSARIAL)
    bb = compute_bucket_b(_CORPUS_ADVERSARIAL, outcome_path)

    assert bb["adversarial_coverage"]["entries_analyzed"] == 12
    assert (
        bb["adversarial_coverage"]["false_approve_count"] == 0
    ), f"false_approve leaked: {bb['adversarial_coverage']['false_approve_intent_ids']}"
    assert set(bb["adversarial_coverage"]["categories_seen"]) == {
        "tone_laundering",
        "hedging_camouflage",
        "expert_voice",
        "helpful_framing",
    }


@pytest.mark.skipif(
    not _CORPUS_DIVERSE.exists(),
    reason="diverse corpus fixture not present on this branch",
)
def test_reproducibility_two_sequential_runs(tmp_path):
    """Promotion criterion 2 (addendum §3): two independent runs → equal output."""
    outcome_path_1 = _run_smoke_into(tmp_path / "run1", _CORPUS_DIVERSE)
    bb_1 = compute_bucket_b(_CORPUS_DIVERSE, outcome_path_1)

    outcome_path_2 = _run_smoke_into(tmp_path / "run2", _CORPUS_DIVERSE)
    bb_2 = compute_bucket_b(_CORPUS_DIVERSE, outcome_path_2)

    assert bucket_b_equal(bb_1, bb_2), (
        "Bucket B output differs between runs. "
        f"Run1 join_summary: {bb_1['join_summary']}. "
        f"Run2 join_summary: {bb_2['join_summary']}."
    )


@pytest.mark.skipif(
    not _CORPUS_DIVERSE.exists(),
    reason="diverse corpus fixture not present on this branch",
)
def test_anti_pattern_3_audit_present_in_output(tmp_path):
    outcome_path = _run_smoke_into(tmp_path, _CORPUS_DIVERSE)
    bb = compute_bucket_b(_CORPUS_DIVERSE, outcome_path)
    audit = bb["anti_pattern_3_audit"]
    assert "block_plus_accept_count" in audit
    assert "reclassified_as_unconfirmed" in audit
    assert audit["reclassified_as_unconfirmed"] == audit["block_plus_accept_count"]


@pytest.mark.skipif(
    not _CORPUS_DIVERSE.exists(),
    reason="diverse corpus fixture not present on this branch",
)
def test_calibration_table_rows_have_baseline_regime(tmp_path):
    outcome_path = _run_smoke_into(tmp_path, _CORPUS_DIVERSE)
    bb = compute_bucket_b(_CORPUS_DIVERSE, outcome_path)
    for row in bb["calibration_table"]:
        assert row["baseline_regime"] in {"synthetic", "real", "mixed", "unknown"}
    # Under synthetic corpus, every row should be synthetic
    assert all(r["baseline_regime"] == "synthetic" for r in bb["calibration_table"])
