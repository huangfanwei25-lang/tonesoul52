from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .soul_db import JsonlSoulDB, MemorySource, SoulDB
from .stats import average_coherence, count_by_verdict, most_common_divergence


@dataclass
class ConsolidationResult:
    patterns: Dict[str, object]
    meta_reflection: str


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
