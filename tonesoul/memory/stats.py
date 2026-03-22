from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, Optional


def _extract_verdict(entry: dict) -> Optional[str]:
    if not isinstance(entry, dict):
        return None

    verdict_value = entry.get("verdict")
    if isinstance(verdict_value, dict):
        verdict_value = verdict_value.get("verdict") or verdict_value.get("decision")
    if isinstance(verdict_value, str):
        return verdict_value.strip().lower()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        verdict_block = transcript.get("verdict")
        if isinstance(verdict_block, dict):
            verdict_value = verdict_block.get("verdict") or verdict_block.get("decision")
            if isinstance(verdict_value, str):
                return verdict_value.strip().lower()
    return None


def _extract_divergence(entry: dict) -> Optional[dict]:
    if not isinstance(entry, dict):
        return None
    divergence = entry.get("divergence_analysis")
    if isinstance(divergence, dict):
        return divergence
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        divergence = transcript.get("divergence_analysis")
        if isinstance(divergence, dict):
            return divergence
    return None


def _extract_coherence(entry: dict) -> Optional[float]:
    if not isinstance(entry, dict):
        return None
    coherence_value = entry.get("coherence")
    if isinstance(coherence_value, (int, float)):
        return float(coherence_value)
    if isinstance(coherence_value, dict):
        for key in ("overall", "c_inter", "approval_rate", "min_confidence"):
            value = coherence_value.get(key)
            if isinstance(value, (int, float)):
                return float(value)

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        coherence = transcript.get("coherence")
        if isinstance(coherence, dict):
            for key in ("overall", "c_inter", "approval_rate", "min_confidence"):
                value = coherence.get(key)
                if isinstance(value, (int, float)):
                    return float(value)
    return None


def count_by_verdict(entries: Iterable[dict]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for entry in entries:
        verdict = _extract_verdict(entry)
        if verdict:
            counter[verdict] += 1
    return dict(counter)


def most_common_divergence(entries: Iterable[dict]) -> Optional[str]:
    counter: Counter[str] = Counter()
    for entry in entries:
        divergence = _extract_divergence(entry)
        if not divergence:
            continue
        for key in ("concern", "object"):
            values = divergence.get(key, [])
            if not isinstance(values, list):
                continue
            for item in values:
                if isinstance(item, str) and item.strip():
                    counter[item.strip()] += 1
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def average_coherence(entries: Iterable[dict]) -> float:
    values = []
    for entry in entries:
        coherence = _extract_coherence(entry)
        if coherence is not None:
            values.append(coherence)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)
