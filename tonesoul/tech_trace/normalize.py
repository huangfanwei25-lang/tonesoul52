import argparse
import json
import os
import re
from typing import Dict, List, Optional

from .capture import load_text, normalize_tags, stable_hash, utc_now


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _prune_none(value: object) -> object:
    if isinstance(value, dict):
        return {key: _prune_none(val) for key, val in value.items() if val is not None}
    if isinstance(value, list):
        return [_prune_none(item) for item in value if item is not None]
    return value


def _collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def _summary_from_text(text: str, limit: int) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _extract_claims(text: str, limit: int, min_chars: int) -> List[str]:
    if not text:
        return []
    if limit <= 0:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    cleaned = []
    for sentence in sentences:
        item = sentence.strip()
        if len(item) < min_chars:
            continue
        cleaned.append(item)
        if len(cleaned) >= limit:
            break
    if not cleaned and len(text.strip()) >= min_chars:
        cleaned.append(text.strip())
    return cleaned[:limit]


def _load_json_arg(value: Optional[str], label: str) -> Optional[object]:
    if value is None:
        return None
    try:
        if os.path.exists(value):
            with open(value, "r", encoding="utf-8-sig") as handle:
                payload = json.load(handle)
        else:
            payload = json.loads(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be JSON or a JSON file path: {exc}") from exc
    return payload


def _normalize_claims(claims: Optional[object]) -> Optional[List[Dict[str, object]]]:
    if claims is None:
        return None
    if not isinstance(claims, list):
        raise ValueError("claims must be a JSON list.")
    normalized: List[Dict[str, object]] = []
    for idx, item in enumerate(claims):
        if isinstance(item, str):
            text = item.strip()
            if not text:
                continue
            normalized.append(
                {
                    "id": f"claim_{stable_hash(f'{idx}:{text}')}",
                    "text": text,
                }
            )
            continue
        if isinstance(item, dict):
            entry = dict(item)
            text = entry.get("text") or entry.get("claim") or entry.get("statement")
            if text and "text" not in entry:
                entry["text"] = text
            if "id" not in entry and isinstance(text, str) and text:
                entry["id"] = f"claim_{stable_hash(f'{idx}:{text}')}"
            normalized.append(entry)
    return normalized or None


def _normalize_links(links: Optional[object]) -> Optional[List[Dict[str, object]]]:
    if links is None:
        return None
    if not isinstance(links, list):
        raise ValueError("links must be a JSON list.")
    normalized: List[Dict[str, object]] = []
    for item in links:
        if isinstance(item, str):
            uri = item.strip()
            if not uri:
                continue
            normalized.append({"uri": uri})
            continue
        if isinstance(item, dict):
            normalized.append(dict(item))
    return normalized or None


def _normalize_attributions(attributions: Optional[object]) -> Optional[List[Dict[str, object]]]:
    if attributions is None:
        return None
    if not isinstance(attributions, list):
        raise ValueError("attributions must be a JSON list.")
    normalized: List[Dict[str, object]] = []
    for item in attributions:
        if isinstance(item, str):
            ref = item.strip()
            if not ref:
                continue
            normalized.append({"reference": ref})
            continue
        if isinstance(item, dict):
            normalized.append(dict(item))
    return normalized or None


def normalize_record(
    raw_text: str,
    capture_id: Optional[str],
    source: Dict[str, object],
    source_grade: Optional[str],
    summary: Optional[str],
    notes: Optional[str],
    tags: Optional[list],
    max_length: Optional[int],
    claims: Optional[object],
    links: Optional[object],
    attributions: Optional[object],
    auto_claims: bool = False,
    auto_claim_limit: int = 12,
    auto_claim_min_chars: int = 24,
) -> Dict[str, object]:
    normalized_text = _collapse_whitespace(raw_text)
    if max_length and max_length > 0:
        normalized_text = normalized_text[:max_length]
    summary_text = summary or _summary_from_text(normalized_text, 160)
    claim_source = claims
    if claim_source is None and auto_claims:
        claim_source = _extract_claims(normalized_text, auto_claim_limit, auto_claim_min_chars)
    stamp = utc_now()
    normalize_id = f"normalize_{stable_hash(f'{stamp}:{len(normalized_text)}')}"
    payload = {
        "normalize_id": normalize_id,
        "normalized_at": stamp,
        "capture_id": capture_id,
        "source": _prune_none(source),
        "source_grade": source_grade,
        "summary": summary_text,
        "normalized_text": normalized_text,
        "claims": _normalize_claims(claim_source),
        "links": _normalize_links(links),
        "attributions": _normalize_attributions(attributions),
        "raw_hash": stable_hash(raw_text),
        "normalized_hash": stable_hash(normalized_text),
        "notes": notes,
        "tags": normalize_tags(tags),
    }
    return _prune_none(payload)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize a Tech-Trace capture note.")
    parser.add_argument("--input", help="Capture JSON to normalize.")
    parser.add_argument("--text", help="Inline text (used if --input missing).")
    parser.add_argument("--source-type", default="unknown", help="Source type override.")
    parser.add_argument("--uri", help="Source URI override.")
    parser.add_argument("--title", help="Source title override.")
    parser.add_argument("--source-grade", choices=["A", "B", "C"], help="Evidence grade override.")
    parser.add_argument("--summary", help="Optional summary.")
    parser.add_argument("--notes", help="Optional notes.")
    parser.add_argument("--tag", action="append", help="Tag (repeatable).")
    parser.add_argument("--max-length", type=int, help="Max length for normalized text.")
    parser.add_argument("--claims", help="JSON list or path for claim objects.")
    parser.add_argument("--links", help="JSON list or path for related links.")
    parser.add_argument("--attributions", help="JSON list or path for claim source refs.")
    parser.add_argument(
        "--auto-claims",
        action="store_true",
        help="Auto-extract claims from text when --claims is not provided.",
    )
    parser.add_argument(
        "--auto-claim-limit",
        type=int,
        default=12,
        help="Max claim count for auto-extraction.",
    )
    parser.add_argument(
        "--auto-claim-min-chars",
        type=int,
        default=24,
        help="Minimum characters for auto-extracted claims.",
    )
    parser.add_argument("--output", help="Output JSON path.")
    return parser


def _load_capture(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Capture payload must be a JSON object.")
    return payload


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()

    capture_payload = None
    if args.input:
        capture_payload = _load_capture(args.input)
        raw_text = str(capture_payload.get("raw_text") or capture_payload.get("text") or "")
    else:
        raw_text = load_text(None, args.text)

    if not raw_text:
        parser.error("Provide --input with raw_text or pass --text.")

    capture_id = capture_payload.get("capture_id") if isinstance(capture_payload, dict) else None
    source = {}
    if capture_payload and isinstance(capture_payload.get("source"), dict):
        source = dict(capture_payload["source"])

    if args.source_type:
        source["type"] = args.source_type
    if args.uri:
        source["uri"] = args.uri
    if args.title:
        source["title"] = args.title

    source_grade = args.source_grade
    if source_grade is None and isinstance(source, dict):
        source_grade = source.get("grade")

    try:
        claims = _load_json_arg(args.claims, "--claims")
        links = _load_json_arg(args.links, "--links")
        attributions = _load_json_arg(args.attributions, "--attributions")
    except ValueError as exc:
        parser.error(str(exc))

    payload = normalize_record(
        raw_text=raw_text,
        capture_id=capture_id if isinstance(capture_id, str) else None,
        source=source,
        source_grade=source_grade,
        summary=args.summary,
        notes=args.notes,
        tags=args.tag,
        max_length=args.max_length,
        claims=claims,
        links=links,
        attributions=attributions,
        auto_claims=args.auto_claims,
        auto_claim_limit=args.auto_claim_limit,
        auto_claim_min_chars=args.auto_claim_min_chars,
    )

    output_path = args.output
    if not output_path:
        output_dir = os.path.join(_workspace_root(), "generated", "tech_trace")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{payload['normalize_id']}.json")
    else:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return {"normalized": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"normalized.json: {paths['normalized']}")
