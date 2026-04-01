#!/usr/bin/env python3
"""
Run the ToneSoul observer-window / low-drift-anchor readout.

Purpose: produce a compact bounded summary of what is currently
stable / contested / stale without requiring a full repo re-read.

Usage:
    python scripts/run_observer_window.py --agent <your-id>
    python scripts/run_observer_window.py --agent <your-id> --json-out docs/status/observer_window_latest.json
    python scripts/run_observer_window.py --agent <your-id> --markdown-out docs/status/observer_window_latest.md

Authority: advisory only - output must not be promoted into canonical governance truth.
Last Updated: 2026-04-02
"""

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
        description="Run the ToneSoul observer-window / low-drift-anchor readout.",
    )
    parser.add_argument(
        "--agent", default="observer-window-cli", help="Agent ID for session-start query"
    )
    parser.add_argument("--state-path", type=Path, default=None)
    parser.add_argument("--traces-path", type=Path, default=None)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Path to write JSON output (e.g. docs/status/observer_window_latest.json)",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Path to write Markdown output",
    )
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _render_markdown(anchor: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Observer Window / Low-Drift Anchor",
        "",
        f"> Generated at `{anchor.get('generated_at', '')}`. Advisory only.",
        "",
        f"**Summary**: `{anchor.get('summary_text', '')}`",
        "",
        "> [!NOTE]",
        f"> {anchor.get('receiver_note', '')}",
        "",
    ]

    counts = anchor.get("counts") or {}
    canonical_center = anchor.get("canonical_center") or {}
    current_short_board = canonical_center.get("current_short_board") or {}
    hot_memory_ladder = anchor.get("hot_memory_ladder") or {}
    hot_memory_decay_map = anchor.get("hot_memory_decay_map") or {}

    lines.extend(["## Canonical Center", ""])
    lines.append(
        f"- Parent surfaces: `{', '.join(canonical_center.get('parent_surfaces') or [])}`"
    )
    lines.append(f"- Receiver rule: `{canonical_center.get('receiver_rule', '')}`")
    correction = canonical_center.get("successor_correction") or {}
    if correction:
        lines.append(f"- Successor correction: `{correction.get('summary_text', '')}`")
        lines.append(f"- Correction rule: `{correction.get('correction_rule', '')}`")
        required_checks = correction.get("required_checks") or []
        if required_checks:
            lines.append(f"- Required checks: `{', '.join(required_checks)}`")
    lines.append(f"- Current short board visible: `{current_short_board.get('present', False)}`")
    if current_short_board.get("items"):
        lines.append("- Current short board:")
        for item in current_short_board.get("items") or []:
            lines.append(f"  - {item}")
    else:
        lines.append(
            f"- Short board note: `{current_short_board.get('summary_text', 'not visible')}`"
        )
    lines.append("")

    lines.extend(["## Hot-Memory Ladder", ""])
    lines.append(f"- Summary: `{hot_memory_ladder.get('summary_text', '')}`")
    lines.append(f"- Receiver note: `{hot_memory_ladder.get('receiver_note', '')}`")
    lines.append("")
    for layer in hot_memory_ladder.get("layers") or []:
        lines.append(f"- `{layer.get('layer', 'unknown')}`: `{layer.get('status', 'unknown')}`")
        lines.append(f"  - sources: `{', '.join(layer.get('primary_sources') or [])}`")
        lines.append(f"  - receiver_rule: `{layer.get('receiver_rule', '')}`")
        lines.append(f"  - note: {layer.get('note', '')}")
    if not hot_memory_ladder.get("layers"):
        lines.append("- *(none)*")
    lines.append("")

    lines.extend(["## Hot-Memory Decay / Compression", ""])
    lines.append(f"- Summary: `{hot_memory_decay_map.get('summary_text', '')}`")
    lines.append(f"- Receiver note: `{hot_memory_decay_map.get('receiver_note', '')}`")
    lines.append("")
    for layer in hot_memory_decay_map.get("layers") or []:
        lines.append(f"- `{layer.get('layer', 'unknown')}`: `{layer.get('use_posture', 'unknown')}`")
        lines.append(f"  - status: `{layer.get('status', 'unknown')}`")
        lines.append(f"  - decay_posture: `{layer.get('decay_posture', '')}`")
        lines.append(f"  - compression_posture: `{layer.get('compression_posture', '')}`")
        if layer.get("quarantine_reason"):
            lines.append(f"  - quarantine_reason: `{layer.get('quarantine_reason', '')}`")
        lines.append(f"  - note: {layer.get('note', '')}")
    if not hot_memory_decay_map.get("layers"):
        lines.append("- *(none)*")
    lines.append("")

    lines.extend(["## Stable", "", f"({counts.get('stable', 0)} items)", ""])
    for item in anchor.get("stable") or []:
        detail = f" - `{item['detail']}`" if item.get("detail") else ""
        lines.append(f"- **{item['claim']}**{detail}")
        lines.append(f"  - source: `{item['evidence_source']}`")
    if not anchor.get("stable"):
        lines.append("- *(none)*")
    lines.append("")

    lines.extend(["## Contested", "", f"({counts.get('contested', 0)} items)", ""])
    for item in anchor.get("contested") or []:
        detail = f" - `{item['detail']}`" if item.get("detail") else ""
        lines.append(f"- **{item['claim']}**{detail}")
        lines.append(f"  - source: `{item['evidence_source']}`")
    if not anchor.get("contested"):
        lines.append("- *(none)*")
    lines.append("")

    lines.extend(["## Stale", "", f"({counts.get('stale', 0)} items)", ""])
    for item in anchor.get("stale") or []:
        detail = f" - `{item['detail']}`" if item.get("detail") else ""
        lines.append(f"- **{item['claim']}**{detail}")
        lines.append(f"  - source: `{item['evidence_source']}`")
    if not anchor.get("stale"):
        lines.append("- *(none)*")
    lines.append("")

    delta = anchor.get("delta_summary") or {}
    lines.extend(
        [
            "## Delta Since Last Seen",
            "",
            f"- First observation: `{delta.get('first_observation', False)}`",
            f"- Has updates: `{delta.get('has_updates', False)}`",
            f"- New compactions: `{delta.get('new_compaction_count', 0)}`",
            f"- New checkpoints: `{delta.get('new_checkpoint_count', 0)}`",
            f"- New traces: `{delta.get('new_trace_count', 0)}`",
            "",
        ]
    )

    return "\n".join(lines)


