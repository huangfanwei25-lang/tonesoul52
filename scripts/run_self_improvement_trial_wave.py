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
