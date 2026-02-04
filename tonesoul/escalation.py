import json
import os
from typing import Dict, List, Optional

from .error_event import ErrorEvent, ErrorLedger
from .issue_codes import IssueCode, issue


def decision_mode_from_context(context: Dict[str, object]) -> str:
    time_island = context.get("time_island") if isinstance(context, dict) else {}
    if not isinstance(time_island, dict):
        return "normal"
    kairos = time_island.get("kairos")
    if not isinstance(kairos, dict):
        return "normal"
    return str(kairos.get("decision_mode") or "normal")


def load_drift_metrics(nodes_path: Optional[str]) -> Dict[str, object]:
    metrics = {
        "available": False,
        "count": 0,
        "max_delta_norm": None,
        "avg_delta_norm": None,
    }
    if not nodes_path or not os.path.exists(nodes_path):
        return metrics
    with open(nodes_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return metrics
    nodes = payload.get("nodes")
    if not isinstance(nodes, list):
        return metrics
    drift_values: List[float] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        drift = node.get("drift")
        if not isinstance(drift, dict):
            continue
        value = drift.get("delta_norm")
        if isinstance(value, (int, float)):
            drift_values.append(float(value))
    metrics["available"] = True
    if not drift_values:
        return metrics
    metrics["count"] = len(drift_values)
    metrics["max_delta_norm"] = max(drift_values)
    metrics["avg_delta_norm"] = sum(drift_values) / len(drift_values)
    return metrics


def decide_escalation(
    poav_total: Optional[float],
    poav_threshold: float,
    drift_max: Optional[float],
    drift_threshold: float,
    decision_mode: str,
) -> Dict[str, object]:
    reasons: List[str] = []
    if poav_total is not None and poav_total < poav_threshold:
        reasons.append(issue(IssueCode.POAV_BELOW_THRESHOLD))
    if drift_max is not None and drift_max >= drift_threshold:
        reasons.append(issue(IssueCode.DRIFT_ABOVE_THRESHOLD))

    decision = "none"
    if reasons:
        if decision_mode == "lockdown" or issue(IssueCode.POAV_BELOW_THRESHOLD) in reasons:
            decision = "quarantine"
        else:
            decision = "jump"
    return {"decision": decision, "reasons": reasons}


def record_escalation(
    decision: str,
    reasons: List[str],
    metrics: Dict[str, object],
    ledger_path: Optional[str],
    decision_mode: str,
    run_id: Optional[str],
) -> Optional[str]:
    if decision == "none" or not ledger_path:
        return None
    ledger_dir = os.path.dirname(ledger_path)
    if ledger_dir:
        os.makedirs(ledger_dir, exist_ok=True)
    payload = {
        "decision": decision,
        "reasons": reasons,
        "metrics": metrics,
        "decision_mode": decision_mode,
        "run_id": run_id,
    }
    event = ErrorEvent(
        behavior=f"Escalation: {decision}",
        context=json.dumps(payload, sort_keys=True),
        behavior_type="action",
        input_signal="yss_gate",
        mode_at_time=decision_mode,
        island_id=run_id or "",
        consequence_summary=f"{decision} triggered by escalation gate.",
        strategy=(
            "Hold outputs and request review."
            if decision == "quarantine"
            else "Escalate to jump path."
        ),
        strategy_type="escalate",
        implementation_notes="Recorded by escalation gate.",
    )
    ledger = ErrorLedger(ledger_path)
    return ledger.record(event)
