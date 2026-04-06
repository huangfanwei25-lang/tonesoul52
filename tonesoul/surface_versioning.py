"""Repo-native surface versioning and consumer-lineage helpers."""

from __future__ import annotations

from typing import Any


def build_surface_versioning_readout() -> dict[str, Any]:
    """Return one bounded versioning and lineage view for current repo-native consumers."""

    fallback_chain = [
        "session_start:tiered_v1",
        "observer_window:anchor_window_v1",
        "r_memory_packet:packet_v1",
    ]
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

    compatibility_posture = {
        "summary_text": (
            "surface_compatibility codex=repo_native_entry "
            "dashboard=bounded_adapter claude=bounded_adapter "
            "fallback=session_start->observer_window->r_memory_packet"
        ),
        "fallback_chain": fallback_chain,
        "consumer_statuses": [
            {
                "consumer": "codex_cli",
                "surface": "session_start",
                "compatibility": "repo_native_entry",
                "parity_requirement": "must_preserve_first_hop_order",
                "fallback_order": fallback_chain,
            },
            {
                "consumer": "dashboard_operator_shell",
                "surface": "dashboard_tier_shell",
                "compatibility": "bounded_adapter",
                "parity_requirement": "must_preserve_first_hop_order",
                "fallback_order": fallback_chain,
            },
            {
                "consumer": "claude_style_shell",
                "surface": "claude_entry_adapter",
                "compatibility": "bounded_adapter",
                "parity_requirement": "must_preserve_first_hop_order",
                "fallback_order": fallback_chain,
            },
        ],
        "shared_expectation": (
            "All consumers should preserve the same first-hop order, closeout meaning, and mutation-gate story even when their panes or phrasing differ."
        ),
        "receiver_rule": (
            "Use compatibility posture to confirm which shells are repo-native versus bounded adapters, then fall back through the shared chain instead of treating any consumer shell as sovereign truth."
        ),
    }

    return {
        "present": True,
        "summary_text": (
            "surface_versioning session_start=tiered_v1 "
            "observer_window=anchor_window_v1 packet=packet_v1 "
            "dashboard=dashboard_shell_v1 claude=claude_entry_v1"
        ),
        "runtime_surfaces": runtime_surfaces,
        "consumer_shells": consumer_shells,
        "compatibility_posture": compatibility_posture,
        "fallback_rule": (
            "If a consumer shell is missing fields or looks mismatched, fall back to Tier 1 session-start first, then observer-window, and only then pull packet detail."
        ),
        "source_of_truth_rule": (
            "Runtime truth remains in repo-native entry and readout surfaces. Consumer shells are bounded adapters and must not outrank their parent surfaces."
        ),
    }
