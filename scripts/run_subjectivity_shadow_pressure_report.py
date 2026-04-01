"""Generate aggregated retrieval-pressure metrics from subjectivity shadow queries."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_shadow import build_subjectivity_shadow_pressure_report

JSON_FILENAME = "subjectivity_shadow_pressure_latest.json"
MARKDOWN_FILENAME = "subjectivity_shadow_pressure_latest.md"
DEFAULT_QUERIES = (
    "governance",
    "provenance",
    "boundary",
    "tension",
    "memory",
)
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


def _read_query_file(path: Path) -> list[str]:
    rows: list[str] = []
    if not path.exists():
        return rows
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = str(raw_line or "").strip()
        if not line or line.startswith("#"):
            continue
        rows.append(line)
    return rows


def _resolve_queries(
    explicit_queries: list[str], query_file: Path | None
) -> tuple[list[str], bool]:
    resolved = [str(query or "").strip() for query in explicit_queries if str(query or "").strip()]
    if query_file is not None:
        resolved.extend(_read_query_file(query_file))
    deduped: list[str] = []
    seen: set[str] = set()
    for query in resolved:
        key = query.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
    if deduped:
        return deduped, False
    return list(DEFAULT_QUERIES), True


def build_report(
    db_path: Path,
    *,
    queries: list[str] | None = None,
    query_file: Path | None = None,
    source_name: str | None = None,
    profile: str = "classified_first",
    limit: int = 5,
    candidate_limit: int = 20,
) -> tuple[dict[str, Any], str]:
    db_exists = db_path.exists()
    source = _resolve_source(source_name)
    resolved_queries, used_default_queries = _resolve_queries(queries or [], query_file)
    pressure = build_subjectivity_shadow_pressure_report(
        SqliteSoulDB(db_path=db_path),
        queries=resolved_queries,
        source=source,
        profile=profile,
        limit=limit,
        candidate_limit=candidate_limit,
    )

    warnings: list[str] = []
    if not db_exists:
        warnings.append(
            f"soul db path did not exist before shadow pressure run: {db_path.as_posix()}"
        )
    if used_default_queries:
        warnings.append("no explicit queries provided; used default subjectivity shadow query set")
    if int(pressure["metrics"]["no_hit_query_count"]) == int(pressure["metrics"]["query_count"]):
        warnings.append("all queries returned zero baseline candidates")

    payload = {
        "generated_at": _iso_now(),
        "overall_ok": int(pressure["metrics"]["query_count"]) > 0,
        "source": "scripts/run_subjectivity_shadow_pressure_report.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "queries": resolved_queries,
            "source_filter": source.value if source is not None else "all",
            "profile": profile,
            "limit": int(limit),
            "candidate_limit": int(candidate_limit),
            "query_file": query_file.as_posix() if query_file is not None else None,
        },
        "pressure": pressure,
        "warnings": warnings,
        "issues": [],
    }
    return payload, _render_markdown(payload)


def _render_markdown(payload: dict[str, Any]) -> str:
    pressure = payload.get("pressure", {})
    metrics = pressure.get("metrics", {})
    lines = [
        "# Subjectivity Shadow Pressure Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- profile: {payload.get('inputs', {}).get('profile', '')}",
        f"- source_filter: {payload.get('inputs', {}).get('source_filter', 'all')}",
        "",
        "## Metrics",
        f"- query_count: {metrics.get('query_count', 0)}",
        f"- changed_query_rate: {metrics.get('changed_query_rate', 0.0)}",
        f"- top1_changed_rate: {metrics.get('top1_changed_rate', 0.0)}",
        f"- pressure_query_rate: {metrics.get('pressure_query_rate', 0.0)}",
        f"- avg_overlap_rate: {metrics.get('avg_overlap_rate', 0.0)}",
        f"- avg_classified_lift: {metrics.get('avg_classified_lift', 0.0)}",
        f"- tension_top1_gain_rate: {metrics.get('tension_top1_gain_rate', 0.0)}",
        f"- reviewed_vow_top1_gain_rate: {metrics.get('reviewed_vow_top1_gain_rate', 0.0)}",
        "",
        "## Query Samples",
    ]

    query_rows = list(pressure.get("queries") or [])
    if query_rows:
        for row in query_rows[:12]:
            lines.append(
                "- "
                f"{row.get('query')} "
                f"(changed={str(bool(row.get('query_changed'))).lower()}, "
                f"top1_changed={str(bool(row.get('top1_changed'))).lower()}, "
                f"classified_lift={row.get('classified_lift', 0)}, "
                f"reviewed_vow_lift={row.get('reviewed_vow_lift', 0)})"
            )
    else:
        lines.append("- None")

    no_hit_queries = list(pressure.get("no_hit_queries") or [])
    if no_hit_queries:
        lines.append("")
        lines.append("## No-Hit Queries")
        for query in no_hit_queries:
            lines.append(f"- {query}")

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
        description="Generate aggregated retrieval-pressure metrics from subjectivity shadow queries."
    )
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Repeat to add explicit query strings. Falls back to a default set when omitted.",
    )
    parser.add_argument(
        "--query-file",
        default=None,
        help="Optional newline-delimited query file. Blank lines and # comments are ignored.",
    )
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
    parser.add_argument("--limit", type=int, default=5, help="Top results to compare per query.")
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
    query_file = Path(args.query_file).resolve() if args.query_file else None
    payload, markdown = build_report(
        db_path,
        queries=list(args.query or []),
        query_file=query_file,
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
