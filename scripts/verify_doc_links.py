"""
Verify relative markdown links in tracked docs resolve to tracked files.

Why this exists (2026-07-02): an external audit found ~145 broken markdown links,
including 19 absolute Windows paths leaking the local directory layout, and 6 links
that resolve on the author's disk but are dead in any fresh clone (target present
but untracked). One-time cleanup rots; this verifier makes link integrity a
checkable, fail-able condition, same pattern as verify_status_freshness.py.

Rules:
- Only tracked *.md files are scanned (git ls-files -z; C-quoting-safe for
  non-ASCII filenames like docs/環境設定.md).
- Fenced code blocks (```) are skipped — recovered/damaged docs contain
  link-shaped fragments inside fences that are not navigation.
- http(s)/mailto/#anchor links are ignored.
- FAILURE classes:
  - absolute: target is an absolute path (C:/..., /C:/..., /home/...) — leaks a
    machine layout and never resolves elsewhere.
  - missing: relative target does not exist.
  - untracked: relative target exists on disk but is not tracked — dead in a
    fresh clone (the failure a naive os.path.exists check cannot see).
- EXEMPT prefixes: frozen mirrors whose links are knowingly broken relative to
  their original repo root (see docs/design/tonesoul-reference/sources/_MIRROR_NOTICE.md).

Exit codes: 0 ok; 1 failures found and --strict given.

Usage:
    python scripts/verify_doc_links.py
    python scripts/verify_doc_links.py --strict
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_DIR = REPO_ROOT / "docs" / "status"
JSON_FILENAME = "doc_links_latest.json"
MARKDOWN_FILENAME = "doc_links_latest.md"

EXEMPT_PREFIXES = ("docs/design/tonesoul-reference/sources/",)

LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
ABSOLUTE_PATTERN = re.compile(r"^<?/?[A-Za-z]:[/\\]|^/(?:home|usr|tmp|Users)/")


@dataclass(frozen=True)
class LinkViolation:
    file: str
    line: int
    target: str
    kind: str  # absolute | missing | untracked


def list_tracked(repo_root: Path) -> set[str]:
    raw = subprocess.run(
        ["git", "ls-files", "-z"], cwd=repo_root, capture_output=True, check=True
    ).stdout.decode("utf-8")
    return {entry for entry in raw.split("\0") if entry}


def iter_links(text: str):
    """Yield (line_number, target) for markdown links outside fenced code blocks."""
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_PATTERN.finditer(line):
            yield line_no, match.group(2)


def check_file(md_path: str, text: str, tracked: set[str], repo_root: Path) -> list[LinkViolation]:
    violations: list[LinkViolation] = []
    base = (repo_root / md_path).parent
    for line_no, raw_target in iter_links(text):
        target = raw_target.split("#")[0]
        if not target or raw_target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if ABSOLUTE_PATTERN.match(target):
            violations.append(LinkViolation(md_path, line_no, raw_target, "absolute"))
            continue
        resolved = (base / target).resolve()
        try:
            rel = resolved.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            rel = None
        if not resolved.exists():
            violations.append(LinkViolation(md_path, line_no, raw_target, "missing"))
        elif rel is not None and resolved.is_file() and rel not in tracked:
            violations.append(LinkViolation(md_path, line_no, raw_target, "untracked"))
    return violations


def evaluate(repo_root: Path = REPO_ROOT, tracked: set[str] | None = None) -> dict:
    tracked_set = list_tracked(repo_root) if tracked is None else tracked
    md_files = sorted(f for f in tracked_set if f.endswith(".md"))
    violations: list[LinkViolation] = []
    scanned = exempt = 0
    for md_path in md_files:
        if any(md_path.startswith(prefix) for prefix in EXEMPT_PREFIXES):
            exempt += 1
            continue
        full = repo_root / md_path
        if not full.exists():  # tracked but not checked out (should not happen)
            continue
        scanned += 1
        text = full.read_text(encoding="utf-8", errors="replace")
        violations.extend(check_file(md_path, text, tracked_set, repo_root))
    counts = {
        kind: sum(1 for v in violations if v.kind == kind)
        for kind in ("absolute", "missing", "untracked")
    }
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "scripts/verify_doc_links.py",
        "overall_ok": not violations,
        "policy": {"exempt_prefixes": list(EXEMPT_PREFIXES)},
        "summary": {
            "md_files_scanned": scanned,
            "md_files_exempt": exempt,
            "violation_count": len(violations),
            **counts,
        },
        "violations": [asdict(v) for v in violations],
    }


def _render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Doc Links Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- overall_ok: `{str(payload['overall_ok']).lower()}`",
        f"- scanned: {summary['md_files_scanned']} (exempt mirror files: {summary['md_files_exempt']})",
        f"- violations: {summary['violation_count']}"
        f" (absolute {summary['absolute']}, missing {summary['missing']},"
        f" untracked {summary['untracked']})",
        "",
    ]
    if payload["violations"]:
        lines.append("| file | line | kind | target |")
        lines.append("|---|---|---|---|")
        for v in payload["violations"]:
            lines.append(f"| {v['file']} | {v['line']} | {v['kind']} | `{v['target']}` |")
        lines.append("")
    lines.append(
        "An `untracked` violation means the target exists on the author's disk but is"
        " dead in a fresh clone — the failure a naive existence check cannot see."
    )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify relative markdown links resolve to tracked files."
    )
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any violation.")
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Report only; do not update docs/status/doc_links_latest.*",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = evaluate()
    if not args.no_write:
        (STATUS_DIR / JSON_FILENAME).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (STATUS_DIR / MARKDOWN_FILENAME).write_text(
            _render_markdown(payload), encoding="utf-8", newline="\n"
        )
    summary = payload["summary"]
    print(
        "doc_links "
        f"ok={str(payload['overall_ok']).lower()} "
        f"scanned={summary['md_files_scanned']} violations={summary['violation_count']} "
        f"(absolute={summary['absolute']} missing={summary['missing']} "
        f"untracked={summary['untracked']})"
    )
    for v in payload["violations"][:20]:
        print(f"  FAIL {v['file']}:{v['line']} [{v['kind']}] {v['target']}")
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
