from __future__ import annotations

from tonesoul.runtime_adapter_normalization import (
    build_council_dossier_summary,
    find_recycled_carry_forward_hazard,
    normalize_closeout_payload,
)


def test_normalize_closeout_payload_blocks_on_stop_action() -> None:
    payload = normalize_closeout_payload(
        {},
        next_action="STOP: wait for human approval before continuing",
    )

    assert payload["status"] == "blocked"
    assert payload["stop_reason"] == ""
    assert payload["note"] == "Closeout is blocked; do not treat this handoff as completed work."


def test_find_recycled_carry_forward_hazard_requires_new_evidence() -> None:
    latest = {
        "compaction_id": "c2",
        "carry_forward": ["keep packet-first session cadence stable"],
        "evidence_refs": ["docs/AI_QUICKSTART.md"],
    }
    previous = {
        "compaction_id": "c1",
        "carry_forward": ["keep packet-first session cadence stable"],
        "evidence_refs": ["docs/AI_QUICKSTART.md"],
    }

    hazard = find_recycled_carry_forward_hazard(
        newer_compactions=[latest],
        all_compactions=[latest, previous],
    )

    assert "recycled carry_forward" in hazard


def test_build_council_dossier_summary_surfaces_realism_note() -> None:
    summary = build_council_dossier_summary(
        {
            "final_verdict": "approve",
            "confidence_posture": "descriptive_only",
            "coherence_score": 0.81,
            "dissent_ratio": 0.2,
            "minority_report": [
                {
                    "perspective": "critic",
                    "decision": "concern",
                    "confidence": 0.61,
                    "reasoning": "Grounding remains thin.",
                    "evidence": ["docs/MATH_FOUNDATIONS.md"],
                }
            ],
            "confidence_decomposition": {
                "calibration_status": "descriptive_only",
                "adversarial_posture": "survived_dissent",
            },
        }
    )

    assert summary["has_minority_report"] is True
    assert "Descriptive agreement record only" in summary["realism_note"]
