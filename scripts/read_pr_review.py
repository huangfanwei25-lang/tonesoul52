"""Read a PR's review in one command — the Tier-2 Codex<->Claude bridge read side.

`gh pr view --comments` does NOT include inline (line-level) review comments — a known gh
limitation. This pulls all three surfaces and formats them readably:

  1. review summaries  (gh pr view --json reviews)        — APPROVED / CHANGES_REQUESTED / COMMENTED + body
  2. inline comments   (gh api .../pulls/<pr>/comments)   — per-file, per-line review threads
  3. conversation      (gh pr view --json comments)       — top-level PR comments

So when Codex (or any reviewer) posts a review to the PR, Claude reads it with one command
instead of the human relaying it: `python scripts/read_pr_review.py <pr> --author codex`.

The formatting is a pure function (testable without network); the gh calls are a thin shell.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Optional


def _gh(args: List[str]) -> str:
    """Thin gh shell. utf-8 with replace so Windows cp950 never crashes the read."""
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _matches(author: str, author_filter: Optional[str]) -> bool:
    return author_filter is None or author_filter.lower() in (author or "").lower()


def format_review(
    reviews: List[Dict[str, Any]],
    inline: List[Dict[str, Any]],
    comments: List[Dict[str, Any]],
    author_filter: Optional[str] = None,
) -> str:
    """Pure formatter: all three review surfaces → readable text. No network."""
    lines: List[str] = []

    rv = [
        r
        for r in reviews
        if _matches(_author(r), author_filter) and (r.get("body") or r.get("state"))
    ]
    lines.append(f"## Review summaries ({len(rv)})")
    for r in rv:
        body = (r.get("body") or "").strip()
        lines.append(f"  [{r.get('state', '?')}] @{_author(r)}")
        if body:
            lines.extend(f"      {ln}" for ln in body.splitlines())

    inl = [c for c in inline if _matches(_author(c), author_filter)]
    lines.append(f"\n## Inline comments ({len(inl)})")
    for c in inl:
        loc = c.get("path", "?")
        line_no = c.get("line") or c.get("original_line")
        if line_no:
            loc += f":{line_no}"
        lines.append(f"  @{_author(c)} — {loc}")
        for ln in (c.get("body") or "").strip().splitlines():
            lines.append(f"      {ln}")

    cm = [
        c for c in comments if _matches(_author(c), author_filter) and (c.get("body") or "").strip()
    ]
    lines.append(f"\n## Conversation comments ({len(cm)})")
    for c in cm:
        lines.append(f"  @{_author(c)}")
        for ln in (c.get("body") or "").strip().splitlines():
            lines.append(f"      {ln}")

    if not (rv or inl or cm):
        suffix = f" from an author matching '{author_filter}'" if author_filter else ""
        lines.append(f"\n(no review content found{suffix})")
    return "\n".join(lines)


def _author(obj: Dict[str, Any]) -> str:
    """gh pr view uses {'author': {'login': ...}}; gh api uses {'user': {'login': ...}}."""
    a = obj.get("author") or obj.get("user") or {}
    if isinstance(a, dict):
        return a.get("login") or a.get("name") or "?"
    return str(a) if a else "?"


def fetch(pr: str) -> Dict[str, List[Dict[str, Any]]]:  # pragma: no cover - network
    view = json.loads(_gh(["pr", "view", pr, "--json", "reviews,comments"]))
    repo = json.loads(_gh(["repo", "view", "--json", "nameWithOwner"]))["nameWithOwner"]
    inline = json.loads(_gh(["api", f"repos/{repo}/pulls/{pr}/comments", "--paginate"]))
    return {
        "reviews": view.get("reviews", []),
        "comments": view.get("comments", []),
        "inline": inline if isinstance(inline, list) else [],
    }


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - thin CLI
    import argparse
    import sys

    p = argparse.ArgumentParser(prog="read_pr_review", description=__doc__)
    p.add_argument("pr", help="PR number")
    p.add_argument(
        "--author", help="only show content from authors matching this substring (e.g. codex)"
    )
    args = p.parse_args(argv)
    data = fetch(args.pr)
    out = format_review(data["reviews"], data["inline"], data["comments"], args.author)
    sys.stdout.buffer.write((out + "\n").encode("utf-8", errors="replace"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
