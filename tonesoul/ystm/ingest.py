import json
from typing import Dict, List, Optional, Sequence


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_optional_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_str(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _prune_none(value: object) -> object:
    if isinstance(value, dict):
        return {key: _prune_none(val) for key, val in value.items() if val is not None}
    if isinstance(value, list):
        return [_prune_none(item) for item in value if item is not None]
    return value


def load_segments(path: str) -> Sequence[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "segments" in payload:
        segments = payload["segments"]
    else:
        segments = payload
    if not isinstance(segments, list):
        raise ValueError("Input JSON must be a list of segments or {segments: [...]} wrapper.")
    return normalize_segments(segments)


def normalize_segments(segments: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    normalized: List[Dict[str, object]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ValueError("Each segment must be a JSON object.")
        for key in ("text", "mode", "domain"):
            if key not in segment:
                raise ValueError(f"Segment missing required field: {key}")
        source = segment.get("source") if isinstance(segment.get("source"), dict) else {}
        source_grade = _to_optional_str(segment.get("source_grade"))
        if source_grade is None:
            source_grade = _to_optional_str(source.get("grade"))
        source_payload = _prune_none(
            {
                "type": _to_optional_str(segment.get("source_type"))
                or _to_optional_str(source.get("type")),
                "uri": _to_optional_str(segment.get("source_uri"))
                or _to_optional_str(source.get("uri")),
                "hash": _to_optional_str(segment.get("source_hash"))
                or _to_optional_str(source.get("hash")),
                "grade": source_grade,
                "retrieved_at": _to_optional_str(segment.get("source_retrieved_at"))
                or _to_optional_str(source.get("retrieved_at")),
                "verified_by": _to_optional_str(segment.get("source_verified_by"))
                or _to_optional_str(source.get("verified_by")),
            }
        )
        math_coords = (
            segment.get("math_coords") if isinstance(segment.get("math_coords"), dict) else {}
        )
        math_payload = _prune_none(
            {
                "height": (
                    _to_optional_float(segment.get("math_height"))
                    if segment.get("math_height") is not None
                    else _to_optional_float(math_coords.get("height"))
                ),
                "geology": (
                    _to_optional_str(segment.get("math_geology"))
                    if segment.get("math_geology") is not None
                    else _to_optional_str(math_coords.get("geology"))
                ),
                "ruggedness": (
                    _to_optional_float(segment.get("math_ruggedness"))
                    if segment.get("math_ruggedness") is not None
                    else _to_optional_float(math_coords.get("ruggedness"))
                ),
            }
        )
        item = {
            "text": str(segment["text"]),
            "mode": str(segment["mode"]),
            "domain": str(segment["domain"]),
            "turn_id": int(segment.get("turn_id", index + 1)),
            "submode": segment.get("submode"),
            "subdomain": segment.get("subdomain"),
            "mode_confidence": _to_float(segment.get("mode_confidence", 0.9), 0.9),
            "domain_confidence": _to_float(segment.get("domain_confidence", 0.9), 0.9),
            "timestamp": segment.get("timestamp"),
            "version_id": segment.get("version_id"),
            "E_srsp": _to_float(segment.get("E_srsp", 0.0), 0.0),
            "E_risk": _to_float(segment.get("E_risk", 0.0), 0.0),
        }
        if source_payload:
            item["source"] = source_payload
        if source_grade:
            item["source_grade"] = source_grade
        if math_payload:
            item["math_coords"] = math_payload
        normalized.append(item)
    return normalized
