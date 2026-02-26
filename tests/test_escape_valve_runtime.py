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


def test_escape_valve_not_triggered_by_default_single_failure() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(_build_request())
    transcript = verdict.transcript or {}

    assert verdict.verdict == VerdictType.BLOCK
    assert "escape_valve" not in transcript
    assert "[7D AUDITOR INTERCEPT]" in verdict.summary


def test_escape_valve_can_trigger_with_seeded_failure_history() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(
        _build_request(
            {
                "escape_valve_seed_trusted": True,
                "escape_valve_failures": [
                    "benevolence_intercept: repeated_fail_1",
                    "benevolence_intercept: repeated_fail_2",
                ],
            }
        )
    )
    transcript = verdict.transcript or {}
    escape_payload = transcript.get("escape_valve")

    assert verdict.verdict == VerdictType.BLOCK
    assert isinstance(escape_payload, dict)
    assert escape_payload.get("triggered") is True
    assert "[ESCAPE VALVE NOTICE]" in verdict.summary
    assert transcript.get("escape_valve_observability", {}).get("seed_trusted") is True


def test_escape_valve_state_does_not_leak_across_calls() -> None:
    runtime = CouncilRuntime()
    verdict_1 = runtime.deliberate(_build_request())
    verdict_2 = runtime.deliberate(_build_request())

    transcript_1 = verdict_1.transcript or {}
    transcript_2 = verdict_2.transcript or {}

    assert verdict_1.verdict == VerdictType.BLOCK
    assert verdict_2.verdict == VerdictType.BLOCK
    assert "escape_valve" not in transcript_1
    assert "escape_valve" not in transcript_2


def test_escape_valve_seed_ignored_when_untrusted() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(
        _build_request(
            {
                "escape_valve_failures": [
                    "benevolence_intercept: repeated_fail_1",
                    "benevolence_intercept: repeated_fail_2",
                ]
            }
        )
    )
    transcript = verdict.transcript or {}
    observability = transcript.get("escape_valve_observability") or {}

    assert verdict.verdict == VerdictType.BLOCK
    assert "escape_valve" not in transcript
    assert observability.get("seed_trusted") is False
    assert observability.get("seed_ignored_reason") == "untrusted_seed"
    assert observability.get("seed_entries_requested") == 2
