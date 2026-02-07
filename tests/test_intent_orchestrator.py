"""Intent-Aware Orchestrator Test"""

import sys

sys.path.insert(0, ".")

from tools.handoff_builder import ContextSummary
from tools.orchestrator import HealthMonitor, Orchestrator


def test_intent_awareness():
    health_monitor = HealthMonitor()

    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=health_monitor,
    )

    context = ContextSummary(
        user_goal="intent awareness",
        key_concepts=["axioms", "intent"],
        current_files=["tools/orchestrator.py"],
    )

    orchestrator.handle_request("axiom check", context_summary=context)
    health_monitor.update_quota(0.05)

    result = orchestrator.handle_request("axiom check", context_summary=context)

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("status") in ("handoff", "continue")
    assert payload.get("switched") is True


if __name__ == "__main__":
    test_intent_awareness()
