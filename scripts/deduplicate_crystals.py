"""
Deduplicate memory/crystals.jsonl by rule.

Policy:
- Keep one row per normalized rule.
- Keep max(weight), max(access_count), latest created_at/source_pattern.
- Union tags with stable order.

Usage:
    python scripts/deduplicate_crystals.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.crystallizer import Crystal  # noqa: E402


def _parse_iso(value: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _norm_rule(value: str) -> str:
    return str(value or "").strip().lower()


def _sort_key(item: Crystal) -> Tuple[float, int, datetime]:
    return (float(item.weight), int(item.access_count), _parse_iso(item.created_at))


def deduplicate(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {"before": 0, "after": 0, "duplicates_removed": 0, "invalid_rows": 0}

    parsed: List[Crystal] = []
    invalid_rows = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                invalid_rows += 1
                continue
            crystal = Crystal.from_dict(payload if isinstance(payload, dict) else {})
            if crystal is None:
                invalid_rows += 1
                continue
            parsed.append(crystal)

    merged: Dict[str, Crystal] = {}
    for crystal in parsed:
        key = _norm_rule(crystal.rule)
        existing = merged.get(key)
        if existing is None:
            merged[key] = crystal
            continue

        current_dt = _parse_iso(existing.created_at)
        incoming_dt = _parse_iso(crystal.created_at)
        latest = crystal if incoming_dt >= current_dt else existing
        older = existing if latest is crystal else crystal
        tags = list(dict.fromkeys([*latest.tags, *older.tags]))
        merged[key] = Crystal(
            rule=latest.rule,
            source_pattern=latest.source_pattern,
            weight=max(float(existing.weight), float(crystal.weight)),
            created_at=latest.created_at,
            access_count=max(int(existing.access_count), int(crystal.access_count)),
            tags=tags,
        )

    unique = sorted(merged.values(), key=_sort_key, reverse=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in unique:
            handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    before = len(parsed)
    after = len(unique)
    return {
        "before": before,
        "after": after,
        "duplicates_removed": max(0, before - after),
        "invalid_rows": invalid_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deduplicate crystals.jsonl by rule.")
    parser.add_argument("--path", default="memory/crystals.jsonl", help="Path to crystals.jsonl")
    args = parser.parse_args()

    path = Path(args.path)
    stats = deduplicate(path)
    payload = {
        "path": str(path),
        "before": stats["before"],
        "after": stats["after"],
        "duplicates_removed": stats["duplicates_removed"],
        "invalid_rows": stats["invalid_rows"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
