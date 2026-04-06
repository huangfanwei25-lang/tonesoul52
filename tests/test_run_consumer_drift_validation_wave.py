from __future__ import annotations

from scripts.run_consumer_drift_validation_wave import build_consumer_drift_report


def _surface_versioning() -> dict:
    return {
        "summary_text": "surface_versioning session_start=tiered_v1 observer_window=anchor_window_v1",
        "fallback_rule": "If a consumer shell is missing fields or looks mismatched, fall back to Tier 1 session-start first, then observer-window, and only then pull packet detail.",
    }


def test_build_consumer_drift_report_marks_aligned_state() -> None:
    report = build_consumer_drift_report(
        agent="drift-wave",
        tier1_bundle={
            "canonical_center": {
                "current_short_board": {"summary_text": "Phase 785: surface versioning"}
            },
            "closeout_attention": {"status": "complete"},
            "surface_versioning": _surface_versioning(),
        },
        observer_window={
            "canonical_center": {
                "current_short_board": {"summary_text": "Phase 785: surface versioning"}
            },
            "closeout_attention": {"status": "complete"},
            "surface_versioning": _surface_versioning(),
        },
        dashboard_shell={
            "canonical_cards": {"short_board": "Phase 785: surface versioning"},
            "closeout_attention": {"status": "complete"},
        },
        claude_adapter_payload={
            "adapter": {
                "current_context": {
                    "short_board": "Phase 785: surface versioning",
                    "closeout_status": "complete",
                },
                "surface_versioning": _surface_versioning(),
            }
        },
    )

    assert report["status"] == "aligned"
    assert all(check["ok"] for check in report["parity_checks"])


def test_build_consumer_drift_report_marks_drift_when_closeout_diverges() -> None:
    report = build_consumer_drift_report(
        agent="drift-wave",
        tier1_bundle={
            "canonical_center": {"current_short_board": {"summary_text": "Phase 785"}},
            "closeout_attention": {"status": "partial"},
            "surface_versioning": _surface_versioning(),
        },
        observer_window={
            "canonical_center": {"current_short_board": {"summary_text": "Phase 785"}},
            "closeout_attention": {"status": "complete"},
            "surface_versioning": _surface_versioning(),
        },
        dashboard_shell={
            "canonical_cards": {"short_board": "Phase 785"},
            "closeout_attention": {"status": "partial"},
        },
        claude_adapter_payload={
            "adapter": {
                "current_context": {"short_board": "Phase 785", "closeout_status": "partial"},
                "surface_versioning": _surface_versioning(),
            }
        },
    )

    by_field = {check["field"]: check for check in report["parity_checks"]}
    assert report["status"] == "drift_detected"
    assert by_field["closeout_status"]["ok"] is False
