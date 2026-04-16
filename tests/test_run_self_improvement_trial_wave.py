from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

if not importlib.util.find_spec("streamlit"):
    pytest.skip("streamlit not installed", allow_module_level=True)

from scripts.run_self_improvement_trial_wave import (
    _probe_hook_chain_trigger_clarity,
    run_self_improvement_trial_wave,
)


def test_run_self_improvement_trial_wave_returns_completed_report() -> None:
    report = run_self_improvement_trial_wave(agent="trial-wave")

    assert report["status"] == "completed"
    assert report["bundle"] == "self_improvement_trial_wave"
    assert report["next_short_board"] == (
        "Explicitly ratify the next active bucket; do not silently auto-open queued governance-depth work."
    )
    assert len(report["candidates"]) == 19
    assert report["candidates"][0]["result_surface"]["surface_status"] == "promoted_result"
    assert (
        report["candidates"][-1]["candidate_record"]["candidate_id"]
        == "dashboard_command_shelf_activation_clarity_v1"
    )


def test_probe_hook_chain_trigger_clarity_reads_tier1(monkeypatch) -> None:
    seen: dict[str, int] = {}

    def fake_run_session_start_bundle(
        *,
        agent_id: str,
        state_path: Path | None = None,
        traces_path: Path | None = None,
        no_ack: bool = True,
        tier: int = 2,
    ) -> dict:
        seen["tier"] = tier
        return {
            "hook_chain": {
                "selection_rule": "Prefer mutation_preflight.next_followup first.",
                "hooks": [
                    {
                        "name": "publish_push_posture",
                        "status": "recommended_now",
                    },
                    {
                        "name": "shared_edit_path_overlap",
                        "status": "available",
                    },
                ],
                "stages": [
                    {
                        "name": "publish_push_posture",
                        "activation_signals": ["publish action visible"],
                    },
                    {
                        "name": "shared_edit_path_overlap",
                        "activation_signals": ["shared edit visible"],
                    },
                ],
                "current_recommendation": {
                    "present": True,
                    "target": "publish_push.posture_preflight",
                },
            },
            "mutation_preflight": {
                "next_followup": {
                    "target": "publish_push.posture_preflight",
                }
            },
        }

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        fake_run_session_start_bundle,
    )

    result = _probe_hook_chain_trigger_clarity(
        agent="trial-wave",
        state_path=None,
        traces_path=None,
    )

    assert seen["tier"] == 1
    assert result["present"] is True
    assert "recommended=publish_push_posture" in result["summary_text"]
