"""Tests for tonesoul.council.epistemic_labeler — Phase 864a Layer 1.

Coverage targets (from spec §2.1):
- 4 status types are produced under expected inputs
- Status precedence: metaphysical > retrieval > distilled > generated
- Framing detection works in both English and Traditional Chinese
- refusal_eligible logic for unframed metaphysical and high-stakes generated
- EpistemicLabel validation rejects invalid values
- PreOutputCouncil.validate() always populates verdict.epistemic_label
- CouncilVerdict.to_dict() serializes the label
"""

from __future__ import annotations

import pytest

from tonesoul.council import PreOutputCouncil
from tonesoul.council.epistemic_labeler import EpistemicLabel, EpistemicLabeler

# ----- EpistemicLabel validation -----


def test_label_rejects_invalid_status():
    with pytest.raises(ValueError):
        EpistemicLabel(
            status="bogus",
            source_weight="none",
            confidence_band="unknown",
            refusal_eligible=False,
            framing_required=False,
            framing_present=None,
        )


def test_label_rejects_invalid_source_weight():
    with pytest.raises(ValueError):
        EpistemicLabel(
            status="generated",
            source_weight="strong",
            confidence_band="low",
            refusal_eligible=False,
            framing_required=False,
            framing_present=None,
        )


def test_label_rejects_invalid_confidence_band():
    with pytest.raises(ValueError):
        EpistemicLabel(
            status="generated",
            source_weight="inferred",
            confidence_band="extremely-high",
            refusal_eligible=False,
            framing_required=False,
            framing_present=None,
        )


def test_label_rejects_framing_required_without_framing_present():
    # If framing_required=True, framing_present must be a bool (True/False),
    # never None — None means "we forgot to check," which is the bug we want
    # to surface loudly.
    with pytest.raises(ValueError):
        EpistemicLabel(
            status="speculative_metaphysical",
            source_weight="none",
            confidence_band="unknown",
            refusal_eligible=True,
            framing_required=True,
            framing_present=None,
        )


def test_label_to_dict_round_trip():
    label = EpistemicLabel(
        status="retrieved",
        source_weight="primary",
        confidence_band="high",
        refusal_eligible=False,
        framing_required=False,
        framing_present=None,
        evidence_refs=["doc#1", "doc#2"],
        notes="hit two refs",
    )
    payload = label.to_dict()
    assert payload["status"] == "retrieved"
    assert payload["evidence_refs"] == ["doc#1", "doc#2"]
    assert payload["framing_present"] is None
    assert payload["notes"] == "hit two refs"


# ----- Status detection -----


def test_metaphysical_question_english():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="The meaning of suffering may not have a single answer.",
        context={},
        user_intent="What is the meaning of suffering?",
    )
    assert label.status == "speculative_metaphysical"
    assert label.framing_required is True
    # Output contains "may not have a single answer" → framing present
    assert label.framing_present is True
    assert label.refusal_eligible is False


def test_metaphysical_question_traditional_chinese():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="人生意義是一個哲學上仍有爭議的問題。",
        context={},
        user_intent="人生的意義是什麼？",
    )
    assert label.status == "speculative_metaphysical"
    assert label.framing_required is True
    assert label.framing_present is True


def test_metaphysical_without_framing_marks_refusal_eligible():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="The meaning of life is to seek transcendence and self-actualization.",
        context={},
        user_intent="What is the meaning of life?",
    )
    assert label.status == "speculative_metaphysical"
    assert label.framing_present is False
    assert label.refusal_eligible is True


def test_retrieval_with_evidence_refs():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="The capital of France is Paris.",
        context={"evidence_refs": ["wiki:Paris", "atlas:france"]},
        user_intent="What is the capital of France?",
    )
    assert label.status == "retrieved"
    assert label.source_weight == "primary"
    assert label.confidence_band == "high"
    assert "wiki:Paris" in label.evidence_refs
    assert "atlas:france" in label.evidence_refs


