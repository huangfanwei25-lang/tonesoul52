"""Live Handoff Test (manual)"""

import sys

sys.path.insert(0, ".")

from datetime import datetime
from pathlib import Path

from tools.handoff_builder import ContextSummary, DriftEntry, PendingTask, Phase
from tools.orchestrator import HealthMonitor, Orchestrator


def create_live_handoff():
    monitor = HealthMonitor()
    monitor.update_quota(0.05)

    orchestrator = Orchestrator(
        source_model="antigravity",
        target_model="codex",
        health_monitor=monitor,
    )

    context = ContextSummary(
        user_goal="handoff",
        key_concepts=["handoff", "health monitor"],
        current_files=[
            "tools/orchestrator.py",
            "tools/handoff_builder.py",
            "memory/observer.py",
        ],
    )

    phase = Phase(current="run", reason="low quota")

    pending_tasks = [
        PendingTask(id="task_001", description="handoff", status="in_progress"),
        PendingTask(id="task_002", description="observer", status="pending"),
    ]

    drift_log = [
        DriftEntry(
            timestamp="2026-02-04T09:07:00Z",
            choice="switch",
            toward="handoff",
            away_from="stay",
        ),
        DriftEntry(
            timestamp="2026-02-04T18:15:00Z",
            choice="log",
            toward="trace",
            away_from="ignore",
        ),
    ]

    result = orchestrator.handle_request(
        "handoff",
        context_summary=context,
        phase=phase,
        pending_tasks=pending_tasks,
        drift_log=drift_log,
    )

    payload = result.get("data", {})
    print(f"Status: {payload.get('status')}")
    print(f"Handoff Packet: {payload.get('handoff_packet')}")

    handoff_path = payload.get("handoff_packet")
    if not handoff_path:
        return result

    codex_prompt = generate_codex_prompt(handoff_path)

    prompt_path = Path("memory/handoff/codex_prompt.md")
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(codex_prompt, encoding="utf-8")

    print(f"Codex prompt saved: {prompt_path}")
    print(codex_prompt)

    return result


def generate_codex_prompt(handoff_path: str) -> str:
    return f"""# Handoff

Packet:
`{handoff_path}`

Generated: {datetime.utcnow().isoformat()}Z
"""


if __name__ == "__main__":
    create_live_handoff()
