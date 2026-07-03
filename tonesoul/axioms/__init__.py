# DORMANT (as of 2026-07-03): unwired — no live importer in tonesoul/scripts/apps/api; only this package's own tests. The live axiom carrier is the repo-root AXIOMS.json, not this package. See docs/SUCCESSOR_MAP.md §6a / docs/status/repo_atlas_2026-07-03.md §2.7.
from __future__ import annotations

__ts_layer__ = "axioms"
__ts_purpose__ = (
    "Axioms package: immutable governance axioms and living insights from system observation."
)

from .living_insights import (
    SEED_INSIGHTS,
    InsightStatus,
    InsightStore,
    LivingInsight,
    default_store,
)

__all__ = [
    "InsightStatus",
    "InsightStore",
    "LivingInsight",
    "SEED_INSIGHTS",
    "default_store",
]
