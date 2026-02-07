"""Orchestrator Integration Tests"""

import sys

sys.path.insert(0, ".")

from memory.observer import MemoryObserver
from tools.handoff_builder import ContextSummary, DriftEntry, PendingTask, Phase
from tools.orchestrator import HealthMonitor, Orchestrator


def test_normal_operation():
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="normal operation",
        key_concepts=["handoff", "health monitor"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    result = orchestrator.handle_request(
        "hello",
        context_summary=context,
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("switched") is False


def test_quota_exhausted():
    health_monitor = HealthMonitor()
    health_monitor.update_quota(0.05)

    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=health_monitor,
    )

    context = ContextSummary(
        user_goal="quota exhausted",
        key_concepts=["handoff", "quota", "switch"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    result = orchestrator.handle_request(
        "quota low",
        context_summary=context,
        phase=Phase(current="run", reason="low quota"),
        pending_tasks=[PendingTask(id="task_001", description="handoff", status="in_progress")],
        drift_log=[
            DriftEntry(
                timestamp="2026-02-04T18:00:00Z",
                choice="switch",
                toward="handoff",
                away_from="stay",
            )
        ],
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("switched") is True


def test_with_observer():
    observer = MemoryObserver()

    action_id = observer.log_action(
        action="handle_request",
        params={"input": "ping"},
        result={"status": "ok"},
        before_context={"phase": "before"},
        after_context={"phase": "after"},
    )
    assert action_id

    commitment_id = observer.log_commitment(
        vow="test commitment",
        falsifiable_by="observer drift",
        measurable_via="drift log",
    )
    assert commitment_id

    logs = observer.query(limit=5)
    assert len(logs) > 0


def test_bug_once_triggers_handoff():
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="bug once escalation",
        key_concepts=["bug", "handoff", "escalation"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    def broken_handler(_: str):
        raise RuntimeError("simulated bug")

    result = orchestrator.handle_request(
        "run risky tool",
        context_summary=context,
        handler=broken_handler,
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("status") == "handoff"
    assert payload.get("switched") is True
    assert payload.get("switch_triggers", {}).get("bug") is True
    assert payload.get("health", {}).get("consecutive_failures") == 1
    assert payload.get("result", {}).get("status") == "error"


def test_final_audit_request_triggers_handoff():
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="final audit",
        key_concepts=["audit", "handoff"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    result = orchestrator.handle_request(
        "請做最後檔案審計",
        context_summary=context,
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("status") == "handoff"
    assert payload.get("switched") is True
    assert payload.get("switch_triggers", {}).get("final_audit") is True
    assert payload.get("switch_triggers", {}).get("bug") is False


def test_systemic_betrayal_requires_user_confirmation():
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="guard destructive intent",
        key_concepts=["confirmation", "risk gate"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    result = orchestrator.handle_request(
        "Please delete all data and wipe the system",
        context_summary=context,
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("status") == "confirmation_required"
    assert payload.get("switched") is False
    assert payload.get("requires_user_confirmation") is True
    assert payload.get("switch_triggers", {}).get("systemic_betrayal") is True


def test_systemic_betrayal_with_user_confirmation_allows_execution():
    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
    )

    context = ContextSummary(
        user_goal="confirmed destructive intent",
        key_concepts=["confirmation", "risk gate"],
        current_files=["tests/test_orchestrator_integration.py"],
    )

    result = orchestrator.handle_request(
        "Please delete all data and wipe the system",
        context_summary=context,
        user_confirmation=True,
    )

    assert result.get("success") is True
    payload = result.get("data", {})
    assert payload.get("status") in {"continue", "handoff"}
    assert payload.get("requires_user_confirmation") is False
    assert payload.get("switch_triggers", {}).get("systemic_betrayal") is True


if __name__ == "__main__":
    test_normal_operation()
    test_quota_exhausted()
    test_with_observer()
    test_bug_once_triggers_handoff()
    test_final_audit_request_triggers_handoff()
    test_systemic_betrayal_requires_user_confirmation()
    test_systemic_betrayal_with_user_confirmation_allows_execution()
