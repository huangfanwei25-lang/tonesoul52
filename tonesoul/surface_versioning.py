"""Repo-native surface versioning and consumer-lineage helpers."""

from __future__ import annotations

from typing import Any


def build_surface_versioning_readout() -> dict[str, Any]:
    """Return one bounded versioning and lineage view for current repo-native consumers."""

    runtime_surfaces = [
        {
            "surface": "session_start",
            "version": "tiered_v1",
            "kind": "runtime_entry",
            "derives_from": ["readiness", "canonical_center", "consumer_contract"],
            "fallback_to": "observer_window",
        },
        {
            "surface": "observer_window",
            "version": "anchor_window_v1",
            "kind": "runtime_orientation",
            "derives_from": ["canonical_center", "consumer_contract", "delta_summary"],
            "fallback_to": "r_memory_packet",
        },
        {
            "surface": "r_memory_packet",
            "version": "packet_v1",
            "kind": "runtime_detail",
            "derives_from": ["runtime_adapter", "operator_guidance"],
            "fallback_to": "",
        },
    ]

    consumer_shells = [
        {
            "consumer": "codex_cli",
            "surface": "session_start",
            "version": "cli_entry_v1",
            "derived_from": "session_start:tiered_v1",
        },
        {
            "consumer": "dashboard_operator_shell",
            "surface": "dashboard_tier_shell",
            "version": "dashboard_shell_v1",
            "derived_from": "session_start:tiered_v1",
        },
        {
            "consumer": "claude_style_shell",
            "surface": "claude_entry_adapter",
            "version": "claude_entry_v1",
            "derived_from": "session_start:tiered_v1",
        },
    ]

    return {
        "present": True,
        "summary_text": (
            "surface_versioning session_start=tiered_v1 "
            "observer_window=anchor_window_v1 packet=packet_v1 "
            "dashboard=dashboard_shell_v1 claude=claude_entry_v1"
        ),
        "runtime_surfaces": runtime_surfaces,
        "consumer_shells": consumer_shells,
        "fallback_rule": (
            "If a consumer shell is missing fields or looks mismatched, fall back to Tier 1 session-start first, then observer-window, and only then pull packet detail."
        ),
        "source_of_truth_rule": (
            "Runtime truth remains in repo-native entry and readout surfaces. Consumer shells are bounded adapters and must not outrank their parent surfaces."
        ),
    }
