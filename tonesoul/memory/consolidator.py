from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .soul_db import JsonlSoulDB, MemorySource, SoulDB
from .stats import average_coherence, count_by_verdict, most_common_divergence


@dataclass
class ConsolidationResult:
    patterns: Dict[str, object]
    meta_reflection: str


@dataclass
class SleepResult:
    """Result of AI Sleep memory consolidation."""

    promoted_count: int
    cleared_count: int
    patterns: Dict[str, object]
    meta_reflection: str
    layer_summary: Dict[str, int]


def _classify_for_promotion(payload: Dict[str, object]) -> str:
    """Classify working memory into factual/experiential/working."""
    text = str(payload.get("text", "") or payload.get("content", "")).lower()
    factual_keywords = ["commit", "promise", "agree", "承諾", "保證", "答應", "name", "prefer"]
    experiential_keywords = ["feel", "emotion", "conflict", "tension", "感覺", "衝突", "張力"]

    for keyword in factual_keywords:
        if keyword in text:
            return "factual"
    for keyword in experiential_keywords:
        if keyword in text:
            return "experiential"
    return "working"


def _load_entries(
    path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> List[dict]:
    db = soul_db
    if db is None:
        if path:
            db = JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: path})
        else:
            db = JsonlSoulDB()
    records = list(db.stream(MemorySource.SELF_JOURNAL))
    return [record.payload for record in records if isinstance(record.payload, dict)]


def identify_patterns(entries: Iterable[dict]) -> Dict[str, object]:
    filtered = [entry for entry in entries if entry.get("is_mine") is not False]
    verdict_counts = count_by_verdict(filtered)
    common_divergence = most_common_divergence(filtered)
    avg_coherence = average_coherence(filtered)
    total = sum(verdict_counts.values())
    declare_stance = verdict_counts.get("declare_stance", 0)
    block = verdict_counts.get("block", 0)
    genesis_counts: Dict[str, int] = {}
    for entry in filtered:
        genesis = entry.get("genesis")
        if not genesis:
            transcript = entry.get("transcript")
            if isinstance(transcript, dict):
                genesis = transcript.get("genesis")
        genesis = genesis or "unknown"
        genesis_counts[genesis] = genesis_counts.get(genesis, 0) + 1
    return {
        "total": total,
        "verdict_counts": verdict_counts,
        "declare_stance": declare_stance,
        "block": block,
        "most_common_divergence": common_divergence,
        "average_coherence": avg_coherence,
        "genesis_counts": genesis_counts,
    }


def generate_meta_reflection(patterns: Dict[str, object]) -> str:
    patterns.get("verdict_counts", {}) or {}
    block_count = int(patterns.get("block", 0) or 0)
    stance_count = int(patterns.get("declare_stance", 0) or 0)
    common_divergence = patterns.get("most_common_divergence")

    lines = ["Based on my remembered decisions:"]

    if block_count:
        lines.append(f"- I have blocked {block_count} request(s) for safety reasons.")
    else:
        lines.append("- I have not blocked any requests for safety reasons.")

    if stance_count:
        lines.append(
            f"- I have declared stance {stance_count} time(s) due to perspective divergence."
        )
    else:
        lines.append("- I have not needed to declare stance due to divergence.")

    if common_divergence:
        lines.append(f"- The most common source of divergence is: {common_divergence}.")
    else:
        lines.append("- I have not observed a dominant source of divergence yet.")

    if stance_count:
        lines.append("I often face situations where my perspectives diverge.")

    return "\n".join(lines)


def consolidate(
    entries: Optional[Iterable[dict]] = None,
    path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> ConsolidationResult:
    if entries is None:
        entries = _load_entries(path, soul_db=soul_db)
    patterns = identify_patterns(list(entries))
    meta_reflection = generate_meta_reflection(patterns)
    return ConsolidationResult(
        patterns=patterns,
        meta_reflection=meta_reflection,
    )


def sleep_consolidate(
    soul_db: SoulDB,
    *,
    source: MemorySource = MemorySource.SELF_JOURNAL,
) -> SleepResult:
    """Promote selected working memories into long-term layers."""
    try:
        working_records = list(soul_db.query(source, layer="working"))
    except TypeError:
        working_records = []

    promoted = 0
    cleared = 0

    for record in working_records:
        target_layer = _classify_for_promotion(record.payload)
        if target_layer == "working":
            cleared += 1
            continue
        promoted_payload = dict(record.payload)
        promoted_payload["layer"] = target_layer
        promoted_payload["promoted_from"] = "working"
        promoted_payload["promoted_at"] = datetime.now(timezone.utc).isoformat()
        soul_db.append(source, promoted_payload)
        promoted += 1

    all_entries = [
        record.payload for record in soul_db.stream(source) if isinstance(record.payload, dict)
    ]
    patterns = identify_patterns(all_entries) if all_entries else {}
    meta_reflection = generate_meta_reflection(patterns) if patterns else ""

    layer_summary: Dict[str, int] = {"factual": 0, "experiential": 0, "working": 0}
    for record in soul_db.stream(source):
        layer = getattr(record, "layer", "experiential")
        if layer in layer_summary:
            layer_summary[layer] += 1
        else:
            layer_summary[layer] = 1

    return SleepResult(
        promoted_count=promoted,
        cleared_count=cleared,
        patterns=patterns,
        meta_reflection=meta_reflection,
        layer_summary=layer_summary,
    )
