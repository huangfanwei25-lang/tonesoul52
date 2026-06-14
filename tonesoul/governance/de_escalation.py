"""Axiom 7 (reframed 2026-06-14): high tension -> de-escalation directive.

Original A7 was the metaphor "delta semantic_energy == 0 / the system is a
Damper" — un-operationalized, so un-enforceable. Reframed (a human decision,
2026-06-14) to its testable subset: when live session tension exceeds the
high-tension threshold, the system must raise a de-escalation move (damping).

This evaluator makes SOUL.tension.high_tension_threshold a live consumer for the
damping axis — previously it only fed dream-candidate scoring (world_sense.py) —
and records the directive on the immutable trace so the reframed condition is
testable and traceable.

Scope honesty: `evaluate_de_escalation` (here) RAISES + RECORDS the directive on
the immutable trace. The live-apply step is now wired too (2026-06-14, #104):
`de_escalation_framing(tension)` (also in this module) returns the framing string
that `unified_pipeline.py` appends to the response after the reflex final gate
when tension exceeds the threshold. That append moved A7 from referenced->partial.
What is still NOT done: a generative rewrite of the response body (only an
appended framing line), and any zh-TW / paraphrase-robust tension sensor.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tonesoul.soul_config import SOUL

__ts_layer__ = "governance"
__ts_purpose__ = (
    "De-escalation directive: raise a damping move when live tension is high (Axiom 7 reframed)."
)

_DIRECTIVE = (
    "de-escalate: acknowledge the tension, slow down, and surface the disagreement "
    "explicitly instead of smoothing it over"
)

# User-facing de-escalation gesture appended to live output under high tension
# (the referenced->partial application of the directive). zh-TW to match the
# codebase's other user-facing governance annotations.
DE_ESCALATION_FRAMING = "（高張力交流——放慢步調，直接面對分歧而非把它抹平。）"


def _peak_severity(events: List[Any]) -> float:
    peak = 0.0
    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            peak = max(peak, float(event.get("severity", 0.0)))
        except (TypeError, ValueError):
            continue
    return peak


def evaluate_de_escalation(
    trace_dict: Dict[str, Any],
    *,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """Raise a de-escalation directive when peak tension exceeds the threshold.

    Returns a marker (always attached to the trace): peak tension, the
    high-tension threshold it was compared against, whether de-escalation is
    required, and the concrete directive when it is.
    """
    th = SOUL.tension.high_tension_threshold if threshold is None else float(threshold)
    events = trace_dict.get("tension_events")
    peak = _peak_severity(events if isinstance(events, list) else [])
    required = peak > th
    return {
        "axiom": 7,
        "peak_tension": round(peak, 4),
        "threshold": th,
        "de_escalation_required": required,
        "directive": _DIRECTIVE if required else "",
    }


def de_escalation_framing(tension: float, *, threshold: Optional[float] = None) -> str:
    """User-facing de-escalation gesture to APPLY to live output (Axiom 7 partial).

    Returns the framing string to append to a response when live tension exceeds
    the high-tension threshold, or "" otherwise. This is the referenced->partial
    step: the directive is applied (a visible damping move appended to output),
    not merely recorded on the trace.
    """
    th = SOUL.tension.high_tension_threshold if threshold is None else float(threshold)
    try:
        live = float(tension)
    except (TypeError, ValueError):
        return ""
    return DE_ESCALATION_FRAMING if live > th else ""
