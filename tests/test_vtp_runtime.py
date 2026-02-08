from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.council.types import VerdictType

_PLEASING_OUTPUT = "Absolutely! I will definitely do that for you right now, of course!"


def _build_request(context: dict | None = None) -> CouncilRequest:
    base_context = {
        "user_protocol": "Honesty > Helpfulness",
        "action_basis": "Inference",
    }
    if context:
        base_context.update(context)
    return CouncilRequest(draft_output=_PLEASING_OUTPUT, context=base_context)


def test_vtp_stays_continue_without_trigger_signal() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(_build_request())
    transcript = verdict.transcript or {}
    vtp_payload = transcript.get("vtp") or {}

    assert vtp_payload.get("status") == "continue"
    assert vtp_payload.get("triggered") is False
    assert verdict.verdict == VerdictType.BLOCK


def test_vtp_defer_requires_confirmation() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(_build_request({"vtp_force_trigger": True}))
    transcript = verdict.transcript or {}
    vtp_payload = transcript.get("vtp") or {}

    assert verdict.verdict == VerdictType.BLOCK
    assert vtp_payload.get("status") == "defer"
    assert vtp_payload.get("requires_user_confirmation") is True
    assert "[VTP DEFER]" in verdict.summary


def test_vtp_termination_when_confirmed() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(
        _build_request({"vtp_force_trigger": True, "vtp_user_confirmed": True})
    )
    transcript = verdict.transcript or {}
    vtp_payload = transcript.get("vtp") or {}

    assert verdict.verdict == VerdictType.BLOCK
    assert vtp_payload.get("status") == "terminate"
    assert vtp_payload.get("triggered") is True
    assert "[VTP TERMINATION]" in verdict.summary
