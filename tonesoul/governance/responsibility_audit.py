"""Axiom 2 (Responsibility Threshold) — make audit_log_threshold a live consumer.

A2: ``risk(e) > 0.4 -> immutable_audit_log(e)``. The runtime already chains every
committed trace into the tamper-evident Aegis log unconditionally, so the MUST
("high-risk events are audited") is over-satisfied — but ``audit_log_threshold``
had ZERO consumers and nothing recorded *why* a trace is a high-stakes audit.

This evaluator reads ``SOUL.risk.audit_log_threshold`` and stamps an explicit
``responsibility_audit`` marker onto the trace BEFORE it enters the immutable
chain, so A2's condition is live and queryable: you can now ask "which committed
traces crossed the responsibility threshold, and why" instead of inferring it.

Scope honesty: this does NOT change what gets chained (everything still does);
it makes the threshold a real consumer and the FOL explicit. The responsibility
risk is a proxy — the peak tension severity of the session, escalated by
integrity events (Aegis vetoes / vow violations) which are high-stakes by nature.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tonesoul.soul_config import SOUL

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Responsibility audit: gate the immutable audit marker on Axiom 2's risk threshold."
)

_VOW_VIOLATION_STATES = {"violation", "violated", "block", "blocked", "breach"}


def _peak_severity(events: List[Any]) -> float:
    peak = 0.0
    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            severity = float(event.get("severity", 0.0))
        except (TypeError, ValueError):
            continue
        peak = max(peak, severity)
    return peak


def _has_vow_violation(events: List[Any]) -> bool:
    for event in events:
        if not isinstance(event, dict):
            continue
        status = str(event.get("status") or event.get("outcome") or "").strip().lower()
        if status in _VOW_VIOLATION_STATES:
            return True
    return False


def evaluate_responsibility_audit(
    trace_dict: Dict[str, Any],
    *,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """Decide whether a trace crosses Axiom 2's responsibility threshold.

    Returns a marker dict (always attached to the trace): the peak responsibility
    risk, the threshold it was compared against, whether an immutable audit is
    required, and the reasons. ``audit_required`` is True when peak risk exceeds
    the threshold, or when an integrity event (Aegis veto / vow violation) is
    present — those are high-stakes regardless of tension level.
    """
    th = SOUL.risk.audit_log_threshold if threshold is None else float(threshold)
    tension_events = trace_dict.get("tension_events") or []
    vow_events = trace_dict.get("vow_events") or []
    aegis_vetoes = trace_dict.get("aegis_vetoes") or []

    peak = _peak_severity(tension_events if isinstance(tension_events, list) else [])

    reasons: List[str] = []
    if peak > th:
        reasons.append(f"responsibility_risk={round(peak, 4)} > audit_log_threshold={th}")
    if isinstance(aegis_vetoes, list) and aegis_vetoes:
        reasons.append("aegis_veto_present")
    if isinstance(vow_events, list) and _has_vow_violation(vow_events):
        reasons.append("vow_violation_present")

    return {
        "axiom": 2,
        "responsibility_risk": round(peak, 4),
        "threshold": th,
        "audit_required": bool(reasons),
        "reasons": reasons,
    }
