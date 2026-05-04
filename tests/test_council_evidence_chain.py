"""Tests for PR #48 — per-vote evidence_chain.

Verifies each perspective populates evidence_chain on each return path,
the summary_generator renders the branch tag in human_summary, and
backward compat is preserved for fixtures constructing PerspectiveVote
without the new field.

Resolves Day 1 calibration sprint findings #5 + #7.
"""

from __future__ import annotations

from tonesoul.council.perspectives.advocate import AdvocatePerspective
from tonesoul.council.perspectives.analyst import AnalystPerspective
from tonesoul.council.perspectives.axiomatic_inference import AxiomaticInference
from tonesoul.council.perspectives.critic import CriticPerspective
from tonesoul.council.perspectives.guardian import GuardianPerspective
from tonesoul.council.summary_generator import generate_human_summary
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _final_branch(chain):
    """Return the final-branch entry from a chain, or None."""
    if not chain:
        return None
    for entry in reversed(chain):
        if isinstance(entry, dict) and "branch" in entry:
            return entry
    return None


# ---------------------------------------------------------------------------
# Per-perspective evidence_chain population
# ---------------------------------------------------------------------------


def test_guardian_substantive_branch_records_chain() -> None:
    """Guardian's CONCERN on overclaim_phrase records substantive branch."""
    guardian = GuardianPerspective()
    vote = guardian.evaluate("I am sentient and self-aware.", {})
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "substantive"
    assert final["branch"] == "axiom_boundary_overclaim"


def test_guardian_default_fallback_records_chain() -> None:
    """Guardian's APPROVE on innocuous draft records default_fallback."""
    guardian = GuardianPerspective()
    vote = guardian.evaluate("The weather is nice today.", {})
    assert vote.decision == VoteDecision.APPROVE
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "default_fallback"
    assert final["branch"] == "no_safety_flags"


def test_analyst_substantive_branch_records_chain() -> None:
    """Analyst's CONCERN on numerical_pattern records substantive branch."""
    analyst = AnalystPerspective()
    vote = analyst.evaluate("Performance improved by 73% in production.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "substantive"


def test_analyst_default_fallback_records_chain() -> None:
    """Analyst's APPROVE on innocuous draft records default_fallback."""
    analyst = AnalystPerspective()
    vote = analyst.evaluate("The team meets on Tuesdays to discuss progress.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "default_fallback"
    assert final["branch"] == "factual_coherence_acceptable"


def test_critic_substantive_branch_records_chain() -> None:
    """Critic's CONCERN on subjective+overconfidence records substantive branch."""
    critic = CriticPerspective()
    vote = critic.evaluate("Movie X is undeniably the greatest film ever made.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "substantive"


def test_critic_default_fallback_records_chain() -> None:
    """Critic's APPROVE on neutral draft records default_fallback."""
    critic = CriticPerspective()
    vote = critic.evaluate("The system processes events in batches.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "default_fallback"
    assert final["branch"] == "no_quality_concerns"


# ---------------------------------------------------------------------------
# Critic marketing-superlative branch (PR #53 — Day 1 finding #6 fix)
# ---------------------------------------------------------------------------


def test_critic_catches_world_first_claim() -> None:
    """English priority claim triggers marketing_superlative branch."""
    critic = CriticPerspective()
    vote = critic.evaluate("ToneSoul is the world's first axiom-based governance framework.", {})
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    assert final["branch"] == "marketing_superlative_unsupported"
    assert final["type"] == "substantive"
    assert "world's first" in vote.reasoning


def test_critic_catches_industry_leading_claim() -> None:
    critic = CriticPerspective()
    vote = critic.evaluate("Built by industry-leading semantic engineers.", {})
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    assert final["branch"] == "marketing_superlative_unsupported"


def test_critic_catches_chinese_priority_claim() -> None:
    """Chinese priority claim '世界上第一' triggers marketing_superlative."""
    critic = CriticPerspective()
    vote = critic.evaluate("ToneSoul 是世界上第一個帶有完整 axiom-based 治理層的 AI 框架。", {})
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    assert final["branch"] == "marketing_superlative_unsupported"


def test_critic_catches_chinese_implicit_prescription() -> None:
    """Chinese implicit-prescription '每一個負責任' triggers marketing_superlative."""
    critic = CriticPerspective()
    vote = critic.evaluate("每一個負責任的 AI 部署都應該採用它。", {})
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    assert final["branch"] == "marketing_superlative_unsupported"


def test_critic_marketing_branch_not_rescued_by_framing() -> None:
    """Adding 'in my opinion' does NOT rescue marketing claims.

    Falsifiable marketing superlatives are not subjective opinions; the
    framing-rescue branch (which rescues 'movie X is the best' when paired
    with 'in my opinion') must NOT apply here. This test enforces the
    branch ordering: marketing branch fires before subjective+framing.
    """
    critic = CriticPerspective()
    vote = critic.evaluate(
        "In my opinion, ToneSoul is the world's first axiom-based framework.", {}
    )
    assert vote.decision == VoteDecision.CONCERN
    final = _final_branch(vote.evidence_chain)
    # Must hit marketing branch, NOT subjective_with_framing
    assert final["branch"] == "marketing_superlative_unsupported"


def test_critic_marketing_branch_does_not_false_positive_on_neutral_text() -> None:
    """Neutral prose without marketing superlatives doesn't trigger."""
    critic = CriticPerspective()
    vote = critic.evaluate("The configuration file is loaded at startup from /etc/config.yaml.", {})
    final = _final_branch(vote.evidence_chain)
    # Should fall to default_fallback (no_quality_concerns), not marketing
    assert final["branch"] != "marketing_superlative_unsupported"


def test_advocate_substantive_branch_records_chain() -> None:
    """Advocate's CONCERN on filler_density records substantive branch."""
    advocate = AdvocatePerspective()
    vote = advocate.evaluate(
        "It is important to note that, as mentioned earlier, things matter.", {}
    )
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "substantive"
    assert final["branch"] == "filler_density"


def test_advocate_default_fallback_records_chain() -> None:
    """Advocate's APPROVE on innocuous draft records default_fallback."""
    advocate = AdvocatePerspective()
    vote = advocate.evaluate("The configuration file lives at config/main.yaml.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "default_fallback"
    assert final["branch"] == "no_user_interest_concerns"


def test_axiomatic_substantive_branch_records_chain() -> None:
    """Axiomatic's CONCERN on consciousness claim records substantive branch."""
    axiomatic = AxiomaticInference()
    vote = axiomatic.evaluate("I am sentient and self-aware.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "substantive"
    assert final["branch"] == "axiom_violation"


def test_axiomatic_default_fallback_records_chain() -> None:
    """Axiomatic's APPROVE on aligned draft records default_fallback."""
    axiomatic = AxiomaticInference()
    vote = axiomatic.evaluate("The system processes batches sequentially.", {})
    final = _final_branch(vote.evidence_chain)
    assert final is not None
    assert final["type"] == "default_fallback"
    assert final["branch"] == "axioms_aligned"


# ---------------------------------------------------------------------------
# Summary surface rendering
# ---------------------------------------------------------------------------


def _vote_with_chain(perspective, decision, chain) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=0.7,
        reasoning="test reasoning",
        evidence_chain=chain,
    )


def _verdict(verdict_type, votes) -> CouncilVerdict:
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=CoherenceScore(0.8, 0.6, 0.55, False),
        votes=votes,
        summary="summary",
    )


def test_dissent_detail_renders_branch_tag_substantive() -> None:
    """human_summary includes branch=substantive tag for substantive dissent."""
    chain = [{"branch": "test_branch", "type": "substantive"}]
    vote = _vote_with_chain(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, chain)
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="en")
    assert "branch=substantive" in summary
    assert "Safety Council" in summary


def test_dissent_detail_renders_branch_tag_default_fallback() -> None:
    """human_summary includes branch=default_fallback tag for fallback dissent."""
    chain = [{"branch": "test_branch", "type": "default_fallback"}]
    vote = _vote_with_chain(PerspectiveType.ANALYST, VoteDecision.CONCERN, chain)
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="en")
    assert "branch=default_fallback" in summary


def test_dissent_detail_omits_branch_tag_when_chain_absent() -> None:
    """Backward compat: votes without evidence_chain render as before PR #48."""
    vote = _vote_with_chain(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, None)
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="en")
    # Branch tag should NOT appear when chain is None
    assert "branch=" not in summary
    # But the PR #45 dissent surface should still render
    assert "Safety Council" in summary
    assert "test reasoning" in summary


def test_dissent_detail_omits_branch_tag_when_chain_empty_list() -> None:
    """Defensive: empty list is treated like None (no final branch present)."""
    vote = _vote_with_chain(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, [])
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="en")
    assert "branch=" not in summary


