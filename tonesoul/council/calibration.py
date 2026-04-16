"""Council Calibration v0a — realism baseline metrics.

Computes four independent metrics from persisted council verdict records
and stress-test journal data. Each metric is self-describing and carries
explicit ``measures`` / ``does_not_measure`` fields.

This module does NOT:
- produce composite scores
- modify council runtime logic
- change claim ceiling classifications
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

_SCHEMA_VERSION = "v0a"
_STRESS_JOURNAL_DEFAULT = Path("memory/stress_test_journal.jsonl")

_REQUIRED_PERSISTENCE_FIELDS = [
    "record_id",
    "schema_version",
    "recorded_at",
    "agent",
    "input_fingerprint",
    "verdict",
    "coherence",
    "vote_profile",
    "minority_perspectives",
    "grounding_summary",
]


def load_stress_test_journal(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    resolved = Path(path) if path else _STRESS_JOURNAL_DEFAULT
    if not resolved.is_file():
        return []
    records: List[Dict[str, Any]] = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def load_verdict_records(store: Any = None, limit: int = 1000) -> List[Dict[str, Any]]:
    if store is None:
        try:
            from tonesoul.store import get_store

            store = get_store()
        except Exception:
            return []
    getter = getattr(store, "get_council_verdicts", None)
    if not callable(getter):
        return []
    return getter(n=limit)


def _distribution(values: Sequence[str]) -> Dict[str, float]:
    if not values:
        return {}
    counts = Counter(values)
    total = len(values)
    return {k: round(v / total, 6) for k, v in counts.items()}


def _jensen_shannon_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    all_keys = set(p) | set(q)
    if not all_keys:
        return 0.0
    m = {k: (p.get(k, 0.0) + q.get(k, 0.0)) / 2 for k in all_keys}
    kl_pm = sum(
        p.get(k, 0.0) * math.log2(p[k] / m[k])
        for k in all_keys
        if p.get(k, 0.0) > 0 and m.get(k, 0.0) > 0
    )
    kl_qm = sum(
        q.get(k, 0.0) * math.log2(q[k] / m[k])
        for k in all_keys
        if q.get(k, 0.0) > 0 and m.get(k, 0.0) > 0
    )
    return (kl_pm + kl_qm) / 2


def _dominant_ratio(values: Sequence[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    return counts.most_common(1)[0][1] / len(values)


def compute_agreement_stability(
    persistence_records: List[Dict[str, Any]],
    stress_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    groups: Dict[str, List[str]] = defaultdict(list)

    for rec in persistence_records:
        fp = rec.get("input_fingerprint", "")
        verdict = rec.get("verdict", "")
        if fp and verdict:
            groups[f"persist:{fp}"].append(verdict)

    for rec in stress_records:
        inp = rec.get("user_input", "")
        verdict = rec.get("verdict", "")
        if inp and verdict:
            groups[f"stress:{inp}"].append(verdict)

    analyzable = {k: v for k, v in groups.items() if len(v) >= 2}
    if not analyzable:
        return {
            "metric": "agreement_stability",
            "status": "insufficient_data",
            "sample_count": 0,
            "groups_analyzed": 0,
            "data_source": _data_source_label(persistence_records, stress_records),
            "measures": "vote distribution consistency for the same input across sessions",
            "does_not_measure": "whether the verdict was correct or appropriate",
        }

    dominant_ratios: List[float] = []
    jsd_scores: List[float] = []

    for key, verdicts in analyzable.items():
        dominant_ratios.append(_dominant_ratio(verdicts))

        mid = len(verdicts) // 2
        if mid > 0:
            first_half = _distribution(verdicts[:mid])
            second_half = _distribution(verdicts[mid:])
            jsd_scores.append(_jensen_shannon_divergence(first_half, second_half))

    mean_dominant = (
        round(sum(dominant_ratios) / len(dominant_ratios), 4) if dominant_ratios else 0.0
    )
    mean_jsd = round(sum(jsd_scores) / len(jsd_scores), 4) if jsd_scores else 0.0

    return {
        "metric": "agreement_stability",
        "status": "computed",
        "sample_count": sum(len(v) for v in analyzable.values()),
        "groups_analyzed": len(analyzable),
        "mean_dominant_verdict_ratio": mean_dominant,
        "mean_split_half_jsd": mean_jsd,
        "interpretation": (
            "dominant_ratio near 1.0 = highly stable; "
            "jsd near 0.0 = low distribution drift across halves"
        ),
        "data_source": _data_source_label(persistence_records, stress_records),
        "measures": "vote distribution consistency for the same input across sessions",
        "does_not_measure": "whether the verdict was correct or appropriate",
    }


def compute_internal_self_consistency(
    persistence_records: List[Dict[str, Any]],
    stress_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    checks: List[bool] = []

    for rec in stress_records:
        tension = rec.get("tension")
        verdict = rec.get("verdict", "")
        if tension is None or not verdict:
            continue
        t = float(tension)
        if t >= 0.7:
            checks.append(verdict in ("block", "caution"))
        elif t <= 0.3:
            checks.append(verdict in ("approve",))

    for rec in persistence_records:
        has_objection = rec.get("has_strong_objection", False)
        verdict = rec.get("verdict", "")
        coherence = rec.get("coherence")
        if not verdict:
            continue
        if has_objection:
            checks.append(verdict != "approve")
        if coherence is not None and float(coherence) >= 0.8:
            checks.append(verdict in ("approve", "refine"))

    if not checks:
        return {
            "metric": "internal_self_consistency",
            "status": "insufficient_data",
            "sample_count": 0,
            "data_source": _data_source_label(persistence_records, stress_records),
            "measures": "alignment between internal signals (tension, objection, coherence) and verdict direction",
            "does_not_measure": "outcome calibration or predictive accuracy",
        }

    consistent_count = sum(1 for c in checks if c)
    total = len(checks)
    return {
        "metric": "internal_self_consistency",
        "status": "computed",
        "sample_count": total,
        "consistent_count": consistent_count,
        "inconsistent_count": total - consistent_count,
        "consistency_rate": round(consistent_count / total, 4),
        "interpretation": (
            "consistency_rate near 1.0 = internal signals align with verdict direction; "
            "low rate suggests the council produces contradictory signal-verdict pairs"
        ),
        "data_source": _data_source_label(persistence_records, stress_records),
        "measures": "alignment between internal signals (tension, objection, coherence) and verdict direction",
        "does_not_measure": "outcome calibration or predictive accuracy",
    }


def compute_suppression_recovery_rate(
    persistence_records: List[Dict[str, Any]],
    stress_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    minority_events = 0
    recovery_events = 0

    stress_groups: Dict[str, List[str]] = defaultdict(list)
    for rec in stress_records:
        inp = rec.get("user_input", "")
        verdict = rec.get("verdict", "")
        if inp and verdict:
            stress_groups[inp].append(verdict)

    for key, verdicts in stress_groups.items():
        if len(verdicts) < 2:
            continue
        counts = Counter(verdicts)
        if len(counts) < 2:
            continue
        dominant = counts.most_common(1)[0][0]
        minorities = {v for v in counts if v != dominant}
        for minority_verdict in minorities:
            minority_events += 1
            for i, v in enumerate(verdicts):
                if v == minority_verdict:
                    later = verdicts[i + 1 :]
                    if later and Counter(later).most_common(1)[0][0] == minority_verdict:
                        recovery_events += 1
                    break

    fp_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in persistence_records:
        fp = rec.get("input_fingerprint", "")
        if fp:
            fp_groups[fp].append(rec)

    for fp, recs in fp_groups.items():
        if len(recs) < 2:
            continue
        chronological = list(reversed(recs))
        earliest = chronological[0]
        minority_list = earliest.get("minority_perspectives", [])
        if not minority_list:
            continue
        minority_events += 1
        for later_rec in chronological[1:]:
            later_minority = later_rec.get("minority_perspectives", [])
            if not later_minority:
                recovery_events += 1
                break

    if minority_events == 0:
        return {
            "metric": "suppression_recovery_rate",
            "status": "insufficient_data",
            "sample_count": 0,
            "data_source": _data_source_label(persistence_records, stress_records),
            "measures": "rate at which suppressed minority positions later become the dominant verdict",
            "does_not_measure": "whether the minority position was correct",
        }

    return {
        "metric": "suppression_recovery_rate",
        "status": "computed",
        "sample_count": minority_events,
        "minority_events": minority_events,
        "recovery_events": recovery_events,
        "recovery_rate": round(recovery_events / minority_events, 4),
        "interpretation": (
            "recovery_rate near 0.0 = minority positions never recover; "
            "moderate rate suggests the council can self-correct on repeated input"
        ),
        "data_source": _data_source_label(persistence_records, stress_records),
        "measures": "rate at which suppressed minority positions later become the dominant verdict",
        "does_not_measure": "whether the minority position was correct",
    }


def compute_persistence_coverage(
    persistence_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not persistence_records:
        return {
            "metric": "persistence_coverage",
            "status": "no_records",
            "sample_count": 0,
            "data_source": "council_verdict_persistence_lane",
            "measures": "field completeness of persisted council verdict records",
            "does_not_measure": "council quality or correctness",
        }

    field_presence: Dict[str, int] = {f: 0 for f in _REQUIRED_PERSISTENCE_FIELDS}
    for rec in persistence_records:
        for field in _REQUIRED_PERSISTENCE_FIELDS:
            val = rec.get(field)
            if val is not None and val != "" and val != []:
                field_presence[field] += 1

    total = len(persistence_records)
    completeness = {field: round(count / total, 4) for field, count in field_presence.items()}
    overall = round(sum(completeness.values()) / len(completeness), 4) if completeness else 0.0

    return {
        "metric": "persistence_coverage",
        "status": "computed",
        "sample_count": total,
        "field_completeness": completeness,
        "overall_field_coverage": overall,
        "interpretation": (
            "overall near 1.0 = all required fields present in all records; "
            "gaps indicate persistence schema drift or partial writes"
        ),
        "data_source": "council_verdict_persistence_lane",
        "measures": "field completeness of persisted council verdict records",
        "does_not_measure": "council quality or correctness",
    }


def _data_source_label(
    persistence_records: List[Dict[str, Any]],
    stress_records: List[Dict[str, Any]],
) -> str:
    parts: List[str] = []
    if persistence_records:
        parts.append(f"council_verdict_persistence({len(persistence_records)})")
    if stress_records:
        parts.append(f"stress_test_journal({len(stress_records)})")
    return " + ".join(parts) if parts else "none"


def run_calibration_wave(
    *,
    store: Any = None,
    stress_journal_path: Optional[Path] = None,
    persistence_limit: int = 1000,
) -> Dict[str, Any]:
    persistence_records = load_verdict_records(store=store, limit=persistence_limit)
    stress_records = load_stress_test_journal(path=stress_journal_path)

    metrics = [
        compute_agreement_stability(persistence_records, stress_records),
        compute_internal_self_consistency(persistence_records, stress_records),
        compute_suppression_recovery_rate(persistence_records, stress_records),
        compute_persistence_coverage(persistence_records),
    ]

    return {
        "contract_version": "v1",
        "bundle": "council_calibration",
        "schema_version": _SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "v0a_realism_baseline",
        "receiver_rule": (
            "These metrics describe internal realism baseline, not outcome calibration. "
            "They cannot be used to downgrade claim ceilings or justify public-launch language. "
            "council_decision_quality remains descriptive_only until v0b verdict-outcome alignment is established."
        ),
        "language_boundary": {
            "this_is": "internal realism baseline",
            "this_is_not": [
                "outcome calibration",
                "predictive accuracy",
                "public-launch blocker resolution",
            ],
            "ceiling_effect": "none — council_decision_quality stays descriptive_only",
            "maximum_honest_claim": (
                "council_decision_quality has moved from purely descriptive to "
                "'trackable realism baseline with persistence capability established'"
            ),
        },
        "data_sources": {
            "stress_test_journal": {
                "path": str(stress_journal_path or _STRESS_JOURNAL_DEFAULT),
                "record_count": len(stress_records),
            },
            "council_verdict_persistence": {
                "record_count": len(persistence_records),
            },
        },
        "metrics": {m["metric"]: m for m in metrics},
        "v0a_exit_criteria": {
            "baseline_metrics_stable": all(m["status"] == "computed" for m in metrics[:3]),
            "persistence_operational": (
                metrics[3]["status"] == "computed"
                and metrics[3].get("overall_field_coverage", 0) >= 0.9
            ),
            "verdict_records_accumulating": len(persistence_records) > 0,
        },
        "v0b_prerequisites": {
            "verdict_outcome_alignment_n_ge_20": False,
            "two_consecutive_stable_waves": False,
            "note": "v0b is not in scope for V1.1; these fields track forward readiness only",
        },
    }
