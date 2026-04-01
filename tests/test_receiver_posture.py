from __future__ import annotations

from tonesoul.receiver_posture import build_receiver_parity_readout


def test_receiver_parity_prioritizes_scenario_specific_alerts_over_generic_evidence_alert() -> None:
    readout = build_receiver_parity_readout(
        council_snapshot={},
        project_memory_summary={
            "evidence_readout_posture": {
                "summary_text": "evidence summary",
                "lanes": [
                    {
                        "lane": "continuity_effectiveness",
                        "classification": "runtime_present",
                    }
                ],
            },
            "subject_refresh": {
                "promotion_hazards": [
                    "recycled carry_forward without new evidence",
                ]
            },
            "working_style_anchor": {
                "decision_preferences": ["prefer packet before repo scan"],
            },
            "working_style_observability": {
                "status": "partial",
            },
            "working_style_import_limits": {
                "safe_apply": ["scan_order: use packet first"],
            },
        },
    )

    assert len(readout["alerts"]) == 6
    assert len(readout["primary_alerts"]) == 4
    assert all(
        "Evidence readout is a bounded honesty shortcut" not in alert
        for alert in readout["primary_alerts"]
    )
    assert (
        "Latest carry-forward repeats an older handoff without new evidence"
        in readout["primary_alerts"][0]
    )
    assert any(
        "Compaction-backed subject refresh is currently blocked" in alert
        for alert in readout["primary_alerts"]
    )
    assert any(
        "Working-style continuity is advisory only" in alert for alert in readout["primary_alerts"]
    )
    assert any(
        "Shared working-style continuity is only partially reinforced" in alert
        for alert in readout["primary_alerts"]
    )


def test_receiver_parity_keeps_generic_evidence_alert_when_no_higher_signal_exists() -> None:
    readout = build_receiver_parity_readout(
        council_snapshot={},
        project_memory_summary={
            "evidence_readout_posture": {
                "summary_text": "evidence summary",
                "lanes": [
                    {
                        "lane": "continuity_effectiveness",
                        "classification": "runtime_present",
                    }
                ],
            }
        },
    )

    assert readout["alerts"] == readout["primary_alerts"]
    assert len(readout["primary_alerts"]) == 1
    assert "Evidence readout is a bounded honesty shortcut" in readout["primary_alerts"][0]


def test_receiver_parity_prioritizes_dossier_realism_alerts() -> None:
    readout = build_receiver_parity_readout(
        council_snapshot={
            "calibration_status": "descriptive_only",
            "has_minority_report": True,
            "evolution_suppression_flag": True,
        },
        project_memory_summary={
            "evidence_readout_posture": {
                "summary_text": "evidence summary",
                "lanes": [
                    {
                        "lane": "continuity_effectiveness",
                        "classification": "runtime_present",
                    }
                ],
            }
        },
    )

    assert len(readout["alerts"]) == 4
    assert len(readout["primary_alerts"]) == 4
    assert "Latest council dossier confidence is descriptive_only" in readout["primary_alerts"][0]
    assert any("minority dissent" in alert for alert in readout["primary_alerts"])
    assert any("evolution suppression" in alert for alert in readout["primary_alerts"])
