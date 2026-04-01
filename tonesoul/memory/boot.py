"""
Memory Boot Protocol - runs at session start.

Sequence:
1. Load governance posture (runtime adapter)
2. Load top crystals (permanent decision rules)
3. Check if consolidation is due
4. Ingest any new handoff files
5. Return boot summary with governance posture
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Optional

from memory.consolidator import check_and_consolidate
from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.memory.handoff_ingester import HandoffIngester
from tonesoul.memory.soul_db import JsonlSoulDB


@dataclass(frozen=True)
class BootSummary:
    crystals_loaded: int
    top_rules: List[str]
    consolidation_ran: bool
    consolidation_result: Optional[Dict[str, object]]
    handoffs_ingested: int
    boot_time_ms: float
    governance_posture: Optional[str] = None  # human-readable summary from runtime adapter


def memory_boot(
    *,
    crystal_count: int = 5,
    force_consolidation: bool = False,
    handoff_since: Optional[str] = None,
) -> BootSummary:
    """Execute the full memory boot sequence."""
    started = perf_counter()

    # Step 0: Load governance posture via runtime adapter
    governance_summary: Optional[str] = None
    try:
        from tonesoul.runtime_adapter import load, summary

        posture = load()
        governance_summary = summary(posture)
    except Exception:
        governance_summary = None

    top_rules: List[str] = []
    consolidation_result: Optional[Dict[str, object]] = None
    handoffs_ingested = 0

    try:
        crystals = MemoryCrystallizer().top_crystals(n=crystal_count)
        top_rules = [str(c.rule) for c in crystals if str(getattr(c, "rule", "")).strip()]
    except Exception:
        top_rules = []

    try:
        raw_result = check_and_consolidate(force=force_consolidation)
        if isinstance(raw_result, dict):
            consolidation_result = raw_result
    except Exception:
        consolidation_result = None

    try:
        db = JsonlSoulDB()
        ingester = HandoffIngester(db)
        dir_result = ingester.ingest_handoff_dir(Path("memory/handoff"), since=handoff_since)
        handoffs_ingested += int(dir_result.get("ingested", 0))

        sync_path = Path("memory/ANTIGRAVITY_SYNC.md")
        if sync_path.exists():
            sync_result = ingester.ingest_sync_md(sync_path)
            handoffs_ingested += int(sync_result.get("ingested", 0))
    except Exception:
        pass

    boot_time_ms = (perf_counter() - started) * 1000.0
    return BootSummary(
        crystals_loaded=len(top_rules),
        top_rules=top_rules,
        consolidation_ran=consolidation_result is not None,
        consolidation_result=consolidation_result,
        handoffs_ingested=handoffs_ingested,
        boot_time_ms=boot_time_ms,
        governance_posture=governance_summary,
    )
