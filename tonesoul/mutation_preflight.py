"""Successor-facing mutation/write/publish preflight helpers."""

from __future__ import annotations

from typing import Any


def _point(
    name: str,
    *,
    control_type: str,
    posture: str,
    source_of_truth: list[str],
    current_guard: str,
    receiver_note: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "control_type": control_type,
        "posture": posture,
        "source_of_truth": list(source_of_truth),
        "current_guard": current_guard,
        "receiver_note": receiver_note,
    }


def _build_next_followup(
    *,
    shared_code_posture: str,
    publish_push_posture: str,
    task_board_posture: str,
) -> dict[str, str]:
    if shared_code_posture in {
        "blocked",
        "coordinate_before_shared_edits",
        "claim_before_shared_edits",
    }:
        return {
            "target": "shared_code_edit.path_overlap_preflight",
            "classification": "existing_runtime_hook",
            "command": (
                "python scripts/run_shared_edit_preflight.py --agent <your-id> "
                "--path <repo-path>"
            ),
            "reason": (
                "Use the shared-edit preflight first; current readiness or claim pressure says path-level coordination is the shortest side-effect lane."
            ),
            "why_here": (
                "Shared code mutation is the current friction point, so overlap and claim pressure should be resolved before broader publish or board actions."
            ),
        }
    if publish_push_posture in {"blocked", "review_before_push"}:
        return {
            "target": "publish_push.posture_preflight",
            "classification": "existing_runtime_hook",
            "command": "python scripts/run_publish_push_preflight.py --agent <your-id>",
            "reason": (
                "Use the publish/push preflight first; current repo, closeout, or launch posture makes outward-facing side effects the shortest bounded review lane."
            ),
            "why_here": (
                "Publish/push posture is the current friction point, so side-effect review should stay ahead of broader planning changes."
            ),
        }
    if task_board_posture in {"docs_plans_first", "human_review_required"}:
        return {
            "target": "task_board.parking_preflight",
            "classification": "existing_runtime_hook",
            "command": (
                "python scripts/run_task_board_preflight.py --agent <your-id> "
                "--proposal-kind external_idea --target-path task.md"
            ),
            "reason": (
                "Use the bounded task-board preflight before changing task.md; it keeps outside ideas parked in docs/plans until a human or accepted program explicitly ratifies them."
            ),
            "why_here": (
                "Task-board routing is the current friction point, so parking discipline should stay ahead of short-board mutation."
            ),
        }
    return {
        "target": "shared_code_edit.path_overlap_preflight",
        "classification": "existing_runtime_hook",
        "command": (
            "python scripts/run_shared_edit_preflight.py --agent <your-id> " "--path <repo-path>"
        ),
        "reason": (
            "If the next step mutates repo paths, start with the bounded shared-edit preflight rather than assuming local isolation."
        ),
        "why_here": (
            "No stronger mutation friction is visible right now, so shared-edit overlap remains the narrowest reusable hook."
        ),
    }


