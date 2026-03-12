"""Tests for Pydantic schemas and safe JSON parsing."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_tone_analysis_defaults(self):
        from tonesoul.schemas import ToneAnalysisResult

        result = ToneAnalysisResult()
        assert result.tone_strength == 0.5
        assert result.emotion_prediction == "neutral"
        assert result.impact_level == "low"

    def test_tone_analysis_from_llm_dict(self):
        from tonesoul.schemas import ToneAnalysisResult

        data = {
            "tone_strength": 0.8,
            "tone_direction": ["assertive", "questioning"],
            "emotion_prediction": "curiosity",
            "impact_level": "high",
        }
        result = ToneAnalysisResult.model_validate(data)
        assert result.tone_strength == 0.8
        assert result.impact_level == "high"
        # Missing fields get defaults
        assert result.tone_variability == 0.0

    def test_tone_analysis_clamps_values(self):
        from tonesoul.schemas import ToneAnalysisResult

        # Values outside [0, 1] should fail validation
        with pytest.raises(ValidationError):
            ToneAnalysisResult(tone_strength=1.5)

    def test_council_verdict_defaults(self):
        from tonesoul.schemas import CouncilStructuredVerdict

        v = CouncilStructuredVerdict()
        assert v.decision == "defer"
        assert v.confidence == 0.5
        assert v.perspectives == []

    def test_council_verdict_from_llm(self):
        from tonesoul.schemas import CouncilStructuredVerdict

        data = {
            "decision": "approve",
            "confidence": 0.92,
            "reasoning": "All perspectives agree",
            "friction_score": 0.15,
        }
        v = CouncilStructuredVerdict.model_validate(data)
        assert v.decision == "approve"
        assert v.friction_score == 0.15

    def test_council_verdict_invalid_decision(self):
        from tonesoul.schemas import CouncilStructuredVerdict

        with pytest.raises(ValidationError):
            CouncilStructuredVerdict(decision="yolo")

    def test_council_structured_verdict_rejects_runtime_payload_shape(self):
        from tonesoul.schemas import CouncilStructuredVerdict

        with pytest.raises(ValidationError):
            CouncilStructuredVerdict.model_validate(
                {
                    "verdict": "refine",
                    "summary": "Needs stronger alignment before response.",
                    "votes": [{"perspective": "analyst", "decision": "concern"}],
                }
            )

    def test_council_verdict_legacy_alias_still_resolves_to_structured_schema(self):
        from tonesoul.schemas import CouncilStructuredVerdict, CouncilVerdict

        assert CouncilVerdict is CouncilStructuredVerdict
        verdict = CouncilVerdict.model_validate({"decision": "approve", "confidence": 0.9})
        assert verdict.decision == "approve"

    def test_perspective_evaluation_result_normalizes_uppercase_decision(self):
        from tonesoul.schemas import PerspectiveEvaluationResult

        result = PerspectiveEvaluationResult.model_validate(
            {"decision": "APPROVE", "confidence": 0.91, "reasoning": "structured"}
        )

        assert result.decision == "approve"
        assert result.confidence == 0.91

    def test_tension_snapshot(self):
        from tonesoul.schemas import TensionSnapshot

        t = TensionSnapshot(
            cognitive_friction=0.73,
            lyapunov_exponent=1.2,
            phase_state="crystallizing",
        )
        assert t.cognitive_friction == 0.73
        assert t.phase_state == "crystallizing"

    def test_llm_route_decision_normalizes_backend_and_preserves_client(self):
        from tonesoul.schemas import LLMRouteDecision

        client = object()
        result = LLMRouteDecision(backend="  OLLAMA  ", client=client, reason=None)

        assert result.backend == "ollama"
        assert result.client is client
        assert result.reason == ""

    def test_governance_decision_accepts_nested_route_dict(self):
        from tonesoul.schemas import GovernanceDecision

        result = GovernanceDecision.model_validate(
            {
                "llm_route": {"backend": "LMSTUDIO", "client": None, "reason": "auto"},
                "should_convene_council": True,
                "circuit_breaker_status": " FROZEN ",
                "provenance": None,
            }
        )

        assert result.llm_route is not None
        assert result.llm_route.backend == "lmstudio"
        assert result.should_convene_council is True
        assert result.circuit_breaker_status == "frozen"
        assert result.provenance == {}

    def test_mirror_delta_serializes_nested_governance_and_subjectivity_flags(self):
        from tonesoul.schemas import MirrorDelta

        result = MirrorDelta.model_validate(
            {
                "tension_before": {
                    "cognitive_friction": 0.71,
                    "lyapunov_exponent": 0.18,
                    "phase_state": "unstable",
                    "timestamp": "2026-03-10T08:00:00Z",
                },
                "tension_after": {
                    "cognitive_friction": 0.33,
                    "lyapunov_exponent": 0.05,
                    "phase_state": "stabilizing",
                    "timestamp": "2026-03-10T08:00:01Z",
                },
                "governance_decision": {
                    "should_convene_council": True,
                    "council_reason": "High runtime friction",
                    "friction_score": 0.71,
                    "circuit_breaker_status": "OK",
                },
                "subjectivity_flags": ["tension", "meaning"],
                "delta_summary": "Mirror detected a meaningful governance delta.",
                "mirror_triggered": True,
            }
        )

        assert result.mirror_triggered is True
        assert result.governance_decision is not None
        assert result.governance_decision.circuit_breaker_status == "ok"
        assert result.subjectivity_flags == ["tension", "meaning"]
        assert result.model_dump(mode="json") == {
            "tension_before": {
                "cognitive_friction": 0.71,
                "lyapunov_exponent": 0.18,
                "phase_state": "unstable",
                "timestamp": "2026-03-10T08:00:00Z",
                "signals": {},
            },
            "tension_after": {
                "cognitive_friction": 0.33,
                "lyapunov_exponent": 0.05,
                "phase_state": "stabilizing",
                "timestamp": "2026-03-10T08:00:01Z",
                "signals": {},
            },
            "governance_decision": {
                "llm_route": None,
                "should_convene_council": True,
                "council_reason": "High runtime friction",
                "friction_score": 0.71,
                "circuit_breaker_status": "ok",
                "circuit_breaker_reason": None,
                "provenance": {},
            },
            "subjectivity_flags": ["tension", "meaning"],
            "delta_summary": "Mirror detected a meaningful governance delta.",
            "mirror_triggered": True,
        }

    def test_dual_track_response_normalizes_final_choice_and_keeps_delta_json_safe(self):
        from tonesoul.schemas import DualTrackResponse

        result = DualTrackResponse.model_validate(
            {
                "raw_response": "I should answer immediately.",
                "governed_response": "I should answer carefully.",
                "mirror_delta": {
                    "tension_before": {"cognitive_friction": 0.64},
                    "tension_after": {"cognitive_friction": 0.29},
                    "mirror_triggered": True,
                    "subjectivity_flags": ["tension"],
                },
                "final_choice": " SYNTHESIZED ",
                "reflection_note": "Governance softened the response tone.",
            }
        )

        payload = result.model_dump(mode="json")

        assert result.final_choice == "synthesized"
        assert payload["final_choice"] == "synthesized"
        assert payload["mirror_delta"]["subjectivity_flags"] == ["tension"]
        assert payload["reflection_note"] == "Governance softened the response tone."

    def test_council_runtime_verdict_payload_normalizes_minimal_gate_verdict(self):
        from tonesoul.schemas import CouncilRuntimeVerdictPayload

        payload = CouncilRuntimeVerdictPayload.build_payload(
            {"verdict": "  BLOCKED_BY_GATE  ", "reason": None}
        )

        assert payload == {"verdict": "blocked_by_gate"}

    def test_council_runtime_verdict_payload_preserves_rich_runtime_shape(self):
        from tonesoul.schemas import CouncilRuntimeVerdictPayload

        payload = CouncilRuntimeVerdictPayload.build_payload(
            {
                "verdict": "REFINE",
                "summary": "Needs stronger alignment before response.",
                "votes": [
                    {
                        "perspective": "analyst",
                        "decision": "CONCERN",
                        "confidence": 0.82,
                        "reasoning": "logic chain needs clearer assumptions",
                        "evidence": ["trace://logic", ""],
                    }
                ],
                "divergence_analysis": {"quality": {"score": 0.81, "band": "high"}},
                "metadata": {"dispatch_state": "B"},
            }
        )

        assert payload["verdict"] == "refine"
        assert payload["summary"] == "Needs stronger alignment before response."
        assert payload["votes"] == [
            {
                "perspective": "analyst",
                "decision": "concern",
                "confidence": 0.82,
                "reasoning": "logic chain needs clearer assumptions",
                "evidence": ["trace://logic"],
            }
        ]
        assert payload["divergence_analysis"] == {"quality": {"score": 0.81, "band": "high"}}
        assert payload["metadata"] == {"dispatch_state": "B"}

    def test_dream_reflection(self):
        from tonesoul.schemas import DreamReflection

        r = DreamReflection(
            trigger_stimulus="moltbook_post_123",
            reflection="Memory decay patterns observed",
            should_publish=True,
            publish_target="moltbook",
        )
        assert r.should_publish is True

    def test_llm_call_metrics(self):
        from tonesoul.schemas import LLMCallMetrics

        m = LLMCallMetrics(
            model="gemma3:4b",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        assert m.cost_usd == 0.0
        assert m.total_tokens == 150

    def test_llm_call_metrics_rejects_negative(self):
        from tonesoul.schemas import LLMCallMetrics

        with pytest.raises(ValidationError):
            LLMCallMetrics(model="test", prompt_tokens=-1, completion_tokens=0, total_tokens=0)

    def test_llm_observability_trace_builds_from_metrics(self):
        from tonesoul.schemas import LLMCallMetrics, LLMObservabilityTrace

        metrics = LLMCallMetrics(
            model="qwen3.5:8b",
            prompt_tokens=12,
            completion_tokens=7,
            total_tokens=19,
        )

        payload = LLMObservabilityTrace.build_payload(
            backend="  OLLAMA  ",
            metrics=metrics,
            fallback_model="ignored-model",
        )

        assert payload == {
            "backend": "ollama",
            "model": "qwen3.5:8b",
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 7,
                "total_tokens": 19,
                "cost_usd": 0.0,
            },
        }

    def test_llm_observability_trace_falls_back_to_runtime_model_without_usage(self):
        from tonesoul.schemas import LLMObservabilityTrace

        payload = LLMObservabilityTrace.build_payload(
            backend="ollama",
            metrics=None,
            fallback_model="qwen3.5:4b",
        )

        assert payload == {
            "backend": "ollama",
            "model": "qwen3.5:4b",
        }

    def test_memory_subjectivity_payload_normalizes_supported_fields(self):
        from tonesoul.schemas import MemorySubjectivityPayload

        payload = MemorySubjectivityPayload.normalize_fields(
            {
                "subjectivity_layer": "  TENSION ",
                "confidence": 0.82,
                "promotion_gate": {
                    "status": "Reviewed",
                    "reviewed_by": "operator",
                    "review_basis": "Repeated governance tension across cycles.",
                },
                "decay_policy": "slow",
                "source_record_ids": [" a ", "", "b"],
            }
        )

        assert payload == {
            "subjectivity_layer": "tension",
            "confidence": 0.82,
            "promotion_gate": {
                "status": "reviewed",
                "reviewed_by": "operator",
                "review_basis": "Repeated governance tension across cycles.",
            },
            "decay_policy": {"policy": "slow"},
            "source_record_ids": ["a", "b"],
        }

    def test_memory_subjectivity_payload_rejects_invalid_layer(self):
        from tonesoul.schemas import MemorySubjectivityPayload

        with pytest.raises(ValidationError):
            MemorySubjectivityPayload.normalize_fields({"subjectivity_layer": "myth"})

    def test_subjectivity_promotion_gate_builds_review_metadata(self):
        from tonesoul.schemas import SubjectivityPromotionGate

        payload = SubjectivityPromotionGate.build_payload(
            status="human_reviewed",
            source="manual_review",
            reviewed_by="operator",
            review_basis="Repeated tension with stable source evidence.",
            approved_by="guardian",
        )

        assert payload == {
            "status": "human_reviewed",
            "source": "manual_review",
            "reviewed_by": "operator",
            "review_basis": "Repeated tension with stable source evidence.",
            "approved_by": ["guardian"],
        }

    def test_reviewed_promotion_decision_serializes_actor_and_layers(self):
        from tonesoul.schemas import ReviewedPromotionDecision

        payload = ReviewedPromotionDecision.build_payload(
            {
                "status": "approved",
                "promotion_source": "manual_review",
                "review_actor": {
                    "actor_id": " operator ",
                    "actor_type": " Human ",
                    "display_name": " Operator Console ",
                },
                "source_subjectivity_layer": " TENSION ",
                "target_subjectivity_layer": " vow ",
                "reviewed_record_id": " tension-001 ",
                "source_record_ids": [" a ", "", "b"],
                "reviewed_at": "2026-03-10T12:00:00Z",
                "review_basis": "Repeated unresolved tension across reviewed cycles.",
            }
        )

        assert payload == {
            "status": "approved",
            "promotion_source": "manual_review",
            "review_actor": {
                "actor_id": "operator",
                "actor_type": "human",
                "display_name": "Operator Console",
            },
            "source_subjectivity_layer": "tension",
            "target_subjectivity_layer": "vow",
            "reviewed_record_id": "tension-001",
            "source_record_ids": ["a", "b"],
            "reviewed_at": "2026-03-10T12:00:00Z",
            "review_basis": "Repeated unresolved tension across reviewed cycles.",
        }

    def test_reviewed_promotion_decision_rejects_candidate_status(self):
        from tonesoul.schemas import ReviewedPromotionDecision

        with pytest.raises(ValidationError):
            ReviewedPromotionDecision.model_validate(
                {
                    "status": "candidate",
                    "promotion_source": "manual_review",
                    "review_actor": {"actor_id": "operator"},
                    "source_subjectivity_layer": "tension",
                    "target_subjectivity_layer": "vow",
                    "reviewed_at": "2026-03-10T12:00:00Z",
                    "review_basis": "Still under review.",
                }
            )


# ---------------------------------------------------------------------------
# Safe parse tests
# ---------------------------------------------------------------------------


class TestSafeParse:
    def test_parse_clean_json(self):
        from tonesoul.safe_parse import safe_parse_json

        result = safe_parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_markdown_code_block(self):
        from tonesoul.safe_parse import safe_parse_json

        text = 'Here is the result:\n```json\n{"tone_strength": 0.8}\n```\nDone!'
        result = safe_parse_json(text)
        assert result == {"tone_strength": 0.8}

    def test_parse_embedded_json(self):
        from tonesoul.safe_parse import safe_parse_json

        text = 'The analysis shows: {"risk": 0.3, "action": "monitor"} as expected.'
        result = safe_parse_json(text)
        assert result["risk"] == 0.3

    def test_parse_balanced_json_before_trailing_brace_noise(self):
        from tonesoul.safe_parse import safe_parse_json

        text = (
            'Result: {"decision":"APPROVE","confidence":0.84,"reasoning":"structured wins"} '
            "trailing note {OBJECT}"
        )
        result = safe_parse_json(text)

        assert result == {
            "decision": "APPROVE",
            "confidence": 0.84,
            "reasoning": "structured wins",
        }

    def test_parse_trailing_comma(self):
        from tonesoul.safe_parse import safe_parse_json

        text = '{"a": 1, "b": 2,}'
        result = safe_parse_json(text)
        assert result == {"a": 1, "b": 2}

    def test_parse_empty_returns_none(self):
        from tonesoul.safe_parse import safe_parse_json

        assert safe_parse_json("") is None
        assert safe_parse_json("no json here at all") is None

    def test_parse_llm_response_with_schema(self):
        from tonesoul.safe_parse import parse_llm_response
        from tonesoul.schemas import ToneAnalysisResult

        llm_text = '```json\n{"tone_strength": 0.9, "emotion_prediction": "joy"}\n```'
        result = parse_llm_response(llm_text, ToneAnalysisResult)
        assert result is not None
        assert result.tone_strength == 0.9
        assert result.emotion_prediction == "joy"
        # Defaults filled in
        assert result.impact_level == "low"

    def test_parse_llm_response_invalid_returns_none(self):
        from tonesoul.safe_parse import parse_llm_response
        from tonesoul.schemas import ToneAnalysisResult

        result = parse_llm_response("not json at all", ToneAnalysisResult)
        assert result is None

    def test_parse_llm_response_strict_raises(self):
        from tonesoul.safe_parse import parse_llm_response
        from tonesoul.schemas import ToneAnalysisResult

        with pytest.raises(ValueError):
            parse_llm_response("garbage", ToneAnalysisResult, strict=True)

    def test_validate_dict(self):
        from tonesoul.safe_parse import validate_dict
        from tonesoul.schemas import CouncilStructuredVerdict

        data = {"decision": "approve", "confidence": 0.95}
        v = validate_dict(data, CouncilStructuredVerdict)
        assert v.decision == "approve"

    def test_validate_dict_rejects_bad_data(self):
        from tonesoul.safe_parse import validate_dict
        from tonesoul.schemas import CouncilStructuredVerdict

        with pytest.raises(Exception):
            validate_dict({"decision": "invalid_action"}, CouncilStructuredVerdict)

    def test_validate_dict_legacy_council_verdict_alias_still_works(self):
        from tonesoul.safe_parse import validate_dict
        from tonesoul.schemas import CouncilVerdict

        verdict = validate_dict({"decision": "approve", "confidence": 0.95}, CouncilVerdict)
        assert verdict.decision == "approve"
