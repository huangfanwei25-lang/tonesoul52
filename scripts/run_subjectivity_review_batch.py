"""Generate an operator review batch from subjectivity tension groups."""

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

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB  # noqa: E402
from tonesoul.memory.subjectivity_handoff import (  # noqa: E402
    extend_handoff_markdown,
    extend_status_lines_markdown,
)
from tonesoul.memory.subjectivity_review_batch import (  # noqa: E402
    build_subjectivity_review_batch_report,
)

JSON_FILENAME = "subjectivity_review_batch_latest.json"
MARKDOWN_FILENAME = "subjectivity_review_batch_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _resolve_source(value: str | None) -> MemorySource | None:
    if value is None:
        return None
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    return MemorySource(normalized)


def build_report(
    db_path: Path,
    *,
    source_name: str | None = None,
) -> tuple[dict[str, Any], str]:
    warnings: list[str] = []
    issues: list[str] = []
    db_exists = db_path.exists()
    source = _resolve_source(source_name)
    batch = build_subjectivity_review_batch_report(SqliteSoulDB(db_path=db_path), source=source)

    unresolved_row_count = int(batch.get("summary", {}).get("unresolved_row_count") or 0)
    review_group_count = int(batch.get("summary", {}).get("review_group_count") or 0)
    if not db_exists:
        warnings.append(f"soul db path did not exist before review-batch run: {db_path.as_posix()}")
    if unresolved_row_count == 0:
        warnings.append("no unresolved tension rows found for review batching")
    if unresolved_row_count > 0 and review_group_count == 0:
        issues.append("unresolved tensions existed but no review groups were produced")

    payload = {
        "generated_at": _iso_now(),
        "overall_ok": len(issues) == 0,
        "source": "scripts/run_subjectivity_review_batch.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "source": source.value if source is not None else "all",
        },
        "batch": batch,
        "issues": issues,
        "warnings": warnings,
    }
    return payload, _render_markdown(payload)


