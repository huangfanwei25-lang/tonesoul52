from __future__ import annotations

from tonesoul.surface_versioning import build_surface_versioning_readout


def test_build_surface_versioning_readout_keeps_runtime_and_consumer_split() -> None:
    payload = build_surface_versioning_readout()

    assert payload["present"] is True
    assert "session_start=tiered_v1" in payload["summary_text"]
    assert payload["runtime_surfaces"][0]["surface"] == "session_start"
    assert payload["runtime_surfaces"][1]["surface"] == "observer_window"
    assert payload["consumer_shells"][0]["consumer"] == "codex_cli"
    assert payload["consumer_shells"][1]["surface"] == "dashboard_tier_shell"
    assert payload["consumer_shells"][2]["version"] == "claude_entry_v1"
    compatibility = payload["compatibility_posture"]
    assert (
        compatibility["summary_text"]
        == "surface_compatibility codex=repo_native_entry dashboard=bounded_adapter claude=bounded_adapter fallback=session_start->observer_window->r_memory_packet"
    )
    assert compatibility["fallback_chain"] == [
        "session_start:tiered_v1",
        "observer_window:anchor_window_v1",
        "r_memory_packet:packet_v1",
    ]
    assert compatibility["consumer_statuses"][1]["compatibility"] == "bounded_adapter"
    assert "Tier 1 session-start first" in payload["fallback_rule"]
