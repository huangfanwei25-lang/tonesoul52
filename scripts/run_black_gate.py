"""
ToneSoul Black gate runner.

PR/push events should block only on changed Python files inside the maintained
surfaces. Scheduled runs may still inspect the whole repo baseline, but they do
so in advisory mode so long-standing formatting debt does not keep unrelated
operational lanes red.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

DEFAULT_LOCAL_BASE_CANDIDATES = ["origin/master", "origin/main", "master", "main"]
DEFAULT_ROOTS = ["tonesoul", "tests", "scripts"]
DEFAULT_ARTIFACT_PATH = "black_gate_report.json"


def _run_git(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _sha_exists(revision: str) -> bool:
    candidate = str(revision or "").strip()
    if not candidate:
        return False
    proc = _run_git(["cat-file", "-t", candidate])
    return proc.returncode == 0


def _merge_base(base_ref: str, head_sha: str) -> str | None:
    proc = _run_git(["merge-base", base_ref, head_sha])
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def _first_existing_base_ref(candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        normalized = str(candidate or "").strip()
        if normalized and _sha_exists(normalized):
            return normalized
    return None


def _collect_changed_files(spec: str) -> list[str]:
    proc = _run_git(["diff", "--name-only", "--diff-filter=ACMR", spec])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"failed to diff {spec}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _show_commit_files(revision: str) -> list[str]:
    proc = _run_git(["show", "--name-only", "--diff-filter=ACMR", "--pretty=format:", revision])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"failed to inspect {revision}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _normalize_roots(roots: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        str(root).replace("\\", "/").strip("/").lower() for root in roots if str(root or "").strip()
    )


def _is_target_python_path(path: str, roots: Iterable[str]) -> bool:
    normalized = str(path or "").replace("\\", "/").lstrip("./")
    if not normalized.endswith(".py"):
        return False
    lowered = normalized.lower()
    for root in _normalize_roots(roots):
        if lowered == root or lowered.startswith(f"{root}/"):
            return True
    return False


def resolve_black_mode(event_name: str) -> str:
    normalized = str(event_name or "").strip()
    if normalized == "schedule":
        return "advisory_full"
    return "blocking_changed"


def collect_targets(
    *,
    event_name: str,
    head_sha: str,
    before_sha: str | None,
    pr_base_sha: str | None,
    pr_head_sha: str | None,
    local_base_candidates: list[str],
    roots: list[str],
) -> dict[str, Any]:
    mode = resolve_black_mode(event_name)
    normalized_head = str(head_sha or "HEAD").strip() or "HEAD"
    normalized_event = str(event_name or "").strip()

    if mode == "advisory_full":
        targets = sorted(
            str(path.as_posix())
            for root in roots
            for path in Path(root).rglob("*.py")
            if path.is_file()
        )
        return {
            "event_name": normalized_event or "local",
            "mode": mode,
            "diff_spec": None,
            "base_ref": None,
            "targets": targets,
        }

    diff_spec: str | None = None
    base_ref: str | None = None

    if normalized_event == "pull_request":
        resolved_base = str(pr_base_sha or "").strip()
        resolved_head = str(pr_head_sha or normalized_head).strip() or normalized_head
        if resolved_base:
            diff_spec = f"{resolved_base}...{resolved_head}"
            base_ref = resolved_base
    elif normalized_event == "push":
        resolved_before = str(before_sha or "").strip()
        if resolved_before and resolved_before != "0000000000000000000000000000000000000000":
            if _sha_exists(resolved_before):
                diff_spec = f"{resolved_before}..{normalized_head}"
                base_ref = resolved_before
    else:
        base_ref = _first_existing_base_ref(local_base_candidates)
        if base_ref:
            merge_base = _merge_base(base_ref, normalized_head)
            if merge_base and merge_base != normalized_head:
                diff_spec = f"{merge_base}..{normalized_head}"

    changed_files = (
        _collect_changed_files(diff_spec) if diff_spec else _show_commit_files(normalized_head)
    )
    targets = sorted({path for path in changed_files if _is_target_python_path(path, roots)})
    return {
        "event_name": normalized_event or "local",
        "mode": mode,
        "diff_spec": diff_spec,
        "base_ref": base_ref,
        "targets": targets,
    }


def _run_black(targets: list[str], line_length: int) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "black",
        "--check",
        "--diff",
        "--line-length",
        str(line_length),
        *targets,
    ]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _emit_json(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ToneSoul's bounded Black formatting gate.")
    parser.add_argument("--event-name", default=os.environ.get("EVENT_NAME", ""))
    parser.add_argument("--head-sha", default=os.environ.get("GITHUB_SHA", "HEAD"))
    parser.add_argument("--before-sha", default=os.environ.get("BEFORE_SHA", ""))
    parser.add_argument("--pr-base-sha", default=os.environ.get("PR_BASE_SHA", ""))
    parser.add_argument("--pr-head-sha", default=os.environ.get("PR_HEAD_SHA", ""))
    parser.add_argument(
        "--local-base-ref",
        action="append",
        default=[],
        help="Candidate local base ref. May be repeated.",
    )
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Root directories to include. May be repeated.",
    )
    parser.add_argument("--line-length", type=int, default=100)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--artifact-path", default=DEFAULT_ARTIFACT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    local_base_candidates = list(args.local_base_ref or []) or list(DEFAULT_LOCAL_BASE_CANDIDATES)
    roots = list(args.root or []) or list(DEFAULT_ROOTS)
    report = collect_targets(
        event_name=args.event_name,
        head_sha=args.head_sha,
        before_sha=args.before_sha,
        pr_base_sha=args.pr_base_sha,
        pr_head_sha=args.pr_head_sha,
        local_base_candidates=local_base_candidates,
        roots=roots,
    )
    report["line_length"] = int(args.line_length)
    report["blocking"] = report["mode"] == "blocking_changed"
    report["skipped"] = False
    report["ok"] = True
    report["exit_code"] = 0
    report["stdout"] = ""
    report["stderr"] = ""

    targets = list(report["targets"])
    if not targets:
        report["skipped"] = True
        report["summary"] = "No matching changed Python targets for the Black gate."
    else:
        proc = _run_black(targets, int(args.line_length))
        report["exit_code"] = int(proc.returncode)
        report["stdout"] = proc.stdout
        report["stderr"] = proc.stderr
        report["ok"] = proc.returncode == 0
        report["summary"] = (
            f"Black {'passed' if report['ok'] else 'reported drift'} for {len(targets)} target(s)."
        )

    artifact_path = Path(args.artifact_path)
    artifact_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _emit_json(report)

    if args.strict and report["blocking"] and not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
