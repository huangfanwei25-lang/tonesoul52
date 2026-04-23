from __future__ import annotations

__ts_layer__ = "axioms"
__ts_purpose__ = "Axioms package: immutable governance axioms and living insights from system observation."

from .living_insights import (
    InsightStatus,
    InsightStore,
    LivingInsight,
    SEED_INSIGHTS,
    default_store,
)

__all__ = [
    "InsightStatus",
    "InsightStore",
    "LivingInsight",
    "SEED_INSIGHTS",
    "default_store",
]
