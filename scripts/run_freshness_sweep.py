#!/usr/bin/env python3
"""Layer 4 substrate-stack: session-start freshness sweep.

Substrate Stack Theory (docs/philosophy/substrate_stack_theory_2026-05-14.md)
§6.1 + §7 articulate: Layer 5 (memory entries) alone does not install
reflex — anti-pattern memories were written but the same family of error
recurred four times in one session. Real defense lives at Layer 4
(tool wrapper / session-start sweep).

This script measures freshness of state that AI agents tend to read
without refreshing first, and writes a manifest to tmp/. Each step is
independently fault-tolerant — network or auth failures degrade
gracefully (marked "failed" with a short reason, never crashes).

Sweeps:
  1. git fetch origin --prune          → refresh remote refs
  2. branch ahead/behind vs upstream   → catch stale local master
  3. codebase_graph_latest.json age    → catch stale structural snapshot
  4. gh repo list <user>               → catch scope assumption
  5. gh pr list --state open           → catch stale PR mental model

Exit code 0 unless --strict (then non-zero on any stale/failed step).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = REPO_ROOT / "tmp"
DEFAULT_GIT_TIMEOUT = 30
DEFAULT_GH_TIMEOUT = 60
DEFAULT_CODEBASE_GRAPH_TTL_HOURS = 24


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso() -> str:
    return _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as exc:
        return 127, "", f"command not found: {exc}"


def step_git_fetch() -> dict[str, Any]:
    rc, _stdout, stderr = _run(
        ["git", "fetch", "origin", "--prune", "--quiet"],
        timeout=DEFAULT_GIT_TIMEOUT,
    )
    return {
        "step": "git_fetch",
        "status": "ok" if rc == 0 else "failed",
        "exit_code": rc,
        "stderr_tail": stderr[-200:] if stderr else "",
    }


def step_branch_drift() -> dict[str, Any]:
    rc1, current_branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=10)
    if rc1 != 0:
        return {
            "step": "branch_drift",
            "status": "failed",
            "reason": "could not resolve HEAD",
        }

    upstream_rc, upstream, _ = _run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        timeout=10,
    )
    if upstream_rc != 0:
        upstream = "origin/master"

    rc2, counts, stderr2 = _run(
        ["git", "rev-list", "--left-right", "--count", f"{upstream}...HEAD"],
        timeout=10,
    )
    if rc2 != 0:
        return {
            "step": "branch_drift",
            "status": "failed",
            "current_branch": current_branch,
            "upstream": upstream,
            "reason": stderr2[:200] if stderr2 else "rev-list failed",
        }
    parts = counts.split()
    if len(parts) != 2:
        return {
            "step": "branch_drift",
            "status": "failed",
            "current_branch": current_branch,
            "upstream": upstream,
            "reason": f"unexpected rev-list output: {counts!r}",
        }
    behind, ahead = int(parts[0]), int(parts[1])
    return {
        "step": "branch_drift",
        "status": "ok",
        "current_branch": current_branch,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
    }


def step_codebase_graph_freshness(ttl_hours: int) -> dict[str, Any]:
    graph_path = REPO_ROOT / "docs" / "status" / "codebase_graph_latest.json"
    if not graph_path.exists():
        return {
            "step": "codebase_graph",
            "status": "missing",
            "path": str(graph_path.relative_to(REPO_ROOT)),
            "recommendation": "run: python scripts/analyze_codebase_graph.py",
        }
    try:
        data = json.loads(graph_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "step": "codebase_graph",
            "status": "failed",
            "reason": f"json decode: {exc}",
        }
    gen_at = data.get("generated_at")
    if not gen_at:
        return {"step": "codebase_graph", "status": "no_timestamp"}
    try:
        gen_dt = datetime.strptime(gen_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return {
            "step": "codebase_graph",
            "status": "bad_timestamp",
            "generated_at": gen_at,
        }
    age = _now_utc() - gen_dt
    age_hours = round(age.total_seconds() / 3600, 1)
    is_stale = age > timedelta(hours=ttl_hours)
    out: dict[str, Any] = {
        "step": "codebase_graph",
        "status": "stale" if is_stale else "fresh",
        "generated_at": gen_at,
        "age_hours": age_hours,
        "ttl_hours": ttl_hours,
    }
    if is_stale:
        out["recommendation"] = (
            "run: python scripts/analyze_codebase_graph.py "
            "(graph is older than TTL -- re-run before reasoning from it)"
        )
    return out


def step_gh_repo_list(github_user: str) -> dict[str, Any]:
    rc, stdout, stderr = _run(
        [
            "gh",
            "repo",
            "list",
            github_user,
            "--limit",
            "50",
            "--json",
            "name,updatedAt,isArchived",
        ],
        timeout=DEFAULT_GH_TIMEOUT,
    )
    if rc != 0:
        return {
            "step": "gh_repo_list",
            "status": "failed",
            "user": github_user,
            "reason": stderr[:200] if stderr else f"exit {rc}",
        }
    try:
        repos = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "step": "gh_repo_list",
            "status": "failed",
            "user": github_user,
            "reason": f"json decode: {exc}",
        }
    active = [r for r in repos if not r.get("isArchived")]
    return {
        "step": "gh_repo_list",
        "status": "ok",
        "user": github_user,
        "total": len(repos),
        "active": len(active),
        "names": sorted(r["name"] for r in active),
    }


def step_gh_pr_list() -> dict[str, Any]:
    rc, stdout, stderr = _run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--json",
            "number,title,headRefName,isDraft,mergeable",
        ],
        timeout=DEFAULT_GH_TIMEOUT,
    )
    if rc != 0:
        return {
            "step": "gh_pr_list",
            "status": "failed",
            "reason": stderr[:200] if stderr else f"exit {rc}",
        }
    try:
        prs = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "step": "gh_pr_list",
            "status": "failed",
            "reason": f"json decode: {exc}",
        }
    return {
        "step": "gh_pr_list",
        "status": "ok",
        "open_count": len(prs),
        "prs": [
            {
                "n": p["number"],
                "branch": p["headRefName"],
                "draft": p.get("isDraft", False),
                "mergeable": p.get("mergeable"),
                "title": p["title"][:80],
            }
            for p in prs
        ],
    }


_STATUS_MARKERS = {
    "ok": "OK",
    "fresh": "FRESH",
    "stale": "STALE",
    "failed": "FAIL",
    "missing": "MISS",
    "skipped": "skip",
    "no_timestamp": "WARN",
    "bad_timestamp": "WARN",
}


def render_summary(manifest: dict[str, Any]) -> str:
    lines: list[str] = [f"[freshness sweep @ {manifest['swept_at']}]"]
    for step in manifest["steps"]:
        name = step["step"]
        status = step["status"]
        marker = _STATUS_MARKERS.get(status, status.upper())
        line = f"  [{marker:5s}] {name}"
        if name == "branch_drift" and status == "ok":
            line += (
                f": {step['current_branch']} vs {step['upstream']}  "
                f"ahead={step['ahead']} behind={step['behind']}"
            )
        elif name == "codebase_graph" and status in ("stale", "fresh"):
            line += f": age={step['age_hours']}h ttl={step['ttl_hours']}h"
        elif name == "gh_repo_list" and status == "ok":
            line += f": {step['active']} active / {step['total']} total"
        elif name == "gh_pr_list" and status == "ok":
            line += f": {step['open_count']} open PR"
        elif status == "failed":
            line += f": {step.get('reason', '')[:80]}"
        lines.append(line)
    recs = [s["recommendation"] for s in manifest["steps"] if s.get("recommendation")]
    if recs:
        lines.append("")
        lines.append("Recommendations:")
        for rec in recs:
            lines.append(f"  - {rec}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--skip-gh", action="store_true", help="skip gh subcommands (offline mode)")
    parser.add_argument("--skip-fetch", action="store_true", help="skip git fetch (offline mode)")
    parser.add_argument("--github-user", default="Fan1234-1", help="GitHub user for repo list")
    parser.add_argument(
        "--ttl-hours",
        type=int,
        default=DEFAULT_CODEBASE_GRAPH_TTL_HOURS,
        help="codebase_graph staleness threshold in hours (default 24)",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress stdout summary")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any step fails or is stale",
    )
    args = parser.parse_args()

    swept_at = _utc_iso()
    steps: list[dict[str, Any]] = []

    if args.skip_fetch:
        steps.append({"step": "git_fetch", "status": "skipped", "reason": "--skip-fetch"})
    else:
        steps.append(step_git_fetch())

    steps.append(step_branch_drift())
    steps.append(step_codebase_graph_freshness(args.ttl_hours))

    if args.skip_gh:
        steps.append({"step": "gh_repo_list", "status": "skipped", "reason": "--skip-gh"})
        steps.append({"step": "gh_pr_list", "status": "skipped", "reason": "--skip-gh"})
    else:
        steps.append(step_gh_repo_list(args.github_user))
        steps.append(step_gh_pr_list())

    manifest = {
        "swept_at": swept_at,
        "tool": "scripts/run_freshness_sweep.py",
        "purpose": "Layer 4 substrate-stack: surface stale state before session work",
        "theory_anchor": "docs/philosophy/substrate_stack_theory_2026-05-14.md §6.1, §7",
        "steps": steps,
    }

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    safe_ts = swept_at.replace(":", "").replace("-", "")
    manifest_path = TMP_DIR / f"freshness_sweep_{safe_ts}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if not args.quiet:
        print(render_summary(manifest))
        print()
        print(f"manifest: {manifest_path.relative_to(REPO_ROOT)}")

    if args.strict:
        bad = {"failed", "stale", "missing"}
        if any(s["status"] in bad for s in steps):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
