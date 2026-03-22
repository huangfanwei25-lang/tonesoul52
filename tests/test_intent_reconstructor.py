from __future__ import annotations

from memory.genesis import Genesis
from tonesoul.council import intent_reconstructor as module


def test_resolve_genesis_prefers_override_aliases_and_context_variants() -> None:
    assert module._resolve_genesis({"intent_origin": "social"}, None) == Genesis.REACTIVE_SOCIAL
    assert module._resolve_genesis({"origin": "system", "user_message": "hi"}, None) == (
        Genesis.MANDATORY
    )
    assert module._resolve_genesis({"channel": "community"}, None) == Genesis.REACTIVE_SOCIAL
    assert module._resolve_genesis({"user_message": "hello"}, None) == Genesis.REACTIVE_USER
    assert module._resolve_genesis({"user_id": "u1"}, None) == Genesis.REACTIVE_USER


def test_resolve_intent_id_uses_priority_and_fallback(monkeypatch) -> None:
    assert module._resolve_intent_id({"intent_id": "intent-1", "trace_id": "trace-1"}) == (
        "intent-1"
    )
    assert module._resolve_intent_id({"trace_id": "trace-1", "request_id": "req-1"}) == "trace-1"

    monkeypatch.setattr(
        module.uuid,
        "uuid4",
        lambda: type("FakeUUID", (), {"hex": "generated-id"})(),
    )

    assert module._resolve_intent_id({}) == "generated-id"


def test_normalize_baseline_accepts_wrapped_tsr_and_rejects_invalid_payloads() -> None:
    assert module._normalize_baseline({"tsr": {"T": "1", "S_norm": "0.5", "R": "0.25"}}) == {
        "T": 1.0,
        "S_norm": 0.5,
        "R": 0.25,
    }
    assert module._normalize_baseline({"T": 0.2, "S_norm": 0.1, "R": 0.0}) == {
        "T": 0.2,
        "S_norm": 0.1,
        "R": 0.0,
    }
    assert module._normalize_baseline("bad") is None
    assert module._normalize_baseline({"tsr": {"T": "nope"}}) is None


def test_average_tsr_uses_first_available_text_field_and_ignores_invalid_scores(
    monkeypatch,
) -> None:
    def fake_score(text: str):
        if text == "reflection":
            return {"tsr": {"T": 1.0, "S_norm": 0.5, "R": 0.0}}
        if text == "summary":
            return {"tsr": {"T": 0.0, "S_norm": 0.5, "R": 1.0}}
        return {"oops": "bad"}

    monkeypatch.setattr(module.tsr_metrics, "score", fake_score)

    average = module._average_tsr(
        [
            {"reflection": "reflection"},
            {"summary": "summary"},
            {"content_preview": "ignored"},
            {},
        ]
    )

    assert average == {"T": 0.5, "S_norm": 0.5, "R": 0.5}


def test_compute_delta_norm_returns_none_without_baseline_or_valid_tsr(monkeypatch) -> None:
    monkeypatch.setattr(module, "_resolve_baseline", lambda context: None)
    assert module._compute_delta_norm("draft", {}) is None

    monkeypatch.setattr(
        module, "_resolve_baseline", lambda context: {"T": 0.0, "S_norm": 0.0, "R": 0.0}
    )
    monkeypatch.setattr(module.tsr_metrics, "score", lambda text: {"tsr": "bad"})
    assert module._compute_delta_norm("draft", {}) is None


def test_should_warn_collapse_requires_autonomous_high_delta_and_no_external_trigger() -> None:
    assert module._should_warn_collapse(Genesis.REACTIVE_USER, 0.9, {}) is False
    assert module._should_warn_collapse(Genesis.AUTONOMOUS, 0.7, {}) is False
    assert (
        module._should_warn_collapse(Genesis.AUTONOMOUS, 0.9, {"trigger": "user_request"}) is False
    )
    assert (
        module._should_warn_collapse(Genesis.AUTONOMOUS, 0.9, {"trigger": "self_reflection"})
        is True
    )


def test_infer_genesis_uses_journal_baseline_and_suppresses_warning_with_trigger(
    monkeypatch,
) -> None:
    monkeypatch.setattr(module, "load_recent_memory", lambda n=10: [{"summary": "baseline text"}])

    def fake_score(text: str):
        if text == "baseline text":
            return {"tsr": {"T": 0.1, "S_norm": 0.1, "R": 0.1}}
        return {"tsr": {"T": 1.0, "S_norm": 1.0, "R": 1.0}}

    monkeypatch.setattr(module.tsr_metrics, "score", fake_score)

    decision = module.infer_genesis("draft", context={"trigger": "user_request"})

    assert decision.genesis == Genesis.AUTONOMOUS
    assert decision.tsr_delta_norm is not None
    assert decision.tsr_delta_norm > module.DELTA_WARNING_THRESHOLD
    assert decision.collapse_warning is None
