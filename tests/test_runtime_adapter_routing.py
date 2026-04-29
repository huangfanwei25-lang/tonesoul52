from __future__ import annotations

from typing import Any, Dict

import pytest

from tonesoul.runtime_adapter_routing import (
    build_routing_event,
    build_routing_summary,
    persist_routed_signal,
    route_r_memory_signal,
    safe_list_routing_events,
    slug_from_summary,
)

# ─── slug_from_summary ───────────────────────────────────────────────────────


class TestSlugFromSummary:
    def test_basic_slug(self):
        assert slug_from_summary("Hello World", fallback="fb") == "hello-world"

    def test_special_chars_become_dashes(self):
        assert slug_from_summary("a!b@c", fallback="fb") == "a-b-c"

    def test_consecutive_non_alnum_single_dash(self):
        result = slug_from_summary("a  --  b", fallback="fb")
        assert result == "a-b"

    def test_empty_string_uses_fallback(self):
        assert slug_from_summary("", fallback="fb") == "fb"

    def test_none_uses_fallback(self):
        assert slug_from_summary(None, fallback="fb") == "fb"

    def test_prefix_prepended(self):
        result = slug_from_summary("work item", fallback="fb", prefix="cp")
        assert result == "cp-work-item"

    def test_prefix_with_empty_summary(self):
        result = slug_from_summary("", fallback="task", prefix="cp")
        assert result == "cp-task"

    def test_leading_trailing_dashes_stripped(self):
        result = slug_from_summary("!leading", fallback="fb")
        assert not result.startswith("-")


# ─── route_r_memory_signal ───────────────────────────────────────────────────


class TestRouteRMemorySignalSurface:
    def test_prefer_surface_overrides_shape(self):
        route = route_r_memory_signal(
            agent_id="agent", summary="test", prefer_surface="perspective"
        )
        assert route["surface"] == "perspective"
        assert route["confidence"] == "forced"

    def test_invalid_prefer_surface_raises(self):
        with pytest.raises(ValueError, match="Unknown preferred surface"):
            route_r_memory_signal(agent_id="a", prefer_surface="invalid")

    def test_subject_shape_wins_over_claim(self):
        route = route_r_memory_signal(
            agent_id="a",
            task_id="t1",
            stable_vows=["vow1"],
        )
        assert route["surface"] == "subject_snapshot"
        assert route["confidence"] == "high"

    def test_claim_shape_only_task_id(self):
        route = route_r_memory_signal(agent_id="a", task_id="task-001", summary="work")
        assert route["surface"] == "claim"
        assert route["confidence"] == "high"

    def test_compaction_shape_carry_forward(self):
        route = route_r_memory_signal(agent_id="a", carry_forward=["item"])
        assert route["surface"] == "compaction"

    def test_perspective_shape_stance(self):
        route = route_r_memory_signal(agent_id="a", stance="cautious")
        assert route["surface"] == "perspective"

    def test_perspective_shape_tensions(self):
        route = route_r_memory_signal(agent_id="a", tensions=["tension1"])
        assert route["surface"] == "perspective"

    def test_checkpoint_shape_pending_paths(self):
        route = route_r_memory_signal(agent_id="a", pending_paths=["path/to/file"])
        assert route["surface"] == "checkpoint"

    def test_summary_only_is_checkpoint_low_confidence(self):
        route = route_r_memory_signal(agent_id="a", summary="just a summary")
        assert route["surface"] == "checkpoint"
        assert route["confidence"] == "low"

    def test_secondary_signals_present(self):
        route = route_r_memory_signal(agent_id="a")
        assert "secondary_signals" in route
        for key in ("claim", "checkpoint", "compaction", "perspective", "subject_snapshot"):
            assert key in route["secondary_signals"]

    def test_claim_with_compaction_routes_to_compaction(self):
        # task_id + carry_forward → compaction takes priority over claim
        route = route_r_memory_signal(agent_id="a", task_id="t1", carry_forward=["item"])
        assert route["surface"] == "compaction"

    def test_agent_id_in_payload(self):
        route = route_r_memory_signal(agent_id="my-agent")
        assert route["payload"]["agent"] == "my-agent"

    def test_source_defaults_to_direct(self):
        route = route_r_memory_signal(agent_id="a")
        assert route["payload"]["source"] == "direct"

    def test_custom_source_preserved(self):
        route = route_r_memory_signal(agent_id="a", source="api")
        assert route["payload"]["source"] == "api"


