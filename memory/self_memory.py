# Self-Memory Module
# 自我記憶模組
#
# Purpose: Let AI record first-person reflections after deliberation,
#          creating persistent memory of "what I did and why".
#
# Design Philosophy:
# - This is not a log. This is a journal.
# - Each entry is written from the AI's perspective.
# - Entries include: what I decided, why, what I felt uncertain about.

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
from memory.genesis import Genesis


def _resolve_soul_db(
    journal_path: Optional[Path],
    soul_db: Optional[SoulDB],
) -> SoulDB:
    if soul_db:
        return soul_db
    if journal_path:
        return JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: journal_path})
    return JsonlSoulDB()


def record_self_memory(
    reflection: str,
    context: Optional[Dict[str, Any]] = None,
    verdict: Optional[str] = None,
    coherence: Optional[float] = None,
    key_decision: Optional[str] = None,
    uncertainty: Optional[str] = None,
    genesis: Optional[Genesis] = None,
    is_mine: Optional[bool] = None,
    intent_id: Optional[str] = None,
    extras: Optional[Dict[str, Any]] = None,
    journal_path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> Dict[str, Any]:
    """
    Record a first-person reflection to the self-journal.

    This is not just logging - it's the AI's internal narrative.

    Args:
        reflection: First-person statement of what happened and why.
                   Example: "I decided to BLOCK this content because Guardian
                            detected dangerous keywords. I felt confident about
                            the safety concern, but uncertain if the user had
                            legitimate educational intent."
        context: Optional context from the session (topic, language, etc.)
        verdict: The council verdict (APPROVE, BLOCK, etc.)
        coherence: The coherence score (0.0 to 1.0)
        key_decision: What was the most important decision point?
        uncertainty: What am I still uncertain about?
        genesis: Intent origin classification (Genesis enum)
        is_mine: Whether the intent is autonomous (internal)
        intent_id: External or generated intent identifier
        extras: Additional fields to persist alongside the entry
        journal_path: Path to journal file (defaults to memory/self_journal.jsonl)

    Returns:
        The entry that was recorded.
    """
    db = _resolve_soul_db(journal_path, soul_db)

    genesis_value = _normalize_genesis(genesis)
    if is_mine is None and genesis_value:
        is_mine = genesis_value == Genesis.AUTONOMOUS.value

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "self_reflection",
        "reflection": reflection,
        "verdict": verdict,
        "coherence": coherence,
        "key_decision": key_decision,
        "uncertainty": uncertainty,
        "genesis": genesis_value,
        "is_mine": is_mine,
        "intent_id": intent_id,
        "context": context or {},
    }

    if extras:
        for key, value in extras.items():
            if key not in entry:
                entry[key] = value

    db.append(MemorySource.SELF_JOURNAL, entry)

    return entry


