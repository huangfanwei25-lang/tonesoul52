"""Crystallization Pipeline — session end → journal → consolidation → crystals → RAG.

Orchestrates the full learning accumulation cycle. Each stage is best-effort;
failures are logged but never block the governance commit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .session_digest import digest_session

# ---------------------------------------------------------------------------
# Pipeline result
# ---------------------------------------------------------------------------


@dataclass
class PipelineResult:
    """Outcome of a single pipeline run."""

    digest_written: bool = False
    consolidation_ran: bool = False
    crystals_generated: int = 0
    rag_ingested: int = 0
    wisdom_delta: float = 0.0
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONSOLIDATION_INTERVAL = 5  # run consolidation every N sessions
WISDOM_BETA = 0.05  # SI blend rate for wisdom signal
_CRYSTAL_DENSITY_CAP = 50  # crystal count for full signal

# Routing lanes — classify digests by governance relevance
_GOVERNANCE_KEYWORDS = {"vow", "axiom", "aegis", "drift", "council", "governance", "誓言", "治理"}
_CONTINUITY_KEYWORDS = {"handoff", "checkpoint", "compaction", "session", "交接", "延續"}
# Everything else → "learning" lane


def classify_lane(topics: List[str], learnings: List[str]) -> str:
    """Classify a digest into a routing lane: governance / continuity / learning."""
    text = " ".join(topics + learnings).lower()
    if any(kw in text for kw in _GOVERNANCE_KEYWORDS):
        return "governance"
    if any(kw in text for kw in _CONTINUITY_KEYWORDS):
        return "continuity"
    return "learning"


# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------


def _write_digest(
    trace: Dict[str, Any],
    compaction: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Stage 1: Extract and persist a session digest to self_journal."""
    from .soul_db import JsonlSoulDB, MemorySource

    entry = digest_session(trace, compaction)
    entry["lane"] = classify_lane(entry.get("topics", []), entry.get("learnings", []))
    db = JsonlSoulDB()
    db.append(MemorySource.SELF_JOURNAL, entry)
    return entry


def _maybe_consolidate(session_count: int, force: bool = False):
    """Stage 2: Trigger consolidation if session_count hits the interval."""
    if not force and session_count % CONSOLIDATION_INTERVAL != 0:
        return None

    from .consolidator import consolidate

    return consolidate()


def _adapt_patterns(consolidation_result) -> Dict[str, Any]:
    """Stage 3a: Translate consolidator output → crystallizer input vocabulary."""
    patterns = consolidation_result.patterns
    verdict_counts = patterns.get("verdict_counts", {})

    # Count low-tension approvals (approve with avg_weighted_tension < 0.3)
    low_tension_approvals = 0
    avg_wt = float(patterns.get("average_weighted_tension", 0.0))
    approve_count = int(verdict_counts.get("approve", 0))
    if avg_wt < 0.3:
        low_tension_approvals = approve_count

    return {
        "verdicts": verdict_counts,
        "low_tension_approvals": low_tension_approvals,
        "autonomous_high_delta": patterns.get("genesis_counts", {}).get("autonomous", 0),
        "collapse_warnings": {},
        "resonance_convergences": 0,
    }


def _crystallize(patterns: Dict[str, Any]):
    """Stage 3b: Run crystallizer on adapted patterns."""
    from .crystallizer import MemoryCrystallizer

    crystallizer = MemoryCrystallizer()
    return crystallizer.crystallize(patterns)


def _compute_wisdom_delta(
    tension_events: List[Dict[str, Any]],
) -> float:
    """Stage 4: Compute the wisdom accumulation signal for SI.

    Components:
    - crystal_signal: density of active crystals (learning is alive)
    - quality_bonus: session coherence (productive session)
    - rediscovery_penalty: known issues re-discovered (negative signal)
    """
    from .crystallizer import MemoryCrystallizer

    crystallizer = MemoryCrystallizer()
    summary = crystallizer.freshness_summary()
    crystals = crystallizer.load_crystals()

    crystal_count = int(summary.get("total_crystals", 0))
    active_count = int(summary.get("active_count", 0))
    active_ratio = active_count / max(1, crystal_count) if crystal_count else 0.0

    # Crystal density signal (capped)
    crystal_signal = min(1.0, crystal_count / _CRYSTAL_DENSITY_CAP) * active_ratio

    # Session coherence from tension events
    severities = [float(t.get("severity", 0.0)) for t in tension_events]
    avg_sev = sum(severities) / max(1, len(severities)) if severities else 0.0
    quality_bonus = (1.0 - avg_sev) * 0.5

    # Rediscovery penalty: tension topics matching existing crystal rules
    rediscoveries = _count_rediscoveries(tension_events, crystals)
    rediscovery_penalty = min(0.5, rediscoveries * 0.1)

    return round(
        max(0.0, min(1.0, crystal_signal + quality_bonus - rediscovery_penalty)),
        4,
    )


def _count_rediscoveries(
    tension_events: List[Dict[str, Any]],
    crystals,
) -> int:
    """Count how many tension topics overlap with known crystal rules."""
    if not tension_events or not crystals:
        return 0

    # Collect meaningful keywords from crystal rules
    crystal_keywords = set()
    for c in crystals:
        rule_text = getattr(c, "rule", "") or ""
        for word in rule_text.lower().split():
            if len(word) > 4:  # skip short words
                crystal_keywords.add(word)

    if not crystal_keywords:
        return 0

    count = 0
    for t in tension_events:
        topic = str(t.get("topic", "")).lower()
        if any(kw in topic for kw in crystal_keywords):
            count += 1
    return count


