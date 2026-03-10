"""Generate a read-only shadow query artifact for subjectivity-aware retrieval."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_shadow import build_subjectivity_shadow_report

JSON_FILENAME = "subjectivity_shadow_query_latest.json"
MARKDOWN_FILENAME = "subjectivity_shadow_query_latest.md"
_PROFILE_CHOICES = ("classified_first", "tension_first", "reviewed_vow_first")


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
    query: str,
    source_name: str | None = None,
    profile: str = "classified_first",
    limit: int = 5,
    candidate_limit: int = 20,
) -> tuple[dict[str, Any], str]:
    db_exists = db_path.exists()
    source = _resolve_source(source_name)
    shadow = build_subjectivity_shadow_report(
        SqliteSoulDB(db_path=db_path),
        query=query,
        source=source,
        profile=profile,
        limit=limit,
        candidate_limit=candidate_limit,
    )

    warnings: list[str] = []
    if not db_exists:
        warnings.append(f"soul db path did not exist before shadow query run: {db_path.as_posix()}")
    if int(shadow.get("candidate_count") or 0) == 0:
        warnings.append("no baseline candidates found for query")

    payload = {
        "generated_at": _iso_now(),
        "overall_ok": int(shadow["metrics"]["baseline_count"]) > 0,
        "source": "scripts/run_subjectivity_shadow_query.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "query": str(query or "").strip(),
            "source_filter": source.value if source is not None else "all",
            "profile": profile,
            "limit": int(limit),
            "candidate_limit": int(candidate_limit),
        },
        "shadow": shadow,
        "warnings": warnings,
    }
    return payload, _render_markdown(payload)


def _render_result_lines(rows: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        lines.append(
            f"- {row.get('title', '')} "
            f"(baseline={row.get('baseline_score', 0)}, "
            f"shadow={row.get('shadow_score', row.get('baseline_score', 0))}, "
            f"subjectivity={row.get('subjectivity_layer', 'unclassified')}, "
            f"status={row.get('promotion_status', 'none')})"
        )
        summary = str(row.get("summary") or "").strip()
        if summary:
            lines.append(f"  - {summary}")
    if not lines:
        lines.append("- None")
    return lines


def _render_markdown(payload: dict[str, Any]) -> str:
    shadow = payload.get("shadow", {})
    metrics = shadow.get("metrics", {})
    delta = shadow.get("delta", {})
    lines = [
        "# Subjectivity Shadow Query Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- query: {payload.get('inputs', {}).get('query', '')}",
        f"- profile: {payload.get('inputs', {}).get('profile', '')}",
        f"- source_filter: {payload.get('inputs', {}).get('source_filter', 'all')}",
        "",
        "## Metrics",
        f"- candidate_count: {shadow.get('candidate_count', 0)}",
        f"- baseline_count: {metrics.get('baseline_count', 0)}",
        f"- shadow_count: {metrics.get('shadow_count', 0)}",
        f"- overlap_count: {metrics.get('overlap_count', 0)}",
        f"- promoted_count: {metrics.get('promoted_count', 0)}",
        f"- demoted_count: {metrics.get('demoted_count', 0)}",
        "",
        "## Baseline Results",
    ]
    lines.extend(_render_result_lines(list(shadow.get("baseline_results") or [])))
    lines.append("")
    lines.append("## Shadow Results")
    lines.extend(_render_result_lines(list(shadow.get("shadow_results") or [])))
    lines.append("")
    lines.append("## Delta")
    lines.append(f"- overlap_ids: {', '.join(delta.get('overlap_ids', [])) or '(none)'}")
    lines.append(f"- promoted_ids: {', '.join(delta.get('promoted_ids', [])) or '(none)'}")
    lines.append(f"- demoted_ids: {', '.join(delta.get('demoted_ids', [])) or '(none)'}")

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
        description="Generate a read-only subjectivity shadow query artifact."
    )
    parser.add_argument("query", help="Query text used for baseline and shadow retrieval.")
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter.",
    )
    parser.add_argument(
        "--profile",
        choices=_PROFILE_CHOICES,
        default="classified_first",
        help="Subjectivity-aware shadow rerank profile.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Top results to show.")
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=20,
        help="Baseline candidate pool size before shadow reranking.",
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
    payload, markdown = build_report(
        db_path,
        query=args.query,
        source_name=args.source,
        profile=args.profile,
        limit=args.limit,
        candidate_limit=args.candidate_limit,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
