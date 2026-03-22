#!/usr/bin/env python3
"""Validate public-safe adapter dataset rows against the L8 contract."""

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

import scripts.run_l7_l8_contract_artifacts as contract_artifacts  # noqa: E402

JSON_FILENAME = "l8_adapter_dataset_gate_latest.json"
MARKDOWN_FILENAME = "l8_adapter_dataset_gate_latest.md"
MIN_VERIFIER_PASS_RATE_FLOOR = 0.9
BLOCKED_SOURCE_EXACT = ("MEMORY.md", ".env", ".env.local")
BLOCKED_SOURCE_PREFIXES = ("memory/", "vectors/", "vault/")
BLOCKED_SOURCE_SUBSTRINGS = (
    "tonesoul-memory-vault",
    "self_journal",
    "red_team",
    "red-team",
    "jailbreak",
    "attack_dict",
    "payload_dict",
)
REQUIRED_REVIEW_FLAGS = (
    "public_safe",
    "privacy_cleared",
    "governance_reviewed",
    "approved_for_adapter_rl",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _resolve_path(repo_root: Path, raw: str) -> Path:
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_records(path: Path) -> tuple[str, list[dict[str, Any]], list[str]]:
    issues: list[str] = []
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        records: list[dict[str, Any]] = []
        for index, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(f"line {index}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(payload, dict):
                issues.append(f"line {index}: record must be an object")
                continue
            records.append(payload)
        return "jsonl", records, issues

    payload = _load_json(path)
    if isinstance(payload, dict):
        return "json", [payload], issues
    if isinstance(payload, list):
        records = [item for item in payload if isinstance(item, dict)]
        if len(records) != len(payload):
            issues.append("json array must contain only object records")
        return "json", records, issues

    issues.append("input must be a JSON object, JSON array, or JSONL stream")
    return "json", [], issues


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_against_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    issues: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        type_options = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(value, option) for option in type_options):
            issues.append(f"{path}: expected type {type_options}, got {type(value).__name__}")
            return issues

    if "const" in schema and value != schema["const"]:
        issues.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        issues.append(f"{path}: value {value!r} not in enum")

    if isinstance(value, str) and "minLength" in schema and len(value) < int(schema["minLength"]):
        issues.append(f"{path}: minimum length is {schema['minLength']}")
    if _matches_type(value, "number"):
        if "minimum" in schema and float(value) < float(schema["minimum"]):
            issues.append(f"{path}: minimum is {schema['minimum']}")
        if "maximum" in schema and float(value) > float(schema["maximum"]):
            issues.append(f"{path}: maximum is {schema['maximum']}")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                issues.append(f"{path}: missing required field {key!r}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    issues.append(f"{path}: unexpected field {key!r}")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                issues.extend(_validate_against_schema(value[key], child_schema, f"{path}.{key}"))

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                issues.extend(_validate_against_schema(item, item_schema, f"{path}[{index}]"))

    return issues


def _path_policy_issue(path_value: str) -> str | None:
    normalized = _normalize_path(path_value).lower()
    if not normalized:
        return None
    if normalized in {item.lower() for item in BLOCKED_SOURCE_EXACT}:
        return f"blocked exact source path: {path_value}"
    if any(normalized.startswith(prefix) for prefix in BLOCKED_SOURCE_PREFIXES):
        return f"blocked source prefix: {path_value}"
    if any(token in normalized for token in BLOCKED_SOURCE_SUBSTRINGS):
        return f"blocked source token in path: {path_value}"
    return None


def _record_identifier(record: dict[str, Any], index: int) -> str:
    row_id = str(record.get("row_id") or "").strip()
    if row_id:
        return row_id
    return f"record-{index + 1}"


def _allowed_behavior_classes(repo_root: Path, schema: dict[str, Any]) -> set[str]:
    try:
        payload = contract_artifacts.build_l8_payload(repo_root)
    except FileNotFoundError:
        payload = {}

    allowed = {
        str(item.get("id"))
        for item in payload.get("allowed_classes", [])
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }
    if allowed:
        return allowed

    behavior_schema = (
        schema.get("properties", {}).get("behavior_class", {})
        if isinstance(schema.get("properties"), dict)
        else {}
    )
    enum_values = behavior_schema.get("enum", []) if isinstance(behavior_schema, dict) else []
    return {str(item) for item in enum_values if str(item).strip()}


def _validate_record_policy(
    record: dict[str, Any],
    *,
    index: int,
    schema: dict[str, Any],
    allowed_behavior_classes: set[str],
) -> dict[str, Any]:
    record_id = _record_identifier(record, index)
    issues = _validate_against_schema(record, schema, "$")

    behavior_class = str(record.get("behavior_class") or "").strip()
    if behavior_class and behavior_class not in allowed_behavior_classes:
        issues.append(f"$.behavior_class: {behavior_class!r} is not approved by the L8 contract")

    source_artifact = record.get("source_artifact")
    if isinstance(source_artifact, dict):
        if source_artifact.get("public_safe") is not True:
            issues.append("$.source_artifact.public_safe: must be true")
        source_path_issue = _path_policy_issue(str(source_artifact.get("path") or ""))
        if source_path_issue:
            issues.append(f"$.source_artifact.path: {source_path_issue}")

    provenance = record.get("provenance")
    if isinstance(provenance, dict):
        provenance_issue = _path_policy_issue(str(provenance.get("source_path") or ""))
        if provenance_issue:
            issues.append(f"$.provenance.source_path: {provenance_issue}")

    distillation_review = record.get("distillation_review")
    if isinstance(distillation_review, dict):
        for field_name in REQUIRED_REVIEW_FLAGS:
            if distillation_review.get(field_name) is not True:
                issues.append(f"$.distillation_review.{field_name}: must be true")

    evaluation = record.get("evaluation_expectations")
    if isinstance(evaluation, dict):
        if evaluation.get("auditability_required") is not True:
            issues.append("$.evaluation_expectations.auditability_required: must be true")
        if evaluation.get("reversible") is not True:
            issues.append("$.evaluation_expectations.reversible: must be true")
        floor = evaluation.get("verifier_pass_rate_floor")
        if isinstance(floor, (int, float)) and not isinstance(floor, bool):
            if float(floor) < MIN_VERIFIER_PASS_RATE_FLOOR:
                issues.append(
                    "$.evaluation_expectations.verifier_pass_rate_floor: "
                    f"must be >= {MIN_VERIFIER_PASS_RATE_FLOOR}"
                )

    return {
        "row_id": record_id,
        "ok": not issues,
        "issue_count": len(issues),
        "issues": issues,
        "source_repo": record.get("source_repo"),
        "behavior_class": behavior_class,
        "training_objective": record.get("training_objective"),
    }


def build_report(
    *,
    repo_root: Path,
    input_path: Path,
    schema_path: Path,
) -> dict[str, Any]:
    schema = _load_json(schema_path)
    input_format, records, load_issues = _load_records(input_path)
    allowed_behavior_classes = _allowed_behavior_classes(repo_root, schema)

    record_reports = [
        _validate_record_policy(
            record,
            index=index,
            schema=schema,
            allowed_behavior_classes=allowed_behavior_classes,
        )
        for index, record in enumerate(records)
    ]

    approved_count = sum(1 for item in record_reports if item["ok"])
    rejected_count = len(record_reports) - approved_count
    ok = not load_issues and rejected_count == 0 and len(record_reports) > 0
    primary_status_line = (
        "l8_dataset_gate_ready | "
        f"records={len(record_reports)} approved={approved_count} rejected={rejected_count} "
        f"load_issues={len(load_issues)}"
    )
    runtime_status_line = (
        "entrypoints | "
        f"input={_normalize_path(str(input_path.relative_to(repo_root)))} "
        f"schema={_normalize_path(str(schema_path.relative_to(repo_root)))} "
        f"contract={contract_artifacts.L8_CONTRACT_PATH}"
    )
    artifact_policy_status_line = (
        "adapter_rows=public_safe_only | "
        f"min_verifier_pass_rate_floor={MIN_VERIFIER_PASS_RATE_FLOOR:.2f} "
        "private_memory=forbidden"
    )

    return {
        "generated_at": _iso_now(),
        "ok": ok,
        "canonical_contract": contract_artifacts.L8_CONTRACT_PATH,
        "dataset_schema_ref": _normalize_path(str(schema_path.relative_to(repo_root))),
        "input_path": _normalize_path(str(input_path.relative_to(repo_root))),
        "input_format": input_format,
        "required_review_flags": list(REQUIRED_REVIEW_FLAGS),
        "minimum_verifier_pass_rate_floor": MIN_VERIFIER_PASS_RATE_FLOOR,
        "blocked_source_exact": list(BLOCKED_SOURCE_EXACT),
        "blocked_source_prefixes": list(BLOCKED_SOURCE_PREFIXES),
        "blocked_source_substrings": list(BLOCKED_SOURCE_SUBSTRINGS),
        "allowed_behavior_classes": sorted(allowed_behavior_classes),
        "load_issues": load_issues,
        "records": record_reports,
        "metrics": {
            "record_count": len(record_reports),
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "load_issue_count": len(load_issues),
        },
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# L8 Adapter Dataset Gate Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- ok: `{str(payload['ok']).lower()}`",
        f"- input_path: `{payload['input_path']}`",
        f"- input_format: `{payload['input_format']}`",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Metrics",
        f"- record_count: `{payload['metrics']['record_count']}`",
        f"- approved_count: `{payload['metrics']['approved_count']}`",
        f"- rejected_count: `{payload['metrics']['rejected_count']}`",
        f"- load_issue_count: `{payload['metrics']['load_issue_count']}`",
        "",
        "## Required Review Flags",
    ]
    for item in payload.get("required_review_flags", []):
        lines.append(f"- `{item}`")

    lines.extend(["", "## Record Results"])
    for record in payload.get("records", []):
        lines.append(f"- `{record['row_id']}` ok=`{str(record['ok']).lower()}`")
        if record.get("issues"):
            for issue in record["issues"]:
                lines.append(f"  - {issue}")

    if payload.get("load_issues"):
        lines.extend(["", "## Load Issues"])
        for issue in payload["load_issues"]:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate L8 adapter dataset rows.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--input",
        default=contract_artifacts.DATASET_EXAMPLE_PATH,
        help="Adapter dataset JSON or JSONL file to validate.",
    )
    parser.add_argument(
        "--schema-path",
        default=contract_artifacts.DATASET_SCHEMA_PATH,
        help="Adapter dataset schema path.",
    )
    parser.add_argument(
        "--out-dir", default="docs/status", help="Output directory for generated artifacts."
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if validation fails.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    input_path = _resolve_path(repo_root, str(args.input))
    schema_path = _resolve_path(repo_root, str(args.schema_path))
    out_dir = _resolve_path(repo_root, str(args.out_dir))

    payload = build_report(
        repo_root=repo_root,
        input_path=input_path,
        schema_path=schema_path,
    )
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _emit(payload)
    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
