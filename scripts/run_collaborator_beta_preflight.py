#!/usr/bin/env python3
"""Run a bounded collaborator-beta preflight bundle."""

from __future__ import annotations

import argparse
import json
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


def _extract_compact_signal(text: str, *, prefix: str) -> str:
    for chunk in str(text).split("|"):
        candidate = chunk.strip()
        marker = f"{prefix}="
        if candidate.startswith(marker):
            return candidate[len(marker) :].strip()
    return ""


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


def _build_command(base: Path, *, agent: str, state_path: Path | None, traces_path: Path | None) -> list[str]:
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
    start_command = _build_command(
        START_AGENT_SESSION,
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    ) + ["--no-ack"]
    packet_command = _build_command(
        RUN_PACKET,
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )

    start_payload = _run_json_command(start_command)
    packet_payload = _run_json_command(packet_command)

    diagnose_mode = "compact_subprocess"
    diagnose_command = [sys.executable, "-m", "tonesoul.diagnose", "--compact", "--agent", agent]
    if state_path is None and traces_path is None:
        compact_diagnostic = _normalize_compact_diagnostic(_run_text_command(diagnose_command))
    else:
        diagnose_mode = "embedded_from_session_start"
        compact_diagnostic = _normalize_compact_diagnostic(start_payload.get("compact_diagnostic", ""))

    task_track_hint = start_payload.get("task_track_hint") or {}
    launch_claim_posture = (
        ((packet_payload.get("project_memory_summary") or {}).get("launch_claim_posture") or {})
    )
    coordination_mode = packet_payload.get("coordination_mode") or {}
    evidence_readout = (
        ((packet_payload.get("project_memory_summary") or {}).get("evidence_readout_posture") or {})
    )
    validation_wave = _load_validation_wave(validation_wave_path or Path(""))
    aegis_status = _extract_compact_signal(compact_diagnostic, prefix="aegis") or _extract_compact_signal(
        start_payload.get("compact_diagnostic", ""),
        prefix="aegis",
    )
    claim_recommendation = str(task_track_hint.get("claim_recommendation", "unknown"))
    scope_note = (
        "guided collaborator beta only; file-backed remains launch default and public launch stays deferred"
    )

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

    max_alert_count = max((int(item.get("receiver_alert_count", 0) or 0) for item in validation_wave), default=0)
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

    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "overall_status": overall_status,
        "repo_root": str(REPO_ROOT),
        "agent": agent,
        "commands": {
            "session_start": " ".join(start_command),
            "packet": " ".join(packet_command),
            "diagnose": " ".join(diagnose_command) if diagnose_mode == "compact_subprocess" else "embedded_from_session_start",
        },
        "entry_stack": {
            "session_start": {
                "ok": True,
                "readiness": str((start_payload.get("readiness") or {}).get("status", "unknown")),
                "task_track": str(task_track_hint.get("suggested_track", "unknown")),
                "claim_recommendation": claim_recommendation,
                "deliberation_mode": str(
                    (start_payload.get("deliberation_mode_hint") or {}).get("suggested_mode", "unknown")
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
                "compact_line": compact_diagnostic,
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
    validation_wave = payload.get("validation_wave") or {}
    launch_claim_posture = payload.get("launch_claim_posture") or {}
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