def _ingest_to_rag(
    digest: Optional[Dict[str, Any]] = None,
    crystals: Optional[list] = None,
    db_path: str = "./memory_base",
) -> int:
    """Stage 5: Ingest digest + crystals into FAISS vector store."""
    from .openclaw.embeddings import HashEmbedding
    from .openclaw.hippocampus import Hippocampus

    hippo = Hippocampus(db_path=db_path, embedder=HashEmbedding())
    ingested = 0

    if digest:
        text = _digest_to_text(digest)
        hippo.memorize(
            content=text,
            source_file="session_digest",
            origin="pipeline_crystallization",
            tension=digest.get("tension_summary", {}).get("max_severity", 0.0),
            tags=["digest", "session_learning"] + digest.get("topics", []),
            memory_kind="decision",
        )
        ingested += 1

    if crystals:
        for c in crystals:
            rule = getattr(c, "rule", "") or ""
            source = getattr(c, "source_pattern", "") or ""
            tags = getattr(c, "tags", []) or []
            weight = getattr(c, "weight", 0.5)
            hippo.memorize(
                content=f"Crystal rule: {rule}. Source: {source}",
                source_file="crystal",
                origin="pipeline_crystallization",
                tension=weight,
                tags=list(tags) + ["crystal"],
                memory_kind="decision",
            )
            ingested += 1

    return ingested


def _digest_to_text(digest: Dict[str, Any]) -> str:
    """Convert a session digest into a text string for RAG embedding."""
    parts = [f"Session: {digest.get('session_id', 'unknown')}"]
    parts.append(f"Topics: {', '.join(digest.get('topics', []))}")
    for learning in digest.get("learnings", []):
        parts.append(f"Learning: {learning}")
    ts = digest.get("tension_summary", {})
    if ts.get("unresolved_topics"):
        parts.append(f"Unresolved: {', '.join(ts['unresolved_topics'])}")
    shift = digest.get("stance_shift")
    if shift:
        parts.append(f"Stance: from '{shift.get('from')}' to '{shift.get('to')}'")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def run_session_end_pipeline(
    trace: Dict[str, Any],
    session_count: int,
    *,
    compaction: Optional[Dict[str, Any]] = None,
    force_consolidate: bool = False,
) -> PipelineResult:
    """Run the full crystallization pipeline. Called from commit().

    Each stage is best-effort. Failures are captured in result.errors
    but never propagate.
    """
    result = PipelineResult()

    # Stage 1: Digest
    digest_entry = None
    try:
        digest_entry = _write_digest(trace, compaction)
        result.digest_written = True
    except Exception as exc:
        result.errors.append(f"digest: {exc}")

    # Stage 2+3: Consolidation → Crystallization
    new_crystals = None
    try:
        consolidation = _maybe_consolidate(session_count, force=force_consolidate)
        if consolidation is not None:
            result.consolidation_ran = True
            adapted = _adapt_patterns(consolidation)
            new_crystals = _crystallize(adapted)
            result.crystals_generated = len(new_crystals) if new_crystals else 0
    except Exception as exc:
        result.errors.append(f"consolidation/crystallization: {exc}")

    # Stage 3c: Export crystal index snapshot whenever crystals may have changed
    if result.consolidation_ran:
        try:
            export_crystal_index()
        except Exception as exc:
            result.errors.append(f"crystal_index_export: {exc}")

    # Stage 4: Wisdom delta (always compute, even without consolidation)
    try:
        result.wisdom_delta = _compute_wisdom_delta(trace.get("tension_events") or [])
    except Exception as exc:
        result.errors.append(f"wisdom_delta: {exc}")

    # Stage 5: RAG ingestion
    try:
        ingested = _ingest_to_rag(digest=digest_entry, crystals=new_crystals)
        result.rag_ingested = ingested
    except Exception as exc:
        result.errors.append(f"rag_ingest: {exc}")

    return result


# ---------------------------------------------------------------------------
# Crystal index export — machine-readable snapshot of crystallized wisdom
# ---------------------------------------------------------------------------

_INDEX_PATH = Path("memory/crystal_index.json")


def export_crystal_index(output_path: Optional[Path] = None) -> Dict[str, Any]:
    """Export a structured snapshot of all crystals to crystal_index.json.

    Each record uses ToneSoul's native field vocabulary:
      rule           — the crystallized decision rule (what to do / avoid)
      origin         — source pattern that triggered crystallization
      lifecycle      — ETCL stage + phase + freshness score
      signal         — weight (importance) + access_count (usage history)
      classification — routing lane tags (governance / continuity / learning)
    """
    from .crystallizer import MemoryCrystallizer

    crystallizer = MemoryCrystallizer()
    crystals = crystallizer.load_crystals()
    summary = crystallizer.freshness_summary()

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    records = []
    for c in crystals:
        records.append(
            {
                "rule": c.rule,
                "origin": c.source_pattern,
                "lifecycle": {
                    "stage": c.stage,
                    "phase": c.phase,
                    "freshness": round(c.freshness_score, 3),
                    "freshness_status": c.freshness_status,
                },
                "signal": {
                    "weight": round(c.weight, 3),
                    "access_count": c.access_count,
                },
                "classification": c.tags,
            }
        )

    index = {
        "schema": "tonesoul-crystal-index/v1",
        "generated_at": now,
        "total": len(records),
        "summary": summary,
        "records": records,
    }

    out = Path(output_path or _INDEX_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index
