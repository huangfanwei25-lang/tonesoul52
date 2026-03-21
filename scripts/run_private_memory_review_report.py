"""Report dirty private-memory artifacts without collapsing them into public branch content."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.plan_commit_attribution_base_switch as planner  # noqa: E402

JSON_FILENAME = "private_memory_review_latest.json"
MARKDOWN_FILENAME = "private_memory_review_latest.md"

ARCHIVE_PATTERNS: list[tuple[str, str]] = [
    ("memory/antigravity_", "private_journal"),
    ("memory/autonomous/", "private_runtime_namespace"),
]

MIRROR_PATTERNS: list[tuple[str, str]] = [
    ("memory/architecture_reflection_", "mirrored_private_memory"),
    ("memory/crystals.jsonl", "mirrored_private_memory"),
]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _resolve_path(repo_root: Path, value: str) -> Path:
    raw = Path(str(value).strip())
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def _dirty_private_memory_entries(repo_root: Path) -> list[dict[str, Any]]:
    return [
        entry
        for entry in planner.collect_worktree_entries(repo_root)
        if str(entry.get("category") or "") == "memory"
    ]


def _classify_entry(entry: dict[str, Any]) -> dict[str, Any]:
    path = str(entry.get("path") or "").replace("\\", "/")

    for prefix, kind in MIRROR_PATTERNS:
        if path == prefix or path.startswith(prefix):
            return {
                "path": path,
                "category": entry.get("category"),
                "kind": kind,
                "disposition": "mirror_then_archive",
                "notes": "Mirror public-safe learnings into task/reflection/status artifacts, then treat the original memory file as private evidence.",
                "status": entry.get("status"),
                "staged": bool(entry.get("staged")),
                "unstaged": bool(entry.get("unstaged")),
                "untracked": bool(entry.get("untracked")),
            }

    for prefix, kind in ARCHIVE_PATTERNS:
        if path.startswith(prefix):
            notes = (
                "Treat this as private runtime evidence and keep it outside public branch movement."
                if kind == "private_runtime_namespace"
                else "Treat this as private narrative or planning evidence; archive to the private path instead of using it as public branch payload."
            )
            return {
                "path": path,
                "category": entry.get("category"),
                "kind": kind,
                "disposition": "archive_to_private",
                "notes": notes,
                "status": entry.get("status"),
                "staged": bool(entry.get("staged")),
                "unstaged": bool(entry.get("unstaged")),
                "untracked": bool(entry.get("untracked")),
            }

    return {
        "path": path,
        "category": entry.get("category"),
        "kind": "unknown_private_memory",
        "disposition": "inspect",
        "notes": "Private-memory path needs an explicit keep/mirror/archive decision before branch movement.",
        "status": entry.get("status"),
        "staged": bool(entry.get("staged")),
        "unstaged": bool(entry.get("unstaged")),
        "untracked": bool(entry.get("untracked")),
    }


def _group_counts(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(counts.items())]


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Private Memory Review Latest", ""]
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Overall OK: `{str(payload['overall_ok']).lower()}`")
    lines.append(f"- Dirty private memory entries: `{payload['summary']['entry_count']}`")
    lines.append(
        f"- Mirror-then-archive items: `{payload['summary']['mirror_then_archive_count']}`"
    )
    lines.append(f"- Archive-to-private items: `{payload['summary']['archive_to_private_count']}`")
    lines.append(f"- Inspect items: `{payload['summary']['inspect_count']}`")
    lines.append("")
    lines.append("## Mirror Then Archive")
    lines.append("")
    mirror_items = [
        item for item in payload["entries"] if item["disposition"] == "mirror_then_archive"
    ]
    if mirror_items:
        for item in mirror_items:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
            lines.append(f"  - notes: `{item['notes']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Archive To Private")
    lines.append("")
    archive_items = [
        item for item in payload["entries"] if item["disposition"] == "archive_to_private"
    ]
    if archive_items:
        for item in archive_items:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
            lines.append(f"  - notes: `{item['notes']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Inspect")
    lines.append("")
    inspect_items = [item for item in payload["entries"] if item["disposition"] == "inspect"]
    if inspect_items:
        for item in inspect_items:
            lines.append(f"- `{item['path']}` (`{item['kind']}`)")
            lines.append(f"  - notes: `{item['notes']}`")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def build_report(repo_root: Path) -> tuple[dict[str, Any], str]:
    entries = [_classify_entry(entry) for entry in _dirty_private_memory_entries(repo_root)]
    summary = {
        "entry_count": len(entries),
        "mirror_then_archive_count": sum(
            1 for item in entries if item["disposition"] == "mirror_then_archive"
        ),
        "archive_to_private_count": sum(
            1 for item in entries if item["disposition"] == "archive_to_private"
        ),
        "inspect_count": sum(1 for item in entries if item["disposition"] == "inspect"),
        "kind_counts": _group_counts(entries, "kind"),
        "disposition_counts": _group_counts(entries, "disposition"),
    }
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(entries) == 0,
        "source": "scripts/run_private_memory_review_report.py",
        "summary": summary,
        "entries": entries,
        "issues": [] if not entries else ["private_memory_lane_still_dirty"],
        "warnings": [],
    }
    return payload, _render_markdown(payload)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report dirty private-memory artifacts and their settlement semantics."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Directory for status artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero while dirty private memory artifacts remain.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = _resolve_path(repo_root, args.out_dir)
    payload, markdown = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
