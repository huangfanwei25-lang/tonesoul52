#!/usr/bin/env python3
"""PR preflight guard — surface a branch's TRUE scope before you assert it.

Why this exists
---------------
A recurring stale-reference error (memory: feedback_stale_reference_recurrence_pattern;
trace: docs/status/session_retrospective_2026-05-10_to_05-14.md) is asserting a PR's
file scope from ``git diff --cached`` (one's own *commit*) instead of the cumulative
diff vs master, and creating a branch without verifying its base — which silently
stacks one PR on another. PR #188 (2026-06-25) did exactly this: its body claimed
"exactly 2 files" while the GitHub diff was 10, because the branch had been cut from
another agent's PR branch.

The fix is structural, not vigilance: run one command that prints the *cumulative*
scope vs origin/master and flags likely stacking, so the scope you assert comes from
the truth, not from a narrower green proxy.

Honest boundary: this is a frequency-reducer, not a guarantee. The same blind spot
that produced the error can blind the self-check. The external reviewer remains the
backstop for scope/claim accuracy — the author cannot fully self-verify the thing
they are blind to.

Usage
-----
    python scripts/pr_preflight.py            # check current branch vs origin/master
    python scripts/pr_preflight.py --pr 188   # also cross-check GitHub's reported files
    python scripts/pr_preflight.py --no-fetch # skip git fetch (offline)

Exit 0 = looks clean (single Agent author, scope matches GitHub when --pr given).
Exit 1 = possible stacking / scope mismatch you MUST eyeball before asserting.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Dict, List, Optional

_AGENT_TRAILER = re.compile(r"^Agent:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_COMMIT_SEP = "\x1e"  # record separator between commits in git log output
_FIELD_SEP = "\x1f"  # field separator between hash/subject/body


def extract_agent_trailer(commit_message: str) -> Optional[str]:
    """Return the value of the last ``Agent:`` trailer in a commit message, or None."""

    matches = _AGENT_TRAILER.findall(commit_message)
    return matches[-1].strip() if matches else None


def assess_scope(
    files: List[str],
    agent_trailers: List[Optional[str]],
    gh_files: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Assess whether a branch's scope is safe to assert.

    Pure function (no I/O) so it is testable. ``agent_trailers`` is one entry per
    commit in ``origin/master..HEAD`` (None when a commit has no Agent: trailer).
    """

    distinct = sorted({a for a in agent_trailers if a})
    warnings: List[str] = []

    if len(distinct) > 1:
        warnings.append(
            "possible STACKED branch: commits carry >1 distinct Agent: trailer "
            f"({', '.join(distinct)}). Your branch may be cut from another PR — "
            "rebase --onto master before asserting scope."
        )
    if None in agent_trailers:
        warnings.append(
            "at least one commit has no Agent: trailer (Commit Attribution Gate will fail)."
        )
    if gh_files is not None and set(gh_files) != set(files):
        only_gh = sorted(set(gh_files) - set(files))
        only_local = sorted(set(files) - set(gh_files))
        warnings.append(
            "GitHub-reported PR files differ from local cumulative diff "
            f"(only on GitHub: {only_gh or '-'}; only local: {only_local or '-'})."
        )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "distinct_agents": distinct,
        "file_count": len(files),
    }


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def _gh_pr_files(pr: int) -> List[str]:
    out = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", "files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f["path"] for f in json.loads(out)["files"]]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="pr_preflight", description=__doc__)
    parser.add_argument("--pr", type=int, default=None, help="Cross-check this PR's GitHub files")
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch (offline)")
    parser.add_argument("--base", default="origin/master", help="Base ref (default origin/master)")
    args = parser.parse_args(argv)

    if not args.no_fetch:
        try:
            _git("fetch", "origin", "master")
        except subprocess.CalledProcessError:
            print(
                "[pr_preflight] warning: git fetch failed; base ref may be stale.", file=sys.stderr
            )

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    base = _git("merge-base", args.base, "HEAD")
    files = [f for f in _git("diff", "--name-only", f"{base}..HEAD").splitlines() if f]
    raw = _git("log", f"--format=%H{_FIELD_SEP}%B{_COMMIT_SEP}", f"{base}..HEAD")
    bodies = [c.split(_FIELD_SEP, 1)[1] for c in raw.split(_COMMIT_SEP) if _FIELD_SEP in c]
    agent_trailers = [extract_agent_trailer(b) for b in bodies]

    gh_files = _gh_pr_files(args.pr) if args.pr is not None else None
    result = assess_scope(files, agent_trailers, gh_files)

    print(f"branch:          {branch}")
    print(f"base:            {args.base} (merge-base {base[:10]})")
    print(f"commits ahead:   {len(bodies)}  agents: {result['distinct_agents'] or ['(none)']}")
    print(
        f"CUMULATIVE scope vs {args.base}: {result['file_count']} file(s) -- assert THIS, not git diff --cached:"
    )
    for f in files:
        print(f"  {f}")
    if result["warnings"]:
        print("\n[pr_preflight] WARNINGS:")
        for w in result["warnings"]:
            print(f"  - {w}")
        return 1
    print("\n[pr_preflight] clean: single author, scope matches. Safe to assert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
