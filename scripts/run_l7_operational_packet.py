#!/usr/bin/env python3
"""Generate a compact L7 operational packet for later agents."""

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

import scripts.run_changed_surface_checks as changed_surface_checks  # noqa: E402
import scripts.run_l7_l8_contract_artifacts as contract_artifacts  # noqa: E402
import scripts.verify_protected_paths as protected_paths  # noqa: E402

JSON_FILENAME = "l7_operational_packet_latest.json"
MARKDOWN_FILENAME = "l7_operational_packet_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _resolve_optional_path(repo_root: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _load_changed_paths(
    *,
    repo_root: Path,
    changed_files: list[str] | None,
    changed_file_list: Path | None,
    staged: bool,
    base_ref: str | None,
) -> dict[str, Any]:
    explicit_changed = [
        _normalize_path(item) for item in (changed_files or []) if _normalize_path(item)
    ]
    if explicit_changed or changed_file_list is not None or staged or base_ref:
        return protected_paths.collect_changed_paths(
            repo_root=repo_root,
            changed_files=explicit_changed,
            changed_file_list=changed_file_list,
            staged=staged,
            base_ref=base_ref,
        )
    return {
        "mode": "none",
        "command": None,
        "exit_code": 0,
        "paths": [],
    }


def _route_for_question_type(
    payload: dict[str, Any],
    *,
    question_type: str | None,
    changed_paths: list[str],
) -> tuple[dict[str, Any], str, list[str]]:
    routes = list(payload.get("question_routes") or [])
    supported = [
        str(route.get("question_type") or "") for route in routes if route.get("question_type")
    ]
    if question_type:
        selected_type = str(question_type).strip()
        route_source = "explicit"
    elif changed_paths:
        selected_type = "change_validation"
        route_source = "inferred_from_change_surface"
    else:
        selected_type = "latest_repo_state"
        route_source = "default_no_change_context"

    for route in routes:
        if route.get("question_type") == selected_type:
            return route, route_source, supported

    fallback = routes[0] if routes else {}
    return fallback, route_source, supported


def _surface_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(surface.get("id")): surface
        for surface in payload.get("surfaces", [])
        if isinstance(surface, dict) and str(surface.get("id") or "").strip()
    }


