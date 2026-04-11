import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _prune_none(value: object) -> object:
    if isinstance(value, dict):
        return {key: _prune_none(val) for key, val in value.items() if val is not None}
    if isinstance(value, list):
        return [_prune_none(item) for item in value if item is not None]
    return value


def normalize_tags(tags: Optional[List[str]]) -> List[str]:
    if not tags:
        return []
    cleaned = []
    for item in tags:
        if not item:
            continue
        cleaned.append(item.strip())
    return [item for item in cleaned if item]


def load_text(path: Optional[str], text: Optional[str]) -> str:
    if text and text.strip():
        return text.strip()
    if not path:
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().strip()


def capture_record(
    raw_text: str,
    source_type: str,
    uri: Optional[str],
    title: Optional[str],
    grade: Optional[str],
    retrieved_at: Optional[str],
    verified_by: Optional[str],
    notes: Optional[str],
    tags: Optional[List[str]],
) -> Dict[str, object]:
    stamp = utc_now()
    capture_id = f"capture_{stable_hash(f'{stamp}:{len(raw_text)}:{source_type}')}"
    source = {
        "type": source_type,
        "uri": uri,
        "hash": stable_hash(raw_text) if raw_text else None,
        "title": title,
        "grade": grade,
        "retrieved_at": retrieved_at,
        "verified_by": verified_by,
    }
    payload = {
        "capture_id": capture_id,
        "captured_at": stamp,
        "source": _prune_none(source),
        "raw_text": raw_text,
        "notes": notes,
        "tags": normalize_tags(tags),
    }
    return _prune_none(payload)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a Tech-Trace source note.")
    parser.add_argument("--input", help="Optional input text file.")
    parser.add_argument("--text", help="Inline text to capture.")
    parser.add_argument(
        "--source-type", default="unknown", help="Source type (paper/blog/issue/etc)."
    )
    parser.add_argument("--uri", help="Source URI.")
    parser.add_argument("--title", help="Source title.")
    parser.add_argument("--grade", choices=["A", "B", "C"], help="Evidence grade.")
    parser.add_argument("--retrieved-at", help="Retrieval timestamp.")
    parser.add_argument("--verified-by", help="Verifier identity.")
    parser.add_argument("--notes", help="Optional notes.")
    parser.add_argument("--tag", action="append", help="Tag (repeatable).")
    parser.add_argument("--output", help="Output JSON path.")
    return parser


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    raw_text = load_text(args.input, args.text)
    if not raw_text:
        parser.error("Provide --text or --input with non-empty content.")

    payload = capture_record(
        raw_text=raw_text,
        source_type=args.source_type,
        uri=args.uri,
        title=args.title,
        grade=args.grade,
        retrieved_at=args.retrieved_at,
        verified_by=args.verified_by,
        notes=args.notes,
        tags=args.tag,
    )

    output_path = args.output
    if not output_path:
        output_dir = os.path.join(_workspace_root(), "generated", "tech_trace")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{payload['capture_id']}.json")
    else:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return {"capture": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"capture.json: {paths['capture']}")
