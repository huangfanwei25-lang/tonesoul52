"""
Full-text search across memory/self_journal.jsonl with optional filters.

Usage examples:
  python scripts/search_journal.py "resonance" --limit 5
  python scripts/search_journal.py --verdict block --limit 3
  python scripts/search_journal.py --resonance deep_resonance
  python scripts/search_journal.py --date-from 2026-03-01 --date-to 2026-03-02
  python scripts/search_journal.py "tension" --export docs/status/search_results.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DEFAULT_JOURNAL = Path("memory/self_journal.jsonl")


@dataclass
class SearchFilters:
    verdict: str | None = None
    resonance: str | None = None
    genesis: str | None = None
    date_from: date | None = None
    date_to: date | None = None


@dataclass
class SearchResult:
    timestamp: str
    verdict: str
    resonance: str
    genesis: str
    prompt: str
    delta_before: float | None
    delta_after: float | None
    line_number: int


def _entry_payload(raw: dict[str, Any]) -> dict[str, Any]:
    payload = raw.get("payload")
    if isinstance(payload, dict):
        return payload
    return raw


def _write_text(text: str) -> None:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _iter_text_values(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        text = value.strip()
        if text:
            yield text
        return
    if isinstance(value, dict):
        for nested in value.values():
            yield from _iter_text_values(nested)
        return
    if isinstance(value, list):
        for item in value:
            yield from _iter_text_values(item)


def _parse_timestamp(raw: str) -> datetime | None:
    if not raw or not isinstance(raw, str):
        return None
    value = raw.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _extract_timestamp(entry: dict[str, Any]) -> str:
    timestamp = entry.get("timestamp")
    if isinstance(timestamp, str) and timestamp.strip():
        return timestamp.strip()
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        nested = transcript.get("timestamp")
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return "unknown"


def _extract_verdict(entry: dict[str, Any]) -> str:
    verdict = entry.get("verdict")
    if isinstance(verdict, str):
        text = verdict.strip().lower()
        if text:
            return text
    if isinstance(verdict, dict):
        text = str(verdict.get("verdict") or "").strip().lower()
        if text:
            return text
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        nested = transcript.get("verdict")
        if isinstance(nested, dict):
            text = str(nested.get("verdict") or "").strip().lower()
            if text:
                return text
    return "unknown"


def _extract_resonance(entry: dict[str, Any]) -> str:
    for key in ("resonance", "resonance_class", "resonance_type"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        for key in ("resonance", "resonance_class", "resonance_type"):
            value = transcript.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip().lower()
    return "unknown"


def _extract_genesis(entry: dict[str, Any]) -> str:
    for key in ("genesis", "event_source"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        value = transcript.get("genesis")
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return "unknown"


def _extract_prompt(entry: dict[str, Any]) -> str:
    preferred_keys = ("prompt", "input_preview", "reflection", "self_statement", "content")
    for key in preferred_keys:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        for key in preferred_keys:
            value = transcript.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_deltas(entry: dict[str, Any]) -> tuple[float | None, float | None]:
    before_keys = ("delta_before_repair", "delta_before", "tension_before")
    after_keys = ("delta_after_repair", "delta_after", "tension_after")

    before = None
    after = None
    for key in before_keys:
        before = _to_float(entry.get(key))
        if before is not None:
            break

    for key in after_keys:
        after = _to_float(entry.get(key))
        if after is not None:
            break

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        if before is None:
            for key in before_keys:
                before = _to_float(transcript.get(key))
                if before is not None:
                    break
        if after is None:
            for key in after_keys:
                after = _to_float(transcript.get(key))
                if after is not None:
                    break

    return before, after


def _parse_date(raw: str | None) -> date | None:
    if raw is None:
        return None
    return date.fromisoformat(raw)


def _matches_query(payload: dict[str, Any], query: str | None) -> bool:
    if not query:
        return True
    lowered = query.lower()
    for text_value in _iter_text_values(payload):
        if lowered in text_value.lower():
            return True
    return False


def _matches_filters(entry: dict[str, Any], filters: SearchFilters) -> bool:
    if filters.verdict and _extract_verdict(entry) != filters.verdict:
        return False
    if filters.resonance and _extract_resonance(entry) != filters.resonance:
        return False
    if filters.genesis and _extract_genesis(entry) != filters.genesis:
        return False

    if filters.date_from or filters.date_to:
        ts_value = _extract_timestamp(entry)
        parsed_ts = _parse_timestamp(ts_value)
        if parsed_ts is None:
            return False
        ts_date = parsed_ts.date()
        if filters.date_from and ts_date < filters.date_from:
            return False
        if filters.date_to and ts_date > filters.date_to:
            return False

    return True


def iter_journal(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                yield line_number, payload


def search_entries(
    journal_path: Path,
    query: str | None,
    filters: SearchFilters,
    limit: int,
) -> tuple[list[SearchResult], int]:
    results: list[SearchResult] = []
    scanned = 0

    if not journal_path.exists():
        return results, scanned

    normalized_query = query.strip() if query else None
    for line_number, raw in iter_journal(journal_path):
        scanned += 1
        entry = _entry_payload(raw)
        if not _matches_query(entry, normalized_query):
            continue
        if not _matches_filters(entry, filters):
            continue

        delta_before, delta_after = _extract_deltas(entry)
        results.append(
            SearchResult(
                timestamp=_extract_timestamp(entry),
                verdict=_extract_verdict(entry),
                resonance=_extract_resonance(entry),
                genesis=_extract_genesis(entry),
                prompt=_extract_prompt(entry),
                delta_before=delta_before,
                delta_after=delta_after,
                line_number=line_number,
            )
        )
        if len(results) >= limit:
            break

    return results, scanned


def _format_delta(before: float | None, after: float | None) -> str:
    if before is None or after is None:
        return "delta: n/a"
    state = "convergence" if after < before else "non-convergent"
    return f"delta_before: {before:.4f} -> delta_after: {after:.4f} ({state})"


def render_results(
    results: list[SearchResult],
    query: str | None,
    filters: SearchFilters,
    scanned: int,
) -> str:
    lines: list[str] = []
    for item in results:
        lines.append(
            f"[{item.timestamp}] verdict={item.verdict} resonance={item.resonance} genesis={item.genesis}"
        )
        prompt = item.prompt if item.prompt else "(no prompt text)"
        lines.append(f"  prompt: {prompt}")
        lines.append(f"  {_format_delta(item.delta_before, item.delta_after)}")
        lines.append(f"  line: {item.line_number}")
        lines.append("")

    query_label = query if query else "*"
    lines.append(
        f"Found {len(results)} entries matching {query_label!r} "
        f"(verdict={filters.verdict or '*'}, resonance={filters.resonance or '*'}, "
        f"genesis={filters.genesis or '*'}, scanned={scanned})"
    )
    return "\n".join(lines)


def export_markdown(
    output_path: Path,
    results: list[SearchResult],
    query: str | None,
    filters: SearchFilters,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    query_label = query if query else "*"

    lines = [
        "# Journal Search Results",
        "",
        f"- query: `{query_label}`",
        f"- verdict: `{filters.verdict or '*'}`",
        f"- resonance: `{filters.resonance or '*'}`",
        f"- genesis: `{filters.genesis or '*'}`",
        f"- date_from: `{filters.date_from.isoformat() if filters.date_from else '*'}`",
        f"- date_to: `{filters.date_to.isoformat() if filters.date_to else '*'}`",
        "",
        "| timestamp | verdict | resonance | genesis | prompt | delta | line |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in results:
        prompt = (item.prompt or "").replace("|", "\\|")
        delta = _format_delta(item.delta_before, item.delta_after).replace("|", "\\|")
        lines.append(
            f"| {item.timestamp} | {item.verdict} | {item.resonance} | {item.genesis} | "
            f"{prompt} | {delta} | {item.line_number} |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search ToneSoul self journal JSONL.")
    parser.add_argument("query", nargs="?", default=None, help="Optional full-text query.")
    parser.add_argument("--journal-path", default=str(DEFAULT_JOURNAL), help="Journal JSONL path.")
    parser.add_argument(
        "--verdict", default=None, help="Filter verdict, e.g. approve/block/bypassed."
    )
    parser.add_argument(
        "--resonance",
        default=None,
        help="Filter resonance class, e.g. flow/resonance/deep_resonance/divergence.",
    )
    parser.add_argument("--genesis", default=None, help="Filter genesis source.")
    parser.add_argument("--date-from", default=None, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--date-to", default=None, help="End date (YYYY-MM-DD).")
    parser.add_argument("--limit", type=int, default=20, help="Maximum result count.")
    parser.add_argument("--export", default=None, help="Optional markdown export path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.limit <= 0:
        parser.error("--limit must be greater than 0")

    try:
        filters = SearchFilters(
            verdict=(
                args.verdict.strip().lower()
                if isinstance(args.verdict, str) and args.verdict
                else None
            ),
            resonance=(
                args.resonance.strip().lower()
                if isinstance(args.resonance, str) and args.resonance
                else None
            ),
            genesis=(
                args.genesis.strip().lower()
                if isinstance(args.genesis, str) and args.genesis
                else None
            ),
            date_from=_parse_date(args.date_from),
            date_to=_parse_date(args.date_to),
        )
    except ValueError as exc:
        parser.error(str(exc))

    journal_path = Path(args.journal_path)
    results, scanned = search_entries(journal_path, args.query, filters, args.limit)
    _write_text(render_results(results, args.query, filters, scanned))

    if args.export:
        export_markdown(Path(args.export), results, args.query, filters)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
