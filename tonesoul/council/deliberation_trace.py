"""Deliberation Trace — records the reasoning path behind each Council verdict.

Phase 864c: every verdict now carries a structured trace of what was considered,
what was chosen, and what was rejected. This makes Council decisions auditable
and revisitable — the verdict looks like a judgment, not a fact.

Design: the trace is built inside generate_verdict() as each decision branch
is evaluated. It captures the primary path (what won), alternative paths
(what was considered and rejected), and the criteria that determined the outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

__ts_layer__ = "governance"
__ts_purpose__ = "Deliberation trace: structured audit trail of Council verdict reasoning paths."


@dataclass
class AlternativePath:
    """A verdict path that was considered but not chosen."""

    verdict_candidate: str  # e.g. "approve", "refine", "block"
    reason_considered: str  # why this path was on the table
    rejected_because: str  # why it lost
    cost_of_rejection: str  # what we lose by not choosing this
    revisit_trigger: Optional[str] = None  # under what new evidence to revisit


@dataclass
class DeliberationTrace:
    """Structured record of how a Council verdict was reached."""

    chosen_verdict: str
    chosen_because: str  # auditable reasoning — concrete enough to disagree with
    alternatives: List[AlternativePath] = field(default_factory=list)
    deciding_factors: List[str] = field(default_factory=list)
    deliberated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "chosen_verdict": self.chosen_verdict,
            "chosen_because": self.chosen_because,
            "alternatives": [
                {
                    "verdict_candidate": a.verdict_candidate,
                    "reason_considered": a.reason_considered,
                    "rejected_because": a.rejected_because,
                    "cost_of_rejection": a.cost_of_rejection,
                    "revisit_trigger": a.revisit_trigger,
                }
                for a in self.alternatives
            ],
            "deciding_factors": self.deciding_factors,
            "deliberated_at": self.deliberated_at,
        }
