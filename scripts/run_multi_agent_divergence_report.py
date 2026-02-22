"""
Generate multi-agent divergence status artifacts from self-journal records.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "multi_agent_divergence_latest.json"
MARKDOWN_FILENAME = "multi_agent_divergence_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
    return records


def _entry_payload(raw: dict[str, Any]) -> dict[str, Any]:
    payload = raw.get("payload")
    if isinstance(payload, dict):
        return payload
    return raw


def _extract_verdict(entry: dict[str, Any]) -> str:
    verdict = entry.get("verdict")
    if isinstance(verdict, str):
        text = verdict.strip().lower()
        if text:
            return text
    if isinstance(verdict, dict):
        text = str(verdict.get("verdict") or "").strip().lower()
        if text:
            return text
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        verdict_payload = transcript.get("verdict")
        if isinstance(verdict_payload, dict):
            text = str(verdict_payload.get("verdict") or "").strip().lower()
            if text:
                return text
    return "unknown"


def _extract_core_divergence(entry: dict[str, Any]) -> str:
    if isinstance(entry.get("core_divergence"), str):
        text = entry["core_divergence"].strip()
        if text:
            return text
    divergence = entry.get("divergence_analysis")
    if isinstance(divergence, dict):
        text = str(divergence.get("core_divergence") or "").strip()
        if text:
            return text
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        divergence = transcript.get("divergence_analysis")
        if isinstance(divergence, dict):
            text = str(divergence.get("core_divergence") or "").strip()
            if text:
                return text
    return ""


def _validate_contract_record(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"record[{index}]"
    role = record.get("role")
    claim = record.get("claim")
    evidence = record.get("evidence")
    risk = record.get("risk")
    handoff = record.get("handoff")

    if not isinstance(role, str) or not role.strip():
        errors.append(f"{prefix}.role must be non-empty string")
    if not isinstance(claim, str) or not claim.strip():
        errors.append(f"{prefix}.claim must be non-empty string")
    if not isinstance(evidence, list):
        errors.append(f"{prefix}.evidence must be list")
    if not isinstance(risk, dict):
        errors.append(f"{prefix}.risk must be object")
    else:
        if not isinstance(risk.get("level"), str) or not str(risk.get("level")).strip():
            errors.append(f"{prefix}.risk.level must be non-empty string")
        if not isinstance(risk.get("basis"), str) or not str(risk.get("basis")).strip():
            errors.append(f"{prefix}.risk.basis must be non-empty string")
    if not isinstance(handoff, dict):
        errors.append(f"{prefix}.handoff must be object")
    else:
        if (
            not isinstance(handoff.get("next_role"), str)
            or not str(handoff.get("next_role")).strip()
        ):
            errors.append(f"{prefix}.handoff.next_role must be non-empty string")
        if not isinstance(handoff.get("action"), str) or not str(handoff.get("action")).strip():
            errors.append(f"{prefix}.handoff.action must be non-empty string")
    return errors


def build_report(journal_path: Path) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []
    verdict_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    risk_level_counts: Counter[str] = Counter()
    handoff_next_role_counts: Counter[str] = Counter()
    divergence_examples: list[str] = []
    high_risk_record_count = 0
    contract_entry_count = 0
    contract_record_count = 0
    invalid_record_count = 0

    if not journal_path.exists():
        warnings.append(f"journal path does not exist: {journal_path}")
        return {
            "generated_at": _iso_now(),
            "overall_ok": True,
            "inputs": {"journal_path": journal_path.as_posix()},
            "metrics": {
                "entry_count": 0,
                "contract_entry_count": 0,
                "contract_record_count": 0,
                "invalid_record_count": 0,
                "high_risk_record_count": 0,
                "verdict_counts": {},
                "role_counts": {},
                "risk_level_counts": {},
                "handoff_next_role_counts": {},
            },
            "divergence_examples": [],
            "issues": [],
            "warnings": warnings,
        }

    raw_records = _read_jsonl(journal_path)
    entries = [_entry_payload(item) for item in raw_records]

    for entry_index, entry in enumerate(entries):
        verdict_counts[_extract_verdict(entry)] += 1
        core_divergence = _extract_core_divergence(entry)
        if (
            core_divergence
            and core_divergence not in divergence_examples
            and len(divergence_examples) < 10
        ):
            divergence_examples.append(core_divergence)

        transcript = entry.get("transcript")
        if not isinstance(transcript, dict):
            continue
        contract = transcript.get("multi_agent_contract")
        if contract is None:
            continue
        contract_entry_count += 1
        if not isinstance(contract, dict):
            issues.append(f"entry[{entry_index}].multi_agent_contract must be object")
            continue
        records = contract.get("records")
        if not isinstance(records, list):
            issues.append(f"entry[{entry_index}].multi_agent_contract.records must be list")
            continue

        for record_index, record in enumerate(records):
            contract_record_count += 1
            if not isinstance(record, dict):
                invalid_record_count += 1
                issues.append(f"entry[{entry_index}].record[{record_index}] must be object")
                continue
            record_errors = _validate_contract_record(record, record_index)
            if record_errors:
                invalid_record_count += 1
                for detail in record_errors:
                    issues.append(f"entry[{entry_index}].{detail}")
                continue

            role = str(record.get("role")).strip()
            role_counts[role] += 1

            risk = record.get("risk")
            if isinstance(risk, dict):
                level = str(risk.get("level")).strip().lower()
                if level:
                    risk_level_counts[level] += 1
                    if level in {"high", "critical"}:
                        high_risk_record_count += 1

            handoff = record.get("handoff")
            if isinstance(handoff, dict):
                next_role = str(handoff.get("next_role")).strip()
                if next_role:
                    handoff_next_role_counts[next_role] += 1

    overall_ok = len(issues) == 0
    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "inputs": {"journal_path": journal_path.as_posix()},
        "metrics": {
            "entry_count": len(entries),
            "contract_entry_count": contract_entry_count,
            "contract_record_count": contract_record_count,
            "invalid_record_count": invalid_record_count,
            "high_risk_record_count": high_risk_record_count,
            "verdict_counts": dict(verdict_counts),
            "role_counts": dict(role_counts),
            "risk_level_counts": dict(risk_level_counts),
            "handoff_next_role_counts": dict(handoff_next_role_counts),
        },
        "divergence_examples": divergence_examples,
        "issues": issues,
        "warnings": warnings,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    lines = [
        "# Multi-Agent Divergence Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- journal_path: {payload.get('inputs', {}).get('journal_path', '')}",
        "",
        "## Metrics",
        f"- entry_count: {metrics.get('entry_count', 0)}",
        f"- contract_entry_count: {metrics.get('contract_entry_count', 0)}",
        f"- contract_record_count: {metrics.get('contract_record_count', 0)}",
        f"- invalid_record_count: {metrics.get('invalid_record_count', 0)}",
        f"- high_risk_record_count: {metrics.get('high_risk_record_count', 0)}",
    ]

    role_counts = metrics.get("role_counts", {})
    if isinstance(role_counts, dict) and role_counts:
        lines.append("")
        lines.append("## Role Counts")
        for role, count in sorted(role_counts.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append(f"- {role}: {count}")

    risk_counts = metrics.get("risk_level_counts", {})
    if isinstance(risk_counts, dict) and risk_counts:
        lines.append("")
        lines.append("## Risk Levels")
        for level, count in sorted(risk_counts.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append(f"- {level}: {count}")

    handoff_counts = metrics.get("handoff_next_role_counts", {})
    if isinstance(handoff_counts, dict) and handoff_counts:
        lines.append("")
        lines.append("## Handoff Targets")
        for role, count in sorted(
            handoff_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {role}: {count}")

    divergence_examples = payload.get("divergence_examples", [])
    if isinstance(divergence_examples, list) and divergence_examples:
        lines.append("")
        lines.append("## Divergence Examples")
        for item in divergence_examples[:10]:
            lines.append(f"- {item}")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues[:30]:
            lines.append(f"- {issue}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings[:20]:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate multi-agent divergence report.")
    parser.add_argument(
        "--journal-path",
        default="memory/self_journal.jsonl",
        help="Path to self-journal JSONL file.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when invalid contract records are detected.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    journal_path = Path(args.journal_path).resolve()
    out_dir = Path(args.out_dir).resolve()

    payload = build_report(journal_path)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
