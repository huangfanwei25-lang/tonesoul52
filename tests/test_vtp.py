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
    uncertainty_band: str | None = "medium",
    uncertainty_reasons: list[str] | None = None,
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
        uncertainty_level=0.5,
        uncertainty_band=uncertainty_band,
        uncertainty_reasons=uncertainty_reasons or [],
    )


def test_vtp_continue_when_no_high_risk_signal() -> None:
    verdict = _build_verdict(verdict_type=VerdictType.APPROVE, uncertainty_band="low")
    decision = evaluate_vtp(verdict=verdict, context={})

    assert decision.status == VTP_STATUS_CONTINUE
    assert decision.triggered is False
    assert decision.requires_user_confirmation is False


def test_vtp_defer_when_high_risk_without_confirmation() -> None:
    verdict = _build_verdict(uncertainty_band="high")
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True},
    )

    assert decision.status == VTP_STATUS_DEFER
    assert decision.triggered is True
    assert decision.requires_user_confirmation is True
    assert "force_trigger" in decision.evidence


def test_vtp_terminate_when_confirmed_and_genesis_complete() -> None:
    verdict = _build_verdict(uncertainty_band="high")
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True, "vtp_user_confirmed": True},
    )

    assert decision.status == VTP_STATUS_TERMINATE
    assert decision.triggered is True
    assert decision.requires_user_confirmation is False


def test_vtp_defer_when_genesis_incomplete_even_if_confirmed() -> None:
    verdict = _build_verdict(uncertainty_band="high", with_genesis=False)
    decision = evaluate_vtp(
        verdict=verdict,
        context={"vtp_force_trigger": True, "vtp_user_confirmed": True},
    )

    assert decision.status == VTP_STATUS_DEFER
    assert decision.reason == "genesis_context_incomplete"
    assert "genesis_incomplete" in decision.evidence
