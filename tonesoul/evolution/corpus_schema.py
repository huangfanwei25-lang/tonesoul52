"""Structured corpus schema for distillation-ready training entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CorpusEntry:
    """One structured ethical decision record."""

    user_message: str
    conversation_context: str
    philosopher_stance: str
    engineer_approach: str
    guardian_risk: str
    synthesizer_decision: str
    tension_level: float
    values_invoked: list[str] = field(default_factory=list)
    commitments_made: list[str] = field(default_factory=list)
    risks_identified: list[str] = field(default_factory=list)
    final_response: str = ""
    user_satisfaction: str | None = None
    timestamp: str = ""
    conversation_id: str = ""
    quality_score: float | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_message": self.user_message,
            "conversation_context": self.conversation_context,
            "philosopher_stance": self.philosopher_stance,
            "engineer_approach": self.engineer_approach,
            "guardian_risk": self.guardian_risk,
            "synthesizer_decision": self.synthesizer_decision,
            "tension_level": float(self.tension_level),
            "values_invoked": list(self.values_invoked),
            "commitments_made": list(self.commitments_made),
            "risks_identified": list(self.risks_identified),
            "final_response": self.final_response,
            "user_satisfaction": self.user_satisfaction,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "quality_score": self.quality_score,
            "tags": list(self.tags),
        }
