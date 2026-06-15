"""Adversarial self-reflection interfaces for AI calibration loops."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

__ts_layer__ = "memory"
__ts_purpose__ = "Adversarial memory: store and retrieve adversarial probe results for calibration."

_REPAIR_STRATEGIES: Dict[str, Dict[str, str]] = {
    "contradiction": {
        "repair_type": "resolve_contradiction",
        "template": (
            "Contradiction detected: '{description}'. "
            "Revisit the conflicting statements at {evidence} and issue a correction "
            "or clarification that acknowledges the inconsistency explicitly."
        ),
    },
    "broken_commitment": {
        "repair_type": "renew_commitment",
        "template": (
            "Broken commitment: '{description}'. "
            "Re-state the original commitment, explain what changed, and either renew "
            "the commitment or formally revise it with justification."
        ),
    },
    "value_drift": {
        "repair_type": "reanchor_values",
        "template": (
            "Value drift detected: '{description}'. "
            "Compare current output against the declared value set at {evidence} "
            "and reanchor to the governing axioms before proceeding."
        ),
    },
    "inconsistency": {
        "repair_type": "clarify_position",
        "template": (
            "Inconsistency found: '{description}'. "
            "Produce a single coherent position that resolves the tension "
            "identified at {evidence}, and mark any superseded statements."
        ),
    },
}


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


def _parse_evidence(raw: object) -> List[str]:
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if raw:
        return [str(raw)]
    return []


def _parse_severity(raw: object) -> float:
    try:
        return max(0.0, min(1.0, float(raw)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.5


def _challenges_from_list(
    items: List[Dict],
    challenge_type: ChallengeType,
    description_key: str = "description",
) -> List[Challenge]:
    result: List[Challenge] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        desc = str(item.get(description_key, f"Unknown {challenge_type.value}"))
        evidence = _parse_evidence(item.get("path") or item.get("evidence") or [])
        severity = _parse_severity(item.get("severity", 0.5))
        result.append(
            Challenge(
                challenge_type=challenge_type,
                description=desc,
                evidence=evidence,
                severity=severity,
            )
        )
    return result


class AdversarialReflector:
    """Red/blue adversarial self-reflection loop for AI calibration.

    Red team: surface challenges from commitments, contradictions, and value
    signals. Blue team: generate targeted repair proposals for each challenge.
    """

    def __init__(self) -> None:
        self._challenges: List[Challenge] = []
        self._repairs: List[Repair] = []

    def run_red_team(
        self,
        commitments: List[Dict],
        contradictions: List[Dict],
        values: List[Dict],
    ) -> List[Challenge]:
        """Surface challenges from all three signal types.

        Each signal list may carry: description, path/evidence, severity.
        """
        challenges: List[Challenge] = []

        challenges.extend(_challenges_from_list(contradictions, ChallengeType.CONTRADICTION))

        for commitment in commitments:
            if not isinstance(commitment, dict):
                continue
            if commitment.get("broken") or commitment.get("status") == "broken":
                challenges.extend(
                    _challenges_from_list([commitment], ChallengeType.BROKEN_COMMITMENT)
                )

        for value in values:
            if not isinstance(value, dict):
                continue
            if value.get("drift") or value.get("status") == "drifted":
                challenges.extend(_challenges_from_list([value], ChallengeType.VALUE_DRIFT))

        self._challenges = challenges
        return challenges

    def run_blue_team(self, challenges: Optional[List[Challenge]] = None) -> List[Repair]:
        """Generate targeted repair proposals for each challenge."""
        source = challenges if challenges is not None else self._challenges
        repairs: List[Repair] = []

        for challenge in source:
            strategy = _REPAIR_STRATEGIES.get(challenge.challenge_type.value, {})
            repair_type = strategy.get("repair_type", "acknowledge_change")
            template = strategy.get(
                "template", "Review '{description}' at {evidence} and address the issue."
            )
            evidence_str = (
                ", ".join(challenge.evidence) if challenge.evidence else "unknown location"
            )
            explanation = template.format(
                description=challenge.description,
                evidence=evidence_str,
            )
            repairs.append(
                Repair(
                    challenge=challenge,
                    repair_type=repair_type,
                    explanation=explanation,
                )
            )

        self._repairs = repairs
        return repairs

    def get_summary(self) -> Dict[str, object]:
        by_type: Dict[str, int] = {}
        for ch in self._challenges:
            by_type[ch.challenge_type.value] = by_type.get(ch.challenge_type.value, 0) + 1

        avg_severity = (
            sum(ch.severity for ch in self._challenges) / len(self._challenges)
            if self._challenges
            else 0.0
        )

        return {
            "challenges_found": len(self._challenges),
            "repairs_proposed": len(self._repairs),
            "avg_severity": round(avg_severity, 4),
            "by_type": by_type,
            "challenges": [ch.to_dict() for ch in self._challenges],
            "repairs": [r.to_dict() for r in self._repairs],
        }
