from __future__ import annotations

from scripts.run_self_improvement_trial_wave import run_self_improvement_trial_wave


def test_run_self_improvement_trial_wave_returns_completed_report() -> None:
    report = run_self_improvement_trial_wave(agent="trial-wave")

    assert report["status"] == "completed"
    assert report["bundle"] == "self_improvement_trial_wave"
    assert report["next_short_board"] == "Phase 829: Twelfth Trial Candidate Admission"
    assert len(report["candidates"]) == 12
    assert report["candidates"][0]["result_surface"]["surface_status"] == "promoted_result"
    assert report["candidates"][-1]["candidate_record"]["candidate_id"] == "consumer_misread_guard_clarity_v1"
