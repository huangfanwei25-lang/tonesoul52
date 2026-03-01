"""Validate memory governance contract schema/example and publish status artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "memory_governance_contract_latest.json"
MARKDOWN_FILENAME = "memory_governance_contract_latest.md"

ALLOWED_ROUTES = {
    "route_local_llm",
    "route_single_cloud",
    "route_full_council",
    "block_rate_limit",
}
ALLOWED_SOURCE_REPOS = {"tonesoul52", "openclaw-memory"}
WAVE_KEYS = ("uncertainty_shift", "divergence_shift", "risk_shift", "revision_shift")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_markdown(payload: dict[str, Any]) -> str:
    checks = payload.get("checks", [])
    if not isinstance(checks, list):
        checks = []

    lines = [
        "# Memory Governance Contract Latest",
        "",
        f"- generated_at: {payload.get('generated_at', '')}",
        f"- ok: {str(bool(payload.get('ok', False))).lower()}",
        f"- failed_count: {int(payload.get('failed_count', 0) or 0)}",
        f"- warning_count: {int(payload.get('warning_count', 0) or 0)}",
        "",
        "| check | status | detail |",
        "| --- | --- | --- |",
    ]

    for check in checks:
        if not isinstance(check, dict):
            continue
        name = str(check.get("name", "")).replace("|", r"\|")
        status = str(check.get("status", "")).upper().replace("|", r"\|")
        detail = str(check.get("detail", "")).replace("|", r"\|")
        lines.append(f"| {name} | {status} | {detail} |")

    failed = [
        check
        for check in checks
        if isinstance(check, dict) and str(check.get("status", "")).lower() == "fail"
    ]
    if failed:
        lines.append("")
        lines.append("## Failures")
        for item in failed:
            lines.append(f"- `{item.get('name', '')}`: {item.get('detail', '')}")

    warnings = [
        check
        for check in checks
        if isinstance(check, dict) and str(check.get("status", "")).lower() == "warn"
    ]
    if warnings:
        lines.append("")
        lines.append("## Warnings")
        for item in warnings:
            lines.append(f"- `{item.get('name', '')}`: {item.get('detail', '')}")

    return "\n".join(lines) + "\n"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def _bounded_unit_number(value: Any) -> bool:
    if not isinstance(value, (int, float)):
        return False
    value_f = float(value)
    return 0.0 <= value_f <= 1.0


def _safe_read_json(path: Path) -> tuple[Any, str | None]:
    if not path.exists():
        return None, f"file missing: {path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return None, f"invalid json: {exc}"
    return payload, None


def _add_check(checks: list[dict[str, str]], name: str, status: str, detail: str) -> None:
    checks.append({"name": name, "status": status, "detail": detail})


def _validate_wave(
    checks: list[dict[str, str]],
    *,
    name: str,
    wave: Any,
) -> bool:
    if wave is None:
        _add_check(checks, name, "pass", "wave omitted")
        return True
    if not isinstance(wave, dict):
        _add_check(checks, name, "fail", "wave must be object")
        return False

    invalid_keys = [key for key in wave.keys() if key not in WAVE_KEYS]
    if invalid_keys:
        _add_check(
            checks,
            name,
            "fail",
            f"unknown wave keys: {', '.join(sorted(str(k) for k in invalid_keys))}",
        )
        return False

    for key, value in wave.items():
        if not _bounded_unit_number(value):
            _add_check(checks, f"{name}.{key}", "fail", "must be number in [0,1]")
            return False
    _add_check(checks, name, "pass", "wave shape valid")
    return True


def run_check(
    *,
    repo_root: Path,
    schema_relpath: str,
    example_relpath: str,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    schema_path = (repo_root / schema_relpath).resolve()
    example_path = (repo_root / example_relpath).resolve()

    schema_payload, schema_error = _safe_read_json(schema_path)
    if schema_error:
        _add_check(checks, "schema.read", "fail", schema_error)
        schema_payload = None
    else:
        _add_check(checks, "schema.read", "pass", "schema loaded")

    example_payload, example_error = _safe_read_json(example_path)
    if example_error:
        _add_check(checks, "example.read", "fail", example_error)
        example_payload = None
    else:
        _add_check(checks, "example.read", "pass", "example loaded")

    if isinstance(schema_payload, dict):
        root_type = schema_payload.get("type")
        if root_type == "object":
            _add_check(checks, "schema.root_type", "pass", "root type object")
        else:
            _add_check(checks, "schema.root_type", "fail", "root type must be object")

        props = schema_payload.get("properties")
        required = schema_payload.get("required")
        expected_required = {
            "contract_version",
            "generated_at",
            "source_repo",
            "prior_tension",
            "governance_friction",
            "routing_trace",
        }
        if isinstance(required, list) and expected_required.issubset(set(required)):
            _add_check(checks, "schema.required", "pass", "required fields present")
        else:
            _add_check(checks, "schema.required", "fail", "missing required root fields")

        if isinstance(props, dict) and expected_required.issubset(set(props.keys())):
            _add_check(checks, "schema.properties", "pass", "root properties present")
        else:
            _add_check(checks, "schema.properties", "fail", "missing root properties")

    if isinstance(example_payload, dict):
        contract_version = example_payload.get("contract_version")
        if contract_version == "v1":
            _add_check(checks, "example.contract_version", "pass", "contract_version=v1")
        else:
            _add_check(checks, "example.contract_version", "fail", "contract_version must be v1")

        source_repo = example_payload.get("source_repo")
        if isinstance(source_repo, str) and source_repo in ALLOWED_SOURCE_REPOS:
            _add_check(checks, "example.source_repo", "pass", "source_repo valid")
        else:
            _add_check(checks, "example.source_repo", "fail", "invalid source_repo")

        generated_at = example_payload.get("generated_at")
        if isinstance(generated_at, str) and generated_at.strip():
            _add_check(checks, "example.generated_at", "pass", "generated_at present")
        else:
            _add_check(checks, "example.generated_at", "fail", "generated_at missing")

        prior_tension = example_payload.get("prior_tension")
        if not isinstance(prior_tension, dict):
            _add_check(checks, "example.prior_tension", "fail", "prior_tension must be object")
        else:
            delta_t = prior_tension.get("delta_t")
            gate_decision = prior_tension.get("gate_decision")
            if _bounded_unit_number(delta_t):
                _add_check(checks, "example.prior_tension.delta_t", "pass", "delta_t in [0,1]")
            else:
                _add_check(
                    checks, "example.prior_tension.delta_t", "fail", "delta_t must be in [0,1]"
                )

            if isinstance(gate_decision, str) and gate_decision.strip():
                _add_check(
                    checks, "example.prior_tension.gate_decision", "pass", "gate_decision present"
                )
            else:
                _add_check(
                    checks, "example.prior_tension.gate_decision", "fail", "gate_decision missing"
                )

            for key in ("query_tension", "memory_tension"):
                value = prior_tension.get(key)
                if value is None:
                    _add_check(checks, f"example.prior_tension.{key}", "pass", "optional omitted")
                elif _bounded_unit_number(value):
                    _add_check(checks, f"example.prior_tension.{key}", "pass", f"{key} in [0,1]")
                else:
                    _add_check(
                        checks, f"example.prior_tension.{key}", "fail", f"{key} must be in [0,1]"
                    )

            _validate_wave(
                checks,
                name="example.prior_tension.query_wave",
                wave=prior_tension.get("query_wave"),
            )
            _validate_wave(
                checks,
                name="example.prior_tension.memory_wave",
                wave=prior_tension.get("memory_wave"),
            )

        governance_friction = example_payload.get("governance_friction")
        if not isinstance(governance_friction, dict):
            _add_check(
                checks,
                "example.governance_friction",
                "fail",
                "governance_friction must be object",
            )
        else:
            score = governance_friction.get("score")
            if _bounded_unit_number(score):
                _add_check(checks, "example.governance_friction.score", "pass", "score in [0,1]")
            else:
                _add_check(
                    checks,
                    "example.governance_friction.score",
                    "fail",
                    "score must be number in [0,1]",
                )

            components = governance_friction.get("components")
            if not isinstance(components, dict):
                _add_check(
                    checks,
                    "example.governance_friction.components",
                    "fail",
                    "components must be object",
                )
            else:
                for key in ("delta_t", "delta_wave"):
                    value = components.get(key)
                    if value is None:
                        _add_check(
                            checks,
                            f"example.governance_friction.components.{key}",
                            "warn",
                            "value is null",
                        )
                    elif _bounded_unit_number(value):
                        _add_check(
                            checks,
                            f"example.governance_friction.components.{key}",
                            "pass",
                            f"{key} in [0,1]",
                        )
                    else:
                        _add_check(
                            checks,
                            f"example.governance_friction.components.{key}",
                            "fail",
                            f"{key} must be number in [0,1] or null",
                        )

                mismatch = components.get("boundary_mismatch")
                if isinstance(mismatch, bool):
                    _add_check(
                        checks,
                        "example.governance_friction.components.boundary_mismatch",
                        "pass",
                        "boundary_mismatch is boolean",
                    )
                else:
                    _add_check(
                        checks,
                        "example.governance_friction.components.boundary_mismatch",
                        "fail",
                        "boundary_mismatch must be boolean",
                    )

        routing_trace = example_payload.get("routing_trace")
        if not isinstance(routing_trace, dict):
            _add_check(checks, "example.routing_trace", "fail", "routing_trace must be object")
        else:
            route = routing_trace.get("route")
            if isinstance(route, str) and route in ALLOWED_ROUTES:
                _add_check(checks, "example.routing_trace.route", "pass", "route valid")
            else:
                _add_check(checks, "example.routing_trace.route", "fail", "invalid route")

            journal_eligible = routing_trace.get("journal_eligible")
            if isinstance(journal_eligible, bool):
                _add_check(
                    checks,
                    "example.routing_trace.journal_eligible",
                    "pass",
                    "journal_eligible is boolean",
                )
            else:
                _add_check(
                    checks,
                    "example.routing_trace.journal_eligible",
                    "fail",
                    "journal_eligible must be boolean",
                )

            reason = routing_trace.get("reason")
            if isinstance(reason, str) and reason.strip():
                _add_check(checks, "example.routing_trace.reason", "pass", "reason present")
            else:
                _add_check(checks, "example.routing_trace.reason", "fail", "reason missing")

    failed_count = sum(1 for check in checks if check.get("status") == "fail")
    warning_count = sum(1 for check in checks if check.get("status") == "warn")

    payload = {
        "generated_at": _iso_now(),
        "source": "scripts/run_memory_governance_contract_check.py",
        "ok": failed_count == 0,
        "failed_count": failed_count,
        "warning_count": warning_count,
        "inputs": {
            "schema": schema_relpath,
            "example": example_relpath,
        },
        "checks": checks,
    }
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run memory governance contract verification and write status artifacts."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--schema",
        default="spec/governance/memory_governance_contract_v1.schema.json",
        help="Contract schema JSON path.",
    )
    parser.add_argument(
        "--example",
        default="spec/governance/memory_governance_contract_v1.example.json",
        help="Contract example JSON path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when validation fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()

    payload = run_check(
        repo_root=repo_root,
        schema_relpath=args.schema,
        example_relpath=args.example,
    )
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload.get("ok", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
