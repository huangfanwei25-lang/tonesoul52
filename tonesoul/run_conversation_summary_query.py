import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def _resolve_workspace_root() -> Path:
    base = Path(__file__).resolve().parents[1]
    if (base / "memory").exists():
        return base
    return base.parent


def _read_jsonl(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    entries: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                entries.append(payload)
    return entries


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _sort_entries(entries: List[Dict[str, object]]) -> List[Dict[str, object]]:
    def sort_key(item: Dict[str, object]) -> float:
        ts = _parse_time(item.get("timestamp"))
        if ts:
            return ts.timestamp()
        return 0.0

    return sorted(entries, key=sort_key, reverse=True)


def _match_contains(entry: Dict[str, object], keyword: str) -> bool:
    if not keyword:
        return True
    key = keyword.lower()
    user_message = str(entry.get("user_message", "")).lower()
    summary = str(entry.get("assistant_summary", "")).lower()
    return key in user_message or key in summary


def _filter_entries(
    entries: List[Dict[str, object]],
    record_id: Optional[str],
    persona_id: Optional[str],
    status: Optional[str],
    keyword: Optional[str],
) -> List[Dict[str, object]]:
    filtered: List[Dict[str, object]] = []
    for entry in entries:
        if record_id and entry.get("record_id") != record_id:
            continue
        if status and str(entry.get("status", "")).lower() != status.lower():
            continue
        persona = entry.get("persona") if isinstance(entry.get("persona"), dict) else {}
        entry_persona = persona.get("id") if isinstance(persona, dict) else None
        if persona_id and entry_persona != persona_id:
            continue
        if keyword and not _match_contains(entry, keyword):
            continue
        filtered.append(entry)
    return filtered


def _build_index(entries: List[Dict[str, object]]) -> Dict[str, object]:
    by_status: Dict[str, int] = {}
    by_persona: Dict[str, int] = {}
    by_date: Dict[str, int] = {}

    for entry in entries:
        status = str(entry.get("status") or "unknown").lower()
        by_status[status] = by_status.get(status, 0) + 1

        persona = entry.get("persona") if isinstance(entry.get("persona"), dict) else {}
        persona_id = persona.get("id") if isinstance(persona, dict) else "base"
        by_persona[persona_id] = by_persona.get(persona_id, 0) + 1

        ts = _parse_time(entry.get("timestamp"))
        if ts:
            date_key = ts.strftime("%Y-%m-%d")
            by_date[date_key] = by_date.get(date_key, 0) + 1

    return {
        "total": len(entries),
        "by_status": by_status,
        "by_persona": by_persona,
        "by_date": by_date,
    }


def _format_entry(entry: Dict[str, object]) -> str:
    ts = entry.get("timestamp") or ""
    status = entry.get("status") or "unknown"
    persona = entry.get("persona") if isinstance(entry.get("persona"), dict) else {}
    persona_id = persona.get("id") if isinstance(persona, dict) else "base"
    user_message = str(entry.get("user_message", "")).replace("\n", " ")
    assistant_summary = str(entry.get("assistant_summary", "")).replace("\n", " ")
    user_text = user_message[:60] + ("..." if len(user_message) > 60 else "")
    assistant_text = assistant_summary[:80] + ("..." if len(assistant_summary) > 80 else "")
    return f"{ts} | {status} | {persona_id} | {user_text} | {assistant_text}"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query conversation summary ledger.")
    parser.add_argument("--workspace", help="Workspace root path.")
    parser.add_argument("--summary", help="Path to conversation_summary.jsonl.")
    parser.add_argument("--record-id", help="Filter by record_id.")
    parser.add_argument("--persona", help="Filter by persona id.")
    parser.add_argument("--status", help="Filter by status.")
    parser.add_argument("--contains", help="Keyword search in user/summary.")
    parser.add_argument("--limit", type=int, default=20, help="Limit results.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Output aggregated index only.",
    )
    parser.add_argument("--output", help="Optional output file.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve() if args.workspace else _resolve_workspace_root()
    summary_path = (
        Path(args.summary) if args.summary else workspace / "memory" / "conversation_summary.jsonl"
    )
    entries = _read_jsonl(summary_path)
    if not entries:
        print(f"No summaries found at {summary_path}")
        return 1

    entries = _filter_entries(
        entries,
        record_id=args.record_id,
        persona_id=args.persona,
        status=args.status,
        keyword=args.contains,
    )
    entries = _sort_entries(entries)

    if args.limit and args.limit > 0:
        entries = entries[: args.limit]

    output: object
    if args.index:
        output = _build_index(entries)
    else:
        output = (
            entries
            if args.format == "json"
            else "\n".join(_format_entry(entry) for entry in entries)
        )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "json" or args.index:
            output_path.write_text(
                json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        else:
            output_path.write_text(str(output), encoding="utf-8")
    else:
        if args.format == "json" or args.index:
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
