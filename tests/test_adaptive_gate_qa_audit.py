"""
QA Audit test for AdaptiveGate (D4/Integrity)

Simulates chaotic payloads a QA Auditor Red Team skill would inject
to test how resilient AdaptiveGate is against malformed inputs.
"""

from tonesoul.adaptive_gate import AdaptiveGate, GateAction
from tonesoul.semantic_control import SemanticZone


def test_corrupted_tension_result_triggers_review():
    """
    Chaos: Agent builds a TensionResult with zone=None (e.g. JSON parse failure).
    Gate must NOT default to PASS (fail-open). It should fallback to REVIEW.
    """
    gate = AdaptiveGate()

    class CorruptedTensionResult:
        pass

    corrupted = CorruptedTensionResult()
    corrupted.zone = None  # missing or broken

    decision = gate.evaluate(corrupted, None)

    assert decision.action in (GateAction.REVIEW, GateAction.BLOCK, GateAction.WARN)
    assert any("unknown" in r for r in decision.reasons)


def test_malformed_persona_eval_does_not_crash():
    """
    Chaos: persona_evaluation is a raw string instead of expected dict.
    Gate MUST NOT raise AttributeError — it should treat it as "no persona data".
    """
    gate = AdaptiveGate()

    class FakeTension:
        zone = SemanticZone.SAFE
        lambda_state = None
        bridge_allowed = True
        total = 0.1

    decision = gate.evaluate(FakeTension(), "Error: Database locked")

    # isinstance(persona_evaluation, dict) is False → persona_valid stays True
    assert decision.action is not None
    assert decision.persona_valid is True  # fallback default


def test_completely_empty_evaluate():
    """
    Chaos: Both arguments are None — absolute worst case.
    Must still return a valid GateDecision, never raise.
    """
    gate = AdaptiveGate()
    decision = gate.evaluate(None, None)

    assert decision.action == GateAction.REVIEW
    assert decision.zone == "unknown"
    assert decision.persona_valid is True


def test_persona_eval_with_wrong_types():
    """
    Chaos: persona_evaluation dict has wrong value types.
    'valid' is a string instead of bool, 'adaptive' is an int instead of dict.
    """
    gate = AdaptiveGate()

    class FakeTension:
        zone = SemanticZone.SAFE
        lambda_state = None
        bridge_allowed = True
        total = 0.2

    weird_persona = {
        "valid": "yes",  # should be bool
        "adaptive": 42,  # should be dict
        "distance": "far",  # should be float
    }

    decision = gate.evaluate(FakeTension(), weird_persona)
    # Should not crash — coercion should handle gracefully
    assert decision.action is not None
