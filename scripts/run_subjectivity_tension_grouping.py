"""Generate a grouping and triage report for unresolved subjectivity tensions."""

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
    extend_handoff_markdown,
    extend_status_lines_markdown,
)
from tonesoul.memory.subjectivity_triage import (  # noqa: E402
    build_subjectivity_tension_group_report,
)

JSON_FILENAME = "subjectivity_tension_groups_latest.json"
MARKDOWN_FILENAME = "subjectivity_tension_groups_latest.md"


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
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    return MemorySource(normalized)


def build_report(
    db_path: Path,
    *,
    source_name: str | None = None,
) -> tuple[dict[str, Any], str]:
    warnings: list[str] = []
    issues: list[str] = []
    db_exists = db_path.exists()
    source = _resolve_source(source_name)
    report = build_subjectivity_tension_group_report(
        SqliteSoulDB(db_path=db_path),
        source=source,
    )

    unresolved_row_count = int(report.get("summary", {}).get("unresolved_row_count") or 0)
    multi_direction_topic_count = int(
        report.get("summary", {}).get("multi_direction_topic_count") or 0
    )
    if not db_exists:
        warnings.append(f"soul db path did not exist before grouping run: {db_path.as_posix()}")
    if unresolved_row_count == 0:
        warnings.append("no unresolved tension rows found")
    if (
        unresolved_row_count > 0
        and int(report.get("summary", {}).get("semantic_group_count") or 0) == 0
    ):
        issues.append("unresolved tensions existed but no semantic groups were produced")
    if multi_direction_topic_count > 0:
        warnings.append(
            "some topics span multiple inferred directions; verify split boundaries before review"
        )

    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(issues) == 0,
        "source": "scripts/run_subjectivity_tension_grouping.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "source": source.value if source is not None else "all",
        },
        "grouping": report,
        "issues": issues,
        "warnings": warnings,
    }
    return payload, _render_markdown(payload)


def _render_markdown(payload: dict[str, Any]) -> str:
    grouping = payload.get("grouping", {})
    summary = grouping.get("summary", {})
    handoff = grouping.get("handoff", {})
    semantic_groups = list(grouping.get("semantic_groups") or [])
    lineage_groups = list(grouping.get("lineage_groups") or [])
    multi_direction_topics = list(grouping.get("multi_direction_topics") or [])
    status_lines = grouping.get("status_lines")

    def _format_histogram(histogram: Any) -> str:
        if not isinstance(histogram, dict) or not histogram:
            return ""
        parts: list[str] = []
        for count, total in sorted(histogram.items(), key=lambda item: int(item[0])):
            parts.append(f"{count}=>{total}")
        return ", ".join(parts)

    lines = [
        "# Subjectivity Tension Groups Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- db_path: {payload.get('inputs', {}).get('db_path', '')}",
        f"- source: {payload.get('inputs', {}).get('source', 'all')}",
    ]

    extend_handoff_markdown(
        lines,
        handoff=handoff,
        extra_fields=["top_group_shape"],
    )

    lines.extend(
        [
            "",
            "## Summary",
            f"- unresolved_row_count: {summary.get('unresolved_row_count', 0)}",
            f"- semantic_group_count: {summary.get('semantic_group_count', 0)}",
            f"- lineage_group_count: {summary.get('lineage_group_count', 0)}",
            f"- multi_direction_topic_count: {summary.get('multi_direction_topic_count', 0)}",
        ]
    )

    recommendation_counts = summary.get("recommendation_counts", {})
    if isinstance(recommendation_counts, dict) and recommendation_counts:
        lines.append("")
        lines.append("## Recommendation Counts")
        for name, count in sorted(
            recommendation_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    duplicate_pressure_counts = summary.get("duplicate_pressure_counts", {})
    if isinstance(duplicate_pressure_counts, dict) and duplicate_pressure_counts:
        lines.append("")
        lines.append("## Duplicate Pressure Counts")
        for name, count in sorted(
            duplicate_pressure_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    producer_followup_counts = summary.get("producer_followup_counts", {})
    if isinstance(producer_followup_counts, dict) and producer_followup_counts:
        lines.append("")
        lines.append("## Producer Follow-Up Counts")
        for name, count in sorted(
            producer_followup_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    extend_status_lines_markdown(lines, status_lines)

    lines.append("")
    lines.append("## Semantic Groups")
    if semantic_groups:
        for group in semantic_groups:
            lines.append(
                "- "
                f"{group.get('topic', '<unknown>')} "
                f"(`{group.get('direction', '')}`, `{group.get('friction_band', '')}`, "
                f"rows={group.get('record_count', 0)}, lineages={group.get('lineage_count', 0)}, "
                f"cycles={group.get('cycle_count', 0)}, sources={group.get('source_url_count', 0)}`)"
            )
            lines.append(f"  - recommendation: `{group.get('triage_recommendation', '')}`")
            lines.append(f"  - group_shape: {group.get('group_shape', '')}")
            lines.append(f"  - reason: {group.get('triage_reason', '')}")
            lines.append(f"  - duplicate_pressure: {group.get('duplicate_pressure', '')}")
            lines.append(f"  - producer_followup: {group.get('producer_followup', '')}")
            lines.append(
                "  - density: "
                f"rows_per_lineage={group.get('rows_per_lineage', 0)}, "
                f"rows_per_cycle={group.get('rows_per_cycle', 0)}"
            )
            lines.append(
                "  - lineage_density: "
                f"repeated_lineages={group.get('repeated_lineage_count', 0)}, "
                f"dense_lineages={group.get('dense_lineage_count', 0)}, "
                f"singleton_lineages={group.get('singleton_lineage_count', 0)}, "
                f"max_rows_per_lineage={group.get('max_lineage_record_count', 0)}"
            )
            histogram_text = _format_histogram(group.get("lineage_record_histogram"))
            if histogram_text:
                lines.append(f"  - lineage_record_histogram: {histogram_text}")
            if group.get("duplicate_pressure_reason"):
                lines.append(
                    f"  - duplicate_pressure_reason: {group.get('duplicate_pressure_reason', '')}"
                )
            source_urls = list(group.get("source_urls") or [])
            if source_urls:
                lines.append(f"  - source_urls: {', '.join(source_urls[:3])}")
            stimulus_lineages = list(group.get("stimulus_lineages") or [])
            if stimulus_lineages:
                lines.append(f"  - stimulus_lineages: {', '.join(stimulus_lineages[:4])}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Topics With Multiple Directions")
    if multi_direction_topics:
        for item in multi_direction_topics:
            lines.append(
                "- "
                f"{item.get('topic', '<unknown>')} "
                f"(directions={', '.join(item.get('directions', []))})"
            )
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Lineage Groups")
    if lineage_groups:
        for group in lineage_groups[:12]:
            lines.append(
                "- "
                f"{group.get('stimulus_lineage', '')} "
                f"(`{group.get('topic', '<unknown>')}`, rows={group.get('record_count', 0)}, "
                f"cycles={group.get('cycle_count', 0)})"
            )
    else:
        lines.append("- None")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a grouping and triage report for unresolved subjectivity tensions."
    )
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for the latest JSON/Markdown artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    db_path = Path(args.db_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    payload, markdown = build_report(db_path, source_name=args.source)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