class TestRoutePayloadShape:
    def test_claim_payload_has_task_id(self):
        route = route_r_memory_signal(agent_id="a", task_id="my-task", summary="s")
        assert "task_id" in route["payload"]
        assert route["payload"]["task_id"] == "my-task"

    def test_claim_payload_slug_from_summary_when_no_task_id(self):
        route = route_r_memory_signal(
            agent_id="a",
            summary="do the work",
            prefer_surface="claim",
        )
        assert route["payload"]["task_id"] == "do-the-work"

    def test_perspective_payload_has_stance(self):
        route = route_r_memory_signal(agent_id="a", stance="open")
        assert route["payload"]["stance"] == "open"

    def test_perspective_payload_default_stance_provisional(self):
        route = route_r_memory_signal(agent_id="a", prefer_surface="perspective")
        assert route["payload"]["stance"] == "provisional"

    def test_checkpoint_payload_has_checkpoint_id_with_cp_prefix(self):
        route = route_r_memory_signal(agent_id="a", pending_paths=["x"])
        assert route["payload"]["checkpoint_id"].startswith("cp-")

    def test_compaction_payload_has_carry_forward(self):
        route = route_r_memory_signal(agent_id="a", carry_forward=["keep this"])
        assert "keep this" in route["payload"]["carry_forward"]

    def test_subject_snapshot_payload_has_stable_vows(self):
        route = route_r_memory_signal(agent_id="a", stable_vows=["vow1"])
        assert "vow1" in route["payload"]["stable_vows"]


# ─── persist_routed_signal ───────────────────────────────────────────────────