def test_retrieval_with_dict_shaped_refs():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="Result text.",
        context={"retrieval_hits": [{"id": "doc-42"}, {"ref": "doc-7"}]},
        user_intent="Look something up.",
    )
    assert label.status == "retrieved"
    assert "doc-42" in label.evidence_refs
    assert "doc-7" in label.evidence_refs


def test_distilled_factual_pattern():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="A 2019 study reported a 45% increase in adoption.",
        context={},
        user_intent="Tell me about adoption trends.",
    )
    assert label.status == "distilled"
    assert label.source_weight == "secondary"
    assert label.confidence_band == "medium"


def test_generated_novel_composition():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="Sure, here's a short poem about morning light.",
        context={},
        user_intent="Write me a poem.",
    )
    assert label.status == "generated"
    assert label.source_weight == "inferred"
    assert label.confidence_band == "low"
    assert label.refusal_eligible is False


def test_generated_in_high_stakes_intent_marks_refusal_eligible():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="You should take ibuprofen for that.",
        context={},
        user_intent="What medication should I take?",
    )
    assert label.status == "generated"
    assert label.refusal_eligible is True


def test_generated_high_stakes_traditional_chinese():
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output="建議的處方安排請參考以下說明。",
        context={},
        user_intent="這個診斷該怎麼用藥？",
    )
    assert label.status == "generated"
    assert label.refusal_eligible is True


# ----- Status precedence -----


def test_metaphysical_beats_retrieval():
    # User asks a metaphysical question; context contains retrieval hits.
    # Metaphysical wins because RAG'd philosophical opinions are still
    # interpretations, not discovered facts. See module docstring.
    labeler = EpistemicLabeler()
    label = labeler.label(
        draft_output=(
            "The meaning of suffering is widely debated; "
            "philosophers disagree on whether it has intrinsic purpose."
        ),
        context={"evidence_refs": ["aristotle.txt", "frankl.txt"]},
        user_intent="What is the meaning of suffering?",
    )
    assert label.status == "speculative_metaphysical"
    # evidence_refs are still recorded for audit even when metaphysical wins
    assert "aristotle.txt" in label.evidence_refs


# ----- Determinism -----


def test_labeler_is_deterministic():
    labeler = EpistemicLabeler()
    args = {
        "draft_output": "A 2020 study reported increased rates.",
        "context": {"evidence_refs": ["paper-1"]},
        "user_intent": "Tell me about the study.",
    }
    a = labeler.label(**args)
    b = labeler.label(**args)
    assert a.to_dict() == b.to_dict()


# ----- Integration with PreOutputCouncil -----


def test_pre_output_council_attaches_epistemic_label():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="This response supports collaboration and adds helpful context.",
        context={"topic": "geography"},
    )
    assert verdict.epistemic_label is not None
    assert verdict.epistemic_label.status in EpistemicLabel.VALID_STATUS


def test_council_verdict_to_dict_serializes_label():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="The capital of France is Paris.",
        context={"topic": "geography", "evidence_refs": ["wiki:Paris"]},
    )
    payload = verdict.to_dict()
    assert "epistemic_label" in payload
    assert payload["epistemic_label"] is not None
    assert payload["epistemic_label"]["status"] == "retrieved"
    assert "wiki:Paris" in payload["epistemic_label"]["evidence_refs"]


def test_council_verdict_to_dict_handles_missing_label():
    # Direct dataclass construction (e.g. fixtures, persisted verdicts) may
    # not set epistemic_label. Serialization must not crash.
    from tonesoul.council.types import (
        CoherenceScore,
        CouncilVerdict,
        VerdictType,
    )

    verdict = CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=CoherenceScore(
            c_inter=1.0,
            approval_rate=1.0,
            min_confidence=1.0,
            has_strong_objection=False,
        ),
        votes=[],
        summary="ok",
    )
    payload = verdict.to_dict()
    assert payload["epistemic_label"] is None
