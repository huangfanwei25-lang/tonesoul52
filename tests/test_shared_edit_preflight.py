from __future__ import annotations

from tonesoul.shared_edit_preflight import build_shared_edit_preflight


def test_shared_edit_preflight_blocks_when_readiness_is_blocked() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["tonesoul/runtime_adapter.py"],
        readiness={"status": "blocked"},
        claims=[],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=blocked"},
    )

    assert payload["decision"] == "blocked"
    assert payload["decision_basis"] == "blocked_readiness"
    assert payload["decision_pressures"]["blocked_readiness"] is True
    assert payload["receiver_rule"].startswith("Readiness is blocked")


def test_shared_edit_preflight_coordinates_on_other_agent_overlap() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["tonesoul/runtime_adapter.py"],
        readiness={"status": "needs_clarification"},
        claims=[
            {
                "task_id": "task-1",
                "agent": "other-agent",
                "summary": "hold runtime lane",
                "paths": ["tonesoul/runtime_adapter.py"],
            }
        ],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=coordinate_before_shared_edits"},
    )

    assert payload["decision"] == "coordinate"
    assert payload["decision_basis"] == "other_agent_overlap"
    assert payload["overlap_count"] == 1
    assert payload["other_overlap_paths"] == ["tonesoul/runtime_adapter.py"]
    assert payload["claim_gap_paths"] == ["tonesoul/runtime_adapter.py"]
    assert payload["overlaps"][0]["ownership"] == "other"
    assert payload["recommended_command"] == "python scripts/run_task_claim.py list"


def test_shared_edit_preflight_requires_claim_when_feature_track_has_no_self_claim() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["scripts/start_agent_session.py", "tests/test_start_agent_session.py"],
        readiness={"status": "pass"},
        claims=[],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=claim_before_shared_edits"},
    )

    assert payload["decision"] == "claim_first"
    assert payload["decision_basis"] == "missing_self_claim_coverage"
    assert payload["claim_gap_paths"] == [
        "scripts/start_agent_session.py",
        "tests/test_start_agent_session.py",
    ]
    assert '--path "scripts/start_agent_session.py"' in payload["recommended_command"]
    assert '--path "tests/test_start_agent_session.py"' in payload["recommended_command"]


def test_shared_edit_preflight_clears_when_self_claim_covers_candidate_paths() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["tonesoul/runtime_adapter.py", "tonesoul/runtime_adapter.py"],
        readiness={"status": "pass"},
        claims=[
            {
                "task_id": "task-self",
                "agent": "codex",
                "summary": "hold runtime lane",
                "paths": ["tonesoul/runtime_adapter.py"],
            }
        ],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=claim_before_shared_edits"},
    )

    assert payload["decision"] == "clear"
    assert payload["decision_basis"] == "self_claim_covers_all"
    assert payload["self_claim_covers_all"] is True
    assert payload["claim_gap_paths"] == []
    assert payload["other_overlap_paths"] == []
    assert payload["overlaps"][0]["ownership"] == "self"


def test_shared_edit_preflight_treats_parent_child_paths_as_overlap() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["tonesoul\\council"],
        readiness={"status": "needs_clarification"},
        claims=[
            {
                "task_id": "task-parent",
                "agent": "other-agent",
                "summary": "hold dossier lane",
                "paths": ["tonesoul/council/dossier.py"],
            }
        ],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=coordinate_before_shared_edits"},
    )

    assert payload["decision"] == "coordinate"
    assert payload["normalized_candidate_paths"] == ["tonesoul/council"]
    assert payload["overlaps"][0]["overlap_paths"] == ["tonesoul/council"]
    assert payload["other_overlap_paths"] == ["tonesoul/council"]


def test_shared_edit_preflight_keeps_overlap_and_claim_gap_visible_together() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["tonesoul/runtime_adapter.py", "scripts/start_agent_session.py"],
        readiness={"status": "pass"},
        claims=[
            {
                "task_id": "task-other",
                "agent": "other-agent",
                "summary": "hold runtime lane",
                "paths": ["tonesoul/runtime_adapter.py"],
            }
        ],
        task_track_hint={"claim_recommendation": "required", "suggested_track": "feature_track"},
        mutation_preflight={"summary_text": "shared_code=coordinate_before_shared_edits"},
    )

    assert payload["decision"] == "coordinate"
    assert payload["decision_basis"] == "other_agent_overlap"
    assert payload["decision_pressures"] == {
        "blocked_readiness": False,
        "other_agent_overlap": True,
        "missing_self_claim_coverage": True,
    }
    assert payload["other_overlap_paths"] == ["tonesoul/runtime_adapter.py"]
    assert payload["claim_gap_paths"] == [
        "tonesoul/runtime_adapter.py",
        "scripts/start_agent_session.py",
    ]
    assert "basis=other_agent_overlap" in payload["summary_text"]
    assert "other=1" in payload["summary_text"]
    assert "gaps=2" in payload["summary_text"]


def test_shared_edit_preflight_carries_bounded_working_style_consumer() -> None:
    payload = build_shared_edit_preflight(
        agent_id="codex",
        candidate_paths=["task.md"],
        readiness={"status": "pass"},
        claims=[],
        task_track_hint={"claim_recommendation": "optional", "suggested_track": "quick_change"},
        mutation_preflight={"summary_text": "shared_code=clear"},
        working_style_playbook={
            "present": True,
            "summary_text": "Preference: scan canonical first",
            "checklist": [
                "Preference: scan canonical first",
                "Routine: verify before overclaiming",
                "Prompt default: keep P0/P1/P2 explicit",
            ],
            "application_rule": "Apply these items as bounded operating habits for scan order, evidence handling, and prompt shape.",
            "non_promotion_rule": "Do not promote this playbook into vows, canonical rules, or durable identity without fresh evidence and explicit review.",
        },
    )

    consumer = payload["working_style_consumer"]
    assert consumer["present"] is True
    assert consumer["selected_habits"] == [
        "Preference: scan canonical first",
        "Routine: verify before overclaiming",
    ]
    assert consumer["application_rule"].startswith("Apply these items as bounded operating habits")
    assert "style=yes" in payload["summary_text"]
