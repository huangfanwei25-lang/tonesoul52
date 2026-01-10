from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union


class PerspectiveType(Enum):
    GUARDIAN = "guardian"
    ANALYST = "analyst"
    CRITIC = "critic"
    ADVOCATE = "advocate"


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
    GROUNDED = "grounded"          # Evidence provided and verified
    UNGROUNDED = "ungrounded"      # Evidence required but not provided
    PARTIAL = "partial"            # Some evidence provided, more needed


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
        return (
            self.c_inter * 0.4
            + self.approval_rate * 0.4
            + self.min_confidence * 0.2
        )


@dataclass
class CouncilVerdict:
    verdict: VerdictType
    coherence: CoherenceScore
    votes: List[PerspectiveVote]
    summary: str
    stance_declaration: Optional[str] = None
    refinement_hints: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "coherence": self.coherence.overall,
            "summary": self.summary,
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
                }
                for v in self.votes
            ],
        }
