#!/usr/bin/env python3
"""Dry-run external trigger reducer for ToneSoul operator decisions.

This runner does not query GitHub, start beta sessions, or write memory.
It accepts explicitly labeled rehearsal events and reduces them into
next_actions / blockers / no-op reasons so operators can test decision
logic without promoting simulated events into evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_FILENAME = "external_trigger_rehearsal_latest.json"
MARKDOWN_FILENAME = "external_trigger_rehearsal_latest.md"

COUNTABLE_SESSION_CLASSIFICATIONS = {
    "clean_pass",
    "usable_with_friction",
    "blocked_by_governance",
    "blocked_by_product_surface",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _normalize_event_type(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def _normalize_pr_number(value: Any) -> str:
    text = str(value or "").strip()
    return text[1:] if text.startswith("#") else text


def _is_known_master_lint_debt(event: dict[str, Any]) -> bool:
    status = str(event.get("status") or event.get("conclusion") or "").strip().lower()
    classification = str(event.get("classification") or event.get("reason") or "").strip().lower()
    return status in {"red", "failure", "failed"} and classification in {
        "known_master_lint_debt_only",
        "master_lint_debt_only",
        "inherited_lint_debt",
    }


def load_events(path: Path) -> list[dict[str, Any]]:
    """Load events from JSON array, {"events": [...]}, or JSONL."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        events: list[dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if isinstance(item, dict):
                events.append(item)
        return events

    if isinstance(payload, dict):
        payload = payload.get("events", [])
    if not isinstance(payload, list):
        raise ValueError("event fixture must be a JSON list, JSONL, or object with an events list")
    return [item for item in payload if isinstance(item, dict)]