def build_mutation_preflight(
    *,
    readiness: dict[str, Any],
    task_track_hint: dict[str, Any],
    deliberation_mode_hint: dict[str, Any],
    import_posture: dict[str, Any],
    canonical_center: dict[str, Any],
    publish_push_preflight: dict[str, Any] | None = None,
    task_board_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bounded mutation/write/publish guard map for successors."""
    surfaces = import_posture.get("surfaces") or {}
    claims_surface = surfaces.get("claims") or {}
    checkpoints_surface = surfaces.get("checkpoints") or {}
    compactions_surface = surfaces.get("compactions") or {}
    subject_refresh_surface = surfaces.get("subject_refresh") or {}
    launch_claims_surface = surfaces.get("launch_claims") or {}
    launch_claim_posture = launch_claims_surface.get("launch_claim_posture") or {}
    publish_push_preflight = dict(publish_push_preflight or {})
    task_board_preflight = dict(task_board_preflight or {})

    readiness_status = str(readiness.get("status", "unknown") or "unknown")
    claim_conflict_count = int(readiness.get("claim_conflict_count", 0) or 0)
    claim_recommendation = str(task_track_hint.get("claim_recommendation", "unknown") or "unknown")
    suggested_track = str(task_track_hint.get("suggested_track", "unclassified") or "unclassified")
    suggested_mode = str(
        deliberation_mode_hint.get("suggested_mode", "unclassified") or "unclassified"
    )
    short_board_present = bool((canonical_center.get("current_short_board") or {}).get("present"))

    if readiness_status == "blocked":
        shared_code_posture = "blocked"
        shared_code_note = "Do not start shared-path edits until blocking reasons clear."
    elif claim_conflict_count > 0:
        shared_code_posture = "coordinate_before_shared_edits"
        shared_code_note = (
            "Visible claim collisions mean path overlap must be coordinated before any shared edit."
        )
    elif claim_recommendation == "required":
        shared_code_posture = "claim_before_shared_edits"
        shared_code_note = (
            "Feature/system-track work should claim shared paths before mutating repo state."
        )
    else:
        shared_code_posture = "bounded_local_edit_first"
        shared_code_note = "Local bounded edits may start without a claim, but claim before crossing into shared paths."

    compaction_obligation = str(
        compactions_surface.get("receiver_obligation", "unknown") or "unknown"
    )
    compaction_closeout = str(compactions_surface.get("closeout_status", "") or "").strip()
    if compaction_obligation == "must_not_promote":
        compaction_posture = "review_only_handoff"
    elif compaction_closeout in {"partial", "blocked", "underdetermined"}:
        compaction_posture = "honest_closeout_required"
    else:
        compaction_posture = "bounded_resumability_handoff"

    subject_refresh_posture = str(
        subject_refresh_surface.get("receiver_obligation", "must_not_promote") or "must_not_promote"
    )

    current_tier = str(launch_claim_posture.get("current_tier", "") or "").strip()
    public_launch_ready = bool(launch_claim_posture.get("public_launch_ready", False))
    if current_tier == "collaborator_beta" and not public_launch_ready:
        launch_claim_language_posture = "bounded_collaborator_beta_only"
    elif current_tier == "internal_alpha":
        launch_claim_language_posture = "internal_alpha_only"
    else:
        launch_claim_language_posture = "deferred_or_unknown"

    publish_push_posture = str(
        publish_push_preflight.get("classification", "review_before_push") or "review_before_push"
    )
    task_board_classification = str(
        task_board_preflight.get("classification", "human_review") or "human_review"
    )
    task_board_write_allowed = bool(task_board_preflight.get("task_md_write_allowed", False))
    if task_board_classification == "task_md_allowed" and task_board_write_allowed:
        task_board_posture = "ratified_followthrough_only"
    elif task_board_classification in {"docs_plans_first", "parking_clear"}:
        task_board_posture = "docs_plans_first"
    else:
        task_board_posture = "human_review_required"

    decision_points = [
        _point(
            "shared_code_edit",
            control_type="existing_runtime_hook",
            posture=shared_code_posture,
            source_of_truth=["readiness", "claim_view", "task_track_hint"],
            current_guard=(
                "Resolve readiness first, then run run_shared_edit_preflight.py before touching shared paths."
            ),
            receiver_note=shared_code_note,
        ),
        _point(
            "claim_write",
            control_type="existing_runtime_hook",
            posture=(
                "expected_on_shared_paths"
                if claim_recommendation == "required"
                else "optional_when_local"
            ),
            source_of_truth=[
                "import_posture.surfaces.claims",
                "task_track_hint.claim_recommendation",
            ],
            current_guard="TTL-backed coordination lock via run_task_claim.py.",
            receiver_note=str(
                claims_surface.get("note", "")
                or "Claims are live coordination signals, not durable permissions."
            ),
        ),
        _point(
            "checkpoint_write",
            control_type="guarded_readout",
            posture="bounded_noncanonical",
            source_of_truth=["import_posture.surfaces.checkpoints"],
            current_guard="Checkpoint next_action can guide resumability but never becomes canonical planning truth.",
            receiver_note=str(
                checkpoints_surface.get("note", "")
                or "Use checkpoints for mid-session resumability, not governance truth."
            ),
        ),
        _point(
            "compaction_write",
            control_type="existing_runtime_hook",
            posture=compaction_posture,
            source_of_truth=["import_posture.surfaces.compactions", "closeout_grammar"],
            current_guard=(
                "Carry-forward stays bounded to resumability and must preserve complete/partial/blocked/underdetermined honestly."
            ),
            receiver_note=str(
                compactions_surface.get("note", "")
                or "Compactions orient resumability only; incomplete closeout must remain visible."
            ),
        ),
        _point(
            "subject_refresh_write",
            control_type="existing_runtime_hook",
            posture=subject_refresh_posture,
            source_of_truth=["import_posture.surfaces.subject_refresh"],
            current_guard=(
                "Only the bounded active_threads compaction-backed path may refresh directly; higher-authority identity fields remain no-promote."
            ),
            receiver_note=str(
                subject_refresh_surface.get("note", "")
                or "Subject refresh may influence review but must not silently promote identity."
            ),
        ),
        _point(
            "task_board_update",
            control_type="human_gated",
            posture=task_board_posture,
            source_of_truth=["task.md", "canonical_center.current_short_board"],
            current_guard=(
                "task.md tracks only accepted programs and ratified short boards; run run_task_board_preflight.py before changing task.md and keep outside ideas in docs/plans until explicitly ratified."
            ),
            receiver_note=str(
                task_board_preflight.get("receiver_note", "")
                or (
                    "The short board is visible and human-managed."
                    if short_board_present
                    else "Do not mutate task.md blindly while the current short board is not visible."
                )
            ),
        ),
        _point(
            "canonical_commit",
            control_type="existing_runtime_hook",
            posture="aegis_locked_commit",
            source_of_truth=["tonesoul.runtime_adapter.commit"],
            current_guard=(
                "commit() acquires the Aegis commit lock and checks the trace before mutating governance state."
            ),
            receiver_note=(
                "Canonical commit is guarded in runtime, not by observer prose; keep trace and commit surfaces honest."
            ),
        ),
        _point(
            "launch_claim_language",
            control_type="guarded_readout",
            posture=launch_claim_language_posture,
            source_of_truth=["import_posture.surfaces.launch_claims"],
            current_guard=(
                "Launch wording is bounded by launch_claim_posture; collaborator-beta is the current safe tier and public-launch remains deferred."
            ),
            receiver_note=str(
                launch_claim_posture.get("receiver_rule", "")
                or "Launch claim language is a wording guard, not a runtime permission surface."
            ),
        ),
        _point(
            "publish_push",
            control_type="existing_runtime_hook",
            posture=publish_push_posture,
            source_of_truth=["repo_state_awareness", "launch_claim_posture", "compaction_closeout"],
            current_guard=(
                "Run run_publish_push_preflight.py before git push, deployment, or other outward-facing publish actions."
            ),
            receiver_note=str(
                publish_push_preflight.get("receiver_note", "")
                or "Publish/push posture should stay bounded by repo-state, closeout, and launch honesty surfaces."
            ),
        ),
    ]

    next_followup = _build_next_followup(
        shared_code_posture=shared_code_posture,
        publish_push_posture=publish_push_posture,
        task_board_posture=task_board_posture,
    )

    return {
        "present": True,
        "summary_text": (
            f"shared_code={shared_code_posture} "
            f"compaction={compaction_posture} "
            f"task_board={task_board_posture} "
            f"commit=aegis_locked_commit "
            f"launch_claims={launch_claim_language_posture} "
            f"publish_push={publish_push_posture}"
        ),
        "receiver_rule": (
            "Readiness and live coordination gate shared mutation first; use the narrowest write lane available, keep closeout honest, and treat launch wording as separate from execution permission."
        ),
        "decision_points": decision_points,
        "next_followup": next_followup,
        "current_context": {
            "readiness_status": readiness_status,
            "task_track": suggested_track,
            "deliberation_mode": suggested_mode,
            "claim_conflict_count": claim_conflict_count,
        },
    }
