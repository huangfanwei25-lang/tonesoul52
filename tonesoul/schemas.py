"""ToneSoul Pydantic Schemas — Data contracts for LLM and governance layers.

These schemas serve as "factory molds" (防呆模具) that validate all data
flowing through ToneSoul. When an LLM returns malformed JSON or missing
fields, Pydantic catches it instantly instead of causing mysterious
downstream crashes.

Usage:
    from tonesoul.schemas import CouncilStructuredVerdict, ToneAnalysisResult
    verdict = CouncilStructuredVerdict.model_validate(llm_json_dict)
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__ts_layer__ = "shared"
__ts_purpose__ = "Pydantic data contracts shared across council, LLM, and governance layers."

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ImpactLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionDecision(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"
    DEFER = "defer"


class LLMBackend(str, Enum):
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"
    AUTO = "auto"


class PerspectiveDecision(str, Enum):
    APPROVE = "approve"
    CONCERN = "concern"
    OBJECT = "object"
    ABSTAIN = "abstain"


class SubjectivityLayer(str, Enum):
    EVENT = "event"
    MEANING = "meaning"
    TENSION = "tension"
    VOW = "vow"
    IDENTITY = "identity"


class SubjectivityPromotionStatus(str, Enum):
    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    HUMAN_REVIEWED = "human_reviewed"
    GOVERNANCE_REVIEWED = "governance_reviewed"
    APPROVED = "approved"
    DEFERRED = "deferred"
    REJECTED = "rejected"


class DispatchTraceSection(TypedDict, total=False):
    """Normalized additive schema for dispatch/routing trace sections."""

    component: str
    timestamp: str
    status: str
    detail: Dict[str, Any]


# ---------------------------------------------------------------------------
# ToneBridge Schemas (Analyzer pipeline output)
# ---------------------------------------------------------------------------


class ToneAnalysisResult(BaseModel):
    """Schema for Stage 1: Tone Analysis output."""

    tone_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    tone_direction: List[str] = Field(default_factory=lambda: ["neutral"])
    tone_variability: float = Field(default=0.0, ge=0.0, le=1.0)
    emotion_prediction: str = Field(default="neutral")
    impact_level: ImpactLevel = Field(default=ImpactLevel.LOW)
    trigger_keywords: List[str] = Field(default_factory=list)
    modulation_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    semantic_intent: str = Field(default="")
    emotional_depth: float = Field(default=0.5, ge=0.0, le=1.0)
    tone_uncertainty: float = Field(default=0.5, ge=0.0, le=1.0)


class MotivePredictionResult(BaseModel):
    """Schema for Stage 2: Motive Prediction output."""

    motive_category: str = Field(default="")
    likely_motive: str = Field(default="")
    trigger_context: str = Field(default="")
    echo_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    resonance_chain_hint: List[str] = Field(default_factory=list)


class CollapseForecastResult(BaseModel):
    """Schema for Stage 3: Collapse Risk Forecasting."""

    collapse_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_factors: List[str] = Field(default_factory=list)
    recommended_action: str = Field(default="")
    time_horizon: str = Field(default="")


# ---------------------------------------------------------------------------
# Council Schemas
# ---------------------------------------------------------------------------


class PerspectiveOutput(BaseModel):
    """Schema for a single Council perspective evaluation."""

    perspective_name: str = Field(default="")
    position: str = Field(default="")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning: str = Field(default="")
    concerns: List[str] = Field(default_factory=list)


class PerspectiveEvaluationResult(BaseModel):
    """Schema for structured LLM output from a single council perspective."""

    decision: PerspectiveDecision = Field(default=PerspectiveDecision.CONCERN)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning: str = Field(default="")

    @field_validator("decision", mode="before")
    @classmethod
    def _normalize_decision(cls, value: object) -> str:
        return str(value or "concern").strip().lower()


class CouncilStructuredVerdict(BaseModel):
    """Schema for structured council deliberation output from an LLM or parser."""

    model_config = ConfigDict(extra="forbid")

    decision: ActionDecision = Field(default=ActionDecision.DEFER)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning: str = Field(default="")
    perspectives: List[PerspectiveOutput] = Field(default_factory=list)
    friction_score: float = Field(default=0.0, ge=0.0)
    dissenting_views: List[str] = Field(default_factory=list)


# Backward-compatible alias for older imports that still use the short name.
CouncilVerdict = CouncilStructuredVerdict


# ---------------------------------------------------------------------------
# Governance Schemas
# ---------------------------------------------------------------------------


class TensionSnapshot(BaseModel):
    """Schema for GovernanceKernel tension computation."""

    cognitive_friction: float = Field(default=0.0, ge=0.0)
    lyapunov_exponent: float = Field(default=0.0)
    phase_state: str = Field(default="stable")
    timestamp: str = Field(default="")
    signals: Dict[str, Any] = Field(default_factory=dict)


class CircuitBreakerState(BaseModel):
    """Schema for circuit breaker status."""

    is_tripped: bool = Field(default=False)
    trip_reason: str = Field(default="")
    cooldown_remaining_sec: float = Field(default=0.0)
    trip_count: int = Field(default=0)


class LLMRouteDecision(BaseModel):
    """Schema for GovernanceKernel LLM backend routing decisions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    backend: str = Field(default="none")
    client: Any = None
    reason: str = Field(default="")

    @field_validator("backend", mode="before")
    @classmethod
    def _normalize_backend(cls, value: object) -> str:
        normalized = str(value or "none").strip().lower()
        return normalized or "none"

    @field_validator("reason", mode="before")
    @classmethod
    def _normalize_reason(cls, value: object) -> str:
        return str(value or "")