def _expand_route_sequence(route: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    surface_by_id = _surface_index(payload)

    def add(kind: str, value: str) -> None:
        if not value:
            return
        entries.append({"kind": kind, "value": value})

    open_first = str(route.get("open_first") or "").strip()
    open_second = str(route.get("open_second") or "").strip()
    then = str(route.get("then") or "").strip()

    add("path", open_first)
    add("path", open_second)

    if then in surface_by_id:
        add("surface", then)
        for example in surface_by_id[then].get("examples", [])[:3]:
            add("path", str(example))
    elif then:
        add("next", then)

    return entries


def build_packet(
    *,
    repo_root: Path,
    question_type: str | None = None,
    changed_files: list[str] | None = None,
    changed_file_list: Path | None = None,
    staged: bool = False,
    base_ref: str | None = None,
    allow_paths: tuple[str, ...] = (),
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    l7_payload = contract_artifacts.build_l7_payload()
    collection = _load_changed_paths(
        repo_root=repo_root,
        changed_files=changed_files,
        changed_file_list=changed_file_list,
        staged=staged,
        base_ref=base_ref,
    )
    changed_paths = list(collection.get("paths", []))
    route, route_source, supported_question_types = _route_for_question_type(
        l7_payload,
        question_type=question_type,
        changed_paths=changed_paths,
    )
    route_question_type = str(route.get("question_type") or "").strip()
    operational_route_source = route_source
    if route_question_type != (question_type or route_question_type):
        operational_route_source = "fallback_first_known_route"

    if collection.get("mode") == "none" and not changed_paths:
        changed_surface_report = {
            "surfaces": [],
            "checks": [],
            "warnings": [],
            "metrics": {
                "changed_path_count": 0,
                "surface_count": 0,
                "planned_check_count": 0,
            },
        }
        protected_report = {
            "ok": True,
            "violation_count": 0,
            "violations": [],
        }
    else:
        changed_surface_report = changed_surface_checks.build_report(
            repo_root=repo_root,
            changed_files=changed_paths,
            allow_paths=allow_paths,
            execute=False,
            python_executable=python_executable,
        )
        protected_report = protected_paths.build_report(
            repo_root=repo_root,
            changed_files=changed_paths,
            allowed_paths=allow_paths,
        )
    open_sequence = _expand_route_sequence(route, l7_payload)
    plan_checks = [
        {
            "name": check.get("name"),
            "command": check.get("command"),
            "surface_ids": list(check.get("surface_ids") or []),
            "reason": check.get("reason"),
            "blocking": bool(check.get("blocking")),
        }
        for check in changed_surface_report.get("checks", [])
    ]
    contract_verifiers = list(l7_payload.get("verifier_checks") or [])
    if plan_checks:
        recommended_checks = plan_checks
    else:
        recommended_checks = [
            {
                "name": item.get("id"),
                "command": item.get("command"),
                "surface_ids": ["verifier"],
                "reason": item.get("use_when"),
                "blocking": True,
            }
            for item in contract_verifiers
        ]

    first_surface = open_sequence[0]["value"] if open_sequence else ""
    second_surface = open_sequence[1]["value"] if len(open_sequence) > 1 else ""
    changed_surface_ids = [
        surface.get("id") for surface in changed_surface_report.get("surfaces", [])
    ]
    protected_violation_count = int(protected_report.get("violation_count", 0))

    primary_status_line = (
        "l7_packet_ready | "
        f"question_type={route_question_type or 'unknown'} "
        f"route_source={operational_route_source} "
        f"changed_paths={len(changed_paths)} "
        f"surfaces={len(changed_surface_ids)} "
        f"protected_violations={protected_violation_count}"
    )
    runtime_status_line = (
        "entrypoints | "
        f"first={first_surface or 'none'} "
        f"second={second_surface or 'none'} "
        f"next={str(route.get('then') or 'none')} "
        f"checks={','.join(check['name'] for check in recommended_checks[:4]) or 'none'}"
    )
    artifact_policy_status_line = (
        "compiled_retrieval=first | "
        f"prose_after_artifacts=true fail_closed={'true' if protected_violation_count else 'false'} "
        f"stop_triggers={len(l7_payload.get('stop_reading_triggers', []))}"
    )

    return {
        "generated_at": _iso_now(),
        "status": "ready",
        "contract_version": "v1",
        "canonical_contract": contract_artifacts.L7_CONTRACT_PATH,
        "question_type": route_question_type,
        "route_source": operational_route_source,
        "supported_question_types": supported_question_types,
        "collection": {
            "mode": collection.get("mode"),
            "command": collection.get("command"),
            "exit_code": collection.get("exit_code"),
        },
        "open_sequence": open_sequence,
        "recommended_checks": recommended_checks,
        "stop_reading_triggers": list(l7_payload.get("stop_reading_triggers") or []),
        "changed_surface_summary": {
            "changed_path_count": len(changed_paths),
            "surface_ids": [str(item) for item in changed_surface_ids if item],
            "planned_check_count": int(
                changed_surface_report.get("metrics", {}).get("planned_check_count", 0)
            ),
            "warnings": list(changed_surface_report.get("warnings") or []),
        },
        "protected_path_summary": {
            "ok": bool(protected_report.get("ok", False)),
            "violation_count": protected_violation_count,
            "violations": list(protected_report.get("violations") or []),
        },
        "authority_order": list(l7_payload.get("default_reading_order") or []),
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": {
            "queue_shape": "l7_packet_ready",
            "requires_operator_action": protected_violation_count > 0,
            "preferred_first_surface": first_surface,
            "preferred_second_surface": second_surface,
            "question_type": route_question_type,
            "primary_status_line": primary_status_line,
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# L7 Operational Packet Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- status: {payload['status']}",
        f"- question_type: `{payload['question_type']}`",
        f"- route_source: `{payload['route_source']}`",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Open Sequence",
    ]
    for item in payload.get("open_sequence", []):
        lines.append(f"- `{item['kind']}`: `{item['value']}`")

    lines.extend(["", "## Recommended Checks"])
    for check in payload.get("recommended_checks", []):
        lines.append(f"- `{check['name']}`: `{check['command']}`")
        if check.get("surface_ids"):
            lines.append(
                "  - surfaces: " + ", ".join(f"`{surface}`" for surface in check["surface_ids"])
            )
        if check.get("reason"):
            lines.append(f"  - reason: {check['reason']}")

    lines.extend(["", "## Changed Surface Summary"])
    changed_surface_summary = payload.get("changed_surface_summary") or {}
    lines.append(f"- changed_path_count: `{changed_surface_summary.get('changed_path_count', 0)}`")
    lines.append(
        "- surface_ids: "
        + (
            ", ".join(f"`{item}`" for item in changed_surface_summary.get("surface_ids", []))
            or "(none)"
        )
    )
    lines.append(
        f"- planned_check_count: `{changed_surface_summary.get('planned_check_count', 0)}`"
    )

    lines.extend(["", "## Protected Path Summary"])
    protected_summary = payload.get("protected_path_summary") or {}
    lines.append(f"- ok: `{str(protected_summary.get('ok', False)).lower()}`")
    lines.append(f"- violation_count: `{protected_summary.get('violation_count', 0)}`")
    for violation in protected_summary.get("violations", []):
        lines.append(
            f"- violation: `{violation.get('path', '')}` via `{violation.get('rule', '')}`"
        )

    lines.extend(["", "## Stop Reading Triggers"])
    for item in payload.get("stop_reading_triggers", []):
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a compact L7 operational packet.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir", default="docs/status", help="Output directory for generated artifacts."
    )
    parser.add_argument(
        "--question-type",
        default=None,
        help="Optional L7 question type override. Defaults to latest_repo_state or change_validation.",
    )
    parser.add_argument(
        "--changed-file", action="append", default=[], help="Explicit changed path."
    )
    parser.add_argument(
        "--changed-file-list",
        default=None,
        help="Path to newline-delimited changed file list.",
    )
    parser.add_argument("--staged", action="store_true", help="Inspect staged changes.")
    parser.add_argument("--base-ref", default=None, help="Compare against git base ref.")
    parser.add_argument(
        "--allow-path", action="append", default=[], help="Protected-path allowlist."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    changed_file_list = _resolve_optional_path(repo_root, args.changed_file_list)
    allow_paths = tuple(
        _normalize_path(path) for path in (args.allow_path or []) if _normalize_path(path)
    )

    payload = build_packet(
        repo_root=repo_root,
        question_type=str(args.question_type).strip() if args.question_type else None,
        changed_files=list(args.changed_file or []),
        changed_file_list=changed_file_list,
        staged=bool(args.staged),
        base_ref=str(args.base_ref).strip() if args.base_ref else None,
        allow_paths=allow_paths,
        python_executable=sys.executable,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
