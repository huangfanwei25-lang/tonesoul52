from __future__ import annotations

from tonesoul.publish_push_preflight import build_publish_push_preflight


def _make_import_posture(
    *,
    closeout_status: str = "",
    receiver_obligation: str = "should_consider",
    unresolved_count: int = 0,
    human_input_required: bool = False,
    current_tier: str = "collaborator_beta",
    public_launch_ready: bool = False,
    blocked_overclaims: list[str] | None = None,
) -> dict:
    return {
        "surfaces": {
            "compactions": {
                "closeout_status": closeout_status,
                "receiver_obligation": receiver_obligation,
                "unresolved_count": unresolved_count,
                "human_input_required": human_input_required,
            },
            "launch_claims": {
                "launch_claim_posture": {
                    "current_tier": current_tier,
                    "public_launch_ready": public_launch_ready,
                    "blocked_overclaims": list(blocked_overclaims or []),
                }
            },
        }
    }


def _make_repo_state(classification: str = "steady") -> dict:
    return {"classification": classification}


def test_publish_push_preflight_blocks_on_blocked_readiness() -> None:
    payload = build_publish_push_preflight(
        readiness={"status": "blocked"},
        import_posture=_make_import_posture(closeout_status="blocked", human_input_required=True),
        repo_state_awareness=_make_repo_state("repo_dirty_without_coordination"),
    )

    assert payload["classification"] == "blocked"
    assert payload["safe_scope"] == "hold_publish"
    assert "readiness_blocked" in payload["blocked_reasons"]
    assert "closeout_blocked" in payload["blocked_reasons"]
    assert "human_input_required" in payload["blocked_reasons"]


def test_publish_push_preflight_requests_review_for_bounded_beta_repo_misread() -> None:
    payload = build_publish_push_preflight(
        readiness={"status": "needs_clarification"},
        import_posture=_make_import_posture(
            closeout_status="partial",
            receiver_obligation="must_not_promote",
            unresolved_count=2,
            current_tier="collaborator_beta",
            public_launch_ready=False,
            blocked_overclaims=["live_shared_memory"],
        ),
        repo_state_awareness=_make_repo_state("baseline_unset"),
    )

    assert payload["classification"] == "review_before_push"
    assert payload["safe_scope"] == "feature_branch_or_guided_beta_only"
    assert "repo_state_baseline_unset" in payload["review_reasons"]
    assert "closeout_partial" in payload["review_reasons"]
    assert "bounded_handoff_must_not_promote" in payload["review_reasons"]
    assert "unresolved_items_visible" in payload["review_reasons"]
    assert "bounded_collaborator_beta_only" in payload["review_reasons"]
    assert "launch_overclaim_boundaries_visible" in payload["review_reasons"]


def test_publish_push_preflight_can_be_clear_when_repo_and_launch_are_clean() -> None:
    payload = build_publish_push_preflight(
        readiness={"status": "pass"},
        import_posture=_make_import_posture(
            closeout_status="complete",
            receiver_obligation="should_consider",
            current_tier="public_launch",
            public_launch_ready=True,
        ),
        repo_state_awareness=_make_repo_state("steady"),
    )

    assert payload["classification"] == "clear"
    assert payload["safe_scope"] == "bounded_branch_push"
    assert payload["blocked_reasons"] == []
    assert payload["review_reasons"] == []
    assert payload["summary_text"].startswith("publish_push=clear repo=steady")
