import os
from typing import Dict, Iterable, Optional

import yaml

from .issue_codes import IssueCode, issue
from .ystm.schema import utc_now

TSR_DELTA_THRESHOLD = 0.4


def _default_policy_path() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "spec", "governance", "dcs_policy.yaml")
    )


def load_dcs_policy(path: Optional[str] = None) -> Dict[str, object]:
    policy_path = path or _default_policy_path()
    if not policy_path or not os.path.exists(policy_path):
        return {}
    with open(policy_path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _extend_reasons(reasons: list, items: Optional[Iterable[str]]) -> None:
    if not items:
        return
    for item in items:
        if item:
            reasons.append(str(item))


def build_dcs_result(
    decision_mode: str,
    p0_passed: bool,
    p0_issues: Optional[Iterable[str]] = None,
    poav_total: Optional[float] = None,
    poav_threshold: float = 0.7,
    mercy_score: Optional[float] = None,
    mercy_threshold: float = 0.1,
    drift_max: Optional[float] = None,
    drift_threshold: float = 4.0,
    tsr_delta_norm: Optional[float] = None,
    escalation_decision: Optional[str] = None,
    policy: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    policy = policy or {}
    thresholds = policy.get("thresholds", {}) if isinstance(policy.get("thresholds"), dict) else {}
    poav_threshold = float(thresholds.get("poav_min", poav_threshold))
    mercy_threshold = float(thresholds.get("mercy_min", mercy_threshold))
    drift_threshold = float(thresholds.get("drift_max", drift_threshold))
    tsr_delta_threshold = float(thresholds.get("tsr_delta_max", TSR_DELTA_THRESHOLD))

    triggers: Dict[str, bool] = {}
    reasons: list = []

    if not p0_passed:
        triggers["p0"] = True
        _extend_reasons(reasons, p0_issues)
    else:
        triggers["p0"] = False

    if escalation_decision and escalation_decision != "none":
        triggers["escalation"] = True
        reasons.append(issue(IssueCode.ESCALATION_DECISION, decision=escalation_decision))
    else:
        triggers["escalation"] = False

    if poav_total is not None and poav_total < poav_threshold:
        triggers["poav"] = True
        reasons.append(issue(IssueCode.POAV_BELOW_THRESHOLD))
    else:
        triggers["poav"] = False
    if mercy_score is not None and mercy_score < mercy_threshold:
        triggers["mercy"] = True
        reasons.append(issue(IssueCode.MERCY_BELOW_THRESHOLD))
    else:
        triggers["mercy"] = False
    if drift_max is not None and drift_max >= drift_threshold:
        triggers["drift"] = True
        reasons.append(issue(IssueCode.DRIFT_ABOVE_THRESHOLD))
    else:
        triggers["drift"] = False
    if tsr_delta_norm is not None and tsr_delta_norm >= tsr_delta_threshold:
        triggers["tsr_delta"] = True
        reasons.append(issue(IssueCode.DCS_TSR_DELTA_HIGH))
    else:
        triggers["tsr_delta"] = False

    decision_mode = (decision_mode or "normal").lower()
    dcs_config = policy.get("dcs", {}) if isinstance(policy.get("dcs"), dict) else {}
    decision_modes = (
        dcs_config.get("decision_modes", {})
        if isinstance(dcs_config.get("decision_modes"), dict)
        else {}
    )
    mode_rules = (
        decision_modes.get(decision_mode, {})
        if isinstance(decision_modes.get(decision_mode), dict)
        else {}
    )
    default_close_on = {"p0", "escalation"}
    default_soft_close_on = {"poav", "mercy", "drift", "tsr_delta"}
    if decision_mode == "lockdown":
        default_close_on = default_close_on | default_soft_close_on
        default_soft_close_on = set()

    close_on = set(mode_rules.get("close_on", default_close_on))
    soft_close_on = set(mode_rules.get("soft_close_on", default_soft_close_on))
    if decision_mode == "lockdown":
        # Lockdown is fail-closed: policy overrides may tighten behavior, but
        # cannot reopen triggers that the built-in lockdown posture closes.
        close_on |= default_close_on
        soft_close_on -= close_on

    closed_triggers = [key for key, active in triggers.items() if active and key in close_on]
    soft_triggers = [
        key
        for key, active in triggers.items()
        if active and key in soft_close_on and key not in close_on
    ]

    if closed_triggers:
        state = "closed"
        decision = "halt"
    elif soft_triggers:
        state = "soft_close"
        decision = "hold"
    else:
        state = "open"
        decision = "proceed"

    return {
        "generated_at": utc_now(),
        "dcs_version": "0.1",
        "decision_mode": decision_mode,
        "state": state,
        "decision": decision,
        "reasons": reasons,
        "thresholds": {
            "poav_min": poav_threshold,
            "mercy_min": mercy_threshold,
            "drift_max": drift_threshold,
            "tsr_delta_max": tsr_delta_threshold,
        },
        "rules": {
            "close_on": sorted(close_on),
            "soft_close_on": sorted(soft_close_on),
        },
        "triggered": {
            "closed": closed_triggers,
            "soft_close": soft_triggers,
        },
        "signals": {
            "p0_passed": p0_passed,
            "poav_total": poav_total,
            "poav_threshold": poav_threshold,
            "mercy_score": mercy_score,
            "mercy_threshold": mercy_threshold,
            "drift_max": drift_max,
            "drift_threshold": drift_threshold,
            "tsr_delta_norm": tsr_delta_norm,
            "escalation_decision": escalation_decision,
        },
        "notes": "DCS is record-only in v0.1; use for closure awareness.",
    }
