"""Tests for AdaptiveGate - Phase II unified gate module."""

from __future__ import annotations

from tonesoul.adaptive_gate import AdaptiveGate, GateAction, GateDecision


class FakeZone:
    def __init__(self, value: str):
        self.value = value


class FakeLambda:
    def __init__(self, value: str):
        self.value = value


class FakeSignals:
    def __init__(self, semantic_delta: float = 0.0, t_ecs: float = 0.0):
        self.semantic_delta = semantic_delta
        self.delta_sigma = semantic_delta
        self.t_ecs = t_ecs


class FakeTensionResult:
    def __init__(
        self,
        zone: str = "safe",
        lambda_state: str = "convergent",
        bridge_allowed: bool = True,
        total: float = 0.3,
        semantic_delta: float = 0.0,
        t_ecs: float = 0.0,
    ):
        self.zone = FakeZone(zone)
        self.lambda_state = FakeLambda(lambda_state)
        self.bridge_allowed = bridge_allowed
        self.total = total
        self.signals = FakeSignals(semantic_delta=semantic_delta, t_ecs=t_ecs)


class TestZoneDecisions:
    def test_safe_zone_passes(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="safe"),
            persona_evaluation={"valid": True, "adaptive": {"factor": 1.0}},
        )
        assert decision.action == GateAction.PASS

    def test_transit_zone_warns(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="transit"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.WARN

    def test_risk_zone_reviews(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="risk"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.REVIEW

    def test_danger_zone_blocks(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="danger"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.BLOCK


class TestPersonaCombinations:
    def test_risk_plus_invalid_persona_blocks(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="risk"),
            persona_evaluation={"valid": False, "reasons": ["deltaT out of range"]},
        )
        assert decision.action == GateAction.BLOCK
        assert "persona_invalid" in decision.reasons[0]

    def test_transit_plus_invalid_persona_reviews(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="transit"),
            persona_evaluation={"valid": False},
        )
        assert decision.action == GateAction.REVIEW

    def test_safe_plus_invalid_persona_warns(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="safe"),
            persona_evaluation={"valid": False},
        )
        assert decision.action == GateAction.WARN


class TestLambdaEscalation:
    def test_chaotic_escalates_pass_to_warn(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="safe", lambda_state="chaotic"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.WARN

    def test_chaotic_escalates_warn_to_review(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="transit", lambda_state="chaotic"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.REVIEW

    def test_chaotic_escalates_review_to_block(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="risk", lambda_state="chaotic"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.BLOCK

    def test_convergent_no_escalation(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="safe", lambda_state="convergent"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.PASS


class TestBridgeGuard:
    def test_bridge_blocked_at_least_warns(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="safe", bridge_allowed=False),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.WARN
        assert not decision.bridge_allowed


class TestWFGYAlignmentRefinement:
    def test_high_t_align_escalates_safe_zone(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(
                zone="safe",
                total=0.1,
                semantic_delta=0.8,
                t_ecs=0.8,
            ),
            persona_evaluation={"valid": True, "distance": 0.8},
        )
        assert decision.action == GateAction.REVIEW
        assert decision.signals["t_align"] >= 0.6
        assert any("t_align=" in reason for reason in decision.reasons)

    def test_t_align_never_demotes_zone_decision(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="risk", semantic_delta=0.0, t_ecs=0.0),
            persona_evaluation={"valid": True, "distance": 0.0},
        )
        assert decision.action == GateAction.REVIEW

    def test_gate_modifier_tightens_alignment_escalation(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(
                zone="safe",
                total=0.1,
                semantic_delta=0.7,
                t_ecs=0.7,
            ),
            persona_evaluation={"valid": True, "distance": 0.7},
            gate_modifier=0.75,
        )
        assert decision.action == GateAction.BLOCK
        assert decision.signals["gate_modifier"] == 0.75


class TestDecisionHelpers:
    def test_should_intercept_on_review(self):
        d = GateDecision(action=GateAction.REVIEW)
        assert AdaptiveGate.should_intercept(d)

    def test_should_intercept_on_block(self):
        d = GateDecision(action=GateAction.BLOCK)
        assert AdaptiveGate.should_intercept(d)

    def test_should_not_intercept_on_pass(self):
        d = GateDecision(action=GateAction.PASS)
        assert not AdaptiveGate.should_intercept(d)

    def test_should_not_intercept_on_warn(self):
        d = GateDecision(action=GateAction.WARN)
        assert not AdaptiveGate.should_intercept(d)

    def test_should_block_only_on_block(self):
        assert AdaptiveGate.should_block(GateDecision(action=GateAction.BLOCK))
        assert not AdaptiveGate.should_block(GateDecision(action=GateAction.REVIEW))

    def test_decision_to_dict(self):
        d = GateDecision(
            action=GateAction.WARN,
            reasons=["test"],
            zone="transit",
            signals={"total_tension": 0.5},
        )
        data = d.to_dict()
        assert data["action"] == "warn"
        assert data["zone"] == "transit"
        assert data["signals"]["total_tension"] == 0.5


class TestEdgeCases:
    def test_no_tension_result(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(tension_result=None, persona_evaluation=None)
        assert decision.action == GateAction.REVIEW

    def test_no_persona_evaluation(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="risk"),
            persona_evaluation=None,
        )
        assert decision.action == GateAction.REVIEW

    def test_danger_overrides_valid_persona(self):
        gate = AdaptiveGate()
        decision = gate.evaluate(
            tension_result=FakeTensionResult(zone="danger"),
            persona_evaluation={"valid": True},
        )
        assert decision.action == GateAction.BLOCK
