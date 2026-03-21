"""Generate operator-facing subjectivity status artifacts from soul.db."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB  # noqa: E402
from tonesoul.memory.subjectivity_handoff import (  # noqa: E402
    build_handoff_surface,
    extend_handoff_markdown,
    extend_status_lines_markdown,
)
from tonesoul.memory.subjectivity_reporting import (  # noqa: E402
    list_subjectivity_records,
    summarize_subjectivity_distribution,
)

JSON_FILENAME = "subjectivity_report_latest.json"
MARKDOWN_FILENAME = "subjectivity_report_latest.md"
_REVIEWED_STATUSES = {"reviewed", "human_reviewed", "governance_reviewed", "approved"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _resolve_source(value: str | None) -> MemorySource | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    return MemorySource(normalized)


def _top_unresolved_status(unresolved_by_status: dict[str, Any]) -> str:
    if not isinstance(unresolved_by_status, dict) or not unresolved_by_status:
        return ""
    name, _ = min(
        unresolved_by_status.items(),
        key=lambda item: (-int(item[1]), str(item[0])),
    )
    return str(name)


def _report_queue_shape(
    *,
    total_records: int,
    unresolved_tension_count: int,
    deferred_tension_count: int,
    reviewed_vow_count: int,
) -> str:
    if total_records == 0:
        return "empty_report"
    if unresolved_tension_count == 0 and reviewed_vow_count > 0:
        return "settled_or_reviewed"
    if unresolved_tension_count == 0:
        return "observational_only"
    if deferred_tension_count == unresolved_tension_count:
        return "deferred_monitoring"
    return "action_required"


def _report_status_line(
    *,
    queue_shape: str,
    total_records: int,
    unresolved_tension_count: int,
    deferred_tension_count: int,
    settled_tension_count: int,
    reviewed_vow_count: int,
    top_unresolved_status: str,
) -> str:
    line = (
        f"{queue_shape} | records={total_records} unresolved={unresolved_tension_count} "
        f"deferred={deferred_tension_count} settled={settled_tension_count} "
        f"reviewed_vows={reviewed_vow_count}"
    )
    if top_unresolved_status:
        line += f" | top_unresolved_status={top_unresolved_status}"
    return line


def build_report(
    db_path: Path,
    *,
    source_name: str | None = None,
    unresolved_limit: int = 10,
    reviewed_vow_limit: int = 10,
) -> tuple[dict[str, Any], str]:
    warnings: list[str] = []
    issues: list[str] = []
    db_exists = db_path.exists()
    source = _resolve_source(source_name)
    soul_db = SqliteSoulDB(db_path=db_path)

    summary = summarize_subjectivity_distribution(soul_db, source=source)
    unresolved_tensions = list_subjectivity_records(
        soul_db,
        source=source,
        unresolved_only=True,
        limit=unresolved_limit,
    )
    vow_rows = list_subjectivity_records(
        soul_db,
        source=source,
        subjectivity_layer="vow",
        limit=None,
    )
    reviewed_vows_all = [
        row for row in vow_rows if str(row.get("promotion_status") or "") in _REVIEWED_STATUSES
    ]
    reviewed_vows = reviewed_vows_all[: max(0, int(reviewed_vow_limit))]

    total_records = int(summary.get("total_records") or 0)
    unresolved_tension_count = int(summary.get("unresolved_tension_count") or 0)
    deferred_tension_count = int(summary.get("deferred_tension_count") or 0)
    settled_tension_count = int(summary.get("settled_tension_count") or 0)
    reviewed_vow_count = len(reviewed_vows_all)
    unresolved_by_status = dict(summary.get("unresolved_by_status") or {})
    top_unresolved_status = _top_unresolved_status(unresolved_by_status)
    queue_shape = _report_queue_shape(
        total_records=total_records,
        unresolved_tension_count=unresolved_tension_count,
        deferred_tension_count=deferred_tension_count,
        reviewed_vow_count=reviewed_vow_count,
    )
    primary_status_line = _report_status_line(
        queue_shape=queue_shape,
        total_records=total_records,
        unresolved_tension_count=unresolved_tension_count,
        deferred_tension_count=deferred_tension_count,
        settled_tension_count=settled_tension_count,
        reviewed_vow_count=reviewed_vow_count,
        top_unresolved_status=top_unresolved_status,
    )

    if not db_exists:
        warnings.append(f"soul db path did not exist before report run: {db_path.as_posix()}")
    if total_records == 0:
        warnings.append("no subjectivity records found")
    if reviewed_vow_count == 0 and total_records > 0:
        warnings.append("no reviewed vow records found")
    if deferred_tension_count > 0:
        warnings.append(
            f"{deferred_tension_count} unresolved tension record(s) are explicitly deferred"
        )
    if unresolved_tension_count > 0:
        issues.append(f"{unresolved_tension_count} unresolved tension record(s) pending review")

    status_lines = [primary_status_line] if primary_status_line else []
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(issues) == 0,
        "source": "scripts/run_subjectivity_report.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "source": source.value if source is not None else "all",
            "unresolved_limit": int(unresolved_limit),
            "reviewed_vow_limit": int(reviewed_vow_limit),
        },
        "metrics": {
            "total_records": total_records,
            "unresolved_tension_count": unresolved_tension_count,
            "deferred_tension_count": deferred_tension_count,
            "settled_tension_count": settled_tension_count,
            "reviewed_vow_count": reviewed_vow_count,
            "event_only_count": int(summary.get("event_only_count") or 0),
            "by_subjectivity_layer": dict(summary.get("by_subjectivity_layer") or {}),
            "by_memory_layer": dict(summary.get("by_memory_layer") or {}),
            "by_promotion_status": dict(summary.get("by_promotion_status") or {}),
            "unresolved_by_status": unresolved_by_status,
            "by_source": dict(summary.get("by_source") or {}),
        },
        "handoff": build_handoff_surface(
            queue_shape=queue_shape,
            requires_operator_action=queue_shape == "action_required",
            status_lines=status_lines,
            extra_fields={"top_unresolved_status": top_unresolved_status},
        ),
        "primary_status_line": primary_status_line,
        "status_lines": status_lines,
        "unresolved_tensions": unresolved_tensions,
        "reviewed_vows": reviewed_vows,
        "issues": issues,
        "warnings": warnings,
    }
    return payload, _render_markdown(payload)


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    handoff = payload.get("handoff", {})
    status_lines = payload.get("status_lines")
    lines = [
        "# Subjectivity Report Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- db_path: {payload.get('inputs', {}).get('db_path', '')}",
        f"- source: {payload.get('inputs', {}).get('source', 'all')}",
    ]

    extend_handoff_markdown(
        lines,
        handoff=handoff,
        extra_fields=["top_unresolved_status"],
    )

    lines.extend(
        [
            "",
            "## Metrics",
            f"- total_records: {metrics.get('total_records', 0)}",
            f"- unresolved_tension_count: {metrics.get('unresolved_tension_count', 0)}",
            f"- deferred_tension_count: {metrics.get('deferred_tension_count', 0)}",
            f"- settled_tension_count: {metrics.get('settled_tension_count', 0)}",
            f"- reviewed_vow_count: {metrics.get('reviewed_vow_count', 0)}",
            f"- event_only_count: {metrics.get('event_only_count', 0)}",
        ]
    )

    extend_status_lines_markdown(lines, status_lines)

    for title, key in (
        ("Subjectivity Layers", "by_subjectivity_layer"),
        ("Memory Layers", "by_memory_layer"),
        ("Promotion Statuses", "by_promotion_status"),
        ("Unresolved Statuses", "unresolved_by_status"),
        ("Sources", "by_source"),
    ):
        values = metrics.get(key, {})
        if isinstance(values, dict) and values:
            lines.append("")
            lines.append(f"## {title}")
            for name, count in sorted(values.items(), key=lambda item: (-int(item[1]), item[0])):
                lines.append(f"- {name}: {count}")

    unresolved = payload.get("unresolved_tensions", [])
    lines.append("")
    lines.append("## Unresolved Tensions")
    if isinstance(unresolved, list) and unresolved:
        for row in unresolved:
            lines.append(
                f"- {row.get('summary', '')} "
                f"(`{row.get('pending_status', '')}`, `{row.get('source', '')}`, `{row.get('timestamp', '')}`)"
            )
            if row.get("review_basis"):
                lines.append(f"  - review_basis: {row.get('review_basis', '')}")
            if row.get("review_notes"):
                lines.append(f"  - review_notes: {row.get('review_notes', '')}")
    else:
        lines.append("- None")

    reviewed_vows = payload.get("reviewed_vows", [])
    lines.append("")
    lines.append("## Reviewed Vows")
    if isinstance(reviewed_vows, list) and reviewed_vows:
        for row in reviewed_vows:
            lines.append(
                f"- {row.get('summary', '')} "
                f"(`{row.get('promotion_status', '')}`, `{row.get('timestamp', '')}`)"
            )
    else:
        lines.append("- None")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues:
            lines.append(f"- {issue}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate operator-facing subjectivity report artifacts."
    )
    parser.add_argument(
        "--db-path",
        default="memory/soul.db",
        help="Path to soul.db.",
    )
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--unresolved-limit",
        type=int,
        default=10,
        help="Maximum unresolved tension rows to include.",
    )
    parser.add_argument(
        "--reviewed-vow-limit",
        type=int,
        default=10,
        help="Maximum reviewed vow rows to include.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when unresolved tensions are still pending review.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    db_path = Path(args.db_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    payload, markdown = build_report(
        db_path,
        source_name=args.source,
        unresolved_limit=args.unresolved_limit,
        reviewed_vow_limit=args.reviewed_vow_limit,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