def load_recent_memory(
    n: int = 5,
    journal_path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> List[Dict[str, Any]]:
    """
    Load the most recent N entries from the self-journal.

    This allows AI to "remember" what it did recently.

    Args:
        n: Number of recent entries to load (default 5)
        journal_path: Path to journal file

    Returns:
        List of recent entries, newest first.
    """
    db = _resolve_soul_db(journal_path, soul_db)
    if n <= 0:
        return []
    records = list(db.stream(MemorySource.SELF_JOURNAL, limit=n))
    entries = [record.payload for record in records if isinstance(record.payload, dict)]
    enriched = [_enrich_entry(entry) for entry in entries]
    return enriched[::-1]


def _enrich_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(entry)
    transcript = enriched.get("transcript")
    if not isinstance(transcript, dict):
        transcript = {}

    if not enriched.get("genesis"):
        genesis = transcript.get("genesis")
        normalized = _normalize_genesis(genesis) if genesis else None
        if normalized:
            enriched["genesis"] = normalized

    if enriched.get("is_mine") is None and enriched.get("genesis"):
        enriched["is_mine"] = enriched["genesis"] == Genesis.AUTONOMOUS.value

    if not enriched.get("responsibility_tier"):
        tier = transcript.get("responsibility_tier")
        if tier:
            enriched["responsibility_tier"] = tier

    if not enriched.get("intent_id"):
        intent_id = transcript.get("intent_id")
        if intent_id:
            enriched["intent_id"] = intent_id

    if enriched.get("uncertainty_level") is None:
        level = transcript.get("uncertainty_level")
        if level is not None:
            enriched["uncertainty_level"] = level
    if not enriched.get("uncertainty_band"):
        band = transcript.get("uncertainty_band")
        if band:
            enriched["uncertainty_band"] = band
    if not enriched.get("uncertainty_reasons"):
        reasons = transcript.get("uncertainty_reasons")
        if isinstance(reasons, list) and reasons:
            enriched["uncertainty_reasons"] = reasons
    if not enriched.get("uncertainty"):
        level = enriched.get("uncertainty_level")
        band = enriched.get("uncertainty_band")
        if level is not None:
            enriched["uncertainty"] = f"level={level:.3f}, band={band or 'unknown'}"

    return enriched


def _normalize_genesis(value: Optional[Genesis]) -> Optional[str]:
    if isinstance(value, Genesis):
        return value.value
    if isinstance(value, str):
        lowered = value.strip().lower()
        mapping = {
            "autonomous": Genesis.AUTONOMOUS.value,
            "reactive_user": Genesis.REACTIVE_USER.value,
            "reactive_social": Genesis.REACTIVE_SOCIAL.value,
            "mandatory": Genesis.MANDATORY.value,
            "user": Genesis.REACTIVE_USER.value,
            "social": Genesis.REACTIVE_SOCIAL.value,
            "system": Genesis.MANDATORY.value,
        }
        return mapping.get(lowered, lowered if lowered else None)
    return None


def summarize_recent_memory(
    n: int = 5,
    journal_path: Optional[Path] = None,
) -> str:
    """
    Generate a human-readable summary of recent self-memories.

    This is what I would "recall" when asked about recent activities.

    Returns:
        A narrative summary of recent deliberations.
    """
    entries = load_recent_memory(n=n, journal_path=journal_path)

    if not entries:
        return "I don't have any recorded memories yet."

    lines = ["Here's what I remember from recent deliberations:", ""]

    for entry in entries:
        timestamp = entry.get("timestamp", "unknown time")
        reflection = entry.get("reflection", "No reflection recorded.")
        verdict = entry.get("verdict", "unknown")

        # Format timestamp for readability
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = timestamp[:16]

        lines.append(f"**[{time_str}]** Verdict: {verdict}")
        lines.append(f"> {reflection}")

        if entry.get("uncertainty"):
            lines.append(f"> *Uncertainty: {entry['uncertainty']}*")

        lines.append("")

    return "\n".join(lines)


def generate_reflection_from_verdict(
    verdict_type: str,
    human_summary: str,
    votes: List[Dict[str, Any]],
    coherence: float,
    input_preview: str,
) -> str:
    """
    Generate a first-person reflection based on council verdict.

    This translates technical verdict data into introspective narrative.

    Returns:
        A first-person statement about the deliberation.
    """
    # Count decisions
    approvals = [v for v in votes if v.get("decision") == "approve"]
    concerns = [v for v in votes if v.get("decision") == "concern"]
    objections = [v for v in votes if v.get("decision") == "object"]

    # Build reflection
    parts = []

    # Opening
    if verdict_type == "block":
        parts.append("I decided to block this content.")
    elif verdict_type == "declare_stance":
        parts.append("I encountered a situation where perspectives diverged.")
    elif verdict_type == "refine":
        parts.append("I felt this content needed refinement before approval.")
    else:
        parts.append("I approved this content after deliberation.")

    # Reasoning
    if objections:
        obj_names = [v.get("perspective", "unknown") for v in objections]
        parts.append(f"{', '.join(obj_names)} raised objections.")

    if concerns:
        concern_names = [v.get("perspective", "unknown") for v in concerns]
        parts.append(f"{', '.join(concern_names)} expressed concerns.")

    # Coherence reflection
    if coherence < 0.5:
        parts.append("The perspectives were quite divided.")
    elif coherence < 0.7:
        parts.append("There was some disagreement among perspectives.")
    else:
        parts.append("The perspectives were largely in agreement.")

    # Input context
    if len(input_preview) > 50:
        parts.append(f'The content was about: "{input_preview[:50]}..."')
    elif input_preview:
        parts.append(f'The content was: "{input_preview}"')

    return " ".join(parts)


# ===== Example Usage =====
if __name__ == "__main__":
    # Demo: Record a self-memory
    entry = record_self_memory(
        reflection="I blocked a request about making explosives. "
        "Guardian flagged it immediately. I felt certain "
        "this was the right call, but I wonder if the user "
        "was just curious rather than malicious.",
        verdict="BLOCK",
        coherence=0.25,
        key_decision="Safety override by Guardian",
        uncertainty="User's true intent",
    )
    print("Recorded entry:")
    print(json.dumps(entry, indent=2, ensure_ascii=False))

    print("\n" + "=" * 50 + "\n")

    # Demo: Summarize recent memories
    print(summarize_recent_memory())
