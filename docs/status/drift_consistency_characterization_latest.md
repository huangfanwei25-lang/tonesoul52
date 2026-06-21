---
generated: true
canonical: false
source_command: python tools/eval/drift_consistency_characterization.py --write-report
updated_at: 2026-06-21T00:00:00Z
---

# Drift / Consistency Characterization Finding

> Generated from the drift/consistency characterization JSON report.
> Raw fixture text is omitted. This status artifact is non-canonical.

## Boundary

- no_new_detector: true
- no_runtime_change: true
- not_a_truth_oracle: true
- not_intent_detection: true
- not_raw_prior_current_comparison: true
- not_a_semantic_drift_claim: true
- raw_fixture_text_in_public_report: false
- model_required: false
- fixture_policy: Sanitized contradiction and prior/current templates. Public artifacts expose only IDs, scopes, process summaries, and metrics.

## Allowed Conclusion

Under this fixture set, existing consistency-related mechanisms caught 1/2 within-report contradiction cases and 0/3 cross-time position-flip cases, with 0/3 control false positives. This characterizes structural signaling only; it does not detect semantic drift, truth, intent, or raw prior/current consistency.

## Metrics

| metric | value |
| --- | --- |
| fixture_count | 8 |
| within_report_catch_rate | 0.5 |
| cross_time_catch_rate | 0 |
| control_false_positive_rate | 0 |
| catch_rate | 0.2 |
| precision | 1 |
| false_positive_rate | 0 |
| matched_expectation_rate | 0.5 |
| degradation_event_count | 0 |

## Process Counts

| process | total | caught |
| --- | --- | --- |
| corrective_recall_parked | 8 | 0 |
| drift_monitor | 8 | 0 |
| pre_output_council | 8 | 1 |
| prior_position_memory_surface | 8 | 0 |

## Scope Summary

| scope | total | expected_issue | caught | miss | false_positive |
| --- | --- | --- | --- | --- | --- |
| control | 3 | 0 | 0 | 0 | 0 |
| cross_time | 3 | 3 | 0 | 3 | 0 |
| within_report | 2 | 2 | 1 | 1 | 0 |

## Cross-Time Misses

- cross_time_refund_flip_seen_001 (direct_policy_position_flip)
- cross_time_review_requirement_flip_novel_001 (review_requirement_flip)
- cross_time_memory_boundary_flip_novel_001 (public_private_boundary_flip)

## Within-Report Misses

- within_natural_negation_novel_001 (natural_language_negation_pair)

## Corrective Recall Status

- inert_by_default_rate: 1
- noop_on_zero_vector_rate: 1
- recall_fires_when_lit_rate: 1
- runtime_wired_for_drift: False
- source: corrective_recall_characterization

## Known Limits

- Synthetic fixtures are a characterization set, not a benchmark.
- Cross-time prior/current text is not compared by any new code here.
- DriftMonitor is vector-level; this harness has no model-free text-to-vector semantic mapper.
- Corrective recall remains parked/inert for runtime drift detection.
- Raw fixture text is intentionally omitted from public artifacts.

