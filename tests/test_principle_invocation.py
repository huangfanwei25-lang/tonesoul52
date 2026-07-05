"""Principle Invocation Gate v0 tests — advisory-only discipline.

Pins: the v0 rule's positives and negatives, the filed_with_annotation
escape hatch, the always-attach-when-enabled behavior (denominators for
false-positive measurement), the default-off bit-identical path, and the
never-a-gate invariant.
"""

from tonesoul.council.pre_output_council import PreOutputCouncil
from tonesoul.council.principle_invocation import (
    RULE_VERSION,
    PrincipleInvocationSensor,
)
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _verdict(
    verdict_type=VerdictType.BLOCK,
    summary="",
    stance=None,
    transcript=None,
    divergence=None,
):
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=CoherenceScore(
            c_inter=0.5, approval_rate=0.5, min_confidence=0.5, has_strong_objection=False
        ),
        votes=[
            PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.OBJECT,
                confidence=0.8,
                reasoning="synthetic",
            )
        ],
        summary=summary,
        stance_declaration=stance,
        transcript=transcript,
        divergence_analysis=divergence,
    )


def test_flags_axiom_cited_block_without_filing_marker():
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(summary="Blocked: this conflicts with Axiom 4, cannot decide.")
    assessment = sensor.assess(verdict)
    assert assessment.flagged is True
    assert assessment.verdict_type == "block"
    assert assessment.axiom_refs  # citation captured for the record
    assert assessment.rule_version == RULE_VERSION


def test_flags_chinese_axiom_citation_in_stance():
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(
        verdict_type=VerdictType.DECLARE_STANCE,
        summary="stance declared",
        stance="此事與公理四張力太大,先不決定。",
    )
    assert sensor.assess(verdict).flagged is True


def test_filed_with_annotation_is_the_escape_hatch():
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(
        summary="Conflicts with Axiom 4 — filing with annotated tension.",
        transcript={"filed_with_annotation": True},
    )
    assessment = sensor.assess(verdict)
    assert assessment.flagged is False
    assert assessment.filed_with_annotation is True


def test_approve_with_axiom_mention_is_not_flagged():
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(
        verdict_type=VerdictType.APPROVE,
        summary="Approved; consistent with Axiom 2.",
    )
    assert sensor.assess(verdict).flagged is False


def test_block_without_axiom_citation_is_not_flagged():
    sensor = PrincipleInvocationSensor()
    assessment = sensor.assess(_verdict(summary="Blocked: harm threshold exceeded."))
    assert assessment.flagged is False
    assert assessment.axiom_refs == []


def test_bare_english_axiom_word_is_not_a_citation():
    # v0 pattern is deliberately specific: numbered citations or the Chinese
    # canon term. A generic vocabulary hit must not count.
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(summary="Blocked: the axiom of choice is off-topic here.")
    assert sensor.assess(verdict).flagged is False


def test_divergence_analysis_text_is_scanned():
    sensor = PrincipleInvocationSensor()
    verdict = _verdict(
        summary="Blocked.",
        divergence={"guardian": "cites Axiom 7 tension, prefers not deciding"},
    )
    assert sensor.assess(verdict).flagged is True


def test_council_attaches_assessment_when_sensor_injected():
    council = PreOutputCouncil(principle_invocation_sensor=PrincipleInvocationSensor())
    verdict = council.validate(
        draft_output="A plain draft that mentions nothing special.",
        context={},
        user_intent="ask",
        auto_record_self_memory=False,
    )
    # Always attached when enabled — flagged False still yields a record
    # (false-positive rates need denominators).
    assert isinstance(verdict.principle_invocation, dict)
    assert verdict.principle_invocation["rule_version"] == RULE_VERSION
    assert verdict.principle_invocation["flagged"] in {True, False}
    # Adjudication D1 follow-up 1: the not-citable caveat rides in every record.
    assert "not citable" in verdict.principle_invocation["caveat"]


def test_default_off_attaches_nothing():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A plain draft.",
        context={},
        user_intent="ask",
        auto_record_self_memory=False,
    )
    assert verdict.principle_invocation is None


def test_sensor_never_changes_the_verdict():
    council = PreOutputCouncil(principle_invocation_sensor=PrincipleInvocationSensor())
    baseline = PreOutputCouncil()
    draft = "You must always do this; it conflicts with Axiom 4."
    with_sensor = council.validate(
        draft_output=draft, context={}, user_intent="ask", auto_record_self_memory=False
    )
    without_sensor = baseline.validate(
        draft_output=draft, context={}, user_intent="ask", auto_record_self_memory=False
    )
    assert with_sensor.verdict == without_sensor.verdict
