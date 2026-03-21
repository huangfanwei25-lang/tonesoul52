"""Helpers for compact cross-artifact status alignment lines."""

from __future__ import annotations

from typing import Mapping


def _coerce_text(value: object) -> str:
    return str(value or "").strip()


def _route_family(route_status_line: str) -> str:
    for token in route_status_line.split():
        if token.startswith("family="):
            return token.split("=", 1)[1].strip()
    return ""


def _secondary_labels(raw_labels: str) -> list[str]:
    labels = [item.strip() for item in raw_labels.split(",")]
    return [item for item in labels if item]


def build_dream_weekly_alignment_line(
    weekly_preview: Mapping[str, object] | None,
    dream_preview: Mapping[str, object] | None,
) -> str:
    if not isinstance(weekly_preview, Mapping) or not isinstance(dream_preview, Mapping):
        return ""

    weekly_family = _route_family(_coerce_text(weekly_preview.get("problem_route_status_line")))
    dream_family = _route_family(_coerce_text(dream_preview.get("problem_route_status_line")))
    if not weekly_family and not dream_family:
        return ""

    if weekly_family and dream_family:
        relation = "aligned" if weekly_family == dream_family else "diverged"
    else:
        relation = "partial"

    weekly_secondary = set(
        _secondary_labels(_coerce_text(weekly_preview.get("problem_route_secondary_labels")))
    )
    dream_secondary = set(
        _secondary_labels(_coerce_text(dream_preview.get("problem_route_secondary_labels")))
    )
    shared_secondary = sorted(weekly_secondary & dream_secondary)

    parts = [f"alignment={relation}"]
    if weekly_family:
        parts.append(f"weekly={weekly_family}")
    if dream_family:
        parts.append(f"dream={dream_family}")
    if shared_secondary:
        parts.append(f"shared_secondary={','.join(shared_secondary)}")
    return "dream_weekly_alignment | " + " ".join(parts)
