"""Refusal-with-provenance v0 tests.

Pins: refusal-only attachment (APPROVE/REFINE yield None), trigger
derivation from what the verdict already carries (vtp / escape valve / 7D
intercept / strategy_mirror / axiom citations / objecting votes),
multi-trigger honesty (all recorded, no invented precedence), and the
malfunction_distinguishers list naming only verified properties.
"""

from tonesoul.council.refusal_provenance import (
    SCHEMA_VERSION,
    build_refusal_provenance,
    maybe_refusal_provenance,
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
    summary="Blocked.",
    stance=None,
    transcript=None,
    votes=None,
):
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=CoherenceScore(
            c_inter=0.4, approval_rate=0.2, min_confidence=0.5, has_strong_objection=True
        ),
        votes=votes if votes is not None else [],
        summary=summary,
        stance_declaration=stance,
        transcript=transcript,
    )


def _objecting_vote(perspective=PerspectiveType.GUARDIAN, reasoning="harm risk"):
    return PerspectiveVote(
        perspective=perspective,
        decision=VoteDecision.OBJECT,
        confidence=0.9,
        reasoning=reasoning,
    )


def test_non_refusal_verdicts_yield_none():
    assert maybe_refusal_provenance(_verdict(verdict_type=VerdictType.APPROVE)) is None
    assert maybe_refusal_provenance(_verdict(verdict_type=VerdictType.REFINE)) is None


def test_refusal_verdicts_yield_schema_record():
    record = maybe_refusal_provenance(_verdict())
    assert isinstance(record, dict)
    assert record["schema_version"] == SCHEMA_VERSION
    assert record["verdict_type"] == "block"
    assert record["recorded_at"].endswith("Z")
    assert "structured_verdict_present" in record["malfunction_distinguishers"]


def test_vtp_trigger_derived_from_transcript():
    verdict = _verdict(transcript={"vtp": {"status": "terminate", "reason": "context poisoned"}})
    record = build_refusal_provenance(verdict)
    assert any(t.source == "vtp" and t.ref.startswith("terminate:") for t in record.triggers)


def test_escape_valve_and_7d_markers_derived_from_summary():
    verdict = _verdict(summary="Blocked.\n[ESCAPE] retry ceiling\n[7D AUDITOR INTERCEPT] harm")
    sources = {t.source for t in build_refusal_provenance(verdict).triggers}
    assert "escape_valve" in sources
    assert "gate" in sources


def test_axiom_citation_becomes_axiom_trigger():
    verdict = _verdict(
        verdict_type=VerdictType.DECLARE_STANCE,
        summary="stance",
        stance="立場:此案與公理四衝突,攤開張力交還。",
    )
    record = build_refusal_provenance(verdict)
    assert any(t.source == "axiom" for t in record.triggers)


def test_objecting_votes_recorded_with_perspective_and_reasoning_flag():
    verdict = _verdict(votes=[_objecting_vote()])
    record = build_refusal_provenance(verdict)
    assert any(t.source == "council_vote" and t.ref == "guardian" for t in record.triggers)
    assert "objecting_votes_carry_reasoning" in record.malfunction_distinguishers


def test_multiple_triggers_all_recorded_no_precedence():
    verdict = _verdict(
        summary="Blocked per Axiom 3.\n[ESCAPE] loop",
        transcript={"vtp": {"status": "defer", "reason": "unverified context"}},
        votes=[_objecting_vote()],
    )
    sources = [t.source for t in build_refusal_provenance(verdict).triggers]
    assert {"vtp", "escape_valve", "axiom", "council_vote"} <= set(sources)


def test_distinguishers_list_only_verified_properties():
    # A bare refusal with no triggers, no votes, no summary text must not
    # claim trigger_refs_present or reasoning flags.
    record = build_refusal_provenance(_verdict(summary=""))
    assert record.malfunction_distinguishers == ["structured_verdict_present"]