def _build_store(*, state_path: Path | None, traces_path: Path | None):
    """Build a FileStore from explicit paths, or return None for auto-discovery."""
    if state_path is None and traces_path is None:
        return None

    from tonesoul.backends.file_store import FileStore

    if traces_path is not None:
        root = traces_path.parent
    elif state_path is not None:
        root = state_path.parent
    else:
        root = Path(".")

    def _resolve_sidecar(name: str) -> Path:
        canonical = root / ".aegis" / name
        legacy = root / name
        return canonical if canonical.exists() else (legacy if legacy.exists() else canonical)

    zones_path = root / "zone_registry.json"
    return FileStore(
        gov_path=state_path,
        traces_path=traces_path,
        zones_path=zones_path,
        claims_path=_resolve_sidecar("task_claims.json"),
        perspectives_path=_resolve_sidecar("perspectives.json"),
        checkpoints_path=_resolve_sidecar("checkpoints.json"),
        compactions_path=_resolve_sidecar("compacted.json"),
        subject_snapshots_path=_resolve_sidecar("subject_snapshots.json"),
        observer_cursors_path=_resolve_sidecar("observer_cursors.json"),
    )


def run_observer_window(
    *,
    agent: str,
    state_path: Path | None = None,
    traces_path: Path | None = None,
) -> dict[str, Any]:
    """
    Run session-start bundle directly (no subprocess), then derive
    a bounded low_drift_anchor from the import_posture and readiness.

    Returns the anchor dict directly.
    """
    from scripts.start_agent_session import run_session_start_bundle
    from tonesoul.observer_window import build_low_drift_anchor

    payload = run_session_start_bundle(
        agent_id=agent,
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
    )

    packet = payload.get("packet") or {}
    readiness = payload.get("readiness") or {}
    raw_import_posture = payload.get("import_posture") or {}
    canonical_center = payload.get("canonical_center") or {}
    import_posture = raw_import_posture.get("surfaces") or raw_import_posture

    return build_low_drift_anchor(
        packet=packet,
        import_posture=import_posture,
        readiness=readiness,
        canonical_center=canonical_center,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        anchor = run_observer_window(
            agent=str(args.agent).strip(),
            state_path=args.state_path,
            traces_path=args.traces_path,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json_out is not None:
        _write_json(args.json_out, anchor)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(_render_markdown(anchor), encoding="utf-8")

    print(json.dumps(anchor, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
