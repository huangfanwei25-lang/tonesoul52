from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Tuple

from .types import PerspectiveVote


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z0-9_]+", str(text or "").lower())
    return {token for token in tokens if len(token) >= 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


@dataclass
class AuditResult:
    is_unique: bool
    similarity_scores: Dict[str, float]
    flagged_pairs: List[str]
    recommendation: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "is_unique": bool(self.is_unique),
            "similarity_scores": {k: round(float(v), 4) for k, v in self.similarity_scores.items()},
            "flagged_pairs": list(self.flagged_pairs),
            "recommendation": self.recommendation,
        }


def _coerce_vote(vote: object, index: int) -> Tuple[str, str, float, str]:
    if isinstance(vote, PerspectiveVote):
        perspective = (
            vote.perspective.value if hasattr(vote.perspective, "value") else str(vote.perspective)
        )
        return perspective, vote.decision.value, float(vote.confidence), vote.reasoning

    if isinstance(vote, dict):
        perspective_raw = vote.get("perspective", f"p{index}")
        decision_raw = vote.get("decision", "approve")
        confidence_raw = vote.get("confidence", 0.5)
        reasoning_raw = vote.get("reasoning", "")
        perspective = (
            perspective_raw.value if hasattr(perspective_raw, "value") else str(perspective_raw)
        )
        decision = decision_raw.value if hasattr(decision_raw, "value") else str(decision_raw)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.5
        return perspective, decision, confidence, str(reasoning_raw)

    return f"p{index}", "approve", 0.5, str(vote)


def audit_persona_uniqueness(
    votes: Iterable[object],
    *,
    similarity_threshold: float = 0.85,
) -> AuditResult:
    """
    Audit whether persona outputs are genuinely diverse or likely reskinned.

    Flags a pair when:
    - decision is the same
    - reasoning Jaccard similarity >= threshold
    - confidence gap <= 0.10
    """
    normalized: List[Tuple[str, str, float, str]] = []
    for idx, vote in enumerate(votes):
        normalized.append(_coerce_vote(vote, idx))

    if len(normalized) < 2:
        return AuditResult(
            is_unique=True,
            similarity_scores={},
            flagged_pairs=[],
            recommendation="Not enough votes to audit persona uniqueness.",
        )

    threshold = max(0.0, min(1.0, float(similarity_threshold)))
    similarity_scores: Dict[str, float] = {}
    flagged_pairs: List[str] = []

    for (p1, d1, c1, r1), (p2, d2, c2, r2) in combinations(normalized, 2):
        pair_key = f"{p1}<->{p2}"
        sim = _jaccard(_tokenize(r1), _tokenize(r2))
        similarity_scores[pair_key] = sim
        if d1 == d2 and sim >= threshold and abs(c1 - c2) <= 0.10:
            flagged_pairs.append(pair_key)

    is_unique = len(flagged_pairs) == 0
    recommendation = (
        "persona outputs appear sufficiently differentiated."
        if is_unique
        else "possible persona reskin detected; diversify role prompts or decision criteria."
    )
    result = AuditResult(
        is_unique=is_unique,
        similarity_scores=similarity_scores,
        flagged_pairs=flagged_pairs,
        recommendation=recommendation,
    )
    try:
        from memory.provenance_chain import ProvenanceManager

        ProvenanceManager().add_record(
            event_type="council_event",
            content={"event": "persona_audit", "is_unique": bool(result.is_unique)},
            metadata={"flagged_pairs": len(result.flagged_pairs)},
        )
    except Exception:
        pass
    return result
