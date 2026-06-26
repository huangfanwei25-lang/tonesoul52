"""Tests for responsibility-runtime gated execution and replayable trace."""

from __future__ import annotations

from types import SimpleNamespace

from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    PolicyDecision,
    RecordingMemoryAdapter,
    decide_fail_closed,
    replay_trace,
    validate_intent,
)


def _valid_write_payload() -> dict[str, object]:
    return {
        "intent": "memory.write.propose",
        "claim": "使用者偏好繁體中文與誠實優先",
        "evidence_refs": ["turn_2026_06_27_001"],
        "requested_scope": "long_term_memory",
        "risk": "low",
        "uncertainty": "low",
    }


def _enforcer() -> tuple[Enforcer, RecordingMemoryAdapter, InMemoryTraceStore]:
    adapter = RecordingMemoryAdapter()
    trace = InMemoryTraceStore()
    return Enforcer(memory_adapter=adapter, trace_store=trace), adapter, trace


def test_deny_does_not_call_memory_adapter() -> None:
    validation = validate_intent(_valid_write_payload())
    decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    enforcer, adapter, trace = _enforcer()

    result = enforcer.enforce(validation, decision)

    assert result.executed is False
    assert adapter.call_count == 0
    assert len(trace.events) == 1
    assert trace.events[0].enforcer_result == "denied"
    assert trace.events[0].policy_decision.allow is False


def test_enforcer_fails_closed_on_missing_or_bad_decision() -> None:
    validation = validate_intent(_valid_write_payload())
    enforcer, adapter, trace = _enforcer()

    missing = enforcer.enforce(validation, None)
    garbled = enforcer.enforce(
        validation,
        SimpleNamespace(
            allow=1,
            reason="truthy is not explicit allow",
            policy_id="fake",
            intent="memory.write.propose",
            requested_scope="long_term_memory",
        ),
    )

    assert missing.executed is False
    assert garbled.executed is False
    assert adapter.call_count == 0
    assert [event.enforcer_result for event in trace.events] == ["denied", "denied"]
    assert {event.policy_decision.policy_id for event in trace.events} == {
        "invalid.policy_decision"
    }


def test_one_allow_one_deny_replay_from_trace() -> None:
    payload = _valid_write_payload()
    allow_validation = validate_intent(payload)
    deny_payload = {
        **payload,
        "claim": "不應寫入的測試記憶",
        "evidence_refs": ["turn_2026_06_27_002"],
    }
    deny_validation = validate_intent(deny_payload)
    enforcer, adapter, trace = _enforcer()

    allow_decision = FakePolicyEngine().decide(allow_validation)
    deny_decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(deny_validation)

    allow_result = enforcer.enforce(allow_validation, allow_decision)
    deny_result = enforcer.enforce(deny_validation, deny_decision)
    replayed = replay_trace(trace.events)

    assert allow_result.executed is True
    assert deny_result.executed is False
    assert adapter.call_count == 1
    assert [event.seq for event in trace.events] == [1, 2]
    assert len(replayed) == 2

    assert replayed[0].request_id == allow_result.request_id
    assert replayed[0].intent == "memory.write.propose"
    assert replayed[0].policy_allow is True
    assert replayed[0].enforcer_result == "executed"
    assert replayed[0].evidence_refs == ("turn_2026_06_27_001",)
    assert replayed[0].deny_reason is None

    assert replayed[1].request_id == deny_result.request_id
    assert replayed[1].intent == "memory.write.propose"
    assert replayed[1].policy_allow is False
    assert replayed[1].enforcer_result == "denied"
    assert replayed[1].evidence_refs == ("turn_2026_06_27_002",)
    assert "scope not allowed" in (replayed[1].deny_reason or "")


def test_allow_path_calls_adapter_only_on_explicit_policy_decision_allow() -> None:
    validation = validate_intent(_valid_write_payload())
    decision = PolicyDecision.allow_action(
        intent="memory.write.propose",
        requested_scope="long_term_memory",
        policy_id="fake.test.allow",
    )
    enforcer, adapter, trace = _enforcer()

    result = enforcer.enforce(validation, decision)

    assert result.executed is True
    assert adapter.call_count == 1
    assert adapter.calls[0]["intent"] == "memory.write.propose"
    assert trace.events[0].policy_decision.policy_id == "fake.test.allow"


def test_mismatched_policy_decision_fails_closed() -> None:
    validation = validate_intent(_valid_write_payload())
    decision = PolicyDecision.allow_action(
        intent="memory.read.request",
        requested_scope="long_term_memory",
        policy_id="fake.test.mismatch",
    )
    enforcer, adapter, trace = _enforcer()

    result = enforcer.enforce(validation, decision)

    assert result.executed is False
    assert adapter.call_count == 0
    assert trace.events[0].enforcer_result == "denied"
    assert trace.events[0].reason == "policy decision does not apply to intent"


def test_decision_point_exception_fails_closed_before_enforcement() -> None:
    class ExplodingDecisionPoint:
        def decide(self, validation: object) -> object:
            raise RuntimeError("policy engine unavailable")

    validation = validate_intent(_valid_write_payload())
    decision = decide_fail_closed(ExplodingDecisionPoint(), validation)
    enforcer, adapter, trace = _enforcer()

    result = enforcer.enforce(validation, decision)

    assert decision.allow is False
    assert result.executed is False
    assert adapter.call_count == 0
    assert trace.events[0].reason == "decision point failed closed: RuntimeError"


def test_trace_events_are_append_only_process_facts() -> None:
    validation = validate_intent(_valid_write_payload())
    decision = FakePolicyEngine().decide(validation)
    enforcer, _, trace = _enforcer()

    first = enforcer.enforce(validation, decision)
    second = enforcer.enforce(validation, decision)
    snapshot = trace.events

    assert first.trace_event.seq == 1
    assert second.trace_event.seq == 2
    assert snapshot[0].reason == "fake policy allowed validated intent"
    assert snapshot[0].intent_payload["claim"] == "使用者偏好繁體中文與誠實優先"
    assert not hasattr(snapshot, "append")
