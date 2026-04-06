from __future__ import annotations

from pathlib import Path

from apps.dashboard.frontend.utils.session_start import (
    build_tier0_start_strip,
    build_tier1_orientation_shell,
    run_session_start_bundle,
)


def test_build_tier0_start_strip_extracts_operator_summary():
    bundle = {
        "present": True,
        "tier": 0,
        "readiness": {"status": "pass"},
        "task_track_hint": {"suggested_track": "feature_track"},
        "deliberation_mode_hint": {"suggested_mode": "lightweight_review"},
        "canonical_center": {"summary_text": "short board visible"},
        "hook_chain": {
            "hooks": [
                {"name": "shared_edit_path_overlap", "status": "active"},
                {"name": "publish_push_posture", "status": "active"},
            ]
        },
        "mutation_preflight": {
            "receiver_rule": "keep bounded",
            "next_followup": {
                "target": "task_board.parking_preflight",
                "classification": "existing_runtime_hook",
                "command": "python scripts/run_task_board_preflight.py ...",
                "reason": "keep ideas parked",
            },
        },
    }

    result = build_tier0_start_strip(bundle)

    assert result["readiness_status"] == "pass"
    assert result["task_track"] == "feature_track"
    assert result["deliberation_mode"] == "lightweight_review"
    assert result["canonical_summary"] == "short board visible"
    assert result["next_followup"]["target"] == "task_board.parking_preflight"
    assert result["hook_badges"][0]["name"] == "shared_edit_path_overlap"


def test_build_tier1_orientation_shell_extracts_cards():
    bundle = {
        "present": True,
        "tier": 1,
        "canonical_center": {
            "source_precedence_summary": "canonical > live > derived",
            "current_short_board": {"summary_text": "Phase 768"},
            "successor_correction": {"summary_text": "observer stable != permission"},
        },
        "subsystem_parity": {
            "counts": {"baseline": 2, "beta_usable": 1, "partial": 1, "deferred": 0},
            "families": [
                {
                    "name": "session_start_bundle",
                    "status": "baseline",
                    "main_gap": "none",
                    "next_bounded_move": "hold",
                }
            ],
        },
        "closeout_attention": {
            "present": True,
            "status": "partial",
            "summary_text": "latest closeout is partial",
            "receiver_rule": "read closeout first",
        },
        "observer_shell": {
            "summary_text": "observer ready",
            "receiver_note": "shell only",
            "counts": {"stable": 3, "contested": 1, "stale": 0},
            "stable_headlines": ["launch tier is collaborator_beta"],
            "contested_headlines": ["council confidence is descriptive_only"],
            "stale_headlines": [],
        },
    }

    result = build_tier1_orientation_shell(bundle)

    assert result["canonical_cards"]["short_board"] == "Phase 768"
    assert result["canonical_cards"]["successor_correction"] == "observer stable != permission"
    assert result["parity_counts"]["baseline"] == 2
    assert result["closeout_attention"]["status"] == "partial"
    assert result["observer_shell"]["contested_headlines"] == [
        "council confidence is descriptive_only"
    ]


def test_run_session_start_bundle_parses_json(monkeypatch, tmp_path: Path):
    class FakeResult:
        returncode = 0
        stdout = '{"tier": 0, "present": true, "readiness": {"status": "pass"}}'
        stderr = ""

    def fake_run(command, cwd, capture_output, text, check):
        assert "--tier" in command
        assert cwd == tmp_path
        assert capture_output is True
        assert text is True
        assert check is False
        return FakeResult()

    monkeypatch.setattr("subprocess.run", fake_run)

    result = run_session_start_bundle(agent_id="dashboard-test", tier=0, repo_root=tmp_path)

    assert result["present"] is True
    assert result["tier"] == 0
    assert result["readiness"]["status"] == "pass"
