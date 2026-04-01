"""
Incremental commit attribution verifier.

This script mirrors the GitHub Actions commit attribution gate but remains usable
locally before pushing. It evaluates the relevant commit range, delegates each
revision to `scripts/verify_commit_attribution.py`, and emits one aggregate report.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _run_git(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _rev_list(spec: str) -> list[str]:
    proc = _run_git(["rev-list", "--reverse", spec])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"failed to list revisions for {spec}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


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


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    normalized_ancestor = str(ancestor or "").strip()
    normalized_descendant = str(descendant or "").strip()
    if not normalized_ancestor or not normalized_descendant:
        return False
    proc = _run_git(["merge-base", "--is-ancestor", normalized_ancestor, normalized_descendant])
    return proc.returncode == 0


def _tree_hash(revision: str) -> str | None:
    candidate = str(revision or "").strip()
    if not candidate:
        return None
    proc = _run_git(["rev-parse", f"{candidate}^{{tree}}"])
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def _first_existing_base_ref(candidates: list[str]) -> str | None:
    for candidate in candidates:
        ref = str(candidate or "").strip()
        if ref and _sha_exists(ref):
            return ref
    return None


def _verify_revision(revision: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/verify_commit_attribution.py", "--rev", revision],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = proc.stdout.strip()
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or output or "attribution check failed") from exc
        raise RuntimeError("invalid attribution payload") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("invalid attribution payload")
    payload.setdefault("rev", revision)
    payload["exit_code"] = int(proc.returncode)
    return payload


def _is_synthetic_merge_commit(payload: dict[str, Any]) -> bool:
    summary = str(payload.get("summary") or "")
    changed_files = payload.get("changed_files")
    if not isinstance(changed_files, list):
        return False
    return summary.startswith("Merge ") and not changed_files


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    if _is_synthetic_merge_commit(normalized):
        normalized["ok"] = True
        normalized["exempted"] = True
        normalized["exemption_reason"] = "synthetic_merge_commit"
    return normalized


def resolve_revision_plan(
    *,
    event_name: str,
    head_sha: str,
    before_sha: str | None,
    pr_base_sha: str | None,
    pr_head_sha: str | None,
    local_base_candidates: list[str],
    enforcement_anchor: str | None = None,
) -> dict[str, Any]:
    normalized_event = str(event_name or "").strip()
    normalized_head = str(head_sha or "HEAD").strip() or "HEAD"
    range_spec: str | None = None
    base_ref: str | None = None
    revisions: list[str] = []
    mode = "single"

    if normalized_event == "pull_request":
        mode = "pull_request_incremental"
        resolved_head = str(pr_head_sha or normalized_head).strip() or normalized_head
        resolved_base = str(pr_base_sha or "").strip()
        if resolved_base:
            range_spec = f"{resolved_base}..{resolved_head}"
            revisions = _rev_list(range_spec)
            base_ref = resolved_base
        else:
            revisions = [resolved_head]
    elif normalized_event == "push":
        mode = "push_incremental"
        resolved_before = str(before_sha or "").strip()
        if resolved_before and resolved_before != "0000000000000000000000000000000000000000":
            if _sha_exists(resolved_before):
                range_spec = f"{resolved_before}..{normalized_head}"
                revisions = _rev_list(range_spec)
                base_ref = resolved_before
            else:
                revisions = [normalized_head]
        else:
            revisions = [normalized_head]
    else:
        mode = "local_incremental"
        base_ref = _first_existing_base_ref(local_base_candidates)
        if base_ref is not None:
            merge_base = _merge_base(base_ref, normalized_head)
            if merge_base and merge_base != normalized_head:
                range_spec = f"{merge_base}..{normalized_head}"
                revisions = _rev_list(range_spec)
        if not revisions:
            revisions = [normalized_head]

    if not revisions:
        revisions = [normalized_head]

    anchor_ref = str(enforcement_anchor or "").strip()
    anchor_used = False
    if anchor_ref and _sha_exists(anchor_ref) and _is_ancestor(anchor_ref, normalized_head):
        anchored_range = f"{anchor_ref}..{normalized_head}"
        anchored_revisions = _rev_list(anchored_range)
        if anchored_revisions:
            mode = "anchored_incremental"
            range_spec = anchored_range
            base_ref = anchor_ref
            revisions = anchored_revisions
            anchor_used = True

    return {
        "event_name": normalized_event or "local",
        "mode": mode,
        "range_spec": range_spec,
        "base_ref": base_ref,
        "checked_revisions": revisions,
        "enforcement_anchor": anchor_ref or None,
        "anchor_override_used": anchor_used,
    }


def build_report(
    *,
    event_name: str,
    head_sha: str,
    before_sha: str | None,
    pr_base_sha: str | None,
    pr_head_sha: str | None,
    local_base_candidates: list[str],
    equivalent_ref: str | None = None,
    enforcement_anchor: str | None = None,
) -> dict[str, Any]:
    plan = resolve_revision_plan(
        event_name=event_name,
        head_sha=head_sha,
        before_sha=before_sha,
        pr_base_sha=pr_base_sha,
        pr_head_sha=pr_head_sha,
        local_base_candidates=local_base_candidates,
        enforcement_anchor=enforcement_anchor,
    )
    results: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    for revision in plan["checked_revisions"]:
        try:
            payload = _normalize_payload(_verify_revision(str(revision)))
        except RuntimeError as exc:
            payload = {
                "rev": str(revision),
                "ok": False,
                "summary": "",
                "error": str(exc),
                "has_agent": False,
                "has_topic": False,
                "exit_code": 1,
            }
        results.append(payload)
        if not payload.get("ok", False):
            missing.append(
                {
                    "rev": str(revision),
                    "summary": str(payload.get("summary") or ""),
                    "error": str(payload.get("error") or ""),
                }
            )

    report = {
        **plan,
        "checked_count": len(plan["checked_revisions"]),
        "missing_count": len(missing),
        "missing": missing,
        "ok": not missing,
        "results": results,
        "advice": {
            "agent_trailer": "Agent: Codex",
            "trace_topic_trailer": "Trace-Topic: <topic-name>",
        },
    }
    normalized_equivalent_ref = str(equivalent_ref or "").strip()
    normalized_head = str(head_sha or "HEAD").strip() or "HEAD"
    if normalized_equivalent_ref:
        head_tree = _tree_hash(normalized_head)
        compare_tree = _tree_hash(normalized_equivalent_ref)
        report["equivalence"] = {
            "head_revision": normalized_head,
            "compare_revision": normalized_equivalent_ref,
            "head_tree": head_tree,
            "compare_tree": compare_tree,
            "tree_equal": bool(head_tree and compare_tree and head_tree == compare_tree),
        }
    return report


def _tree_equivalence_satisfied(report: dict[str, Any]) -> bool:
    equivalence = report.get("equivalence")
    return isinstance(equivalence, dict) and equivalence.get("tree_equal") is True


def _emit_json(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify incremental commit attribution trailers.")
    parser.add_argument(
        "--event-name",
        default=os.environ.get("EVENT_NAME", ""),
        help="GitHub event name. Empty means local mode.",
    )
    parser.add_argument(
        "--head-sha",
        default=os.environ.get("GITHUB_SHA", "HEAD"),
        help="Head revision to inspect.",
    )
    parser.add_argument(
        "--before-sha",
        default=os.environ.get("BEFORE_SHA", ""),
        help="Push-event before SHA.",
    )
    parser.add_argument(
        "--pr-base-sha",
        default=os.environ.get("PR_BASE_SHA", ""),
        help="Pull-request base SHA.",
    )
    parser.add_argument(
        "--pr-head-sha",
        default=os.environ.get("PR_HEAD_SHA", ""),
        help="Pull-request head SHA.",
    )
    parser.add_argument(
        "--local-base-ref",
        action="append",
        default=[],
        help="Local-mode base ref candidate (repeatable). Defaults to origin/master, origin/main, master, main.",
    )
    parser.add_argument(
        "--enforcement-anchor",
        default=os.environ.get("COMMIT_ATTRIBUTION_ANCHOR", ""),
        help="Optional revision after which commit attribution becomes blocking.",
    )
    parser.add_argument(
        "--artifact-path",
        default="commit_attribution.json",
        help="Path to write the aggregate JSON report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any revision lacks attribution trailers.",
    )
    parser.add_argument(
        "--equivalent-ref",
        default="",
        help="Optional ref to compare tree-equivalence against the inspected head revision.",
    )
    parser.add_argument(
        "--require-tree-equivalence",
        action="store_true",
        help="Return non-zero unless --equivalent-ref resolves to a tree-equivalent revision.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    local_base_candidates = (
        list(args.local_base_ref)
        if args.local_base_ref
        else ["origin/master", "origin/main", "master", "main"]
    )
    try:
        report = build_report(
            event_name=args.event_name,
            head_sha=args.head_sha,
            before_sha=args.before_sha,
            pr_base_sha=args.pr_base_sha,
            pr_head_sha=args.pr_head_sha,
            local_base_candidates=local_base_candidates,
            equivalent_ref=args.equivalent_ref,
            enforcement_anchor=args.enforcement_anchor,
        )
    except RuntimeError as exc:
        payload = {
            "ok": False,
            "error": str(exc),
            "event_name": str(args.event_name or "local"),
            "checked_revisions": [],
        }
        Path(args.artifact_path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        _emit_json(payload)
        return 1

    Path(args.artifact_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _emit_json(report)

    if args.require_tree_equivalence and not _tree_equivalence_satisfied(report):
        print(
            "::error::Expected tree-equivalent compare ref when --require-tree-equivalence is enabled."
        )
        return 1

    if args.strict and not report["ok"]:
        print("::error::Missing Agent/Trace-Topic trailers in incremental commits.")
        print("::error::Add commit trailers, for example:")
        print(f"::error::{report['advice']['agent_trailer']}")
        print(f"::error::{report['advice']['trace_topic_trailer']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
