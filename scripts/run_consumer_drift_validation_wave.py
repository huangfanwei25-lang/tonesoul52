#!/usr/bin/env python3
"""Run a bounded cross-consumer drift validation wave."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a bounded cross-consumer drift validation wave.",
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


def _normalize(text: Any) -> str:
    return str(text or "").strip()


def _parity_field(*, name: str, values: dict[str, str]) -> dict[str, Any]:
    non_empty = {key: value for key, value in values.items() if value}
    normalized_values = set(non_empty.values())
    return {
        "field": name,
        "ok": len(normalized_values) <= 1,
        "values": values,
    }


def build_consumer_drift_report(
    *,
    agent: str,
    tier1_bundle: dict[str, Any],
    observer_window: dict[str, Any],
    dashboard_shell: dict[str, Any],
    claude_adapter_payload: dict[str, Any],
) -> dict[str, Any]:
    claude_adapter = dict(claude_adapter_payload.get("adapter") or {})
    session_start_short_board = _normalize(
        ((tier1_bundle.get("canonical_center") or {}).get("current_short_board") or {}).get(
            "summary_text"
        )
    )
    observer_short_board = _normalize(
        ((observer_window.get("canonical_center") or {}).get("current_short_board") or {}).get(
            "summary_text"
        )
    )
    dashboard_short_board = _normalize(
        ((dashboard_shell.get("canonical_cards") or {}).get("short_board"))
    )
    claude_short_board = _normalize((claude_adapter.get("current_context") or {}).get("short_board"))

    session_closeout = _normalize((tier1_bundle.get("closeout_attention") or {}).get("status"))
    observer_closeout = _normalize((observer_window.get("closeout_attention") or {}).get("status"))
    dashboard_closeout = _normalize((dashboard_shell.get("closeout_attention") or {}).get("status"))
    claude_closeout = _normalize((claude_adapter.get("current_context") or {}).get("closeout_status"))

    session_version = _normalize((tier1_bundle.get("surface_versioning") or {}).get("summary_text"))
    observer_version = _normalize((observer_window.get("surface_versioning") or {}).get("summary_text"))
    claude_version = _normalize((claude_adapter.get("surface_versioning") or {}).get("summary_text"))
    dashboard_version = _normalize((tier1_bundle.get("surface_versioning") or {}).get("summary_text"))

    session_fallback = _normalize((tier1_bundle.get("surface_versioning") or {}).get("fallback_rule"))
    observer_fallback = _normalize((observer_window.get("surface_versioning") or {}).get("fallback_rule"))
    claude_fallback = _normalize((claude_adapter.get("surface_versioning") or {}).get("fallback_rule"))
    dashboard_fallback = _normalize((tier1_bundle.get("surface_versioning") or {}).get("fallback_rule"))

    parity_checks = [
        _parity_field(
            name="short_board",
            values={
                "session_start_tier1": session_start_short_board,
                "observer_window": observer_short_board,
                "dashboard_shell": dashboard_short_board,
                "claude_entry_adapter": claude_short_board,
            },
        ),
        _parity_field(
            name="closeout_status",
            values={
                "session_start_tier1": session_closeout,
                "observer_window": observer_closeout,
                "dashboard_shell": dashboard_closeout,
                "claude_entry_adapter": claude_closeout,
            },
        ),
        _parity_field(
            name="surface_versioning",
            values={
                "session_start_tier1": session_version,
                "observer_window": observer_version,
                "dashboard_shell": dashboard_version,
                "claude_entry_adapter": claude_version,
            },
        ),
        _parity_field(
            name="fallback_rule",
            values={
                "session_start_tier1": session_fallback,
                "observer_window": observer_fallback,
                "dashboard_shell": dashboard_fallback,
                "claude_entry_adapter": claude_fallback,
            },
        ),
    ]

    all_ok = all(check["ok"] for check in parity_checks)
    return {
        "contract_version": "v1",
        "bundle": "consumer_drift_validation_wave",
        "agent": agent,
        "status": "aligned" if all_ok else "drift_detected",
        "summary_text": (
            f"consumer_drift status={'aligned' if all_ok else 'drift_detected'} "
            f"checks={len(parity_checks)}"
        ),
        "receiver_rule": (
            "Consumer shells may differ in presentation, but short-board truth, closeout meaning, version summary, and fallback order must stay aligned."
        ),
        "parity_checks": parity_checks,
        "consumers": {
            "session_start_tier1": {
                "short_board": session_start_short_board,
                "closeout_status": session_closeout,
            },
            "observer_window": {
                "short_board": observer_short_board,
                "closeout_status": observer_closeout,
            },
            "dashboard_shell": {
                "short_board": dashboard_short_board,
                "closeout_status": dashboard_closeout,
            },
            "claude_entry_adapter": {
                "short_board": claude_short_board,
                "closeout_status": claude_closeout,
            },
        },
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Consumer Drift Validation Wave",
        "",
        f"**Summary**: `{report.get('summary_text', '')}`",
        "",
        f"> {report.get('receiver_rule', '')}",
        "",
        "## Parity Checks",
        "",
    ]
    for check in report.get("parity_checks") or []:
        lines.append(f"- `{check.get('field', '')}`: `{check.get('ok', False)}`")
        for key, value in (check.get("values") or {}).items():
            lines.append(f"  - `{key}`: {value or '(empty)'}")
    return "\n".join(lines) + "\n"


def run_consumer_drift_validation_wave(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, Any]:
    from apps.dashboard.frontend.utils.session_start import build_tier1_orientation_shell
    from scripts.run_claude_entry_adapter import run_claude_entry_adapter
    from scripts.run_observer_window import run_observer_window
    from scripts.start_agent_session import run_session_start_bundle

    tier1_bundle = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=1,
    )
    dashboard_shell = build_tier1_orientation_shell(tier1_bundle)
    observer_window = run_observer_window(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )
    claude_adapter_payload = run_claude_entry_adapter(
        agent=agent,
        state_path=state_path,
        traces_path=traces_path,
    )

    return build_consumer_drift_report(
        agent=agent,
        tier1_bundle=tier1_bundle,
        observer_window=observer_window,
        dashboard_shell=dashboard_shell,
        claude_adapter_payload=claude_adapter_payload,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = run_consumer_drift_validation_wave(
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
