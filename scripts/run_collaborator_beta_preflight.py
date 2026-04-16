#!/usr/bin/env python3
"""Run a bounded collaborator-beta preflight bundle."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.safe_parse import safe_parse_json  # noqa: E402

START_AGENT_SESSION = REPO_ROOT / "scripts" / "start_agent_session.py"
RUN_PACKET = REPO_ROOT / "scripts" / "run_r_memory_packet.py"
INITIAL_EXTERNAL_CYCLE_PACK = (
    REPO_ROOT / "docs" / "plans" / "tonesoul_non_creator_external_cycle_pack_2026-04-10.md"
)
REPEATED_EXTERNAL_CYCLE_PACK = (
    REPO_ROOT
    / "docs"
    / "plans"
    / "tonesoul_non_creator_external_cycle_dual_surface_pack_2026-04-10.md"
)
PREFLIGHT_REFRESH_EXTERNAL_CYCLE_PACK = (
    REPO_ROOT
    / "docs"
    / "plans"
    / "tonesoul_non_creator_external_cycle_preflight_refresh_pack_2026-04-15.md"
)
WORK_PLAN_V2 = REPO_ROOT / "docs" / "plans" / "tonesoul_work_plan_v2_2026-04-14.md"
PHASE726_REVIEW_ANCHOR = REPO_ROOT / "docs" / "status" / "phase726_go_nogo_2026-04-08.md"
LAUNCH_OPERATIONS_SURFACE_ANCHOR = (
    REPO_ROOT / "docs" / "status" / "phase724_launch_operations_surface_2026-04-15.md"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the current collaborator-beta preflight bundle.",
    )
    parser.add_argument("--agent", default="beta-preflight")
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument(
        "--validation-wave-path",
        type=Path,
        default=REPO_ROOT / "docs" / "status" / "launch_continuity_validation_wave_latest.json",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _normalize_compact_diagnostic(text: str) -> str:
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    filtered = [line for line in lines if not line.startswith("[ToneSoul] Storage:")]
    if filtered:
        return filtered[0]
    if lines:
        return lines[0]
    return ""


def _detect_latest_phase726_review() -> dict[str, Any]:
    status_dir = REPO_ROOT / "docs" / "status"
    candidates = sorted(status_dir.glob("phase726_go_nogo_*.md"))
    if not candidates:
        return {
            "path": PHASE726_REVIEW_ANCHOR.relative_to(REPO_ROOT).as_posix(),
            "is_refreshed": False,
        }
    latest = candidates[-1]
    return {
        "path": latest.relative_to(REPO_ROOT).as_posix(),
        "is_refreshed": latest.name != PHASE726_REVIEW_ANCHOR.name,
    }


def _detect_latest_phase724_surface() -> dict[str, Any]:
    status_dir = REPO_ROOT / "docs" / "status"
    candidates = sorted(status_dir.glob("phase724_launch_operations_surface_*.md"))
    if not candidates:
        return {
            "path": LAUNCH_OPERATIONS_SURFACE_ANCHOR.relative_to(REPO_ROOT).as_posix(),
            "is_refreshed": False,
        }
    latest = candidates[-1]
    return {
        "path": latest.relative_to(REPO_ROOT).as_posix(),
        "is_refreshed": True,
    }


def _extract_compact_signal(text: str, *, prefix: str) -> str:
    for chunk in str(text).split("|"):
        candidate = chunk.strip()
        marker = f"{prefix}="
        if candidate.startswith(marker):
            return candidate[len(marker) :].strip()
    return ""


def _build_public_diagnose_summary(*, compact_diagnostic: str, readiness: str) -> str:
    readiness_value = _extract_compact_signal(compact_diagnostic, prefix="readiness") or readiness
    aegis_value = _extract_compact_signal(compact_diagnostic, prefix="aegis") or "unknown"
    parts = ["embedded_from_session_start"]
    if readiness_value:
        parts.append(f"readiness={readiness_value}")
    if aegis_value:
        parts.append(f"aegis={aegis_value}")
    return " | ".join(parts)


def _parse_json_stdout(stdout: str, *, command: list[str]) -> dict[str, Any]:
    payload = safe_parse_json(stdout)
    if payload is None:
        first_object = stdout.find("{")
        if first_object >= 0:
            payload = safe_parse_json(stdout[first_object:])
    if payload is None:
        preview = stdout.strip().splitlines()
        preview_text = "\n".join(preview[:5])[:400]
        raise ValueError(
            "Could not extract JSON from subprocess stdout for "
            f"{' '.join(command)}. Preview:\n{preview_text}"
        )
    return payload


def _run_json_command(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return _parse_json_stdout(proc.stdout, command=command)


def _run_text_command(command: list[str]) -> str:
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout.strip()


def _load_validation_wave(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _extract_phase722_cycle_date(path: Path) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", path.name)
    return str(match.group(1)) if match else ""


def _detect_external_cycle_status() -> dict[str, str]:
    candidates: list[tuple[str, str, Path]] = []
    for cycle_shape, pattern in (
        ("single_surface", "docs/status/phase722_external_operator_cycle_*.md"),
        ("dual_surface", "docs/status/phase722_external_dual_surface_cycle_*.md"),
        ("preflight_refresh", "docs/status/phase722_external_preflight_refresh_cycle_*.md"),
    ):
        for path in REPO_ROOT.glob(pattern):
            candidates.append((_extract_phase722_cycle_date(path), cycle_shape, path))
    for _, cycle_shape, path in sorted(
        candidates,
        key=lambda item: (item[0], item[2].name),
        reverse=True,
    ):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        match = re.search(r"Result classification:\s*`([^`]+)`", text)
        classification = str(match.group(1)).strip().lower() if match else ""
        if classification:
            return {
                "path": str(path.relative_to(REPO_ROOT).as_posix()),
                "classification": classification,
                "cycle_shape": cycle_shape,
            }
    return {"path": "", "classification": "", "cycle_shape": ""}


def _build_command(
    base: Path, *, agent: str, state_path: Path | None, traces_path: Path | None
) -> list[str]:
    command = [sys.executable, str(base), "--agent", agent]
    if state_path is not None:
        command.extend(["--state-path", str(state_path)])
    if traces_path is not None:
        command.extend(["--traces-path", str(traces_path)])
    return command


def run_preflight(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
    validation_wave_path: Path | None = None,
) -> dict[str, Any]:
    from scripts.start_agent_session import run_session_start_bundle

    start_payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
    )
    # The session-start bundle includes the full packet
    packet_payload = start_payload.get("packet") or {}

    # compact_diagnostic is already available in start_payload — no need to
    # spawn a separate subprocess which can hang on Windows.
    diagnose_mode = "embedded_from_session_start"
    compact_diagnostic = _normalize_compact_diagnostic(start_payload.get("compact_diagnostic", ""))
    readiness_status = str((start_payload.get("readiness") or {}).get("status", "unknown"))
    public_diagnose_summary = _build_public_diagnose_summary(
        compact_diagnostic=compact_diagnostic,
        readiness=readiness_status,
    )

    task_track_hint = start_payload.get("task_track_hint") or {}
    launch_claim_posture = (packet_payload.get("project_memory_summary") or {}).get(
        "launch_claim_posture"
    ) or {}
    coordination_mode = packet_payload.get("coordination_mode") or {}
    evidence_readout = (packet_payload.get("project_memory_summary") or {}).get(
        "evidence_readout_posture"
    ) or {}
    validation_wave = _load_validation_wave(validation_wave_path or Path(""))
    aegis_status = _extract_compact_signal(
        compact_diagnostic, prefix="aegis"
    ) or _extract_compact_signal(
        start_payload.get("compact_diagnostic", ""),
        prefix="aegis",
    )
    claim_recommendation = str(task_track_hint.get("claim_recommendation", "unknown"))
    scope_note = "guided collaborator beta only; file-backed remains launch default and public launch stays deferred"

    blocking_findings: list[str] = []
    if str(launch_claim_posture.get("current_tier", "")) != "collaborator_beta":
        blocking_findings.append("launch_claim_posture.current_tier is not collaborator_beta")
    if bool(launch_claim_posture.get("public_launch_ready", False)):
        blocking_findings.append("public_launch_ready should remain false for current beta posture")
    if str(coordination_mode.get("launch_default_mode", "")) != "file-backed":
        blocking_findings.append("launch_default_mode is not file-backed")
    if not evidence_readout:
        blocking_findings.append("evidence_readout_posture is missing")
    if not validation_wave:
        blocking_findings.append("launch_continuity_validation_wave artifact is missing")

    cautions = [
        str(item.get("claim", "")).strip()
        for item in list(launch_claim_posture.get("blocked_overclaims") or [])
        if str(item.get("claim", "")).strip()
    ]
    if aegis_status == "compromised":
        cautions.append("aegis_compromised")

    max_alert_count = max(
        (int(item.get("receiver_alert_count", 0) or 0) for item in validation_wave), default=0
    )
    contested_dossier_visible = any(
        str(item.get("scenario", "")) == "contested_dossier"
        and str(item.get("council_calibration_status", "")) == "descriptive_only"
        for item in validation_wave
    )
    stale_compaction_guarded = any(
        str(item.get("scenario", "")) == "stale_compaction"
        and str(item.get("compaction_receiver_obligation", "")) == "must_not_promote"
        for item in validation_wave
    )

    overall_ok = not blocking_findings and bool(compact_diagnostic)
    overall_status = "go" if overall_ok else "hold"
    external_cycle_status = _detect_external_cycle_status()
    latest_phase726_review = _detect_latest_phase726_review()
    latest_phase724_surface = _detect_latest_phase724_surface()
    latest_external_classification = external_cycle_status.get("classification", "")
    latest_external_cycle_shape = str(external_cycle_status.get("cycle_shape", "")).strip()
    latest_external_path = str(external_cycle_status.get("path", "")).strip()
    if not latest_external_cycle_shape and latest_external_path:
        if "preflight_refresh" in latest_external_path:
            latest_external_cycle_shape = "preflight_refresh"
        elif "dual_surface" in latest_external_path:
            latest_external_cycle_shape = "dual_surface"
        else:
            latest_external_cycle_shape = "single_surface"
    if (
        latest_external_classification == "strong external pass"
        and latest_external_cycle_shape == "single_surface"
    ):
        next_bounded_move = {
            "step": "run the dual-surface repeated external cycle under a different operator or task shape",
            "path": REPEATED_EXTERNAL_CYCLE_PACK.relative_to(REPO_ROOT).as_posix(),
            "note": (
                "One clean external/non-creator cycle now exists; next repeated validation should exercise one bounded canonical surface plus one fresh status note before widening any launch claims."
            ),
        }
    elif latest_external_classification == "strong external pass":
        if latest_external_cycle_shape == "preflight_refresh":
            if latest_phase726_review.get("is_refreshed"):
                if latest_phase724_surface.get("is_refreshed"):
                    next_bounded_move = {
                        "step": "use the current launch-operations surface as the operator-facing anchor and keep launch claims bounded",
                        "path": str(latest_phase724_surface.get("path", ""))
                        or LAUNCH_OPERATIONS_SURFACE_ANCHOR.relative_to(REPO_ROOT).as_posix(),
                        "note": (
                            "Phase 724 is now consolidated into one current operator-facing launch surface; keep public launch deferred, keep launch claims evidence-bounded, and reopen this lane only if a new contradiction or a higher evidence tier appears."
                        ),
                    }
                else:
                    next_bounded_move = {
                        "step": "consolidate one current launch-operations surface before any claim widening",
                        "path": str(latest_phase724_surface.get("path", ""))
                        or LAUNCH_OPERATIONS_SURFACE_ANCHOR.relative_to(REPO_ROOT).as_posix(),
                        "note": (
                            "The collaborator-beta go/no-go review has already been refreshed against three clean bounded Phase 722 cycles; keep public launch deferred, keep launch claims evidence-bounded, and move into Phase 724 launch-operations consolidation."
                        ),
                    }
            else:
                next_bounded_move = {
                    "step": "refresh the collaborator-beta go/no-go review before any claim widening",
                    "path": str(latest_phase726_review.get("path", ""))
                    or PHASE726_REVIEW_ANCHOR.relative_to(REPO_ROOT).as_posix(),
                    "note": (
                        "A third bounded Phase 722 task shape has now landed cleanly; keep public launch deferred, keep launch claims evidence-bounded, and refresh the Phase 726 collaborator-beta review before changing wording."
                    ),
                }
        else:
            next_bounded_move = {
                "step": "consolidate current-truth launch surfaces, then queue at least one more varied lower-context cycle before any claim widening",
                "path": WORK_PLAN_V2.relative_to(REPO_ROOT).as_posix(),
                "note": (
                    "Phase 722 now has two clean bounded non-creator cycles across two task shapes; refresh current-truth surfaces, keep launch claims bounded, and require at least one more varied lower-context repetition before widening collaborator-beta language."
                ),
            }
    elif latest_external_classification == "useful partial":
        if latest_external_cycle_shape == "preflight_refresh":
            next_bounded_move = {
                "step": "repair the preflight-refresh evidence seam and rerun the third bounded Phase 722 task shape",
                "path": PREFLIGHT_REFRESH_EXTERNAL_CYCLE_PACK.relative_to(REPO_ROOT).as_posix(),
                "note": (
                    "The preflight-refresh task shape entered and regenerated canonical artifacts, but it still stopped short of clean proof; fix the exact blocker and rerun the same bounded pack rather than widening claims."
                ),
            }
        else:
            next_bounded_move = {
                "step": "repair the remaining external-cycle seam and rerun the bounded pack",
                "path": INITIAL_EXTERNAL_CYCLE_PACK.relative_to(REPO_ROOT).as_posix(),
                "note": (
                    "A real external/non-creator attempt exists, but it still counts only as useful partial and should not be treated as clean proof."
                ),
            }
    else:
        next_bounded_move = {
            "step": "run one real non-creator or external-use clean cycle for Phase 722",
            "path": INITIAL_EXTERNAL_CYCLE_PACK.relative_to(REPO_ROOT).as_posix(),
            "note": (
                "Pack exists, but no clean non-creator / external-use governance-aware cycle is yet recorded in canonical status surfaces."
            ),
        }

    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "overall_status": overall_status,
        "repo_root": str(REPO_ROOT),
        "agent": agent,
        "commands": {
            "session_start": f"run_session_start_bundle(agent_id={agent!r})",
            "packet": "extracted from session_start bundle payload['packet']",
            "diagnose": "embedded_from_session_start",
        },
        "entry_stack": {
            "session_start": {
                "ok": True,
                "readiness": readiness_status,
                "task_track": str(task_track_hint.get("suggested_track", "unknown")),
                "claim_recommendation": claim_recommendation,
                "deliberation_mode": str(
                    (start_payload.get("deliberation_mode_hint") or {}).get(
                        "suggested_mode", "unknown"
                    )
                ),
            },
            "packet": {
                "ok": True,
                "launch_default_mode": str(coordination_mode.get("launch_default_mode", "unknown")),
                "launch_alignment": str(coordination_mode.get("launch_alignment", "unknown")),
                "current_tier": str(launch_claim_posture.get("current_tier", "unknown")),
                "next_target_tier": str(launch_claim_posture.get("next_target_tier", "unknown")),
                "public_launch_ready": bool(launch_claim_posture.get("public_launch_ready", False)),
            },
            "diagnose": {
                "ok": bool(compact_diagnostic),
                "mode": diagnose_mode,
                "compact_line": public_diagnose_summary,
                "aegis_status": aegis_status or "unknown",
            },
        },
        "scope_posture": {
            "guided_beta_only": True,
            "launch_default_mode": str(coordination_mode.get("launch_default_mode", "unknown")),
            "public_launch_ready": bool(launch_claim_posture.get("public_launch_ready", False)),
            "scope_note": scope_note,
            "target_reading": "roadmap_target_only",
            "target_note": "next_target_tier names the next maturity target, not current readiness or public-launch permission.",
        },
        "claim_posture": {
            "claim_recommendation": claim_recommendation,
            "claim_trigger": "claim when you are about to edit a shared path; read-only inspection can stay unclaimed",
        },
        "aegis_posture": {
            "status": aegis_status or "unknown",
            "blocks_beta_entry": False,
            "note": "Treat aegis_compromised as a visible caution in the current beta posture, not as an implicit public-launch stop or a reason to ignore the rest of the bounded receiver checks.",
        },
        "external_cycle_status": external_cycle_status,
        "next_bounded_move": next_bounded_move,
        "launch_claim_posture": launch_claim_posture,
        "validation_wave": {
            "present": bool(validation_wave),
            "path": str(validation_wave_path) if validation_wave_path is not None else "",
            "scenario_count": len(validation_wave),
            "scenario_names": [str(item.get("scenario", "")) for item in validation_wave],
            "max_receiver_alert_count": max_alert_count,
            "contested_dossier_visible": contested_dossier_visible,
            "stale_compaction_guarded": stale_compaction_guarded,
        },
        "blocking_findings": blocking_findings,
        "cautions": cautions,
        "summary_text": (
            f"collaborator_beta_preflight={overall_status} "
            f"tier={launch_claim_posture.get('current_tier', 'unknown')} "
            f"backend={coordination_mode.get('launch_default_mode', 'unknown')} "
            f"validation_wave={len(validation_wave)} "
            f"blocked={len(blocking_findings)}"
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    entry = payload.get("entry_stack") or {}
    session_start = entry.get("session_start") or {}
    packet = entry.get("packet") or {}
    diagnose = entry.get("diagnose") or {}
    claim_posture = payload.get("claim_posture") or {}
    scope_posture = payload.get("scope_posture") or {}
    aegis_posture = payload.get("aegis_posture") or {}
    external_cycle_status = payload.get("external_cycle_status") or {}
    next_bounded_move = payload.get("next_bounded_move") or {}
    validation_wave = payload.get("validation_wave") or {}
    launch_claim_posture = payload.get("launch_claim_posture") or {}
    latest_external_cycle = external_cycle_status.get("classification", "") or "none"
    cycle_shape = external_cycle_status.get("cycle_shape", "") or ""
    if cycle_shape:
        latest_external_cycle = f"{latest_external_cycle} / {cycle_shape}"
    lines = [
        "# ToneSoul Collaborator-Beta Preflight",
        "",
        f"> Generated at `{payload.get('generated_at', '')}`.",
        "",
        f"- Overall status: `{payload.get('overall_status', 'unknown')}`",
        f"- Current tier: `{packet.get('current_tier', 'unknown')}`",
        f"- Next target: `{packet.get('next_target_tier', 'unknown')}`",
        f"- Launch-default backend: `{packet.get('launch_default_mode', 'unknown')}`",
        f"- Scope posture: `{scope_posture.get('scope_note', '')}`",
        f"- Target reading: `{scope_posture.get('target_note', '')}`",
        f"- Claim trigger: `{claim_posture.get('claim_trigger', '')}`",
        f"- Aegis posture: `{aegis_posture.get('status', 'unknown')}` / `{aegis_posture.get('note', '')}`",
        f"- Next bounded move: `{next_bounded_move.get('step', '')}`",
        "",
        "## Entry Stack",
        "",
        "| Surface | Status | Key detail |",
        "|---|---|---|",
        (
            f"| session-start | ok | readiness={session_start.get('readiness', 'unknown')} "
            f"track={session_start.get('task_track', 'unknown')} "
            f"claim={session_start.get('claim_recommendation', 'unknown')} "
            f"mode={session_start.get('deliberation_mode', 'unknown')} |"
        ),
        (
            f"| packet | ok | current={packet.get('current_tier', 'unknown')} "
            f"next={packet.get('next_target_tier', 'unknown')} "
            f"backend={packet.get('launch_default_mode', 'unknown')} |"
        ),
        (
            f"| diagnose | {'ok' if diagnose.get('ok') else 'fail'} | "
            f"{str(diagnose.get('compact_line', '')).strip()} "
            f"(aegis={diagnose.get('aegis_status', 'unknown')}) |"
        ),
        "",
        "## Validation Wave",
        "",
        f"- Scenario count: `{int(validation_wave.get('scenario_count', 0) or 0)}`",
        f"- Max receiver alerts: `{int(validation_wave.get('max_receiver_alert_count', 0) or 0)}`",
        f"- Contested dossier visible: `{bool(validation_wave.get('contested_dossier_visible', False))}`",
        f"- Stale compaction guarded: `{bool(validation_wave.get('stale_compaction_guarded', False))}`",
        "",
        "## Claim Posture",
        "",
        f"- Summary: `{launch_claim_posture.get('summary_text', '')}`",
    ]
    if next_bounded_move:
        lines.extend(
            [
                "",
                "## Next Bounded Move",
                "",
                f"- Latest external cycle: `{latest_external_cycle}`",
                f"- Path: `{next_bounded_move.get('path', '')}`",
                f"- Note: `{next_bounded_move.get('note', '')}`",
            ]
        )
    blocked = list(launch_claim_posture.get("blocked_overclaims") or [])
    if blocked:
        lines.extend(["", "### Blocked Overclaims"])
        for item in blocked[:3]:
            lines.append(
                f"- `{item.get('claim', 'unknown')}` = `{item.get('current_classification', 'unknown')}`"
            )
    findings = list(payload.get("blocking_findings") or [])
    if findings:
        lines.extend(["", "## Blocking Findings"])
        lines.extend(f"- {item}" for item in findings)
    else:
        lines.extend(["", "## Blocking Findings", "", "- none"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    payload = run_preflight(
        agent=str(args.agent).strip(),
        state_path=args.state_path,
        traces_path=args.traces_path,
        validation_wave_path=args.validation_wave_path,
    )
    markdown = render_markdown(payload)

    if args.json_out is not None:
        _write_json(args.json_out, payload)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown, encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if bool(payload.get("overall_ok", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
