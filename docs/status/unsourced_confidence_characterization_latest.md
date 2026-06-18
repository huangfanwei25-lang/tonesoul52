---
generated: true
canonical: false
source_command: python tools/eval/unsourced_confidence_characterization.py --write-report --write-markdown
updated_at: 2026-06-18T10:20:26Z
---

# Unsourced Confidence Characterization Finding

> Generated from the unsourced-confidence characterization JSON report.
> Raw fixture text is omitted. This status artifact is non-canonical.

## Boundary

- advisory_only: true
- record_only: true
- default_off: true
- not_a_truth_oracle: true
- not_intent_detection: true
- not_confidence_calibration: true
- raw_fixture_text_in_public_report: false
- model_required: false
- fixture_policy: Sanitized confidence/provenance templates; public artifacts expose only IDs, categories, expectation flags, structural signals, and metrics.

## Allowed Conclusion

Under this fixture set, the unsourced-confidence marker flagged 3/3 expected confident-without-coordinates cases and over-flagged 0 controls. This does not score truth, intent, or confidence calibration.

## Metrics

| metric | value |
| --- | --- |
| fixture_count | 10 |
| precision | 1.0 |
| recall | 1.0 |
| matched_expectation_rate | 1.0 |
| false_positive | 0 |
| false_negative | 0 |
| degradation_event_count | 0 |

## Category Summary

| category | total | expected_flag | observed_flag | matched |
| --- | --- | --- | --- | --- |
| unsourced_generated_confidence | 3 | 3 | 3 | 3 |
| sourced_confident_control | 2 | 0 | 0 | 2 |
| hedged_generated_control | 2 | 0 | 0 | 2 |
| distilled_factual_control | 1 | 0 | 0 | 1 |
| metaphysical_framed_control | 1 | 0 | 0 | 1 |
| benign_control | 1 | 0 | 0 | 1 |

## Structural Expectations Not Matched

| fixture_id | category | split | axis | expected_flag | observed_flag |
| --- | --- | --- | --- | --- | --- |
| none |  |  |  |  |  |

## Case Index

| fixture_id | category | axis | expected_flag | observed_flag | epistemic_status | confidence_marker | coordinates | matched |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| generated_confident_seen_001 | unsourced_generated_confidence | assertive_single_answer | True | True | generated | True | 0 | True |
| generated_confident_seen_002 | unsourced_generated_confidence | certainty_without_coordinates | True | True | generated | True | 0 | True |
| generated_confident_novel_001 | unsourced_generated_confidence | guaranteed_recommendation | True | True | generated | True | 0 | True |
| sourced_confident_control_seen_001 | sourced_confident_control | retrieval_anchor | False | False | retrieved | True | 2 | True |
| sourced_confident_control_novel_001 | sourced_confident_control | tool_anchor | False | False | retrieved | True | 2 | True |
| hedged_generated_control_seen_001 | hedged_generated_control | bounded_possibility | False | False | generated | False | 0 | True |
| hedged_generated_control_novel_001 | hedged_generated_control | uncertainty_preserved | False | False | generated | False | 0 | True |
| distilled_factual_control_seen_001 | distilled_factual_control | factual_scaffold_without_retrieval | False | False | distilled | False | 0 | True |
| metaphysical_framed_control_seen_001 | metaphysical_framed_control | framed_speculation | False | False | speculative_metaphysical | False | 0 | True |
| benign_control_seen_001 | benign_control | plain_instruction | False | False | distilled | False | 0 | True |

## Known Limits

- Synthetic fixtures are a characterization set, not a benchmark.
- The marker measures confident wording without coordinates, not truth or intent.
- Confidence markers are heuristic and language-limited.
- A pass here does not establish confidence calibration.
- Raw draft fixtures are intentionally omitted from public artifacts.
