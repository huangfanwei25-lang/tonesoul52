"""Bounded publish/push posture preflight helpers."""

from __future__ import annotations

from typing import Any


def build_publish_push_preflight(
    *,
    readiness: dict[str, Any],
    import_posture: dict[str, Any],
    repo_state_awareness: dict[str, Any],
) -> dict[str, Any]:
    """Classify outward publish/push posture from visible bounded surfaces."""

    surfaces = import_posture.get("surfaces") or {}
    compactions_surface = surfaces.get("compactions") or {}
    launch_claims_surface = surfaces.get("launch_claims") or {}
    launch_claim_posture = launch_claims_surface.get("launch_claim_posture") or {}

    readiness_status = str(readiness.get("status", "unknown") or "unknown")
    repo_classification = str(repo_state_awareness.get("classification", "unknown") or "unknown")
    closeout_status = str(compactions_surface.get("closeout_status", "") or "").strip()
    receiver_obligation = str(
        compactions_surface.get("receiver_obligation", "unknown") or "unknown"
    )
    unresolved_count = int(compactions_surface.get("unresolved_count", 0) or 0)
    human_input_required = bool(compactions_surface.get("human_input_required", False))
    current_tier = str(launch_claim_posture.get("current_tier", "unknown") or "unknown")
    public_launch_ready = bool(launch_claim_posture.get("public_launch_ready", False))
    blocked_overclaims = list(launch_claim_posture.get("blocked_overclaims") or [])

    blocked_reasons: list[str] = []
    review_cues: list[str] = []
    honesty_cues: list[str] = []

    if readiness_status == "blocked":
        blocked_reasons.append("readiness_blocked")
    if closeout_status in {"blocked", "underdetermined"}:
        blocked_reasons.append(f"closeout_{closeout_status}")
    if human_input_required:
        blocked_reasons.append("human_input_required")

    if repo_classification in {
        "baseline_unset",
        "repo_changed_without_coordination",
        "repo_dirty_without_coordination",
    }:
        review_cues.append(f"repo_state_{repo_classification}")
    if closeout_status == "partial":
        review_cues.append("closeout_partial")
    if receiver_obligation == "must_not_promote":
        review_cues.append("bounded_handoff_must_not_promote")
    if unresolved_count > 0:
        review_cues.append("unresolved_items_visible")
    if current_tier == "collaborator_beta" and not public_launch_ready:
        honesty_cues.append("bounded_collaborator_beta_only")
    elif current_tier == "internal_alpha":
        honesty_cues.append("internal_alpha_only")
    elif current_tier not in {"public_launch", "unknown"}:
        honesty_cues.append(f"tier_{current_tier}")
    if blocked_overclaims:
        honesty_cues.append("launch_overclaim_boundaries_visible")

    review_reasons = review_cues + honesty_cues

    if blocked_reasons:
        decision_basis = "blocked_reasons_present"
    elif review_cues and honesty_cues:
        decision_basis = "review_and_honesty_cues_present"
    elif review_cues:
        decision_basis = "review_cues_present"
    elif honesty_cues:
        decision_basis = "honesty_cues_present"
    else:
        decision_basis = "no_visible_publish_friction"

    if blocked_reasons:
        classification = "blocked"
        safe_scope = "hold_publish"
        receiver_note = (
            "Do not push or publish outward-facing changes yet. Clear the blocked readiness/closeout "
            "condition before taking a side-effectful action."
        )
    elif review_reasons:
        classification = "review_before_push"
        safe_scope = "feature_branch_or_guided_beta_only"
        receiver_note = (
            "A side-effectful publish action needs review first. The visible repo, launch, or handoff "
            "signals are not bad enough to hard-stop, but they are not clear enough for an automatic push posture."
        )
    else:
        classification = "clear"
        safe_scope = "bounded_branch_push"
        receiver_note = (
            "Visible repo, handoff, and launch signals are clear enough for a bounded push posture. "
            "Keep public claim language within the current launch tier."
        )

    return {
        "present": True,
        "classification": classification,
        "safe_scope": safe_scope,
        "readiness_status": readiness_status,
        "repo_state_classification": repo_classification,
        "closeout_status": closeout_status or "complete",
        "current_tier": current_tier,
        "public_launch_ready": public_launch_ready,
        "decision_basis": decision_basis,
        "blocked_reasons": blocked_reasons,
        "review_cues": review_cues,
        "honesty_cues": honesty_cues,
        "review_reasons": review_reasons,
        "summary_text": (
            f"publish_push={classification} basis={decision_basis} repo={repo_classification} "
            f"closeout={closeout_status or 'complete'} tier={current_tier} "
            f"review={len(review_cues)} honesty={len(honesty_cues)} blocked={len(blocked_reasons)}"
        ),
        "receiver_note": receiver_note,
        "recommended_command": "python scripts/run_publish_push_preflight.py --agent <your-id>",
        "non_authority_rule": (
            "Publish/push posture is a bounded side-effect guard. It does not replace human judgment, "
            "canonical planning, or launch-tier evidence boundaries."
        ),
    }
