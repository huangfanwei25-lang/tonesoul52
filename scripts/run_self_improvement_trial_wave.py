#!/usr/bin/env python3
"""Run the first bounded ToneSoul self-improvement trial wave."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the first bounded ToneSoul self-improvement trial wave.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _probe_deliberation_hint(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "start_agent_session.py"),
        "--agent",
        agent,
        "--tier",
        "1",
        "--no-ack",
    ]
    if state_path is not None:
        command.extend(["--state-path", str(state_path)])
    if traces_path is not None:
        command.extend(["--traces-path", str(traces_path)])

    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe failed_to_run={exc}",
        }

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "session-start failed").strip()
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe failed_to_run={message}",
        }

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "present": False,
            "summary_text": f"deliberation_hint_probe invalid_json={exc}",
        }

    hint = dict((payload or {}).get("deliberation_mode_hint") or {})
    active = list(hint.get("active_escalation_signals") or [])
    conditional = list(hint.get("conditional_escalation_triggers") or hint.get("escalation_triggers") or [])
    review_cues = list(hint.get("review_cues") or [])
    split_present = bool(
        isinstance(hint.get("active_escalation_signals"), list)
        and isinstance(hint.get("conditional_escalation_triggers"), list)
        and isinstance(hint.get("review_cues"), list)
    )
    return {
        "present": split_present,
        "summary_text": (
            "deliberation_hint_probe "
            f"mode={str(hint.get('suggested_mode', '') or 'unclassified')} "
            f"active={len(active)} conditional={len(conditional)} review={len(review_cues)} "
            f"split={'yes' if split_present else 'no'}"
        ),
    }


def _probe_task_board_parking(
    *,
    agent: str,
    state_path: Path | None,
    traces_path: Path | None,
) -> dict[str, Any]:
    from scripts.run_task_board_preflight import run_task_board_preflight

    payload = run_task_board_preflight(
        agent=agent,
        proposal_kind="external_idea",
        target_path="task.md",
        state_path=state_path,
        traces_path=traces_path,
    )
    preflight = dict(payload.get("preflight") or {})
    present = bool(
        isinstance(preflight.get("routing_outcome"), str)
        and isinstance(preflight.get("task_md_write_allowed"), bool)
        and isinstance(preflight.get("promotion_posture"), str)
    )
    return {
        "present": present,
        "summary_text": (
            "task_board_probe "
            f"classification={str(preflight.get('classification', '') or 'unknown')} "
            f"write_task_md={'yes' if bool(preflight.get('task_md_write_allowed')) else 'no'} "
            f"promotion={str(preflight.get('promotion_posture', '') or 'unknown')} "
            f"routing={'yes' if present else 'no'}"
        ),
    }


def _probe_shared_edit_preflight() -> dict[str, Any]:
    from tonesoul.shared_edit_preflight import build_shared_edit_preflight

    payload = build_shared_edit_preflight(
        agent_id="trial-wave",
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
        task_track_hint={
            "claim_recommendation": "required",
            "suggested_track": "feature_track",
        },
        mutation_preflight={"summary_text": "shared_code=coordinate_before_shared_edits"},
    )
    present = bool(
        isinstance(payload.get("decision_basis"), str)
        and isinstance(payload.get("other_overlap_paths"), list)
        and isinstance(payload.get("claim_gap_paths"), list)
        and isinstance(payload.get("decision_pressures"), dict)
    )
    return {
        "present": present,
        "summary_text": (
            "shared_edit_probe "
            f"decision={str(payload.get('decision', '') or 'unknown')} "
            f"basis={str(payload.get('decision_basis', '') or 'unknown')} "
            f"other={len(list(payload.get('other_overlap_paths') or []))} "
            f"gaps={len(list(payload.get('claim_gap_paths') or []))} "
            f"pressures={'yes' if isinstance(payload.get('decision_pressures'), dict) else 'no'}"
        ),
    }


def _probe_publish_push_preflight() -> dict[str, Any]:
    from tonesoul.publish_push_preflight import build_publish_push_preflight

    payload = build_publish_push_preflight(
        readiness={"status": "needs_clarification"},
        import_posture={
            "surfaces": {
                "compactions": {
                    "closeout_status": "partial",
                    "receiver_obligation": "must_not_promote",
                    "unresolved_count": 2,
                    "human_input_required": False,
                },
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                        "blocked_overclaims": ["live_shared_memory"],
                    }
                },
            }
        },
        repo_state_awareness={"classification": "baseline_unset"},
    )
    present = bool(
        isinstance(payload.get("decision_basis"), str)
        and isinstance(payload.get("review_cues"), list)
        and isinstance(payload.get("honesty_cues"), list)
        and payload.get("classification") == "review_before_push"
    )
    return {
        "present": present,
        "summary_text": (
            "publish_push_probe "
            f"classification={str(payload.get('classification', '') or 'unknown')} "
            f"basis={str(payload.get('decision_basis', '') or 'unknown')} "
            f"review={len(list(payload.get('review_cues') or []))} "
            f"honesty={len(list(payload.get('honesty_cues') or []))} "
            f"blocked={len(list(payload.get('blocked_reasons') or []))}"
        ),
    }


def _probe_mutation_followup_routing() -> dict[str, Any]:
    from tonesoul.mutation_preflight import build_mutation_preflight

    shared_edit_payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 1},
        task_track_hint={"suggested_track": "feature_track", "claim_recommendation": "required"},
        deliberation_mode_hint={"suggested_mode": "standard_council"},
        import_posture={
            "surfaces": {
                "claims": {},
                "checkpoints": {},
                "compactions": {"receiver_obligation": "should_consider", "closeout_status": ""},
                "subject_refresh": {"receiver_obligation": "must_not_promote"},
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                    }
                },
            }
        },
        canonical_center={"current_short_board": {"present": True}},
        publish_push_preflight={"classification": "review_before_push"},
        task_board_preflight={"classification": "docs_plans_first", "task_md_write_allowed": False},
    )
    publish_payload = build_mutation_preflight(
        readiness={"status": "pass", "claim_conflict_count": 0},
        task_track_hint={"suggested_track": "quick_change", "claim_recommendation": "not_required"},
        deliberation_mode_hint={"suggested_mode": "lightweight_review"},
        import_posture={
            "surfaces": {
                "claims": {},
                "checkpoints": {},
                "compactions": {"receiver_obligation": "should_consider", "closeout_status": ""},
                "subject_refresh": {"receiver_obligation": "must_not_promote"},
                "launch_claims": {
                    "launch_claim_posture": {
                        "current_tier": "collaborator_beta",
                        "public_launch_ready": False,
                    }
                },
            }
        },
        canonical_center={"current_short_board": {"present": True}},
        publish_push_preflight={"classification": "review_before_push"},
        task_board_preflight={"classification": "docs_plans_first", "task_md_write_allowed": False},
    )
    shared_target = str((shared_edit_payload.get("next_followup") or {}).get("target", "")).strip()
    publish_target = str((publish_payload.get("next_followup") or {}).get("target", "")).strip()
    present = (
        shared_target == "shared_code_edit.path_overlap_preflight"
        and publish_target == "publish_push.posture_preflight"
    )
    return {
        "present": present,
        "summary_text": (
            "mutation_followup_probe "
            f"shared_target={shared_target or 'missing'} "
            f"publish_target={publish_target or 'missing'}"
        ),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Self-Improvement Trial Wave",
        "",
        f"**Summary**: `{report.get('summary_text', '')}`",
        "",
        f"> {report.get('receiver_rule', '')}",
        "",
        "## Trial Families",
        "",
    ]
    for family in report.get("trial_families") or []:
        lines.append(f"- `{family}`")
    lines.extend(["", "## Outcomes", ""])
    counts = report.get("outcome_counts") or {}
    for key in ("promote", "park", "retire", "blocked", "not_ready_for_trial"):
        lines.append(f"- `{key}`: `{counts.get(key, 0)}`")
    lines.extend(["", "## Candidates", ""])
    for item in report.get("candidates") or []:
        candidate = item.get("candidate_record") or {}
        closeout = item.get("analyzer_closeout") or {}
        result_surface = item.get("result_surface") or {}
        lines.append(f"- `{candidate.get('candidate_id', 'unknown')}` -> `{closeout.get('status', '')}`")
        lines.append(f"  - target_surface: `{candidate.get('target_surface', '')}`")
        lines.append(f"  - success_metric: `{candidate.get('success_metric', '')}`")
        lines.append(f"  - result_story: {closeout.get('result_story', '')}")
        lines.append(f"  - evidence: `{closeout.get('evidence_bundle_summary', '')}`")
        lines.append(f"  - result_surface: `{result_surface.get('surface_status', '')}`")
        lines.append(f"  - replay_rule: `{result_surface.get('replay_rule', '')}`")
        lines.append(f"  - residue_posture: `{result_surface.get('residue_posture', '')}`")
        unresolved = closeout.get("unresolved_items") or []
        if unresolved:
            lines.append("  - unresolved_items:")
            for unresolved_item in unresolved:
                lines.append(f"    - {unresolved_item}")
        lines.append(f"  - promotion_limit: `{closeout.get('promotion_limit', '')}`")
        lines.append(f"  - next_action: `{closeout.get('next_action', '')}`")
    lines.extend(["", "## Next Short Board", "", f"- `{report.get('next_short_board', '')}`", ""])
    return "\n".join(lines)


def run_self_improvement_trial_wave(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, Any]:
    from scripts.run_consumer_drift_validation_wave import run_consumer_drift_validation_wave
    from tonesoul.self_improvement_trial_wave import build_self_improvement_trial_wave

    consumer_drift_report = run_consumer_drift_validation_wave(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    deliberation_hint_probe = _probe_deliberation_hint(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    task_board_probe = _probe_task_board_parking(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    shared_edit_probe = _probe_shared_edit_preflight()
    publish_push_probe = _probe_publish_push_preflight()
    mutation_followup_probe = _probe_mutation_followup_routing()
    operator_retrieval_contract_present = (
        REPO_ROOT / "docs/architecture/TONESOUL_OPERATOR_RETRIEVAL_QUERY_CONTRACT.md"
    ).exists()
    compiled_landing_zone_spec_present = (
        REPO_ROOT / "docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md"
    ).exists()
    retrieval_runner_present = (REPO_ROOT / "scripts/run_operator_retrieval_query.py").exists()

    return build_self_improvement_trial_wave(
        agent=agent,
        consumer_drift_report=consumer_drift_report,
        deliberation_hint_probe=deliberation_hint_probe,
        task_board_probe=task_board_probe,
        shared_edit_probe=shared_edit_probe,
        publish_push_probe=publish_push_probe,
        mutation_followup_probe=mutation_followup_probe,
        operator_retrieval_contract_present=operator_retrieval_contract_present,
        compiled_landing_zone_spec_present=compiled_landing_zone_spec_present,
        retrieval_runner_present=retrieval_runner_present,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_self_improvement_trial_wave(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
    )
    if args.json_out is not None:
        _write_json(args.json_out, payload)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(_render_markdown(payload), encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