def _render_markdown(payload: dict[str, Any]) -> str:
    batch = payload.get("batch", {})
    summary = batch.get("summary", {})
    handoff = batch.get("handoff", {})
    review_groups = list(batch.get("review_groups") or [])
    status_lines = batch.get("status_lines")
    admissibility_status_lines = batch.get("admissibility_status_lines")

    def _format_histogram(histogram: Any) -> str:
        if not isinstance(histogram, dict) or not histogram:
            return ""
        parts: list[str] = []
        for count, total in sorted(histogram.items(), key=lambda item: int(item[0])):
            parts.append(f"{count}=>{total}")
        return ", ".join(parts)

    lines = [
        "# Subjectivity Review Batch Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- db_path: {payload.get('inputs', {}).get('db_path', '')}",
        f"- source: {payload.get('inputs', {}).get('source', 'all')}",
    ]

    extend_handoff_markdown(
        lines,
        handoff=handoff,
        extra_fields=["top_queue_posture"],
    )

    lines.extend(
        [
            "",
            "## Summary",
            f"- unresolved_row_count: {summary.get('unresolved_row_count', 0)}",
            f"- semantic_group_count: {summary.get('semantic_group_count', 0)}",
            f"- lineage_group_count: {summary.get('lineage_group_count', 0)}",
            f"- review_group_count: {summary.get('review_group_count', 0)}",
        ]
    )

    default_status_counts = summary.get("default_status_counts", {})
    if isinstance(default_status_counts, dict) and default_status_counts:
        lines.append("")
        lines.append("## Default Status Counts")
        for name, count in sorted(
            default_status_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    revisit_readiness_counts = summary.get("revisit_readiness_counts", {})
    if isinstance(revisit_readiness_counts, dict) and revisit_readiness_counts:
        lines.append("")
        lines.append("## Revisit Readiness Counts")
        for name, count in sorted(
            revisit_readiness_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    carry_forward_annotation_counts = summary.get("carry_forward_annotation_counts", {})
    if isinstance(carry_forward_annotation_counts, dict) and carry_forward_annotation_counts:
        lines.append("")
        lines.append("## Carry-Forward Annotations")
        for name, count in sorted(
            carry_forward_annotation_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    queue_posture_counts = summary.get("queue_posture_counts", {})
    if isinstance(queue_posture_counts, dict) and queue_posture_counts:
        lines.append("")
        lines.append("## Queue Postures")
        for name, count in sorted(
            queue_posture_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    duplicate_pressure_counts = summary.get("duplicate_pressure_counts", {})
    if isinstance(duplicate_pressure_counts, dict) and duplicate_pressure_counts:
        lines.append("")
        lines.append("## Duplicate Pressure Counts")
        for name, count in sorted(
            duplicate_pressure_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    producer_followup_counts = summary.get("producer_followup_counts", {})
    if isinstance(producer_followup_counts, dict) and producer_followup_counts:
        lines.append("")
        lines.append("## Producer Follow-Up Counts")
        for name, count in sorted(
            producer_followup_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    operator_followup_counts = summary.get("operator_followup_counts", {})
    if isinstance(operator_followup_counts, dict) and operator_followup_counts:
        lines.append("")
        lines.append("## Operator Follow-Up Counts")
        for name, count in sorted(
            operator_followup_counts.items(), key=lambda item: (-int(item[1]), item[0])
        ):
            lines.append(f"- {name}: {count}")

    admissibility_gate_posture_counts = summary.get("admissibility_gate_posture_counts", {})
    if isinstance(admissibility_gate_posture_counts, dict) and admissibility_gate_posture_counts:
        lines.append("")
        lines.append("## Admissibility Gate Counts")
        for name, count in sorted(
            admissibility_gate_posture_counts.items(),
            key=lambda item: (-int(item[1]), item[0]),
        ):
            lines.append(f"- {name}: {count}")

    admissibility_focus_counts = summary.get("admissibility_focus_counts", {})
    if isinstance(admissibility_focus_counts, dict) and admissibility_focus_counts:
        lines.append("")
        lines.append("## Admissibility Focus Counts")
        for name, count in sorted(
            admissibility_focus_counts.items(),
            key=lambda item: (-int(item[1]), item[0]),
        ):
            lines.append(f"- {name}: {count}")

    extend_status_lines_markdown(lines, status_lines)

    if isinstance(admissibility_status_lines, list) and admissibility_status_lines:
        lines.append("")
        lines.append("## Admissibility Status Lines")
        for line in admissibility_status_lines:
            text = str(line or "").strip()
            if text:
                lines.append(f"- {text}")

    lines.append("")
    lines.append("## Operator Lens")
    if review_groups:
        for group in review_groups:
            lines.append(
                "- " f"{group.get('topic', '<unknown>')} " f"(`{group.get('queue_posture', '')}`)"
            )
            if group.get("operator_lens_summary"):
                lines.append(f"  - summary: {group.get('operator_lens_summary', '')}")
            if group.get("revisit_trigger"):
                lines.append(f"  - revisit_trigger: {group.get('revisit_trigger', '')}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Review Groups")
    if review_groups:
        for group in review_groups:
            lines.append(
                "- "
                f"{group.get('topic', '<unknown>')} "
                f"(`{group.get('triage_recommendation', '')}`, "
                f"default={group.get('default_review_status_if_confirmed', '')}, "
                f"rows={group.get('record_count', 0)}, lineages={group.get('lineage_count', 0)}, "
                f"cycles={group.get('cycle_count', 0)}`)"
            )
            lines.append(f"  - revisit_readiness: {group.get('revisit_readiness', '')}")
            lines.append(
                f"  - carry_forward_annotation: {group.get('carry_forward_annotation', '')}"
            )
            lines.append(f"  - queue_posture: {group.get('queue_posture', '')}")
            lines.append(f"  - duplicate_pressure: {group.get('duplicate_pressure', '')}")
            lines.append(f"  - producer_followup: {group.get('producer_followup', '')}")
            lines.append(f"  - operator_followup: {group.get('operator_followup', '')}")
            if group.get("revisit_trigger"):
                lines.append(f"  - revisit_trigger: {group.get('revisit_trigger', '')}")
            if group.get("revisit_trigger_code"):
                lines.append(f"  - revisit_trigger_code: {group.get('revisit_trigger_code', '')}")
            if group.get("operator_lens_summary"):
                lines.append(f"  - operator_lens_summary: {group.get('operator_lens_summary', '')}")
            if group.get("operator_status_line"):
                lines.append(f"  - operator_status_line: {group.get('operator_status_line', '')}")
            lines.append(
                "  - density: "
                f"rows_per_lineage={group.get('rows_per_lineage', 0)}, "
                f"rows_per_cycle={group.get('rows_per_cycle', 0)}"
            )
            if group.get("history_density_summary"):
                lines.append(
                    f"  - history_density_summary: {group.get('history_density_summary', '')}"
                )
            lines.append(
                "  - lineage_density: "
                f"repeated_lineages={group.get('repeated_lineage_count', 0)}, "
                f"dense_lineages={group.get('dense_lineage_count', 0)}, "
                f"singleton_lineages={group.get('singleton_lineage_count', 0)}, "
                f"max_rows_per_lineage={group.get('max_lineage_record_count', 0)}"
            )
            histogram_text = _format_histogram(group.get("lineage_record_histogram"))
            if histogram_text:
                lines.append(f"  - lineage_record_histogram: {histogram_text}")
            if group.get("duplicate_pressure_reason"):
                lines.append(
                    f"  - duplicate_pressure_reason: {group.get('duplicate_pressure_reason', '')}"
                )
            if group.get("density_compaction_reason"):
                lines.append(
                    f"  - density_compaction_reason: {group.get('density_compaction_reason', '')}"
                )
            lines.append(f"  - basis: {group.get('review_basis_template', '')}")
            admissibility = group.get("axiomatic_admissibility_checklist") or {}
            if admissibility:
                lines.append(
                    "  - admissibility_primary_status_line: "
                    f"{admissibility.get('gate_posture', '')} / {admissibility.get('focus', '')}"
                )
                if group.get("admissibility_status_line"):
                    lines.append(
                        "  - admissibility_status_line: "
                        f"{group.get('admissibility_status_line', '')}"
                    )
                risk_tags = list(admissibility.get("risk_tags") or [])
                if risk_tags:
                    lines.append(f"  - admissibility_risk_tags: {', '.join(risk_tags)}")
                operator_prompt = str(admissibility.get("operator_prompt") or "")
                if operator_prompt:
                    lines.append(f"  - admissibility_prompt: {operator_prompt}")
            pending_status_counts = dict(group.get("pending_status_counts") or {})
            if pending_status_counts:
                counts_text = ", ".join(
                    f"{name}={count}"
                    for name, count in sorted(
                        pending_status_counts.items(), key=lambda item: (-int(item[1]), item[0])
                    )
                )
                lines.append(f"  - pending_status_counts: {counts_text}")
            if group.get("latest_review_timestamp"):
                lines.append(
                    f"  - latest_review_timestamp: {group.get('latest_review_timestamp', '')}"
                )
            if group.get("latest_row_timestamp"):
                lines.append(f"  - latest_row_timestamp: {group.get('latest_row_timestamp', '')}")
            lines.append(
                f"  - rows_after_latest_review: {group.get('rows_after_latest_review', 0)}"
            )
            prior_decision_status_counts = dict(group.get("prior_decision_status_counts") or {})
            if prior_decision_status_counts:
                prior_counts_text = ", ".join(
                    f"{name}={count}"
                    for name, count in sorted(
                        prior_decision_status_counts.items(),
                        key=lambda item: (-int(item[1]), item[0]),
                    )
                )
                lines.append(f"  - prior_decision_status_counts: {prior_counts_text}")
            historical_prior_decision_status_counts = dict(
                group.get("historical_prior_decision_status_counts") or {}
            )
            if historical_prior_decision_status_counts and (
                historical_prior_decision_status_counts != prior_decision_status_counts
            ):
                historical_counts_text = ", ".join(
                    f"{name}={count}"
                    for name, count in sorted(
                        historical_prior_decision_status_counts.items(),
                        key=lambda item: (-int(item[1]), item[0]),
                    )
                )
                lines.append(
                    "  - historical_prior_decision_status_counts: " f"{historical_counts_text}"
                )
            if group.get("latest_matched_review_timestamp"):
                lines.append(
                    "  - latest_matched_review_timestamp: "
                    f"{group.get('latest_matched_review_timestamp', '')}"
                )
            if group.get("latest_review_status"):
                lines.append(f"  - latest_review_status: {group.get('latest_review_status', '')}")
            if group.get("latest_review_actor_id"):
                actor_label = str(group.get("latest_review_actor_id") or "")
                if group.get("latest_review_actor_type"):
                    actor_label += f" ({group.get('latest_review_actor_type', '')})"
                lines.append(f"  - latest_review_actor: {actor_label}")
            if group.get("latest_review_basis"):
                lines.append(f"  - latest_review_basis: {group.get('latest_review_basis', '')}")
            if group.get("latest_review_notes"):
                lines.append(f"  - latest_review_notes: {group.get('latest_review_notes', '')}")
            representative_record_ids = list(group.get("representative_record_ids") or [])
            if representative_record_ids:
                lines.append(
                    f"  - representative_record_ids: {', '.join(representative_record_ids[:6])}"
                )
    else:
        lines.append("- None")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an operator review batch from subjectivity tension groups."
    )
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for the latest JSON/Markdown artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    db_path = Path(args.db_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    payload, markdown = build_report(db_path, source_name=args.source)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, markdown)
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
