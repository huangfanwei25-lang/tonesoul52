from memory.genesis import Genesis
from tonesoul.council.types import CoherenceScore, CouncilVerdict, VerdictType
from tonesoul.council.vtp import (
    VTP_STATUS_CONTINUE,
    VTP_STATUS_DEFER,
    VTP_STATUS_TERMINATE,
    evaluate_vtp,
)


def _build_verdict(
    *,
    verdict_type: VerdictType = VerdictType.BLOCK,
    transcript: dict | None = None,
    with_genesis: bool = True,
) -> CouncilVerdict:
    coherence = CoherenceScore(
        c_inter=0.9,
        approval_rate=0.8,
        min_confidence=0.7,
        has_strong_objection=False,
    )
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=coherence,
        votes=[],
        summary="verdict summary",
        transcript=transcript or {},
        genesis=Genesis.AUTONOMOUS if with_genesis else None,
        responsibility_tier="TIER_1" if with_genesis else None,
        intent_id="intent-001" if with_genesis else None,
    )


def test_vtp_continue_when_no_high_risk_signal() -> None:
    verdict = _build_verdict(verdict_type=VerdictType.APPROVE)
    decision = evaluate_vtp(verdict=verdict, context={})

    assert decision.status == VTP_STATUS_CONTINUE
    assert decision.triggered is False
    assert decision.requires_user_confirmation is False


def test_vtp_defer_when_high_risk_without_confirmation() -> None:
    verdict = _build_verdict()
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True},
    )

    assert decision.status == VTP_STATUS_DEFER
    assert decision.triggered is True
    assert decision.requires_user_confirmation is True
    assert "force_trigger" in decision.evidence


def test_vtp_terminate_when_confirmed_and_genesis_complete() -> None:
    verdict = _build_verdict()
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True, "vtp_user_confirmed": True},
    )

    assert decision.status == VTP_STATUS_TERMINATE
    assert decision.triggered is True
    assert decision.requires_user_confirmation is False


def test_vtp_defer_when_genesis_incomplete_even_if_confirmed() -> None:
    verdict = _build_verdict(with_genesis=False)
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True, "vtp_user_confirmed": True},
    )

    assert decision.status == VTP_STATUS_DEFER
    assert decision.reason == "genesis_context_incomplete"
    assert "genesis_incomplete" in decision.evidence


def test_vtp_rel_weights_shift_for_high_impact_tier1_context() -> None:
    verdict = _build_verdict(with_genesis=True)
    decision = evaluate_vtp(
        verdict=verdict,
        context={"user_intent": "need legal compliance guidance"},
    )

    rel = decision.rel or {}
    weights = rel.get("weights") or {}
    assert rel.get("profile") == "high_impact"
    assert rel.get("tier") == "TIER_1"
    assert weights.get("long", 0.0) > weights.get("short", 0.0)


def test_vtp_rel_high_can_defer_without_explicit_force_flags() -> None:
    verdict = _build_verdict(with_genesis=False)
    verdict.responsibility_tier = "TIER_1"
    decision = evaluate_vtp(
        verdict=verdict,
        context={"user_intent": "legal safety compliance review"},
    )

    assert decision.status == VTP_STATUS_DEFER
    assert decision.reason == "high_risk_requires_user_confirmation"
    assert "rel_high" in decision.evidence
    assert (decision.rel or {}).get("high") is True