def reduce_events(events: list[dict[str, Any]], *, memory_threshold: int = 3) -> dict[str, Any]:
    merged_prs: set[str] = set()
    ci_debt_events: list[dict[str, Any]] = []
    ci_blockers: list[str] = []
    countable_sessions: list[dict[str, Any]] = []
    no_count_sessions: list[dict[str, Any]] = []
    memory_cases: list[dict[str, Any]] = []

    for event in events:
        event_type = _normalize_event_type(event.get("type"))
        if event_type == "pr_merged":
            merged_prs.add(_normalize_pr_number(event.get("number") or event.get("pr")))
            continue
        if event_type in {"ci_completed", "ci_result"}:
            if _is_known_master_lint_debt(event):
                ci_debt_events.append(event)
            else:
                status = str(event.get("status") or event.get("conclusion") or "").strip().lower()
                if status in {"red", "failure", "failed"}:
                    ci_blockers.append(
                        str(
                            event.get("reason")
                            or event.get("classification")
                            or "unknown_ci_failure"
                        )
                    )
            continue
        if event_type == "beta_session_recorded":
            classification = str(event.get("classification") or "").strip().lower()
            if classification in COUNTABLE_SESSION_CLASSIFICATIONS:
                countable_sessions.append(event)
            else:
                no_count_sessions.append(event)
            continue
        if event_type == "memory_inflation_case":
            if bool(event.get("non_obvious", True)) and not bool(event.get("duplicate", False)):
                memory_cases.append(event)

    pr_stack_ready = {"32", "33"}.issubset(merged_prs)
    day6_ready = len(countable_sessions) >= 3
    memory_gate_ready = len(memory_cases) >= int(memory_threshold)

    blocked_by: list[str] = []
    no_op_reasons: list[str] = []
    next_actions: list[dict[str, str]] = []

    if ci_blockers:
        blocked_by.extend(f"ci:{reason}" for reason in ci_blockers)
    elif ci_debt_events:
        no_op_reasons.append("ci_red_is_known_master_lint_debt_only")

    if ci_blockers:
        next_actions.append(
            {
                "id": "day1_start",
                "status": "blocked",
                "action": "do not start Day 1 until unknown CI failures are resolved",
                "rationale": "PR #32/#33 readiness cannot override active CI blockers.",
            }
        )
    elif pr_stack_ready:
        next_actions.append(
            {
                "id": "day1_start",
                "status": "ready",
                "action": "start Day 1 with strategy_mirror scan=True/enforce=False",
                "rationale": "PR #32 and PR #33 are both marked merged in rehearsal events.",
            }
        )
    else:
        missing = sorted({"32", "33"} - merged_prs)
        blocked_by.append("missing_pr_merge:" + ",".join(missing))
        next_actions.append(
            {
                "id": "day1_start",
                "status": "blocked",
                "action": "wait for #32 and #33 to merge before Day 1 starts",
                "rationale": "Required stacked PR merge events are absent.",
            }
        )

    if day6_ready:
        next_actions.append(
            {
                "id": "day6_consolidation",
                "status": "ready",
                "action": "allow Day 6 evidence consolidation",
                "rationale": "At least 3 countable beta session records are present.",
            }
        )
    else:
        next_actions.append(
            {
                "id": "day6_consolidation",
                "status": "blocked",
                "action": "collect more countable beta session records",
                "rationale": f"{len(countable_sessions)} countable sessions present; 3 required.",
            }
        )

    if memory_gate_ready:
        next_actions.append(
            {
                "id": "memory_admission_gate",
                "status": "ready",
                "action": "draft memory admission gate spec outside memory entries",
                "rationale": (
                    f"{len(memory_cases)} non-obvious non-duplicate memory inflation cases "
                    f"meet threshold {int(memory_threshold)}."
                ),
            }
        )
    else:
        next_actions.append(
            {
                "id": "memory_admission_gate",
                "status": "blocked",
                "action": "do not write memory admission gate yet",
                "rationale": (
                    f"{len(memory_cases)} qualifying memory inflation cases present; "
                    f"{int(memory_threshold)} required."
                ),
            }
        )

    if no_count_sessions:
        no_op_reasons.append(f"{len(no_count_sessions)} beta sessions are inconclusive/no-count")

    return {
        "generated_at": _iso_now(),
        "mode": "rehearsal",
        "is_real_evidence": False,
        "event_count": len(events),
        "summary": {
            "merged_prs": sorted(merged_prs),
            "known_ci_debt_events": len(ci_debt_events),
            "countable_beta_sessions": len(countable_sessions),
            "no_count_beta_sessions": len(no_count_sessions),
            "qualifying_memory_inflation_cases": len(memory_cases),
            "memory_threshold": int(memory_threshold),
        },
        "evidence_status": {
            "status": "synthetic_rehearsal_only",
            "rule": "Use this artifact to test next-action logic; do not cite it as external evidence.",
        },
        "next_actions": next_actions,
        "blocked_by": blocked_by,
        "no_op_reasons": no_op_reasons,
        "events": events,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    lines: list[str] = [
        "# External Trigger Rehearsal Latest",
        "",
        f"- generated_at: `{payload.get('generated_at', '')}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- real_evidence: `{bool(payload.get('is_real_evidence'))}`",
        f"- event_count: `{payload.get('event_count', 0)}`",
        "",
        "## Evidence Status",
        f"- status: `{(payload.get('evidence_status') or {}).get('status', '')}`",
        f"- rule: {(payload.get('evidence_status') or {}).get('rule', '')}",
        "",
        "## Summary",
        f"- merged PRs: `{', '.join(summary.get('merged_prs', [])) or 'none'}`",
        f"- known CI debt events: `{summary.get('known_ci_debt_events', 0)}`",
        f"- countable beta sessions: `{summary.get('countable_beta_sessions', 0)}`",
        f"- no-count beta sessions: `{summary.get('no_count_beta_sessions', 0)}`",
        (
            "- qualifying memory inflation cases: "
            f"`{summary.get('qualifying_memory_inflation_cases', 0)}` / "
            f"`{summary.get('memory_threshold', 0)}`"
        ),
        "",
        "## Next Actions",
        "| ID | Status | Action | Rationale |",
        "|---|---|---|---|",
    ]
    for action in payload.get("next_actions", []):
        if not isinstance(action, dict):
            continue
        lines.append(
            "| "
            f"{action.get('id', '')} | "
            f"{action.get('status', '')} | "
            f"{action.get('action', '')} | "
            f"{action.get('rationale', '')} |"
        )

    lines.append("")
    lines.append("## Blocked By")
    blocked_by = payload.get("blocked_by") or []
    if blocked_by:
        lines.extend(f"- `{item}`" for item in blocked_by)
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## No-Op Reasons")
    no_op_reasons = payload.get("no_op_reasons") or []
    if no_op_reasons:
        lines.extend(f"- `{item}`" for item in no_op_reasons)
    else:
        lines.append("- (none)")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reduce explicitly labeled external-trigger rehearsal events."
    )
    parser.add_argument("--events", type=Path, required=True, help="JSON/JSONL rehearsal events")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "docs" / "status")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    parser.add_argument("--memory-threshold", type=int, default=3)
    parser.add_argument("--stdout", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    events = load_events(args.events)
    payload = reduce_events(events, memory_threshold=args.memory_threshold)

    json_out = args.json_out or (args.out_dir / JSON_FILENAME)
    markdown_out = args.markdown_out or (args.out_dir / MARKDOWN_FILENAME)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_out.write_text(render_markdown(payload), encoding="utf-8")

    if args.stdout:
        _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
