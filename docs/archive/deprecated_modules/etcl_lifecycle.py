import json
import os
from typing import Dict, Optional, Tuple

from .ystm.schema import utc_now

STATES = ["T0", "T1", "T2", "T3", "T4", "T5", "T6"]
EVENT_TO_STATE = {
    "deposit": "T1",
    "retrieve": "T2",
    "align": "T3",
    "apply": "T4",
    "feedback": "T5",
    "canonical": "T6",
}


def seed_path_for_run(run_id: str, memory_root: Optional[str] = None) -> str:
    root = memory_root or os.path.join(_workspace_root(), "memory")
    return os.path.join(root, "seeds", f"{run_id}.json")


def load_seed(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Seed payload must be a mapping.")
    return payload


def save_seed(path: str, seed: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(seed, handle, indent=2)


def transition(
    seed: Dict[str, object],
    event: str,
    actor: Optional[str] = None,
    reason: Optional[str] = None,
    allow_same: bool = False,
) -> Tuple[Dict[str, object], Dict[str, object]]:
    if not event:
        raise ValueError("Event is required.")
    event = event.strip()
    current = seed.get("sigma_stamp")
    if current not in STATES:
        current = "T0"

    target = None
    event_lower = event.lower()
    if event_lower in EVENT_TO_STATE:
        target = EVENT_TO_STATE[event_lower]
    elif event in STATES:
        target = event
    elif event_lower == "advance":
        target = _next_state(current)

    if target not in STATES:
        raise ValueError(f"Unknown event or state: {event}")

    if target == current and not allow_same:
        raise ValueError("Target state is the same as current state.")

    if STATES.index(target) < STATES.index(current):
        raise ValueError("Backward transition is not allowed in minimal lifecycle.")

    timestamp = utc_now()
    history = seed.get("state_history")
    if not isinstance(history, list):
        history = []

    entry = {
        "from": current,
        "to": target,
        "event": event_lower,
        "timestamp": timestamp,
    }
    if actor:
        entry["actor"] = actor
    if reason:
        entry["transition_reason"] = reason

    history.append(entry)
    seed["sigma_stamp"] = target
    seed["state_history"] = history
    seed["lifecycle"] = {"state": target, "updated_at": timestamp, "last_event": event_lower}
    return seed, entry


def _next_state(current: str) -> str:
    idx = STATES.index(current)
    return STATES[min(idx + 1, len(STATES) - 1)]


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