class GovernanceDecision(BaseModel):
    """Schema for an aggregated governance turn decision."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm_route: Optional[LLMRouteDecision] = None
    should_convene_council: bool = False
    council_reason: str = Field(default="")
    friction_score: Optional[float] = None
    circuit_breaker_status: str = Field(default="ok")
    circuit_breaker_reason: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("council_reason", mode="before")
    @classmethod
    def _normalize_council_reason(cls, value: object) -> str:
        return str(value or "")

    @field_validator("circuit_breaker_status", mode="before")
    @classmethod
    def _normalize_circuit_breaker_status(cls, value: object) -> str:
        normalized = str(value or "ok").strip().lower()
        return normalized or "ok"

    @field_validator("provenance", mode="before")
    @classmethod
    def _normalize_provenance(cls, value: object) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}


class MirrorDelta(BaseModel):
    """Schema for raw output vs governed projection delta."""

    tension_before: TensionSnapshot
    tension_after: TensionSnapshot
    governance_decision: Optional[GovernanceDecision] = None
    subjectivity_flags: List[SubjectivityLayer] = Field(default_factory=list)
    delta_summary: str = Field(default="")
    mirror_triggered: bool = False

    @field_validator("delta_summary", mode="before")
    @classmethod
    def _normalize_delta_summary(cls, value: object) -> str:
        return str(value or "")


class DualTrackResponse(BaseModel):
    """Schema for raw/governed response pair plus mirror delta."""

    raw_response: str = Field(default="")
    governed_response: str = Field(default="")
    mirror_delta: MirrorDelta
    final_choice: str = Field(default="raw")
    reflection_note: str = Field(default="")

    @field_validator("raw_response", "governed_response", "reflection_note", mode="before")
    @classmethod
    def _normalize_text_fields(cls, value: object) -> str:
        return str(value or "")

    @field_validator("final_choice", mode="before")
    @classmethod
    def _normalize_final_choice(cls, value: object) -> str:
        normalized = str(value or "raw").strip().lower()
        if normalized not in {"raw", "governed", "synthesized"}:
            raise ValueError("final_choice must be raw, governed, or synthesized")
        return normalized or "raw"


class CouncilRuntimeVote(BaseModel):
    """Canonical runtime payload for one council vote entry."""

    model_config = ConfigDict(extra="allow")

    perspective: Optional[str] = None
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    evidence: Optional[List[str]] = None
    requires_grounding: Optional[bool] = None
    grounding_status: Optional[str] = None

    @field_validator("perspective", "reasoning", "grounding_status", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("decision", mode="before")
    @classmethod
    def _normalize_optional_decision(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator("evidence", mode="before")
    @classmethod
    def _normalize_evidence(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            return None
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return normalized


class CouncilRuntimeVerdictPayload(BaseModel):
    """Canonical outward-facing runtime council payload without changing API shape."""

    model_config = ConfigDict(extra="allow")

    verdict: Optional[str] = None
    reason: Optional[str] = None
    coherence: Optional[float] = None
    summary: Optional[str] = None
    votes: Optional[List[CouncilRuntimeVote]] = None
    metadata: Optional[Dict[str, Any]] = None
    divergence_analysis: Optional[Dict[str, Any]] = None
    transcript: Optional[Dict[str, Any]] = None
    human_summary: Optional[str] = None
    grounding_summary: Optional[Dict[str, Any]] = None
    benevolence_audit: Optional[Dict[str, Any]] = None
    persona_uniqueness_audit: Optional[Dict[str, Any]] = None
    persona_audit: Optional[Dict[str, Any]] = None
    responsibility_tier: Optional[str] = None
    intent_id: Optional[str] = None
    collapse_warning: Optional[str] = None
    uncertainty_band: Optional[str] = None
    uncertainty_reasons: Optional[List[str]] = None
    refinement_hints: Optional[List[str]] = None
    stance_declaration: Optional[str] = None

    @field_validator(
        "verdict",
        "reason",
        "summary",
        "human_summary",
        "responsibility_tier",
        "intent_id",
        "collapse_warning",
        "uncertainty_band",
        "stance_declaration",
        mode="before",
    )
    @classmethod
    def _normalize_optional_runtime_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            return None
        return normalized.lower() if cls.__pydantic_validator__ and False else normalized

    @field_validator("verdict", mode="before")
    @classmethod
    def _normalize_verdict(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator(
        "metadata",
        "divergence_analysis",
        "transcript",
        "grounding_summary",
        "benevolence_audit",
        "persona_uniqueness_audit",
        "persona_audit",
        mode="before",
    )
    @classmethod
    def _normalize_optional_dict(cls, value: object) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        return None

    @field_validator("uncertainty_reasons", "refinement_hints", mode="before")
    @classmethod
    def _normalize_optional_str_list(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            return None
        return [str(item).strip() for item in value if str(item).strip()]

    @classmethod
    def build_payload(cls, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            raw = dict(payload)
        else:
            raw = {}
        model = cls.model_validate(raw)
        return model.model_dump(exclude_none=True)


# ---------------------------------------------------------------------------
# Dream Engine Schemas (Phase 7)
# ---------------------------------------------------------------------------


class DreamStimulusRecord(BaseModel):
    """Schema for an external stimulus processed by Dream Engine."""

    source: str = Field(default="")
    title: str = Field(default="")
    content_preview: str = Field(default="")
    tension_score: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_tags: List[str] = Field(default_factory=list)
    fetched_at: str = Field(default="")


class DreamReflection(BaseModel):
    """Schema for a Dream Engine reflection output."""

    trigger_stimulus: str = Field(default="")
    reflection: str = Field(default="")
    new_boundary_rules: List[str] = Field(default_factory=list)
    meta_cognition: str = Field(default="")
    should_publish: bool = Field(default=False)
    publish_target: str = Field(default="")


# ---------------------------------------------------------------------------
# Memory Subjectivity Schemas
# ---------------------------------------------------------------------------


class SubjectivityPromotionGate(BaseModel):
    """Canonical review metadata for subjectivity promotion decisions."""

    status: SubjectivityPromotionStatus = Field(default=SubjectivityPromotionStatus.CANDIDATE)
    source: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_basis: Optional[str] = None
    approved_by: Optional[List[str]] = None
    human_review: Optional[bool] = None
    governance_review: Optional[bool] = None

    @field_validator("status", mode="before")
    @classmethod
    def _normalize_status(cls, value: object) -> str:
        normalized = str(value or SubjectivityPromotionStatus.CANDIDATE.value).strip().lower()
        return normalized or SubjectivityPromotionStatus.CANDIDATE.value

    @field_validator("source", "reviewed_by", "reviewed_at", "review_basis", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("approved_by", mode="before")
    @classmethod
    def _normalize_approved_by(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return [normalized] if normalized else None
        if not isinstance(value, list):
            raise ValueError("approved_by must be a list or string")
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return normalized or None

    @classmethod
    def build_payload(cls, **kwargs: Any) -> Dict[str, Any]:
        gate = cls.model_validate(kwargs)
        return gate.model_dump(mode="json", exclude_none=True)


class SubjectivityReviewActor(BaseModel):
    """Canonical reviewer identity for audited promotion decisions."""

    actor_id: str
    actor_type: str = Field(default="operator")
    display_name: Optional[str] = None

    @field_validator("actor_id", mode="before")
    @classmethod
    def _normalize_actor_id(cls, value: object) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError("actor_id is required")
        return normalized

    @field_validator("actor_type", mode="before")
    @classmethod
    def _normalize_actor_type(cls, value: object) -> str:
        normalized = str(value or "operator").strip().lower()
        return normalized or "operator"

    @field_validator("display_name", mode="before")
    @classmethod
    def _normalize_display_name(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None


class ReviewedPromotionDecision(BaseModel):
    """Auditable decision artifact for explicit subjectivity promotion."""

    status: SubjectivityPromotionStatus = Field(default=SubjectivityPromotionStatus.REVIEWED)
    promotion_source: str = Field(default="manual_review")
    review_actor: SubjectivityReviewActor
    source_subjectivity_layer: SubjectivityLayer
    target_subjectivity_layer: SubjectivityLayer
    reviewed_record_id: Optional[str] = None
    source_record_ids: List[str] = Field(default_factory=list)
    reviewed_at: str
    review_basis: str
    notes: Optional[str] = None

    @field_validator("status", mode="before")
    @classmethod
    def _normalize_review_status(cls, value: object) -> str:
        normalized = getattr(value, "value", value)
        normalized = str(normalized or SubjectivityPromotionStatus.REVIEWED.value).strip().lower()
        return normalized or SubjectivityPromotionStatus.REVIEWED.value

    @field_validator("source_subjectivity_layer", "target_subjectivity_layer", mode="before")
    @classmethod
    def _normalize_subjectivity_layer(cls, value: object) -> str:
        normalized = getattr(value, "value", value)
        normalized = str(normalized or "").strip().lower()
        return normalized

    @field_validator(
        "promotion_source",
        "reviewed_at",
        "review_basis",
        "notes",
        "reviewed_record_id",
        mode="before",
    )
    @classmethod
    def _normalize_required_text(cls, value: object, info: Any) -> Optional[str]:
        normalized = str(value or "").strip()
        if info.field_name in {"promotion_source", "reviewed_at", "review_basis"}:
            if not normalized:
                raise ValueError(f"{info.field_name} is required")
            return normalized
        return normalized or None

    @field_validator("source_record_ids", mode="before")
    @classmethod
    def _normalize_source_record_ids(cls, value: object) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("source_record_ids must be a list")
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return normalized

    @model_validator(mode="after")
    def _validate_decision_status(self) -> "ReviewedPromotionDecision":
        if self.status == SubjectivityPromotionStatus.CANDIDATE:
            raise ValueError("reviewed promotion decision cannot stay in candidate status")
        if self.source_subjectivity_layer == self.target_subjectivity_layer:
            raise ValueError("reviewed promotion requires distinct source and target layers")
        return self

    @classmethod
    def build_payload(cls, payload: Any) -> Dict[str, Any]:
        raw = dict(payload) if isinstance(payload, dict) else {}
        model = cls.model_validate(raw)
        return model.model_dump(mode="json", exclude_none=True)


class MemorySubjectivityPayload(BaseModel):
    """Canonical validation seam for subjectivity-aware memory payload fields."""

    model_config = ConfigDict(extra="ignore")

    subjectivity_layer: Optional[SubjectivityLayer] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    promotion_gate: Optional[SubjectivityPromotionGate] = None
    decay_policy: Optional[Dict[str, Any]] = None
    source_record_ids: Optional[List[str]] = None

    @field_validator("subjectivity_layer", mode="before")
    @classmethod
    def _normalize_subjectivity_layer(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator("promotion_gate", "decay_policy", mode="before")
    @classmethod
    def _normalize_optional_policy_dict(cls, value: object, info: Any) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if info.field_name == "promotion_gate":
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                normalized = value.strip()
                if not normalized:
                    return None
                return {"status": normalized.lower()}
            raise ValueError("promotion_gate must be a dict or string")
        if isinstance(value, dict):
            return {str(key): item for key, item in value.items()}
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            return {"policy": normalized}
        raise ValueError(f"{info.field_name} must be a dict or string")

    @field_validator("source_record_ids", mode="before")
    @classmethod
    def _normalize_source_record_ids(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("source_record_ids must be a list")
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return normalized or None

    @classmethod
    def normalize_fields(cls, payload: Any) -> Dict[str, Any]:
        raw = dict(payload) if isinstance(payload, dict) else {}
        if not any(
            key in raw
            for key in (
                "subjectivity_layer",
                "confidence",
                "promotion_gate",
                "decay_policy",
                "source_record_ids",
            )
        ):
            return {}
        model = cls.model_validate(raw)
        return model.model_dump(mode="json", exclude_none=True)


# ---------------------------------------------------------------------------
# Token Metering Schemas
# ---------------------------------------------------------------------------


class LLMCallMetrics(BaseModel):
    """Schema for token metering of a single LLM call."""

    model: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    latency_ms: Optional[float] = None
    trace_id: Optional[str] = None


class LLMUsageTrace(BaseModel):
    """Schema for emitted LLM usage fields inside runtime observability."""

    prompt_tokens: Optional[int] = Field(default=None, ge=0)
    completion_tokens: Optional[int] = Field(default=None, ge=0)
    total_tokens: Optional[int] = Field(default=None, ge=0)
    cost_usd: Optional[float] = Field(default=None, ge=0.0)
    latency_ms: Optional[float] = Field(default=None, ge=0.0)
    trace_id: Optional[str] = None

    @field_validator("trace_id", mode="before")
    @classmethod
    def _normalize_trace_id(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @classmethod
    def from_metrics(cls, metrics: Any) -> Optional["LLMUsageTrace"]:
        if metrics is None:
            return None

        payload = {
            key: getattr(metrics, key, None)
            for key in (
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "cost_usd",
                "latency_ms",
                "trace_id",
            )
        }
        if not any(value is not None for value in payload.values()):
            return None
        return cls.model_validate(payload)


class LLMObservabilityTrace(BaseModel):
    """Canonical runtime trace payload for LLM backend/model/usage observability."""

    backend: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[LLMUsageTrace] = None

    @field_validator("backend", mode="before")
    @classmethod
    def _normalize_backend(cls, value: object) -> Optional[str]:
        if not isinstance(value, str):
            return None
        normalized = value.strip().lower()
        return normalized or None

    @field_validator("model", mode="before")
    @classmethod
    def _normalize_model(cls, value: object) -> Optional[str]:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    @classmethod
    def build_payload(
        cls,
        *,
        backend: object = None,
        metrics: Any = None,
        fallback_model: object = None,
    ) -> Dict[str, Any]:
        metrics_model = getattr(metrics, "model", None)
        model_value = (
            metrics_model if isinstance(metrics_model, str) and metrics_model.strip() else None
        )
        if model_value is None and isinstance(fallback_model, str) and fallback_model.strip():
            model_value = fallback_model

        usage = LLMUsageTrace.from_metrics(metrics)
        trace = cls.model_validate(
            {
                "backend": backend,
                "model": model_value,
                "usage": usage,
            }
        )
        return trace.model_dump(exclude_none=True)


# ---------------------------------------------------------------------------
# Export all schemas
# ---------------------------------------------------------------------------

__all__ = [
    "ActionDecision",
    "CircuitBreakerState",
    "CouncilVerdict",
    "CollapseForecastResult",
    "CouncilRuntimeVerdictPayload",
    "CouncilRuntimeVote",
    "DualTrackResponse",
    "DreamReflection",
    "DreamStimulusRecord",
    "GovernanceDecision",
    "ImpactLevel",
    "LLMBackend",
    "LLMCallMetrics",
    "LLMObservabilityTrace",
    "LLMRouteDecision",
    "LLMUsageTrace",
    "MotivePredictionResult",
    "MemorySubjectivityPayload",
    "MirrorDelta",
    "PerspectiveDecision",
    "PerspectiveEvaluationResult",
    "PerspectiveOutput",
    "SubjectivityLayer",
    "SubjectivityPromotionGate",
    "SubjectivityPromotionStatus",
    "SubjectivityReviewActor",
    "TensionSnapshot",
    "ToneAnalysisResult",
    "ReviewedPromotionDecision",
]
