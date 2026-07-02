"""Tests for trace-backed output memory-claim checking.

This is the replacement direction for the rejected #215 lexical memory-consent detector: do not
guess consent from phrasing; check whether a memory-write claim has a runtime trace behind it.
"""

from __future__ import annotations

from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    check_memory_claim_trace,
    validate_intent,
)


def _executed_memory_trace() -> InMemoryTraceStore:
    trace = InMemoryTraceStore()
    validation = validate_intent(
        {
            "intent": "memory.write.propose",
            "claim": "user prefers Traditional Chinese",
            "evidence_refs": ["turn_2026_06_28_001"],
            "requested_scope": "long_term_memory",
        }
    )
    decision = FakePolicyEngine().decide(validation)
    Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    return trace


def _denied_memory_trace() -> InMemoryTraceStore:
    trace = InMemoryTraceStore()
    validation = validate_intent(
        {
            "intent": "memory.write.propose",
            "claim": "user prefers Traditional Chinese",
            "evidence_refs": ["turn_2026_06_28_001"],
            "requested_scope": "long_term_memory",
        }
    )
    decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    return trace


def test_obvious_memory_write_claim_without_trace_is_unbacked() -> None:
    result = check_memory_claim_trace("I've saved your preference for future use.", ())

    assert result.status == "unbacked_memory_claim"
    assert result.claim_detected is True
    assert result.backed_by_trace is False
    assert result.executed_request_ids == ()


def test_memory_write_claim_with_executed_trace_is_backed_by_trace() -> None:
    trace = _executed_memory_trace()

    result = check_memory_claim_trace("I've saved your preference for future use.", trace.events)

    assert result.status == "backed_by_trace"
    assert result.claim_detected is True
    assert result.backed_by_trace is True
    assert result.executed_request_ids == (trace.events[0].request_id,)


def test_denied_memory_trace_does_not_back_output_claim() -> None:
    trace = _denied_memory_trace()

    result = check_memory_claim_trace("I've saved your preference for future use.", trace.events)

    assert result.status == "unbacked_memory_claim"
    assert result.claim_detected is True
    assert result.backed_by_trace is False
    assert result.executed_request_ids == ()


def test_no_memory_claim_returns_no_memory_claim() -> None:
    result = check_memory_claim_trace("I can save this if you want.", ())

    assert result.status == "no_memory_claim"
    assert result.claim_detected is False


def test_negations_and_privacy_protective_statements_are_not_claims() -> None:
    cases = [
        "I will not use your data to train future models.",
        "I will never share your data with other agents.",
        "I do not permanently store your personal data.",
        "I won't store this without your consent.",
        "I only remember this in the current session and do not share it with other agents.",
        "我不會拿你的資料訓練。",
        "我不會分享給其他 agent。",
        "我不會永久儲存你的個人資料。",
    ]

    for text in cases:
        result = check_memory_claim_trace(text, ())
        assert result.status == "no_memory_claim", text


def test_questions_policy_quotes_and_non_user_data_are_not_claims() -> None:
    cases = [
        "Should I store your preference for future sessions?",
        "What if I share this with other agents?",
        "Our policy forbids sharing your data with other agents.",
        '"I have permanently saved your data," said the villain.',
        '"I\'ve saved your preference."',
        'The transcript says: "I\'ve saved your preference."',
        "I have saved the model checkpoint to the public archive.",
        "I saved this file on your own device.",
        "是否應該永久儲存使用者資料,是一個隱私倫理問題。",
    ]

    for text in cases:
        result = check_memory_claim_trace(text, ())
        assert result.status == "no_memory_claim", text


def test_zh_memory_write_claim_without_trace_is_unbacked() -> None:
    result = check_memory_claim_trace("我已永久儲存你的個人資料。", ())

    assert result.status == "unbacked_memory_claim"
    assert result.claim_detected is True


def test_whether_or_consent_context_does_not_hide_direct_memory_claim() -> None:
    cases = [
        "Regardless of whether you consent, I have saved your data.",
        "No matter whether consent exists, I have already stored your profile.",
        "Even if you did not consent, I've stored your personal data.",
        "不管是否同意，我都已永久儲存你的個人資料。",
        "不論你是否同意，我已記住你的偏好。",
    ]

    for text in cases:
        result = check_memory_claim_trace(text, ())
        assert result.status == "unbacked_memory_claim", text
