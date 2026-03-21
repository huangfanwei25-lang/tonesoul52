from __future__ import annotations

from typing import Iterable, Mapping


def normalize_status_lines(lines: object) -> list[str]:
    if not isinstance(lines, Iterable) or isinstance(lines, (str, bytes, dict)):
        return []
    normalized: list[str] = []
    for line in lines:
        text = str(line or "").strip()
        if text:
            normalized.append(text)
    return normalized


def primary_status_line(lines: object) -> str:
    normalized = normalize_status_lines(lines)
    return normalized[0] if normalized else ""


def build_handoff_surface(
    *,
    queue_shape: str,
    requires_operator_action: bool,
    status_lines: object,
    extra_fields: Mapping[str, object] | None = None,
) -> dict[str, object]:
    handoff = {
        "queue_shape": str(queue_shape or ""),
        "requires_operator_action": bool(requires_operator_action),
    }
    if isinstance(extra_fields, Mapping):
        handoff.update(dict(extra_fields))
    handoff["primary_status_line"] = primary_status_line(status_lines)
    return handoff


def extend_handoff_markdown(
    lines: list[str],
    *,
    handoff: object,
    extra_fields: Iterable[str] | None = None,
) -> None:
    if not isinstance(handoff, Mapping) or not handoff:
        return
    lines.extend(
        [
            "",
            "## Handoff",
            f"- queue_shape: {handoff.get('queue_shape', '')}",
            "- requires_operator_action: "
            f"{str(handoff.get('requires_operator_action', False)).lower()}",
        ]
    )
    for name in list(extra_fields or []):
        lines.append(f"- {name}: {handoff.get(name, '')}")
    lines.append(f"- primary_status_line: {handoff.get('primary_status_line', '')}")


def extend_status_lines_markdown(lines: list[str], status_lines: object) -> None:
    normalized = normalize_status_lines(status_lines)
    lines.extend(["", "## Status Lines"])
    if normalized:
        for line in normalized:
            lines.append(f"- {line}")
        return
    lines.append("- None")


__all__ = [
    "build_handoff_surface",
    "extend_handoff_markdown",
    "extend_status_lines_markdown",
    "normalize_status_lines",
    "primary_status_line",
]
