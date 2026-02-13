"""Adversarial self-reflection interfaces (experimental stub)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ChallengeType(Enum):
    """Types of challenges surfaced by red-team style reflection."""

    CONTRADICTION = "contradiction"
    BROKEN_COMMITMENT = "broken_commitment"
    VALUE_DRIFT = "value_drift"
    INCONSISTENCY = "inconsistency"


@dataclass
class Challenge:
    """A challenge raised by the adversarial checker."""

    challenge_type: ChallengeType
    description: str
    evidence: List[str] = field(default_factory=list)
    severity: float = 0.5

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": self.challenge_type.value,
            "description": self.description,
            "evidence": list(self.evidence),
            "severity": float(self.severity),
        }


@dataclass
class Repair:
    """A repair proposal mapped from one challenge."""

    challenge: Challenge
    repair_type: str
    explanation: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "challenge": self.challenge.to_dict(),
            "repair_type": self.repair_type,
            "explanation": self.explanation,
        }


class AdversarialReflector:
    """Research stub for red/blue adversarial self-reflection loops."""

    def __init__(self) -> None:
        self._challenges: List[Challenge] = []
        self._repairs: List[Repair] = []

    def run_red_team(
        self,
        commitments: List[Dict],
        contradictions: List[Dict],
        values: List[Dict],
    ) -> List[Challenge]:
        del commitments, values
        challenges: List[Challenge] = []
        for contradiction in contradictions:
            if not isinstance(contradiction, dict):
                continue
            description = str(contradiction.get("description", "Unknown contradiction"))
            raw_severity = contradiction.get("severity", 0.5)
            try:
                severity = float(raw_severity)
            except (TypeError, ValueError):
                severity = 0.5
            evidence_value = contradiction.get("path", [])
            if isinstance(evidence_value, list):
                evidence = [str(item) for item in evidence_value]
            else:
                evidence = [str(evidence_value)] if evidence_value else []
            challenges.append(
                Challenge(
                    challenge_type=ChallengeType.CONTRADICTION,
                    description=description,
                    evidence=evidence,
                    severity=max(0.0, min(1.0, severity)),
                )
            )

        self._challenges = challenges
        return challenges

    def run_blue_team(self, challenges: Optional[List[Challenge]] = None) -> List[Repair]:
        source = challenges or self._challenges
        repairs: List[Repair] = []
        for challenge in source:
            repairs.append(
                Repair(
                    challenge=challenge,
                    repair_type="acknowledge_change",
                    explanation=f"Stub: {challenge.description} — needs review",
                )
            )
        self._repairs = repairs
        return repairs

    def get_summary(self) -> Dict[str, object]:
        return {
            "challenges_found": len(self._challenges),
            "repairs_proposed": len(self._repairs),
            "challenges": [challenge.to_dict() for challenge in self._challenges],
            "repairs": [repair.to_dict() for repair in self._repairs],
        }
