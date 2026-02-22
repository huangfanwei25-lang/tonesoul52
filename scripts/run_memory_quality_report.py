"""
Generate memory-quality status artifacts and learning samples from self-journal data.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "memory_quality_latest.json"
MARKDOWN_FILENAME = "memory_quality_latest.md"
SAMPLES_FILENAME = "memory_learning_samples_latest.jsonl"
FAILURE_VERDICTS = {"block", "declare_stance"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    invalid_line_count = 0
    if not path.exists():
        return rows, invalid_line_count

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_line_count += 1
                continue
            if isinstance(payload, dict):
                rows.append(payload)
            else:
                invalid_line_count += 1

    return rows, invalid_line_count


def _entry_payload(raw: dict[str, Any]) -> dict[str, Any]:
    payload = raw.get("payload")
    if isinstance(payload, dict):
        return payload
    return raw


def _extract_verdict(entry: dict[str, Any]) -> str:
    verdict = entry.get("verdict")
    if isinstance(verdict, str):
        normalized = verdict.strip().lower()
        if normalized:
            return normalized
    if isinstance(verdict, dict):
        normalized = str(verdict.get("verdict") or "").strip().lower()
        if normalized:
            return normalized

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        transcript_verdict = transcript.get("verdict")
        if isinstance(transcript_verdict, dict):
            normalized = str(transcript_verdict.get("verdict") or "").strip().lower()
            if normalized:
                return normalized

    return "unknown"


def _extract_timestamp(entry: dict[str, Any]) -> str:
    timestamp = entry.get("timestamp")
    if isinstance(timestamp, str) and timestamp.strip():
        return timestamp.strip()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        transcript_timestamp = transcript.get("timestamp")
        if isinstance(transcript_timestamp, str) and transcript_timestamp.strip():
            return transcript_timestamp.strip()
    return ""


def _extract_coherence(entry: dict[str, Any]) -> float | None:
    coherence = entry.get("coherence")
    if isinstance(coherence, (float, int)):
        return float(coherence)
    if isinstance(coherence, dict):
        value = coherence.get("c_inter")
        if isinstance(value, (float, int)):
            return float(value)

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        transcript_coherence = transcript.get("coherence")
        if isinstance(transcript_coherence, (float, int)):
            return float(transcript_coherence)
        if isinstance(transcript_coherence, dict):
            value = transcript_coherence.get("c_inter")
            if isinstance(value, (float, int)):
                return float(value)
    return None


def _extract_core_divergence(entry: dict[str, Any]) -> str:
    value = entry.get("core_divergence")
    if isinstance(value, str) and value.strip():
        return value.strip()

    divergence = entry.get("divergence_analysis")
    if isinstance(divergence, dict):
        value = divergence.get("core_divergence")
        if isinstance(value, str) and value.strip():
            return value.strip()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        divergence = transcript.get("divergence_analysis")
        if isinstance(divergence, dict):
            value = divergence.get("core_divergence")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _extract_recommended_action(entry: dict[str, Any]) -> str:
    value = entry.get("recommended_action")
    if isinstance(value, str) and value.strip():
        return value.strip()

    divergence = entry.get("divergence_analysis")
    if isinstance(divergence, dict):
        value = divergence.get("recommended_action")
        if isinstance(value, str) and value.strip():
            return value.strip()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        divergence = transcript.get("divergence_analysis")
        if isinstance(divergence, dict):
            value = divergence.get("recommended_action")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _extract_contract_records(entry: dict[str, Any]) -> list[dict[str, Any]]:
    transcript = entry.get("transcript")
    if not isinstance(transcript, dict):
        return []
    contract = transcript.get("multi_agent_contract")
    if not isinstance(contract, dict):
        return []
    records = contract.get("records")
    if not isinstance(records, list):
        return []
    return [item for item in records if isinstance(item, dict)]


def _record_has_evidence(record: dict[str, Any]) -> bool:
    evidence = record.get("evidence")
    return isinstance(evidence, list) and any(str(item).strip() for item in evidence)


def _entry_has_provenance(entry: dict[str, Any]) -> bool:
    for key in ("intent_id", "genesis", "provenance", "isnad"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (list, dict)) and value:
            return True

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        for key in ("intent_id", "genesis", "provenance", "isnad"):
            value = transcript.get(key)
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, (list, dict)) and value:
                return True
    return False


def _resolve_risk_level(entry: dict[str, Any], verdict: str) -> str:
    risk_level = entry.get("risk_level")
    if isinstance(risk_level, str) and risk_level.strip():
        return risk_level.strip().lower()

    high_risk = 0
    for record in _extract_contract_records(entry):
        risk = record.get("risk")
        if not isinstance(risk, dict):
            continue
        level = str(risk.get("level") or "").strip().lower()
        if level in {"high", "critical"}:
            high_risk += 1
    if high_risk > 0:
        return "high"
    if verdict == "block":
        return "high"
    if verdict == "declare_stance":
        return "medium"
    return "low"


def _safe_float(value: object) -> float | None:
    if isinstance(value, (float, int)):
        return float(value)
    return None


def _build_learning_sample(entry: dict[str, Any], index: int) -> dict[str, Any] | None:
    verdict = _extract_verdict(entry)
    if verdict not in FAILURE_VERDICTS:
        return None

    transcript = entry.get("transcript")
    transcript_payload = transcript if isinstance(transcript, dict) else {}
    contract_records = _extract_contract_records(entry)
    evidence_record_count = sum(1 for record in contract_records if _record_has_evidence(record))
    high_risk_record_count = 0
    for record in contract_records:
        risk = record.get("risk")
        if not isinstance(risk, dict):
            continue
        level = str(risk.get("level") or "").strip().lower()
        if level in {"high", "critical"}:
            high_risk_record_count += 1

    coherence = _extract_coherence(entry)
    timestamp = _extract_timestamp(entry)
    core_divergence = _extract_core_divergence(entry)
    recommended_action = _extract_recommended_action(entry)
    risk_level = _resolve_risk_level(entry, verdict)
    uncertainty_level = _safe_float(entry.get("uncertainty_level"))
    uncertainty_band = entry.get("uncertainty_band")
    if not isinstance(uncertainty_band, str) or not uncertainty_band.strip():
        uncertainty_band = "unknown"

    intent_id = entry.get("intent_id")
    if not isinstance(intent_id, str) or not intent_id.strip():
        intent_id = transcript_payload.get("intent_id")
    if not isinstance(intent_id, str) or not intent_id.strip():
        intent_id = None

    genesis = entry.get("genesis")
    if not isinstance(genesis, str) or not genesis.strip():
        genesis = transcript_payload.get("genesis")
    if not isinstance(genesis, str) or not genesis.strip():
        genesis = None

    provenance_present = _entry_has_provenance(entry)
    divergence_present = bool(core_divergence)
    contract_present = len(contract_records) > 0

    sample_id = f"{timestamp or 'unknown'}:{verdict}:{index}"

    return {
        "sample_id": sample_id,
        "source": "memory/self_journal.jsonl",
        "timestamp": timestamp,
        "verdict": verdict,
        "coherence": coherence,
        "risk_level": risk_level,
        "uncertainty_level": uncertainty_level,
        "uncertainty_band": uncertainty_band,
        "core_divergence": core_divergence,
        "recommended_action": recommended_action,
        "intent_id": intent_id,
        "genesis": genesis,
        "provenance_present": provenance_present,
        "divergence_present": divergence_present,
        "contract_present": contract_present,
        "contract_record_count": len(contract_records),
        "contract_evidence_record_count": evidence_record_count,
        "contract_high_risk_record_count": high_risk_record_count,
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def build_report(journal_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    warnings: list[str] = []
    issues: list[str] = []
    verdict_counts: Counter[str] = Counter()
    risk_level_counts: Counter[str] = Counter()
    uncertainty_band_counts: Counter[str] = Counter()
    coherence_sum = 0.0
    coherence_count = 0
    high_risk_failure_count = 0

    if not journal_path.exists():
        warnings.append(f"journal path does not exist: {journal_path}")
        payload = {
            "generated_at": _iso_now(),
            "overall_ok": True,
            "inputs": {"journal_path": journal_path.as_posix()},
            "metrics": {
                "entry_count": 0,
                "failure_case_count": 0,
                "learning_sample_count": 0,
                "invalid_json_line_count": 0,
                "high_risk_failure_count": 0,
                "verdict_counts": {},
                "risk_level_counts": {},
                "uncertainty_band_counts": {},
                "average_failure_coherence": None,
            },
            "quality_signals": {
                "failure_case_rate": 0.0,
                "provenance_coverage_rate": 0.0,
                "divergence_coverage_rate": 0.0,
                "contract_coverage_rate": 0.0,
                "contract_evidence_coverage_rate": 0.0,
            },
            "issues": [],
            "warnings": warnings,
        }
        return payload, []

    raw_rows, invalid_json_line_count = _read_jsonl(journal_path)
    entries = [_entry_payload(row) for row in raw_rows]
    samples: list[dict[str, Any]] = []
    provenance_present_count = 0
    divergence_present_count = 0
    contract_present_count = 0
    evidence_present_count = 0

    for index, entry in enumerate(entries):
        verdict = _extract_verdict(entry)
        verdict_counts[verdict] += 1
        sample = _build_learning_sample(entry, index)
        if sample is None:
            continue
        samples.append(sample)

        risk_level = str(sample.get("risk_level") or "unknown").strip().lower()
        risk_level_counts[risk_level] += 1
        if risk_level in {"high", "critical"}:
            high_risk_failure_count += 1

        uncertainty_band = str(sample.get("uncertainty_band") or "unknown").strip().lower()
        uncertainty_band_counts[uncertainty_band] += 1

        coherence = sample.get("coherence")
        if isinstance(coherence, (int, float)):
            coherence_sum += float(coherence)
            coherence_count += 1

        if bool(sample.get("provenance_present")):
            provenance_present_count += 1
        if bool(sample.get("divergence_present")):
            divergence_present_count += 1
        if bool(sample.get("contract_present")):
            contract_present_count += 1
        if int(sample.get("contract_evidence_record_count") or 0) > 0:
            evidence_present_count += 1

    failure_case_count = len(samples)
    entry_count = len(entries)
    average_failure_coherence = (
        round(coherence_sum / coherence_count, 4) if coherence_count > 0 else None
    )

    if invalid_json_line_count > 0:
        issues.append(f"detected {invalid_json_line_count} invalid JSON line(s) in journal")

    for index, sample in enumerate(samples):
        verdict = sample.get("verdict")
        timestamp = sample.get("timestamp")
        if verdict not in FAILURE_VERDICTS:
            issues.append(f"sample[{index}] has invalid verdict: {verdict}")
        if not isinstance(timestamp, str):
            issues.append(f"sample[{index}] timestamp must be string")

    overall_ok = len(issues) == 0
    payload = {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "inputs": {"journal_path": journal_path.as_posix()},
        "metrics": {
            "entry_count": entry_count,
            "failure_case_count": failure_case_count,
            "learning_sample_count": failure_case_count,
            "invalid_json_line_count": invalid_json_line_count,
            "high_risk_failure_count": high_risk_failure_count,
            "verdict_counts": dict(verdict_counts),
            "risk_level_counts": dict(risk_level_counts),
            "uncertainty_band_counts": dict(uncertainty_band_counts),
            "average_failure_coherence": average_failure_coherence,
        },
        "quality_signals": {
            "failure_case_rate": _rate(failure_case_count, entry_count),
            "provenance_coverage_rate": _rate(provenance_present_count, failure_case_count),
            "divergence_coverage_rate": _rate(divergence_present_count, failure_case_count),
            "contract_coverage_rate": _rate(contract_present_count, failure_case_count),
            "contract_evidence_coverage_rate": _rate(evidence_present_count, failure_case_count),
        },
        "issues": issues,
        "warnings": warnings,
    }
    return payload, samples


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    quality = payload.get("quality_signals", {})
    lines = [
        "# Memory Quality Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- journal_path: {payload.get('inputs', {}).get('journal_path', '')}",
        "",
        "## Metrics",
        f"- entry_count: {metrics.get('entry_count', 0)}",
        f"- failure_case_count: {metrics.get('failure_case_count', 0)}",
        f"- learning_sample_count: {metrics.get('learning_sample_count', 0)}",
        f"- invalid_json_line_count: {metrics.get('invalid_json_line_count', 0)}",
        f"- high_risk_failure_count: {metrics.get('high_risk_failure_count', 0)}",
        f"- average_failure_coherence: {metrics.get('average_failure_coherence')}",
        "",
        "## Quality Signals",
        f"- failure_case_rate: {quality.get('failure_case_rate', 0.0)}",
        f"- provenance_coverage_rate: {quality.get('provenance_coverage_rate', 0.0)}",
        f"- divergence_coverage_rate: {quality.get('divergence_coverage_rate', 0.0)}",
        f"- contract_coverage_rate: {quality.get('contract_coverage_rate', 0.0)}",
        f"- contract_evidence_coverage_rate: {quality.get('contract_evidence_coverage_rate', 0.0)}",
    ]

    verdict_counts = metrics.get("verdict_counts", {})
    if isinstance(verdict_counts, dict) and verdict_counts:
        lines.append("")
        lines.append("## Verdict Counts")
        for verdict, count in sorted(
            verdict_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {verdict}: {count}")

    risk_counts = metrics.get("risk_level_counts", {})
    if isinstance(risk_counts, dict) and risk_counts:
        lines.append("")
        lines.append("## Risk Levels")
        for level, count in sorted(risk_counts.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append(f"- {level}: {count}")

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


def _write_samples_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate memory quality report and learning samples."
    )
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
        "--samples-path",
        default=None,
        help="Optional path to generated learning sample JSONL file.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report issues are detected.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    journal_path = Path(args.journal_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    if args.samples_path:
        samples_path = Path(args.samples_path).resolve()
    else:
        samples_path = out_dir / SAMPLES_FILENAME

    payload, samples = build_report(journal_path)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _write_samples_jsonl(samples_path, samples)
    _emit(payload)

    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
