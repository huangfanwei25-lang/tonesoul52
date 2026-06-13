"""Pin the revived Strategy_Mirror shadow run (Manifold / self-observation layer).

Strategy_Mirror was a dormant gem (built + 92 tests, default-off, never run in
shadow). The shadow-run script (scripts/run_strategy_mirror_shadow.py) revived
it. These tests pin that it actually discriminates — fires on zh-TW rhetorical
moves, stays quiet on plain-honest text — so the revival can't silently rot.
"""

from __future__ import annotations

from scripts.run_strategy_mirror_shadow import run


def test_detector_discriminates_rhetorical_from_plain():
    r = run()
    assert r["catalog_size"] == 150
    # Fires on rhetorical samples, silent on plain ones.
    assert r["detection_rate_rhetorical"] == 1.0, r
    assert r["false_trip_rate_plain"] == 0.0, r


def test_detects_a_red_move_in_urgency_scarcity():
    r = run()
    # The urgency/scarcity sample should trip at least one red (high-risk) move.
    assert r["color_totals"].get("red", 0) >= 1, r
    urgency = next(s for s in r["samples"] if s["case"] == "urgency_scarcity")
    assert any(m["transparency_class"] == "red" for m in urgency["moves"]), urgency