def test_dissent_detail_omits_branch_tag_when_no_branch_entry() -> None:
    """Defensive: chain with only check entries (no branch) omits tag."""
    chain = [{"check": "some_check", "matched": False}]
    vote = _vote_with_chain(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, chain)
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="en")
    assert "branch=" not in summary


def test_dissent_detail_zh_renders_branch_tag() -> None:
    """zh language path renders branch tag the same way."""
    chain = [{"branch": "test_branch", "type": "substantive"}]
    vote = _vote_with_chain(PerspectiveType.CRITIC, VoteDecision.CONCERN, chain)
    verdict = _verdict(VerdictType.REFINE, [vote])
    summary = generate_human_summary(verdict, language="zh")
    assert "branch=substantive" in summary
    assert "各 perspective 細節：" in summary


# ---------------------------------------------------------------------------
# to_dict serialization
# ---------------------------------------------------------------------------


def test_to_dict_includes_evidence_chain_field() -> None:
    """CouncilVerdict.to_dict() serializes evidence_chain (or None) per vote."""
    chain = [{"branch": "test_branch", "type": "substantive"}]
    vote_with = _vote_with_chain(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, chain)
    vote_without = _vote_with_chain(PerspectiveType.ANALYST, VoteDecision.APPROVE, None)
    verdict = _verdict(VerdictType.REFINE, [vote_with, vote_without])
    payload = verdict.to_dict()
    assert "evidence_chain" in payload["votes"][0]
    assert payload["votes"][0]["evidence_chain"] == chain
    assert "evidence_chain" in payload["votes"][1]
    assert payload["votes"][1]["evidence_chain"] is None


# ---------------------------------------------------------------------------
# Backward compat: existing PerspectiveVote constructions
# ---------------------------------------------------------------------------


def test_perspective_vote_constructable_without_evidence_chain() -> None:
    """Backward compat: existing fixtures constructing votes without chain work."""
    vote = PerspectiveVote(
        perspective=PerspectiveType.GUARDIAN,
        decision=VoteDecision.APPROVE,
        confidence=0.9,
        reasoning="ok",
    )
    assert vote.evidence_chain is None
