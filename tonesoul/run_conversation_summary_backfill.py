import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


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


def _read_existing_record_ids(path: Path) -> set[str]:
    record_ids: set[str] = set()
    if not path.exists():
        return record_ids
    for entry in _read_jsonl(path):
        record_id = entry.get("record_id")
        if isinstance(record_id, str) and record_id:
            record_ids.add(record_id)
    return record_ids


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _timestamp_key(value: Optional[str]) -> Optional[str]:
    parsed = _parse_timestamp(value)
    if not parsed:
        return None
    return parsed.strftime("%Y-%m-%dT%H:%M:%S")


def _truncate(text: str, limit: int = 200) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _resolve_workspace_root() -> Path:
    base = Path(__file__).resolve().parents[1]
    if (base / "memory").exists():
        return base
    fallback = base.parent
    return fallback


def _load_persona_profile(workspace: Path, persona_id: str) -> Optional[Dict[str, object]]:
    if not persona_id:
        return None
    path = workspace / "memory" / "personas" / f"{persona_id}.yaml"
    if not path.exists():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "id": payload.get("id") or persona_id,
        "name": payload.get("name"),
        "home_vector": payload.get("home_vector"),
        "tolerance": payload.get("tolerance"),
        "council_weights": payload.get("council_weights"),
        "goal_weights": payload.get("goal_weights"),
    }


def _build_trace_lookup(entries: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    lookup: Dict[str, Dict[str, object]] = {}
    for entry in entries:
        record_id = entry.get("record_id")
        if isinstance(record_id, str) and record_id and record_id not in lookup:
            lookup[record_id] = entry
    return lookup


def _build_trace_time_lookup(entries: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    lookup: Dict[str, Dict[str, object]] = {}
    for entry in entries:
        time_key = _timestamp_key(entry.get("timestamp"))
        if time_key and time_key not in lookup:
            lookup[time_key] = entry
    return lookup


def _derive_record_id(entry: Dict[str, object], index: int) -> str:
    record_id = entry.get("record_id")
    if isinstance(record_id, str) and record_id:
        return record_id
    time_key = _timestamp_key(entry.get("timestamp"))
    if time_key:
        return time_key.replace("-", "").replace(":", "").replace("T", "")
    return f"legacy_{index:04d}"


def _extract_user_message(entry: Dict[str, object]) -> str:
    context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
    return context.get("user_message") or entry.get("user_message") or ""


def _extract_response(entry: Dict[str, object]) -> str:
    response = entry.get("response")
    return response if isinstance(response, str) else ""


def _build_summary(
    entry: Dict[str, object],
    record_id: str,
    persona_id: str,
    trace_entry: Optional[Dict[str, object]],
    persona_profile: Optional[Dict[str, object]],
) -> Dict[str, object]:
    summary_id = f"summary_{record_id}"
    response = _extract_response(entry)
    shadow = trace_entry.get("shadow") if isinstance(trace_entry, dict) else {}
    vector_estimate = (
        shadow.get("vector_estimate") if isinstance(shadow.get("vector_estimate"), dict) else None
    )
    vector_distance = (
        shadow.get("vector_distance") if isinstance(shadow.get("vector_distance"), dict) else None
    )

    return {
        "summary_id": summary_id,
        "record_id": record_id,
        "timestamp": entry.get("timestamp"),
        "status": entry.get("status") or "unknown",
        "user_message": _extract_user_message(entry),
        "assistant_summary": _truncate(response),
        "persona": {
            "id": persona_id,
            "trace_record_id": (
                trace_entry.get("record_id") if isinstance(trace_entry, dict) else None
            ),
            "vector_estimate": vector_estimate,
            "vector_distance": vector_distance,
            "profile": persona_profile,
        },
        "intent": {},
        "control": {},
        "run_id": entry.get("run_id"),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill conversation summaries.")
    parser.add_argument("--workspace", help="Workspace root path.")
    parser.add_argument("--ledger", help="conversation_ledger.jsonl path.")
    parser.add_argument("--summary", help="conversation_summary.jsonl path.")
    parser.add_argument("--limit", type=int, default=0, help="Limit entries to process.")
    parser.add_argument("--force", action="store_true", help="Rebuild all summaries.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write output.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve() if args.workspace else _resolve_workspace_root()
    ledger_path = (
        Path(args.ledger) if args.ledger else workspace / "memory" / "conversation_ledger.jsonl"
    )
    summary_path = (
        Path(args.summary) if args.summary else workspace / "memory" / "conversation_summary.jsonl"
    )

    conversations = _read_jsonl(ledger_path)
    if not conversations:
        print(f"No conversations found at {ledger_path}")
        return 1

    existing_ids = set() if args.force else _read_existing_record_ids(summary_path)
    trace_entries = _read_jsonl(workspace / "memory" / "persona_trace.jsonl")
    trace_by_id = _build_trace_lookup(trace_entries)
    trace_by_time = _build_trace_time_lookup(trace_entries)

    written = 0
    skipped = 0
    limit = args.limit if args.limit and args.limit > 0 else None

    output_lines: List[str] = []
    for idx, entry in enumerate(conversations):
        if limit is not None and written >= limit:
            break
        record_id = _derive_record_id(entry, idx)
        if record_id in existing_ids:
            skipped += 1
            continue
        persona_id = entry.get("persona_id") or "base"
        persona_profile = _load_persona_profile(workspace, persona_id)
        trace_entry = trace_by_id.get(record_id)
        if not trace_entry:
            time_key = _timestamp_key(entry.get("timestamp"))
            if time_key:
                trace_entry = trace_by_time.get(time_key)

        summary = _build_summary(entry, record_id, persona_id, trace_entry, persona_profile)
        output_lines.append(json.dumps(summary, ensure_ascii=False))
        written += 1

    if args.dry_run:
        print(f"Dry run complete. New summaries: {written}, skipped: {skipped}")
        return 0

    if output_lines:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with summary_path.open("a", encoding="utf-8") as handle:
            for line in output_lines:
                handle.write(line + "\n")

    print(f"Summary backfill complete. New: {written}, skipped: {skipped}")
    print(f"Output: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
