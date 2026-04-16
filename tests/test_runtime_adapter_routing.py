from __future__ import annotations

from typing import Any, Dict

from tonesoul.runtime_adapter_routing import (
    build_routing_event,
    build_routing_summary,
    persist_routed_signal,
    route_r_memory_signal,
)


def test_persist_routed_signal_uses_checkpoint_writer() -> None:
    route = route_r_memory_signal(
        agent_id="codex",
        summary="resume packet cleanup",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="finish routing seam",
        source="test",
    )

    def unexpected(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        raise AssertionError(f"unexpected writer call: {args} {kwargs}")

    def checkpoint_writer(
        checkpoint_id: str,
        *,
        agent_id: str,
        session_id: str,
        summary: str,
        pending_paths: list[str],
        next_action: str,
        source: str,
        ttl_seconds: int,
        store: Any,
    ) -> Dict[str, Any]:
        return {
            "checkpoint_id": checkpoint_id,
            "agent_id": agent_id,
            "session_id": session_id,
            "summary": summary,
            "pending_paths": pending_paths,
            "next_action": next_action,
            "source": source,
            "ttl_seconds": ttl_seconds,
            "store": store,
        }

    written = persist_routed_signal(
        route,
        claim_writer=unexpected,
        perspective_writer=unexpected,
        checkpoint_writer=checkpoint_writer,
        compaction_writer=unexpected,
        subject_snapshot_writer=unexpected,
        store="sentinel-store",
    )

    assert written["checkpoint_id"].startswith("cp-")
    assert written["pending_paths"] == ["tonesoul/runtime_adapter.py"]
    assert written["next_action"] == "finish routing seam"
    assert written["ttl_seconds"] == 86400
    assert written["store"] == "sentinel-store"


def test_build_routing_event_marks_forced_overlap() -> None:
    route = route_r_memory_signal(
        agent_id="codex",
        summary="force compaction despite checkpoint cues",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="review lane choice",
        carry_forward=["preserve observer baseline"],
        prefer_surface="compaction",
    )

    event = build_routing_event(
        route,
        action="write",
        written=True,
        utc_now=lambda: "2026-04-14T12:00:00+00:00",
    )

    assert event["surface"] == "compaction"
    assert event["forced"] is True
    assert event["overlap"] is True
    assert event["misroute_signal"] is True
    assert event["updated_at"] == "2026-04-14T12:00:00+00:00"


def test_build_routing_summary_includes_freshness_hours() -> None:
    summary = build_routing_summary(
        [
            {
                "event_id": "evt-1",
                "agent": "codex",
                "surface": "checkpoint",
                "action": "preview",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "updated_at": "2026-04-14T12:00:00+00:00",
                "summary": "preview checkpoint route",
            }
        ],
        freshness_hours=lambda _: 1.25,
    )

    assert summary["total_events"] == 1
    assert (
        summary["summary_text"]
        == "router=writes=0 previews=1 overrides=0 overlap=0 misroute_signals=0 top=checkpoint"
    )
    assert summary["recent_events"][0]["freshness_hours"] == 1.25