def _noop(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    raise AssertionError(f"unexpected writer: {args} {kwargs}")


class TestPersistRoutedSignal:
    def test_checkpoint_writer_called(self):
        route = route_r_memory_signal(
            agent_id="codex",
            summary="resume packet cleanup",
            pending_paths=["tonesoul/runtime_adapter.py"],
            next_action="finish routing seam",
            source="test",
        )

        def checkpoint_writer(
            checkpoint_id,
            *,
            agent_id,
            session_id,
            summary,
            pending_paths,
            next_action,
            source,
            ttl_seconds,
            store,
        ):
            return {
                "checkpoint_id": checkpoint_id,
                "ttl_seconds": ttl_seconds,
                "store": store,
                "pending_paths": pending_paths,
                "next_action": next_action,
            }

        written = persist_routed_signal(
            route,
            claim_writer=_noop,
            perspective_writer=_noop,
            checkpoint_writer=checkpoint_writer,
            compaction_writer=_noop,
            subject_snapshot_writer=_noop,
            store="sentinel-store",
        )
        assert written["checkpoint_id"].startswith("cp-")
        assert written["pending_paths"] == ["tonesoul/runtime_adapter.py"]
        assert written["next_action"] == "finish routing seam"
        assert written["ttl_seconds"] == 86400
        assert written["store"] == "sentinel-store"

    def test_claim_writer_called(self):
        route = route_r_memory_signal(agent_id="a", task_id="t1", summary="work")
        results = {}

        def claim_writer(task_id, *, agent_id, summary, paths, source, ttl_seconds, store):
            results["task_id"] = task_id
            results["ttl_seconds"] = ttl_seconds
            return results

        persist_routed_signal(
            route,
            claim_writer=claim_writer,
            perspective_writer=_noop,
            checkpoint_writer=_noop,
            compaction_writer=_noop,
            subject_snapshot_writer=_noop,
        )
        assert results["task_id"] == "t1"
        assert results["ttl_seconds"] == 1800

    def test_perspective_writer_called(self):
        route = route_r_memory_signal(agent_id="a", stance="open")
        results = {}

        def perspective_writer(
            agent_id,
            *,
            session_id,
            summary,
            stance,
            tensions,
            proposed_drift,
            proposed_vows,
            evidence_refs,
            source,
            ttl_seconds,
            store,
        ):
            results["stance"] = stance
            results["ttl_seconds"] = ttl_seconds
            return results

        persist_routed_signal(
            route,
            claim_writer=_noop,
            perspective_writer=perspective_writer,
            checkpoint_writer=_noop,
            compaction_writer=_noop,
            subject_snapshot_writer=_noop,
        )
        assert results["stance"] == "open"
        assert results["ttl_seconds"] == 7200

    def test_compaction_writer_called(self):
        route = route_r_memory_signal(agent_id="a", carry_forward=["item"])
        results = {}

        def compaction_writer(
            *,
            agent_id,
            session_id,
            summary,
            carry_forward,
            pending_paths,
            evidence_refs,
            next_action,
            source,
            ttl_seconds,
            limit,
            store,
        ):
            results["carry_forward"] = carry_forward
            results["ttl_seconds"] = ttl_seconds
            results["limit"] = limit
            return results

        persist_routed_signal(
            route,
            claim_writer=_noop,
            perspective_writer=_noop,
            checkpoint_writer=_noop,
            compaction_writer=compaction_writer,
            subject_snapshot_writer=_noop,
        )
        assert "item" in results["carry_forward"]
        assert results["ttl_seconds"] == 604800
        assert results["limit"] == 20

    def test_subject_snapshot_writer_called(self):
        route = route_r_memory_signal(agent_id="a", stable_vows=["vow1"])
        results = {}

        def subject_snapshot_writer(
            *,
            agent_id,
            session_id,
            summary,
            stable_vows,
            durable_boundaries,
            decision_preferences,
            verified_routines,
            active_threads,
            evidence_refs,
            refresh_signals,
            source,
            ttl_seconds,
            limit,
            store,
        ):
            results["stable_vows"] = stable_vows
            results["ttl_seconds"] = ttl_seconds
            results["limit"] = limit
            return results

        persist_routed_signal(
            route,
            claim_writer=_noop,
            perspective_writer=_noop,
            checkpoint_writer=_noop,
            compaction_writer=_noop,
            subject_snapshot_writer=subject_snapshot_writer,
        )
        assert "vow1" in results["stable_vows"]
        assert results["ttl_seconds"] == 2592000
        assert results["limit"] == 12

    def test_missing_surface_raises(self):
        with pytest.raises(ValueError, match="route.surface is required"):
            persist_routed_signal(
                {"surface": "", "payload": {}},
                claim_writer=_noop,
                perspective_writer=_noop,
                checkpoint_writer=_noop,
                compaction_writer=_noop,
                subject_snapshot_writer=_noop,
            )

    def test_unsupported_surface_raises(self):
        with pytest.raises(ValueError, match="Unsupported routed surface"):
            persist_routed_signal(
                {"surface": "unknown_surface", "payload": {}},
                claim_writer=_noop,
                perspective_writer=_noop,
                checkpoint_writer=_noop,
                compaction_writer=_noop,
                subject_snapshot_writer=_noop,
            )


# ─── build_routing_event ─────────────────────────────────────────────────────


class TestBuildRoutingEvent:
    def test_forced_overlap_marks_misroute(self):
        route = route_r_memory_signal(
            agent_id="codex",
            summary="force compaction despite checkpoint cues",
            pending_paths=["tonesoul/runtime_adapter.py"],
            next_action="review lane choice",
            carry_forward=["preserve observer baseline"],
            prefer_surface="compaction",
        )
        event = build_routing_event(
            route, action="write", written=True, utc_now=lambda: "2026-04-14T12:00:00+00:00"
        )
        assert event["surface"] == "compaction"
        assert event["forced"] is True
        assert event["overlap"] is True
        assert event["misroute_signal"] is True

    def test_clean_route_no_misroute(self):
        route = route_r_memory_signal(agent_id="a", carry_forward=["item"])
        event = build_routing_event(route, utc_now=lambda: "ts")
        assert event["forced"] is False
        assert event["misroute_signal"] is False or event["overlap"] is False

    def test_invalid_action_raises(self):
        route = route_r_memory_signal(agent_id="a")
        with pytest.raises(ValueError, match="action must be preview or write"):
            build_routing_event(route, action="invalid", utc_now=lambda: "ts")

    def test_event_id_is_uuid(self):
        import uuid

        route = route_r_memory_signal(agent_id="a")
        event = build_routing_event(route, utc_now=lambda: "ts")
        uuid.UUID(event["event_id"])  # raises if invalid

    def test_required_keys_present(self):
        route = route_r_memory_signal(agent_id="a")
        event = build_routing_event(route, utc_now=lambda: "ts")
        for key in (
            "event_id",
            "agent",
            "surface",
            "action",
            "written",
            "confidence",
            "reason",
            "forced",
            "overlap",
            "misroute_signal",
            "secondary_signal_count",
            "secondary_signals",
            "updated_at",
        ):
            assert key in event

    def test_default_action_is_preview(self):
        route = route_r_memory_signal(agent_id="a")
        event = build_routing_event(route, utc_now=lambda: "ts")
        assert event["action"] == "preview"


# ─── safe_list_routing_events ────────────────────────────────────────────────


class TestSafeListRoutingEvents:
    def test_returns_events_on_success(self):
        events = [{"event_id": "e1"}]
        result = safe_list_routing_events(get_events=lambda n: events)
        assert result == events

    def test_returns_empty_list_on_exception(self):
        def bad_getter(n):
            raise RuntimeError("store down")

        result = safe_list_routing_events(get_events=bad_getter)
        assert result == []

    def test_n_passed_through(self):
        captured = {}

        def getter(n):
            captured["n"] = n
            return []

        safe_list_routing_events(get_events=getter, n=5)
        assert captured["n"] == 5


# ─── build_routing_summary ───────────────────────────────────────────────────


class TestBuildRoutingSummary:
    def test_empty_events_returns_zero_totals(self):
        result = build_routing_summary([])
        assert result["total_events"] == 0
        assert result["dominant_surface"] == ""
        assert result["summary_text"] == "router=no recent adoption telemetry"

    def test_counts_writes_and_previews(self):
        events = [
            {
                "action": "write",
                "surface": "claim",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "a",
                "event_id": "1",
                "updated_at": "t",
                "summary": "s",
            },
            {
                "action": "preview",
                "surface": "claim",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "b",
                "event_id": "2",
                "updated_at": "t",
                "summary": "s",
            },
        ]
        result = build_routing_summary(events)
        assert result["write_count"] == 1
        assert result["preview_count"] == 1

    def test_dominant_surface_most_common(self):
        events = [
            {
                "action": "preview",
                "surface": "checkpoint",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "a",
                "event_id": "1",
                "updated_at": "t",
                "summary": "s",
            },
            {
                "action": "preview",
                "surface": "checkpoint",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "b",
                "event_id": "2",
                "updated_at": "t",
                "summary": "s",
            },
            {
                "action": "preview",
                "surface": "claim",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "c",
                "event_id": "3",
                "updated_at": "t",
                "summary": "s",
            },
        ]
        result = build_routing_summary(events)
        assert result["dominant_surface"] == "checkpoint"

    def test_recent_agents_deduplicated(self):
        events = [
            {
                "action": "preview",
                "surface": "claim",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "same-agent",
                "event_id": str(i),
                "updated_at": "t",
                "summary": "s",
            }
            for i in range(3)
        ]
        result = build_routing_summary(events)
        assert result["recent_agents"].count("same-agent") == 1

    def test_forced_count_incremented(self):
        events = [
            {
                "action": "write",
                "surface": "compaction",
                "forced": True,
                "overlap": False,
                "misroute_signal": True,
                "agent": "a",
                "event_id": "1",
                "updated_at": "t",
                "summary": "s",
            },
        ]
        result = build_routing_summary(events)
        assert result["forced_count"] == 1
        assert result["misroute_signal_count"] == 1

    def test_freshness_hours_attached(self):
        result = build_routing_summary(
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
        assert result["total_events"] == 1
        assert result["recent_events"][0]["freshness_hours"] == 1.25

    def test_summary_text_format(self):
        events = [
            {
                "action": "write",
                "surface": "claim",
                "forced": False,
                "overlap": False,
                "misroute_signal": False,
                "agent": "a",
                "event_id": "1",
                "updated_at": "t",
                "summary": "s",
            },
        ]
        result = build_routing_summary(events)
        assert result["summary_text"].startswith("router=")
        assert "top=claim" in result["summary_text"]
