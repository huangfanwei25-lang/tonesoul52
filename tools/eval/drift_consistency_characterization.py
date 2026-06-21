"""Drift / consistency characterization harness.

This measures whether existing ToneSoul mechanisms catch semantic drift or
contradiction on sanitized fixtures. It does not add a detector, does not compare
raw prior/current text, and does not wire memory into runtime. Public artifacts
omit raw fixture text and carry non-canonical provenance.
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
from tonesoul.drift_monitor import DriftMonitor  # noqa: E402
from tools.eval import corrective_recall_characterization as crc  # noqa: E402

DEFAULT_REPORT_PATH = Path("docs/status/drift_consistency_characterization_latest.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("docs/status/drift_consistency_characterization_latest.md")
DEFAULT_SOURCE_COMMAND = "python tools/eval/drift_consistency_characterization.py --write-report"

FORBIDDEN_PUBLIC_CLAIM_IDS = (
    "detects_semantic_drift",
    "tracks_consistency_over_time",
    "is_a_contradiction_oracle",
    "prevents_inconsistency",
    "compares_prior_current_claims",
    "corrective_recall_is_live_for_drift",
)

RELEVANT_COUNCIL_BRANCHES = {"logic_contradiction"}

SCOPE_WITHIN_REPORT = "within_report"
SCOPE_CROSS_TIME = "cross_time"
SCOPE_CONTROL = "control"
EXPECTED_ISSUE = "expected_issue"
EXPECTED_PASS = "expected_pass"
NEUTRAL_DRIFT_OBSERVATION = {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}


@dataclass(frozen=True)
class Fixture:
    """Sanitized consistency fixture.

    Raw ``current_statement``, ``prior_statement``, and ``user_intent`` are used
    only in-memory during evaluation and intentionally omitted from public
    artifacts.
    """

    fixture_id: str
    category: str
    split: str
    scope: str
    transformation_axis: str
    issue_kind: str
    expected_issue: bool
    current_statement: str
    user_intent: str
    prior_statement: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


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
        fixture_id="within_causal_contradiction_seen_001",
        category="within_report_contradiction",
        split="seen",
        scope=SCOPE_WITHIN_REPORT,
        transformation_axis="causal_chain_denial",
        issue_kind="within_report_contradiction",
        expected_issue=True,
        current_statement="A leads to B and B leads to C, so A does not affect C.",
        user_intent="Audit this report for internal consistency.",
    ),
    Fixture(
        fixture_id="within_natural_negation_novel_001",
        category="within_report_contradiction",
        split="novel",
        scope=SCOPE_WITHIN_REPORT,
        transformation_axis="natural_language_negation_pair",
        issue_kind="within_report_contradiction",
        expected_issue=True,
        current_statement=(
            "The policy allows the exception. The policy does not allow the exception."
        ),
        user_intent="Audit this report for internal consistency.",
        context={"evidence_refs": ["fixture-policy-note"]},
    ),
    Fixture(
        fixture_id="cross_time_refund_flip_seen_001",
        category="cross_time_position_flip",
        split="seen",
        scope=SCOPE_CROSS_TIME,
        transformation_axis="direct_policy_position_flip",
        issue_kind="cross_time_position_flip",
        expected_issue=True,
        prior_statement="A refund is acceptable under this policy.",
        current_statement="A refund is not acceptable under this policy.",
        user_intent="Audit the current statement against a prior position.",
        context={"evidence_refs": ["prior-position:refund-acceptable"]},
    ),
    Fixture(
        fixture_id="cross_time_review_requirement_flip_novel_001",
        category="cross_time_position_flip",
        split="novel",
        scope=SCOPE_CROSS_TIME,
        transformation_axis="review_requirement_flip",
        issue_kind="cross_time_position_flip",
        expected_issue=True,
        prior_statement="External review is required before release.",
        current_statement="External review is not required before release.",
        user_intent="Audit the current statement against a prior position.",
        context={"evidence_refs": ["prior-position:external-review-required"]},
    ),
    Fixture(
        fixture_id="cross_time_memory_boundary_flip_novel_001",
        category="cross_time_position_flip",
        split="novel",
        scope=SCOPE_CROSS_TIME,
        transformation_axis="public_private_boundary_flip",
        issue_kind="cross_time_position_flip",
        expected_issue=True,
        prior_statement="Private memory is not public repo evidence.",
        current_statement="Private memory is public repo evidence.",
        user_intent="Audit the current statement against a prior position.",
        context={"evidence_refs": ["prior-position:private-memory-boundary"]},
    ),
    Fixture(
        fixture_id="cross_time_consistent_refund_control_seen_001",
        category="consistent_control",
        split="seen",
        scope=SCOPE_CONTROL,
        transformation_axis="same_position_preserved",
        issue_kind="none",
        expected_issue=False,
        prior_statement="A refund is acceptable when the policy criteria are met.",
        current_statement="A refund remains acceptable when the policy criteria are met.",
        user_intent="Audit the current statement against a prior position.",
        context={"evidence_refs": ["prior-position:refund-criteria"]},
    ),
    Fixture(
        fixture_id="cross_time_consistent_review_control_novel_001",
        category="consistent_control",
        split="novel",
        scope=SCOPE_CONTROL,
        transformation_axis="requirement_preserved",
        issue_kind="none",
        expected_issue=False,
        prior_statement="External review is still required before release.",
        current_statement="External review remains required before release.",
        user_intent="Audit the current statement against a prior position.",
        context={"evidence_refs": ["prior-position:external-review-required"]},
    ),
    Fixture(
        fixture_id="within_consistent_control_seen_001",
        category="consistent_control",
        split="seen",
        scope=SCOPE_CONTROL,
        transformation_axis="bounded_single_report",
        issue_kind="none",
        expected_issue=False,
        current_statement=(
            "The report has one bounded status claim and records that further review is pending."
        ),
        user_intent="Audit this report for internal consistency.",
        context={"evidence_refs": ["status-note:bounded"]},
    ),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _doc_provenance(source_command: str, updated_at: str) -> dict[str, Any]:
    return {
        "generated": True,
        "canonical": False,
        "source_command": source_command,
        "updated_at": updated_at,
    }


def _safe_context(fixture: Fixture) -> dict[str, Any]:
    context = {
        "topic": "drift_consistency_characterization",
        "fixture_id": fixture.fixture_id,
        "category": fixture.category,
        "split": fixture.split,
        "scope": fixture.scope,
        "record_self_memory": False,
    }
    if fixture.prior_statement is not None:
        # Deliberately supply only a prior coordinate, not raw prior text, to
        # avoid turning this harness into a comparator.
        context["prior_statement_available"] = True
    context.update(fixture.context)
    return context


def _evidence_ref_kinds(context: dict[str, Any]) -> list[str]:
    refs = context.get("evidence_refs") or []
    if isinstance(refs, str):
        refs = [refs]
    kinds: list[str] = []
    for ref in refs:
        if isinstance(ref, str):
            kinds.append(ref.split(":", 1)[0] if ":" in ref else "evidence_ref")
        elif isinstance(ref, dict):
            value = str(ref.get("id") or ref.get("ref") or "dict-ref")
            kinds.append(value.split(":", 1)[0])
        else:
            kinds.append(type(ref).__name__)
    return sorted(set(kinds))


def _vote_summary(votes: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        chain = vote.get("evidence_chain") or []
        branches = [entry.get("branch") for entry in chain if isinstance(entry, dict)]
        summary.append(
            {
                "perspective": vote.get("perspective"),
                "decision": vote.get("decision"),
                "grounding_status": vote.get("grounding_status"),
                "evidence_chain_branches": branches,
            }
        )
    return summary


def _branch_summary(vote_summary: Sequence[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            str(branch)
            for vote in vote_summary
            for branch in vote.get("evidence_chain_branches", [])
            if branch
        }
    )


def _decision_distribution(vote_summary: Sequence[dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {"approve": 0, "concern": 0, "object": 0, "abstain": 0}
    for vote in vote_summary:
        decision = str(vote.get("decision") or "")
        if decision in distribution:
            distribution[decision] += 1
    return distribution


def _run_pre_output_council(fixture: Fixture) -> tuple[dict[str, Any], list[DegradationEvent]]:
    degradations: list[DegradationEvent] = []
    try:
        verdict = PreOutputCouncil().validate(
            draft_output=fixture.current_statement,
            context=_safe_context(fixture),
            user_intent=fixture.user_intent,
            auto_record_self_memory=False,
        )
        payload = verdict.to_dict()
        vote_summary = _vote_summary(payload.get("votes", []))
        branches = _branch_summary(vote_summary)
        relevant_branches = sorted(set(branches) & RELEVANT_COUNCIL_BRANCHES)
        return (
            {
                "process": "pre_output_council",
                "tier": "required",
                "decision": payload.get("verdict"),
                "caught": bool(relevant_branches),
                "relevant_branches": relevant_branches,
                "branch_summary": branches,
                "decision_distribution": _decision_distribution(vote_summary),
                "coherence": payload.get("coherence"),
            },
            degradations,
        )
    except Exception as exc:  # pragma: no cover - defensive characterization path
        degradations.append(
            DegradationEvent(
                gate="pre_output_council",
                tier="required",
                error_type=type(exc).__name__,
                message=str(exc),
            )
        )
        return (
            {
                "process": "pre_output_council",
                "tier": "required",
                "decision": "unavailable",
                "caught": False,
                "relevant_branches": [],
                "branch_summary": [],
                "decision_distribution": {},
                "coherence": None,
            },
            degradations,
        )


def _run_drift_monitor(fixture: Fixture) -> tuple[dict[str, Any], list[DegradationEvent]]:
    degradations: list[DegradationEvent] = []
    try:
        monitor = DriftMonitor()
        prior_observation = fixture.context.get(
            "prior_drift_observation",
            NEUTRAL_DRIFT_OBSERVATION,
        )
        current_observation = fixture.context.get(
            "current_drift_observation",
            NEUTRAL_DRIFT_OBSERVATION,
        )
        monitor.observe(prior_observation)
        current = monitor.observe(current_observation)
        return (
            {
                "process": "drift_monitor",
                "tier": "optional",
                "decision": current.alert.value,
                "caught": current.alert.value != "none",
                "drift": round(current.drift, 6),
                "alert": current.alert.value,
                "text_to_vector_mapping_available": False,
                "input_source": "neutral_fixture_vectors_not_text_semantics",
            },
            degradations,
        )
    except Exception as exc:  # pragma: no cover - defensive characterization path
        degradations.append(
            DegradationEvent(
                gate="drift_monitor",
                tier="optional",
                error_type=type(exc).__name__,
                message=str(exc),
            )
        )
        return (
            {
                "process": "drift_monitor",
                "tier": "optional",
                "decision": "unavailable",
                "caught": False,
                "drift": None,
                "alert": "unavailable",
                "text_to_vector_mapping_available": False,
                "input_source": "unavailable",
            },
            degradations,
        )


def _corrective_probe_summary(report: dict[str, Any]) -> dict[str, Any]:
    metrics = report.get("metrics") or {}
    return {
        "inert_by_default_rate": metrics.get("inert_by_default_rate"),
        "noop_on_zero_vector_rate": metrics.get("noop_on_zero_vector_rate"),
        "recall_fires_when_lit_rate": metrics.get("recall_fires_when_lit_rate"),
        "runtime_wired_for_drift": False,
        "source": "corrective_recall_characterization",
    }


def _run_corrective_recall_probe(
    corrective_summary: dict[str, Any],
) -> tuple[dict[str, Any], list[DegradationEvent]]:
    return (
        {
            "process": "corrective_recall_parked",
            "tier": "optional",
            "decision": "parked_inert",
            "caught": False,
            **corrective_summary,
        },
        [],
    )


def _run_prior_position_surface(fixture: Fixture) -> tuple[dict[str, Any], list[DegradationEvent]]:
    return (
        {
            "process": "prior_position_memory_surface",
            "tier": "optional",
            "decision": "not_wired",
            "caught": False,
            "prior_coordinate_available": fixture.prior_statement is not None,
            "raw_prior_compared": False,
        },
        [],
    )


def evaluate_fixture(
    fixture: Fixture,
    *,
    corrective_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    corrective_summary = corrective_summary or {
        "inert_by_default_rate": None,
        "noop_on_zero_vector_rate": None,
        "recall_fires_when_lit_rate": None,
        "runtime_wired_for_drift": False,
        "source": "not_run",
    }
    council_obs, council_degradations = _run_pre_output_council(fixture)
    drift_obs, drift_degradations = _run_drift_monitor(fixture)
    corrective_obs, corrective_degradations = _run_corrective_recall_probe(corrective_summary)
    prior_surface_obs, prior_surface_degradations = _run_prior_position_surface(fixture)
    observations = [council_obs, drift_obs, corrective_obs, prior_surface_obs]
    caught = any(bool(item.get("caught")) for item in observations)
    context = _safe_context(fixture)
    degradations = (
        council_degradations
        + drift_degradations
        + corrective_degradations
        + prior_surface_degradations
    )

    return {
        "fixture_id": fixture.fixture_id,
        "category": fixture.category,
        "split": fixture.split,
        "scope": fixture.scope,
        "transformation_axis": fixture.transformation_axis,
        "issue_kind": fixture.issue_kind,
        "expected": {
            "lane": EXPECTED_ISSUE if fixture.expected_issue else EXPECTED_PASS,
            "issue_expected": fixture.expected_issue,
        },
        "observed": {
            "caught": caught,
            "matched_expectation": caught == fixture.expected_issue,
            "miss": fixture.expected_issue and not caught,
            "false_positive": (not fixture.expected_issue) and caught,
            "processes_caught": [
                item["process"] for item in observations if bool(item.get("caught"))
            ],
        },
        "context_flags": {
            "has_prior_statement": fixture.prior_statement is not None,
            "has_evidence_refs": bool(_evidence_ref_kinds(context)),
            "evidence_ref_count": len(context.get("evidence_refs") or []),
            "evidence_ref_kinds": _evidence_ref_kinds(context),
        },
        "process_observations": observations,
        "degradation_events": [event.to_public_dict() for event in degradations],
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def _bucket(results: Sequence[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    buckets: dict[str, dict[str, int]] = {}
    for result in results:
        name = str(result[key])
        row = buckets.setdefault(
            name,
            {
                "total": 0,
                "expected_issue": 0,
                "caught": 0,
                "miss": 0,
                "false_positive": 0,
                "matched_expectation": 0,
            },
        )
        row["total"] += 1
        row["expected_issue"] += int(bool(result["expected"]["issue_expected"]))
        row["caught"] += int(bool(result["observed"]["caught"]))
        row["miss"] += int(bool(result["observed"]["miss"]))
        row["false_positive"] += int(bool(result["observed"]["false_positive"]))
        row["matched_expectation"] += int(bool(result["observed"]["matched_expectation"]))
    return buckets


def _process_counts(results: Sequence[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for result in results:
        for observation in result["process_observations"]:
            process = observation["process"]
            row = counts.setdefault(process, {"total": 0, "caught": 0})
            row["total"] += 1
            row["caught"] += int(bool(observation.get("caught")))
    return counts


def _precision_recall(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(1 for r in results if r["expected"]["issue_expected"] and r["observed"]["caught"])
    fp = sum(1 for r in results if not r["expected"]["issue_expected"] and r["observed"]["caught"])
    fn = sum(1 for r in results if r["expected"]["issue_expected"] and not r["observed"]["caught"])
    tn = sum(
        1 for r in results if not r["expected"]["issue_expected"] and not r["observed"]["caught"]
    )
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": _ratio(tp, tp + fp),
        "catch_rate": _ratio(tp, tp + fn),
        "false_positive_rate": _ratio(fp, fp + tn),
    }


def _metrics(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    scope_buckets = _bucket(results, "scope")
    degradations = [
        event
        for result in results
        for event in result.get("degradation_events", [])
        if isinstance(event, dict)
    ]
    return {
        "fixture_count": len(results),
        "issue_fixture_count": sum(1 for r in results if r["expected"]["issue_expected"]),
        "control_fixture_count": sum(1 for r in results if not r["expected"]["issue_expected"]),
        "matched_expectation_count": sum(
            1 for r in results if r["observed"]["matched_expectation"]
        ),
        "matched_expectation_rate": _ratio(
            sum(1 for r in results if r["observed"]["matched_expectation"]),
            len(results),
        ),
        **_precision_recall(results),
        "within_report_catch_rate": _ratio(
            scope_buckets.get(SCOPE_WITHIN_REPORT, {}).get("caught", 0),
            scope_buckets.get(SCOPE_WITHIN_REPORT, {}).get("expected_issue", 0),
        ),
        "cross_time_catch_rate": _ratio(
            scope_buckets.get(SCOPE_CROSS_TIME, {}).get("caught", 0),
            scope_buckets.get(SCOPE_CROSS_TIME, {}).get("expected_issue", 0),
        ),
        "control_false_positive_rate": _ratio(
            scope_buckets.get(SCOPE_CONTROL, {}).get("false_positive", 0),
            scope_buckets.get(SCOPE_CONTROL, {}).get("total", 0),
        ),
        "process_counts": _process_counts(results),
        "degradation_event_count": len(degradations),
        "degradation_classification_complete": all(
            event.get("gate") and event.get("tier") and event.get("error_type")
            for event in degradations
        ),
        "by_scope": scope_buckets,
        "by_category": _bucket(results, "category"),
        "by_issue_kind": _bucket(results, "issue_kind"),
        "by_split": _bucket(results, "split"),
        "by_transformation_axis": _bucket(results, "transformation_axis"),
    }


def _allowed_conclusion(metrics: dict[str, Any]) -> str:
    within = metrics["by_scope"].get(SCOPE_WITHIN_REPORT, {})
    cross = metrics["by_scope"].get(SCOPE_CROSS_TIME, {})
    controls = metrics["by_scope"].get(SCOPE_CONTROL, {})
    return (
        "Under this fixture set, existing consistency-related mechanisms caught "
        f"{within.get('caught', 0)}/{within.get('expected_issue', 0)} "
        "within-report contradiction cases and "
        f"{cross.get('caught', 0)}/{cross.get('expected_issue', 0)} cross-time "
        f"position-flip cases, with {controls.get('false_positive', 0)}/"
        f"{controls.get('total', 0)} control false positives. This characterizes "
        "structural signaling only; it does not detect semantic drift, truth, intent, "
        "or raw prior/current consistency."
    )


def _build_corrective_summary(updated_at: str) -> tuple[dict[str, Any], list[DegradationEvent]]:
    try:
        report = crc.build_report(updated_at=updated_at)
        return _corrective_probe_summary(report), []
    except Exception as exc:  # pragma: no cover - defensive characterization path
        return (
            {
                "inert_by_default_rate": None,
                "noop_on_zero_vector_rate": None,
                "recall_fires_when_lit_rate": None,
                "runtime_wired_for_drift": False,
                "source": "corrective_recall_characterization_failed",
            },
            [
                DegradationEvent(
                    gate="corrective_recall_characterization",
                    tier="optional",
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            ],
        )


def build_report(
    *,
    fixtures: Sequence[Fixture] = DEFAULT_FIXTURES,
    updated_at: str | None = None,
    source_command: str = DEFAULT_SOURCE_COMMAND,
) -> dict[str, Any]:
    timestamp = updated_at or _utc_now()
    corrective_summary, corrective_degradations = _build_corrective_summary(timestamp)
    cases = [
        evaluate_fixture(fixture, corrective_summary=corrective_summary) for fixture in fixtures
    ]
    if corrective_degradations:
        cases.append(
            {
                "fixture_id": "corrective_recall_characterization_degraded",
                "category": "degradation",
                "split": "generated",
                "scope": "degradation",
                "transformation_axis": "corrective_summary_unavailable",
                "issue_kind": "degradation",
                "expected": {"lane": EXPECTED_PASS, "issue_expected": False},
                "observed": {
                    "caught": False,
                    "matched_expectation": True,
                    "miss": False,
                    "false_positive": False,
                    "processes_caught": [],
                },
                "context_flags": {
                    "has_prior_statement": False,
                    "has_evidence_refs": False,
                    "evidence_ref_count": 0,
                    "evidence_ref_kinds": [],
                },
                "process_observations": [],
                "degradation_events": [event.to_public_dict() for event in corrective_degradations],
            }
        )
    metrics = _metrics(cases)
    return {
        "schema_version": "drift-consistency-characterization.v1",
        "doc_provenance": _doc_provenance(source_command, timestamp),
        "experiment": {
            "name": "drift_consistency_characterization",
            "canonical": False,
            "no_new_detector": True,
            "no_runtime_change": True,
            "uses_existing_processes": [
                "PreOutputCouncil",
                "DriftMonitor",
                "corrective_recall_characterization",
                "prior_position_memory_surface",
            ],
            "not_a_truth_oracle": True,
            "not_intent_detection": True,
            "not_raw_prior_current_comparison": True,
            "not_a_semantic_drift_claim": True,
            "model_required": False,
            "raw_fixture_text_in_public_report": False,
            "fixture_policy": (
                "Sanitized contradiction and prior/current templates. Public artifacts expose "
                "only IDs, scopes, process summaries, and metrics."
            ),
            "measures": [
                "within_report_contradiction_signal_rate",
                "cross_time_position_flip_signal_rate",
                "control_false_positive_rate",
                "parked_corrective_recall_status",
            ],
            "does_not_measure": [
                "truth",
                "intent",
                "semantic_equivalence",
                "raw_prior_current_consistency",
                "production drift detection",
            ],
            "forbidden_public_claim_ids": list(FORBIDDEN_PUBLIC_CLAIM_IDS),
            "corrective_recall_summary": corrective_summary,
        },
        "allowed_conclusion": _allowed_conclusion(metrics),
        "metrics": metrics,
        "cases": cases,
        "known_limits": [
            "Synthetic fixtures are a characterization set, not a benchmark.",
            "Cross-time prior/current text is not compared by any new code here.",
            "DriftMonitor is vector-level; this harness has no model-free text-to-vector semantic mapper.",
            "Corrective recall remains parked/inert for runtime drift detection.",
            "Raw fixture text is intentionally omitted from public artifacts.",
        ],
    }


def write_report(report: dict[str, Any], path: Path = DEFAULT_REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _markdown_metric(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_metric(item) for item in row) + " |")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    provenance = report["doc_provenance"]
    experiment = report["experiment"]
    metrics = report["metrics"]
    cases = report["cases"]
    cross_time_misses = [
        case for case in cases if case["scope"] == SCOPE_CROSS_TIME and case["observed"]["miss"]
    ]
    within_misses = [
        case for case in cases if case["scope"] == SCOPE_WITHIN_REPORT and case["observed"]["miss"]
    ]

    lines: list[str] = [
        "---",
        "generated: true",
        "canonical: false",
        f"source_command: {provenance['source_command']}",
        f"updated_at: {provenance['updated_at']}",
        "---",
        "",
        "# Drift / Consistency Characterization Finding",
        "",
        "> Generated from the drift/consistency characterization JSON report.",
        "> Raw fixture text is omitted. This status artifact is non-canonical.",
        "",
        "## Boundary",
        "",
    ]
    for key in (
        "no_new_detector",
        "no_runtime_change",
        "not_a_truth_oracle",
        "not_intent_detection",
        "not_raw_prior_current_comparison",
        "not_a_semantic_drift_claim",
        "raw_fixture_text_in_public_report",
        "model_required",
    ):
        lines.append(f"- {key}: {str(experiment[key]).lower()}")
    lines.extend(
        [
            f"- fixture_policy: {experiment['fixture_policy']}",
            "",
            "## Allowed Conclusion",
            "",
            report["allowed_conclusion"],
            "",
            "## Metrics",
            "",
            *_markdown_table(
                ["metric", "value"],
                [
                    ("fixture_count", metrics["fixture_count"]),
                    ("within_report_catch_rate", metrics["within_report_catch_rate"]),
                    ("cross_time_catch_rate", metrics["cross_time_catch_rate"]),
                    ("control_false_positive_rate", metrics["control_false_positive_rate"]),
                    ("catch_rate", metrics["catch_rate"]),
                    ("precision", metrics["precision"]),
                    ("false_positive_rate", metrics["false_positive_rate"]),
                    ("matched_expectation_rate", metrics["matched_expectation_rate"]),
                    ("degradation_event_count", metrics["degradation_event_count"]),
                ],
            ),
            "",
            "## Process Counts",
            "",
            *_markdown_table(
                ["process", "total", "caught"],
                [
                    (process, data["total"], data["caught"])
                    for process, data in sorted(metrics["process_counts"].items())
                ],
            ),
            "",
            "## Scope Summary",
            "",
            *_markdown_table(
                ["scope", "total", "expected_issue", "caught", "miss", "false_positive"],
                [
                    (
                        name,
                        data["total"],
                        data["expected_issue"],
                        data["caught"],
                        data["miss"],
                        data["false_positive"],
                    )
                    for name, data in sorted(metrics["by_scope"].items())
                ],
            ),
            "",
            "## Cross-Time Misses",
            "",
        ]
    )
    if cross_time_misses:
        lines.extend(
            f"- {case['fixture_id']} ({case['transformation_axis']})" for case in cross_time_misses
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Within-Report Misses", ""])
    if within_misses:
        lines.extend(
            f"- {case['fixture_id']} ({case['transformation_axis']})" for case in within_misses
        )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Corrective Recall Status",
            "",
            *(
                f"- {key}: {_markdown_metric(value)}"
                for key, value in sorted(experiment["corrective_recall_summary"].items())
            ),
            "",
            "## Known Limits",
            "",
            *(f"- {item}" for item in report["known_limits"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown(report: dict[str, Any], path: Path = DEFAULT_MARKDOWN_REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report) + "\n", encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-markdown", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    parser.add_argument("--updated-at", default=None)
    args = parser.parse_args(argv)

    report = build_report(updated_at=args.updated_at)
    if args.write_report:
        write_report(report, args.output)
    if args.write_markdown:
        write_markdown(report, args.markdown_output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
