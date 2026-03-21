from typing import Dict

ACTION_POLICY = {
    "normal": ["verify", "cite", "inquire"],
    "cautious": ["verify", "inquire"],
    "lockdown": ["verify", "cite", "inquire"],  # Seabed Lockdown — Vol-5 §2
}


def _decision_mode(context: Dict[str, object]) -> str:
    time_island = context.get("time_island") if isinstance(context, dict) else {}
    if not isinstance(time_island, dict):
        return "normal"
    kairos = time_island.get("kairos") if isinstance(time_island, dict) else {}
    if not isinstance(kairos, dict):
        return "normal"
    return str(kairos.get("decision_mode") or "normal")


def resolve_action_set(context: Dict[str, object]) -> Dict[str, object]:
    decision_mode = _decision_mode(context)
    allowed_actions = ACTION_POLICY.get(decision_mode, ACTION_POLICY["normal"])
    strict_modes = {
        "cautious": ACTION_POLICY.get("cautious", []),
        "lockdown": ACTION_POLICY.get("lockdown", []),
    }
    return {
        "decision_mode": decision_mode,
        "allowed_actions": list(allowed_actions),
        "strict_mode_policy": strict_modes,
        "rationale": "Minimal action set to reduce risk under strict modes.",
    }
