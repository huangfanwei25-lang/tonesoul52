"""Council types: shared dataclasses/enums for perspectives, votes, and verdicts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Union

from memory.genesis import Genesis

if TYPE_CHECKING:
    from tonesoul.gse.strategy_mirror import StrategySignature

    from .epistemic_labeler import EpistemicLabel
    from .persona_audit import AuditResult


__ts_layer__ = "shared"
__ts_purpose__ = (
    "Shared type primitives (PerspectiveType, VoteDecision, verdicts) for the council subsystem."
)


class PerspectiveType(Enum):
    GUARDIAN = "guardian"
    ANALYST = "analyst"
    CRITIC = "critic"
    ADVOCATE = "advocate"
    AXIOMATIC = "axiomatic"


class VoteDecision(Enum):
    APPROVE = "approve"
    CONCERN = "concern"
    OBJECT = "object"
    ABSTAIN = "abstain"


class VerdictType(Enum):
    APPROVE = "approve"
    REFINE = "refine"
    DECLARE_STANCE = "declare_stance"
    BLOCK = "block"


class GroundingStatus(Enum):
    """Status of evidence grounding for a perspective vote."""

    NOT_REQUIRED = "not_required"  # Content doesn't need external evidence
    GROUNDED = "grounded"  # Evidence provided and verified
    UNGROUNDED = "ungrounded"  # Evidence required but not provided
    PARTIAL = "partial"  # Some evidence provided, more needed


# Maximum confidence when grounding is required but not provided
UNGROUNDED_CONFIDENCE_CAP = 0.6


@dataclass
class PerspectiveVote:
    perspective: Union[PerspectiveType, str]
    decision: VoteDecision
    confidence: float
    reasoning: str
    evidence: Optional[List[str]] = None
    requires_grounding: bool = False
    grounding_status: GroundingStatus = GroundingStatus.NOT_REQUIRED
    # Per-vote evidence_chain (PR #48 — vote_evidence_chain). Records HOW the
    # perspective reached its vote: substantive engagement vs default fallback.
    # Each entry is a dict with at minimum {"branch": <name>, "type": "substantive"
    # | "default_fallback"}. Optional default keeps backward compat for fixtures
    # constructing PerspectiveVote without it. Surface in human_summary via
    # _format_dissent_detail (PR #45 + #48). Resolves Day 1 calibration sprint
    # findings #5 + #7 (substantive vs fallback indistinguishable at vote shape).
    evidence_chain: Optional[List[dict]] = None


@dataclass
class CoherenceScore:
    c_inter: float
    approval_rate: float
    min_confidence: float
    has_strong_objection: bool

    @property
    def overall(self) -> float:
        if self.has_strong_objection:
            return min(self.c_inter, 0.3)
        return self.c_inter * 0.4 + self.approval_rate * 0.4 + self.min_confidence * 0.2


@dataclass
class CouncilVerdict:
    verdict: VerdictType
    coherence: CoherenceScore
    votes: List[PerspectiveVote]
    summary: str
    stance_declaration: Optional[str] = None
    refinement_hints: Optional[List[str]] = None
    transcript: Optional[dict] = None
    human_summary: Optional[str] = None
    divergence_analysis: Optional[dict] = None
    genesis: Optional[Genesis] = None
    responsibility_tier: Optional[str] = None
    intent_id: Optional[str] = None
    is_mine: Optional[bool] = None
    tsr_delta_norm: Optional[float] = None
    collapse_warning: Optional[str] = None
    uncertainty_level: Optional[float] = None
    uncertainty_band: Optional[str] = None
    uncertainty_reasons: Optional[List[str]] = None
    benevolence_audit: Optional[dict] = None  # Added for 7D Backend Auditor
    persona_uniqueness_audit: Optional[dict] = None
    persona_audit: Optional["AuditResult"] = None
    # Phase 864a Layer 1 — see council/epistemic_labeler.py for rationale.
    # Default None preserves backward compatibility for existing callers that
    # build CouncilVerdict directly (tests, persisted fixtures); the runtime
    # PreOutputCouncil.validate() always populates it.
    epistemic_label: Optional["EpistemicLabel"] = None
    # Phase 2 strategy_mirror — attached only when
    # SOUL.gse.strategy_mirror_scan_enabled is True (default off). When present,
    # downstream consumers can read green/yellow/red counts and the
    # requires_block / requires_council_re_review flags. In scan-only shadow
    # mode these flags are observational; in enforce mode they explain why an
    # APPROVE verdict may have been forced to BLOCK.
    # See docs/gse/phase_2_strategy_mirror_spec.md §5 for the integration contract.
    strategy_signature: Optional["StrategySignature"] = None
    deliberation_trace: Optional[object] = None  # DeliberationTrace from 864c

    def to_dict(self) -> dict:
        """
        Convert verdict to dictionary for audit logging.

        Includes evidence and grounding status for each vote.
        """
        persona_audit_payload: dict = {}
        if self.persona_audit is not None:
            if hasattr(self.persona_audit, "to_dict"):
                persona_audit_payload = self.persona_audit.to_dict()  # type: ignore[assignment]
            elif isinstance(self.persona_audit, dict):
                persona_audit_payload = self.persona_audit
        elif isinstance(self.persona_uniqueness_audit, dict):
            persona_audit_payload = self.persona_uniqueness_audit

        return {
            "verdict": self.verdict.value,
            "coherence": self.coherence.overall,
            "summary": self.summary,
            "genesis": self.genesis.value if isinstance(self.genesis, Genesis) else self.genesis,
            "responsibility_tier": self.responsibility_tier,
            "intent_id": self.intent_id,
            "is_mine": self.is_mine,
            "tsr_delta_norm": self.tsr_delta_norm,
            "collapse_warning": self.collapse_warning,
            "uncertainty_level": self.uncertainty_level,
            "uncertainty_band": self.uncertainty_band,
            "uncertainty_reasons": self.uncertainty_reasons or [],
            "votes": [
                {
                    "perspective": (
                        v.perspective.value
                        if isinstance(v.perspective, PerspectiveType)
                        else str(v.perspective)
                    ),
                    "decision": v.decision.value,
                    "confidence": v.confidence,
                    "reasoning": v.reasoning,
                    # Evidence tracking for audit
                    "evidence": v.evidence or [],
                    "requires_grounding": v.requires_grounding,
                    "grounding_status": (
                        v.grounding_status.value
                        if isinstance(v.grounding_status, GroundingStatus)
                        else str(v.grounding_status)
                    ),
                    # Per-vote evidence_chain (PR #48). None when not populated
                    # by the perspective; absent for legacy fixtures.
                    "evidence_chain": v.evidence_chain,
                }
                for v in self.votes
            ],
            # Summary of grounding status across all votes
            "grounding_summary": {
                "has_ungrounded_claims": any(
                    v.grounding_status == GroundingStatus.UNGROUNDED for v in self.votes
                ),
                "total_evidence_sources": sum(len(v.evidence or []) for v in self.votes),
            },
            "transcript": self.transcript or {},
            "benevolence_audit": self.benevolence_audit or {},  # Added for 7D Backend Auditor
            "persona_uniqueness_audit": self.persona_uniqueness_audit or persona_audit_payload,
            "persona_audit": persona_audit_payload,
            "human_summary": self.human_summary,
            "divergence_analysis": self.divergence_analysis or {},
            "epistemic_label": (
                self.epistemic_label.to_dict() if self.epistemic_label is not None else None
            ),
            "strategy_signature": (
                self.strategy_signature.to_dict() if self.strategy_signature is not None else None
            ),
            "deliberation_trace": (
                self.deliberation_trace.to_dict()
                if self.deliberation_trace and hasattr(self.deliberation_trace, "to_dict")
                else None
            ),
        }
