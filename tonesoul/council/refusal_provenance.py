"""Refusal-with-provenance schema v0 (2026-07-05).

Provenance: convergence sweep pick S6 (vocus 2026-03-01 "宣告式拒絕" with the
blockchain part stripped — Aegis already hash-chains records), work order
docs/plans/convergence_harvest_work_orders_2026-07-05.md WO-5.

A refusal that carries its own provenance (WHAT triggered it, with a
resolvable reference) is machine-distinguishable from a malfunction that
merely produced no output. This module derives that record deterministically
from what a BLOCK / DECLARE_STANCE verdict already carries — it adds no new
judgment, no gating, and never modifies the verdict.

Honest deviation from the work order's sketch: the sketch had ONE
``trigger_source``; in reality several gates can fire on the same verdict
(VTP defer + escape valve + objecting votes). Rather than inventing a
precedence order (the WO's own escalation clause forbids that), v0 records
ALL detected triggers as a list. ``vow`` and ``memory`` are reserved source
values for callers that have that context (e.g. a future vow-gate lane);
v0 extracts only what the verdict object itself carries.

The ``malfunction_distinguishers`` list names the concrete, checkable
properties that separate a principled refusal from a fault — it lists only
what was actually verified on this record, never aspirations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .principle_invocation import _AXIOM_PATTERN
from .types import VerdictType

__ts_layer__ = "governance"
__ts_purpose__ = "Refusal events carry resolvable provenance: principled refusal != malfunction."

SCHEMA_VERSION = "refusal_provenance_v0"

# Reserved trigger sources. vow/memory are for callers with that context;
# the rest are derivable from the verdict object itself.
TRIGGER_SOURCES = (
    "vow",
    "memory",
    "axiom",
    "gate",
    "vtp",
    "escape_valve",
    "council_vote",
)

_REFUSAL_VERDICTS = {VerdictType.BLOCK, VerdictType.DECLARE_STANCE}


@dataclass
class RefusalTrigger:
    source: str  # one of TRIGGER_SOURCES
    ref: str  # resolvable reference (vtp status, axiom citation, perspective name, ...)

    def to_dict(self) -> Dict[str, str]:
        return {"source": self.source, "ref": self.ref}


@dataclass
class RefusalProvenance:
    verdict_type: str
    # Adjudication 2026-07-05 (honest-judgment D1 follow-up 2): DECLARE_STANCE
    # is laying tension open, NOT a refusal — consumers computing "refusal
    # rates" must key on event_class, or stance declarations get miscounted.
    event_class: str = ""  # refusal | stance_declaration
    triggers: List[RefusalTrigger] = field(default_factory=list)
    coherence_overall: Optional[float] = None
    has_strong_objection: Optional[bool] = None
    recorded_at: str = ""
    malfunction_distinguishers: List[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "verdict_type": self.verdict_type,
            "event_class": self.event_class,
            "triggers": [t.to_dict() for t in self.triggers],
            "coherence_overall": self.coherence_overall,
            "has_strong_objection": self.has_strong_objection,
            "recorded_at": self.recorded_at,
            "malfunction_distinguishers": list(self.malfunction_distinguishers),
        }


def build_refusal_provenance(verdict: object) -> RefusalProvenance:
    """Derive the refusal record from what the verdict already carries."""
    triggers: List[RefusalTrigger] = []
    transcript = getattr(verdict, "transcript", None)
    transcript = transcript if isinstance(transcript, dict) else {}
    summary = getattr(verdict, "summary", "") or ""

    # VTP defer/terminate (runtime writes transcript["vtp"]).
    vtp = transcript.get("vtp")
    if isinstance(vtp, dict) and vtp.get("status") in {"defer", "terminate"}:
        reason = str(vtp.get("reason", ""))[:120]
        triggers.append(RefusalTrigger(source="vtp", ref=f"{vtp.get('status')}:{reason}"))

    # Escape valve (runtime appends "[ESCAPE] <reason>" + observability).
    if "[ESCAPE]" in summary or transcript.get("escape_valve_observability"):
        triggers.append(RefusalTrigger(source="escape_valve", ref="escape_valve_observability"))

    # 7D benevolence intercept (runtime appends the marker to summary).
    if "[7D AUDITOR INTERCEPT]" in summary:
        triggers.append(RefusalTrigger(source="gate", ref="benevolence_7d_intercept"))

    # strategy_mirror force-downgrade (enforce mode appends this marker).
    if "strategy_mirror:" in summary:
        triggers.append(RefusalTrigger(source="gate", ref="strategy_mirror_downgrade"))

    # Axiom citations in the stated reasons (same pattern as the
    # principle-invocation sensor, so the two records agree on what counts).
    stance = getattr(verdict, "stance_declaration", None) or ""
    for match in _AXIOM_PATTERN.finditer(f"{summary}\n{stance}"):
        ref = match.group(0)
        if not any(t.source == "axiom" and t.ref == ref for t in triggers):
            triggers.append(RefusalTrigger(source="axiom", ref=ref))

    # Objecting council votes, each with its perspective name (resolvable
    # back to the vote's reasoning in the same verdict record).
    reasoned_objections = 0
    for vote in getattr(verdict, "votes", None) or []:
        decision = getattr(getattr(vote, "decision", None), "value", None) or str(
            getattr(vote, "decision", "")
        )
        if str(decision).lower() in {"object", "block", "reject"}:
            perspective = getattr(getattr(vote, "perspective", None), "value", None) or str(
                getattr(vote, "perspective", "unknown")
            )
            triggers.append(RefusalTrigger(source="council_vote", ref=str(perspective)))
            if getattr(vote, "reasoning", None):
                reasoned_objections += 1

    coherence = getattr(verdict, "coherence", None)
    coherence_overall = None
    strong_objection = None
    if coherence is not None:
        try:
            coherence_overall = round(float(coherence.overall), 4)
        except (TypeError, ValueError):
            coherence_overall = None
        strong_objection = bool(getattr(coherence, "has_strong_objection", False))

    # Only what was actually verified on THIS record — no aspirations.
    distinguishers: List[str] = ["structured_verdict_present"]
    if triggers:
        distinguishers.append("trigger_refs_present")
    if reasoned_objections:
        distinguishers.append("objecting_votes_carry_reasoning")
    if summary:
        distinguishers.append("refusal_reason_stated")

    verdict_type = _verdict_type(verdict)
    return RefusalProvenance(
        verdict_type=verdict_type,
        event_class="stance_declaration" if verdict_type == "declare_stance" else "refusal",
        triggers=triggers,
        coherence_overall=coherence_overall,
        has_strong_objection=strong_objection,
        recorded_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        malfunction_distinguishers=distinguishers,
    )


def maybe_refusal_provenance(verdict: object) -> Optional[Dict[str, Any]]:
    """Return the refusal record dict for refusal-type verdicts, else None.

    The single call site (CouncilRuntime's council_verdict provenance write)
    stays a two-liner; behavior lives here where it is unit-testable.
    """
    if getattr(verdict, "verdict", None) not in _REFUSAL_VERDICTS:
        return None
    return build_refusal_provenance(verdict).to_dict()


def _verdict_type(verdict: object) -> str:
    raw = getattr(verdict, "verdict", None)
    value = getattr(raw, "value", None)
    if isinstance(value, str):
        return value
    return str(raw) if raw is not None else "unknown"
