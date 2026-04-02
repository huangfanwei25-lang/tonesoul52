from __future__ import annotations

from tonesoul.repo_state_awareness import build_repo_state_awareness


def _build_awareness(
    *,
    repo_head: str = "abc123",
    dirty_count: int = 0,
    first_observation: bool = False,
    repo_changed: bool = False,
    new_compactions: int = 0,
    new_checkpoints: int = 0,
    new_traces: int = 0,
    new_claims: int = 0,
) -> dict:
    return build_repo_state_awareness(
        project_memory_summary={
            "repo_progress": {
                "head": repo_head,
                "dirty_count": dirty_count,
            }
        },
        delta_feed={
            "first_observation": first_observation,
            "new_compactions": [{"id": f"c{i}"} for i in range(new_compactions)],
            "new_subject_snapshots": [],
            "new_checkpoints": [{"id": f"ck{i}"} for i in range(new_checkpoints)],
            "new_traces": [{"id": f"t{i}"} for i in range(new_traces)],
            "new_claims": [{"id": f"n{i}"} for i in range(new_claims)],
            "released_claim_ids": [],
            "repo_change": {
                "changed": repo_changed,
                "previous_head": "old111",
                "current_head": repo_head,
                "previous_dirty_count": 0,
                "current_dirty_count": dirty_count,
            },
        },
    )


def test_repo_state_awareness_flags_missing_baseline() -> None:
    awareness = _build_awareness(first_observation=True)

    assert awareness["classification"] == "baseline_unset"
    assert awareness["misread_risk"] is True
    assert "No observer baseline exists yet" in awareness["receiver_note"]


def test_repo_state_awareness_flags_repo_change_without_coordination() -> None:
    awareness = _build_awareness(repo_changed=True)

    assert awareness["classification"] == "repo_changed_without_coordination"
    assert awareness["misread_risk"] is True
    assert awareness["coordination_update_count"] == 0


def test_repo_state_awareness_flags_dirty_repo_without_coordination() -> None:
    awareness = _build_awareness(dirty_count=3)

    assert awareness["classification"] == "repo_dirty_without_coordination"
    assert awareness["misread_risk"] is True
    assert awareness["dirty_count"] == 3


def test_repo_state_awareness_reports_steady_when_quiet() -> None:
    awareness = _build_awareness()

    assert awareness["classification"] == "steady"
    assert awareness["misread_risk"] is False
    assert awareness["coordination_update_count"] == 0
