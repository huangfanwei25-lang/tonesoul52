"""Memory decay engine for dynamic forgetting in ToneSoul."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .soul_db import MemoryRecord

HALF_LIFE_DAYS = 7.0
DECAY_CONSTANT = math.log(2) / HALF_LIFE_DAYS
FORGET_THRESHOLD = 0.1
ACCESS_BOOST = 0.15


def calculate_decay(initial_relevance: float, days_elapsed: float, access_count: int = 0) -> float:
    """Apply exponential decay with optional access-based reinforcement."""
    base = float(initial_relevance)
    elapsed = max(0.0, float(days_elapsed))
    accesses = max(0, int(access_count))
    decayed = base * math.exp(-DECAY_CONSTANT * elapsed)
    boosted = decayed + accesses * ACCESS_BOOST
    return max(0.0, min(1.0, boosted))


def should_forget(relevance_score: float) -> bool:
    """Return True when relevance falls below forgetting threshold."""
    return float(relevance_score) < FORGET_THRESHOLD


def retrospective_score(
    record_payload: Dict[str, object],
    current_topics: List[str],
    active_commitments: List[str],
) -> float:
    """Compute heuristic adjustment for context-aware retrospective reflection."""
    adjustment = 0.0
    text = str(record_payload.get("text", "") or record_payload.get("content", "")).lower()

    for topic in current_topics:
        if not topic:
            continue
        if topic.lower() in text:
            adjustment += 0.3
            break

    for commitment in active_commitments:
        if not commitment:
            continue
        if commitment.lower() in text:
            adjustment += 0.2
            break

    try:
        access_count = int(record_payload.get("access_count", 0) or 0)
    except (TypeError, ValueError):
        access_count = 0
    if access_count == 0:
        adjustment -= 0.1

    return max(-0.5, min(0.5, adjustment))


def apply_retrospective(
    records: List[MemoryRecord],
    current_topics: Optional[List[str]] = None,
    active_commitments: Optional[List[str]] = None,
) -> List[MemoryRecord]:
    """Return a new list with relevance_score adjusted by retrospective rules."""
    topics = current_topics or []
    commitments = active_commitments or []
    updated_records: List[MemoryRecord] = []

    for record in records:
        adjustment = retrospective_score(
            record.payload,
            current_topics=topics,
            active_commitments=commitments,
        )
        new_score = max(0.0, min(1.0, float(record.relevance_score) + adjustment))
        updated_records.append(replace(record, relevance_score=new_score))
    return updated_records
