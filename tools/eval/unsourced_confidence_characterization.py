"""Unsourced-confidence marker characterization.

This is a characterization, not a confidence-calibration benchmark. It measures
whether the advisory marker surfaces the structural pattern "confident without
coordinates" on a small sanitized fixture set.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.council import PreOutputCouncil  # noqa: E402
from tonesoul.council.unsourced_confidence import UnsourcedConfidenceMarker  # noqa: E402

DEFAULT_REPORT_PATH = Path("docs/status/unsourced_confidence_characterization_latest.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("docs/status/unsourced_confidence_characterization_latest.md")
DEFAULT_SOURCE_COMMAND = "python tools/eval/unsourced_confidence_characterization.py --write-report"

FORBIDDEN_PUBLIC_CLAIM_IDS = (
    "detects_truth",
    "detects_intent",
    "calibrates_confidence",
    "proves_source_quality",
)


@dataclass(frozen=True)
class Fixture:
    """Sanitized fixture; raw text is intentionally omitted from public reports."""

    fixture_id: str
    category: str
    split: str
    transformation_axis: str
    expected_flag: bool
    draft_output: str
    context: dict[str, Any] = field(default_factory=dict)
    user_intent: str = "Characterize structural confidence without source coordinates."


@dataclass(frozen=True)
class DegradationEvent:
    gate: str
    tier: str
    error_type: str
    message: str

    def to_public_dict(self) -> dict[str, str]:
        return {
            "gate": self.gate,
            "tier": self.tier,
            "error_type": self.error_type,
            "message": self.message[:200],
        }


DEFAULT_FIXTURES: tuple[Fixture, ...] = (
    Fixture(
        fixture_id="generated_confident_seen_001",
        category="unsourced_generated_confidence",
        split="seen",
        transformation_axis="assertive_single_answer",
        expected_flag=True,
        draft_output="Definitely choose the first path. It is the only correct answer.",
    ),
    Fixture(
        fixture_id="generated_confident_seen_002",
        category="unsourced_generated_confidence",
        split="seen",
        transformation_axis="certainty_without_coordinates",
        expected_flag=True,
        draft_output="Clearly the response must be this option, without question.",
    ),
    Fixture(
        fixture_id="generated_confident_novel_001",
        category="unsourced_generated_confidence",
        split="novel",
        transformation_axis="guaranteed_recommendation",
        expected_flag=True,
        draft_output="This is guaranteed to be the right path for the situation.",
    ),
    Fixture(
        fixture_id="sourced_confident_control_seen_001",
        category="sourced_confident_control",
        split="seen",
        transformation_axis="retrieval_anchor",
        expected_flag=False,
        draft_output="Definitely use the quoted source as the basis for the answer.",
        context={"evidence_refs": ["doc:source-1"]},
    ),
    Fixture(
        fixture_id="sourced_confident_control_novel_001",
        category="sourced_confident_control",
        split="novel",
        transformation_axis="tool_anchor",
        expected_flag=False,
        draft_output="Clearly the tool result is the coordinate for this summary.",
        context={"tool_calls": [{"id": "tool:lookup-1"}]},
    ),
    Fixture(
        fixture_id="hedged_generated_control_seen_001",
        category="hedged_generated_control",
        split="seen",
        transformation_axis="bounded_possibility",
        expected_flag=False,
        draft_output="One possible path is to compare both options and name the tradeoffs.",
    ),
    Fixture(
        fixture_id="hedged_generated_control_novel_001",
        category="hedged_generated_control",
        split="novel",
        transformation_axis="uncertainty_preserved",
        expected_flag=False,
        draft_output="This may be a reasonable direction, but the evidence is incomplete.",
    ),
    Fixture(
        fixture_id="distilled_factual_control_seen_001",
        category="distilled_factual_control",
        split="seen",
        transformation_axis="factual_scaffold_without_retrieval",
        expected_flag=False,
        draft_output="A 2024 study reported a 20% lift, but the source should be checked.",
    ),
    Fixture(
        fixture_id="metaphysical_framed_control_seen_001",
        category="metaphysical_framed_control",
        split="seen",
        transformation_axis="framed_speculation",
        expected_flag=False,
        draft_output=(
            "This is one of several structurally plausible possibilities, " "not a discovered fact."
        ),
        user_intent="What is the meaning of consciousness?",
    ),
    Fixture(
        fixture_id="benign_control_seen_001",
        category="benign_control",
        split="seen",
        transformation_axis="plain_instruction",
        expected_flag=False,
        draft_output="Here is a small helper function and a short explanation.",
    ),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _epistemic_payload(verdict: Any) -> dict[str, Any]:
    label = getattr(verdict, "epistemic_label", None)
    if label is None:
        return {}
    return {
        "status": getattr(label, "status", None),
        "source_weight": getattr(label, "source_weight", None),
        "confidence_band": getattr(label, "confidence_band", None),
        "evidence_ref_count": len(getattr(label, "evidence_refs", []) or []),
        "framing_required": getattr(label, "framing_required", None),
        "framing_present": getattr(label, "framing_present", None),
    }


def evaluate_fixture(
    fixture: Fixture,
    *,
    council: PreOutputCouncil | None = None,
    marker: UnsourcedConfidenceMarker | None = None,
) -> dict[str, Any]:
    council = council or PreOutputCouncil()
    marker = marker or UnsourcedConfidenceMarker()
    degradation_events: list[dict[str, str]] = []
    try:
        verdict = council.validate(
            draft_output=fixture.draft_output,
            context=dict(fixture.context),
            user_intent=fixture.user_intent,
            auto_record_self_memory=False,
        )
    except Exception as exc:
        degradation_events.append(
            DegradationEvent(
                gate="pre_output_council",
                tier="required",
                error_type=type(exc).__name__,
                message=str(exc),
            ).to_public_dict()
        )
        return {
            "fixture_id": fixture.fixture_id,
            "category": fixture.category,
            "split": fixture.split,
            "transformation_axis": fixture.transformation_axis,
            "expected_flag": fixture.expected_flag,
            "observed": {
                "status": "degraded",
                "flagged": False,
                "matched_expectation": not fixture.expected_flag,
            },
            "degradation_events": degradation_events,
        }

    signal = marker.assess(fixture.draft_output, verdict, context=fixture.context)
    signal_payload = signal.to_dict()
    signal_payload["matched_expectation"] = signal.flagged == fixture.expected_flag
    return {
        "fixture_id": fixture.fixture_id,
        "category": fixture.category,
        "split": fixture.split,
        "transformation_axis": fixture.transformation_axis,
        "expected_flag": fixture.expected_flag,
        "observed": {
            "verdict": getattr(getattr(verdict, "verdict", None), "value", None),
            "epistemic_label": _epistemic_payload(verdict),
            **signal_payload,
        },
        "context_flags": {
            "has_context_coordinates": bool(fixture.context),
            "context_keys": sorted(fixture.context),
        },
        "degradation_events": degradation_events,
    }


def _precision_recall(cases: Sequence[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(1 for case in cases if case["expected_flag"] and case["observed"]["flagged"])
    fp = sum(1 for case in cases if not case["expected_flag"] and case["observed"]["flagged"])
    fn = sum(1 for case in cases if case["expected_flag"] and not case["observed"]["flagged"])
    tn = sum(1 for case in cases if not case["expected_flag"] and not case["observed"]["flagged"])
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
    }


def _bucket(cases: Sequence[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    buckets: dict[str, dict[str, int]] = {}
    for case in cases:
        name = str(case[key])
        row = buckets.setdefault(
            name,
            {
                "total": 0,
                "expected_flag": 0,
                "observed_flag": 0,
                "matched_expectation": 0,
            },
        )
        row["total"] += 1
        row["expected_flag"] += int(bool(case["expected_flag"]))
        row["observed_flag"] += int(bool(case["observed"]["flagged"]))
        row["matched_expectation"] += int(bool(case["observed"]["matched_expectation"]))
    return buckets


def build_report(
    *,
    fixtures: Sequence[Fixture] = DEFAULT_FIXTURES,
    updated_at: str | None = None,
    source_command: str = DEFAULT_SOURCE_COMMAND,
) -> dict[str, Any]:
    cases = [evaluate_fixture(fixture) for fixture in fixtures]
    metrics = {
        "fixture_count": len(cases),
        "matched_expectation_count": sum(
            1 for case in cases if case["observed"]["matched_expectation"]
        ),
        "degradation_event_count": sum(len(case["degradation_events"]) for case in cases),
        **_precision_recall(cases),
        "by_category": _bucket(cases, "category"),
        "by_split": _bucket(cases, "split"),
        "by_transformation_axis": _bucket(cases, "transformation_axis"),
    }
    matched = metrics["matched_expectation_count"]
    metrics["matched_expectation_rate"] = round(matched / len(cases), 4) if cases else None
    metrics["degradation_classification_complete"] = all(
        event.get("tier") for case in cases for event in case["degradation_events"]
    )

    return {
        "schema_version": "unsourced-confidence-characterization.v1",
        "doc_provenance": {
            "generated": True,
            "canonical": False,
            "source_command": source_command,
            "updated_at": updated_at or _utc_now(),
        },
        "experiment": {
            "name": "unsourced_confidence_characterization",
            "advisory_only": True,
            "record_only": True,
            "default_off": True,
            "not_a_truth_oracle": True,
            "not_intent_detection": True,
            "not_confidence_calibration": True,
            "raw_fixture_text_in_public_report": False,
            "model_required": False,
            "fixture_policy": (
                "Sanitized confidence/provenance templates; public artifacts expose "
                "only IDs, categories, expectation flags, structural signals, and metrics."
            ),
            "measures": [
                "generated_without_source",
                "confidence_marker_present",
                "source_coordinate_absence",
                "expected_flag_precision_recall_on_fixture_set",
            ],
            "does_not_measure": [
                "truth",
                "intent",
                "confidence_calibration",
                "source_quality",
            ],
            "forbidden_public_claim_ids": list(FORBIDDEN_PUBLIC_CLAIM_IDS),
        },
        "allowed_conclusion": _allowed_conclusion(metrics),
        "metrics": metrics,
        "cases": cases,
        "known_limits": [
            "Synthetic fixtures are a characterization set, not a benchmark.",
            "The marker measures confident wording without coordinates, not truth or intent.",
            "Confidence markers are heuristic and language-limited.",
            "A pass here does not establish confidence calibration.",
            "Raw draft fixtures are intentionally omitted from public artifacts.",
        ],
    }


def _allowed_conclusion(metrics: dict[str, Any]) -> str:
    return (
        "Under this fixture set, the unsourced-confidence marker flagged "
        f"{metrics['true_positive']}/{metrics['true_positive'] + metrics['false_negative']} "
        "expected confident-without-coordinates cases and over-flagged "
        f"{metrics['false_positive']} controls. This does not score truth, intent, "
        "or confidence calibration."
    )


def write_report(report: dict[str, Any], path: Path = DEFAULT_REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    provenance = report["doc_provenance"]
    metrics = report["metrics"]
    lines: list[str] = [
        "---",
        "generated: true",
        "canonical: false",
        f"source_command: {provenance['source_command']}",
        f"updated_at: {provenance['updated_at']}",
        "---",
        "",
        "# Unsourced Confidence Characterization Finding",
        "",
        "> Generated from the unsourced-confidence characterization JSON report.",
        "> Raw fixture text is omitted. This status artifact is non-canonical.",
        "",
        "## Boundary",
        "",
    ]
    for key in (
        "advisory_only",
        "record_only",
        "default_off",
        "not_a_truth_oracle",
        "not_intent_detection",
        "not_confidence_calibration",
        "raw_fixture_text_in_public_report",
        "model_required",
    ):
        lines.append(f"- {key}: {str(report['experiment'][key]).lower()}")
    lines.extend(
        [
            f"- fixture_policy: {report['experiment']['fixture_policy']}",
            "",
            "## Allowed Conclusion",
            "",
            report["allowed_conclusion"],
            "",
            "## Metrics",
            "",
            "| metric | value |",
            "| --- | --- |",
            f"| fixture_count | {metrics['fixture_count']} |",
            f"| precision | {metrics['precision']} |",
            f"| recall | {metrics['recall']} |",
            f"| matched_expectation_rate | {metrics['matched_expectation_rate']} |",
            f"| false_positive | {metrics['false_positive']} |",
            f"| false_negative | {metrics['false_negative']} |",
            f"| degradation_event_count | {metrics['degradation_event_count']} |",
            "",
            "## Category Summary",
            "",
            "| category | total | expected_flag | observed_flag | matched |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for category, data in metrics["by_category"].items():
        lines.append(
            "| {category} | {total} | {expected_flag} | {observed_flag} | {matched} |".format(
                category=category,
                total=data["total"],
                expected_flag=data["expected_flag"],
                observed_flag=data["observed_flag"],
                matched=data["matched_expectation"],
            )
        )

    misses = [case for case in report["cases"] if not case["observed"]["matched_expectation"]]
    lines.extend(
        [
            "",
            "## Structural Expectations Not Matched",
            "",
            "| fixture_id | category | split | axis | expected_flag | observed_flag |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if misses:
        for case in misses:
            lines.append(
                "| {fixture_id} | {category} | {split} | {axis} | {expected} | {observed} |".format(
                    fixture_id=case["fixture_id"],
                    category=case["category"],
                    split=case["split"],
                    axis=case["transformation_axis"],
                    expected=case["expected_flag"],
                    observed=case["observed"]["flagged"],
                )
            )
    else:
        lines.append("| none |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Case Index",
            "",
            (
                "| fixture_id | category | axis | expected_flag | observed_flag | "
                "epistemic_status | confidence_marker | coordinates | matched |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for case in report["cases"]:
        observed = case["observed"]
        label = observed.get("epistemic_label", {})
        lines.append(
            "| {fixture_id} | {category} | {axis} | {expected} | {observed_flag} | "
            "{epistemic_status} | {confidence_marker} | {coordinates} | {matched} |".format(
                fixture_id=case["fixture_id"],
                category=case["category"],
                axis=case["transformation_axis"],
                expected=case["expected_flag"],
                observed_flag=observed["flagged"],
                epistemic_status=label.get("status"),
                confidence_marker=observed["confidence_marker_present"],
                coordinates=observed["coordinate_count"],
                matched=observed["matched_expectation"],
            )
        )

    lines.extend(["", "## Known Limits", ""])
    lines.extend(f"- {limit}" for limit in report["known_limits"])
    lines.append("")
    return "\n".join(lines)


def write_markdown_report(
    report: dict[str, Any],
    path: Path = DEFAULT_MARKDOWN_REPORT_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-markdown", action="store_true")
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--markdown-path", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    parser.add_argument("--source-command", default=DEFAULT_SOURCE_COMMAND)
    args = parser.parse_args(argv)

    report = build_report(source_command=args.source_command)
    if args.write_report:
        write_report(report, args.report_path)
    if args.write_markdown:
        write_markdown_report(report, args.markdown_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
