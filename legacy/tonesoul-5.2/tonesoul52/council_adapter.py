import os
import sys
import uuid
from datetime import datetime
from typing import Dict


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run_council(question: str) -> Dict[str, object]:
    try:
        from body.persona_stack import PersonaStack, EchoRouter

        stack = PersonaStack()
        router = EchoRouter(stack)
        output = router.route_to_all(question)
        perspectives = output.get("perspectives", {})
        integration = output.get("integration", "")
        switches = stack.get_switch_history(limit=5)
        active = stack.active_persona or "Core"
    except Exception as exc:
        perspectives = {"Core": f"Fallback perspective (error: {exc})"}
        integration = "Fallback integration"
        switches = []
        active = "Core"

    return {
        "event_type": "persona_council",
        "trace_id": str(uuid.uuid4()),
        "timestamp": _iso_now(),
        "persona": {
            "active": active,
            "switches": switches,
        },
        "council": {
            "perspectives": perspectives,
            "integration": integration,
            "dissent": [],
        },
        "audit": {
            "coverage": 1.0,
            "notes": "auto-generated council event",
        },
    }
