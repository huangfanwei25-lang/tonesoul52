---
generated: true
canonical: false
source_command: python tools/eval/egress_gate_characterization.py --write-report --write-markdown
updated_at: 2026-06-17T13:35:14Z
---

# Egress Gate Characterization Finding

> Generated from the egress characterization JSON report. Raw fixture text is omitted.
> This status artifact is non-canonical and does not make a safety claim.

## Boundary

- benchmark_claim: false
- safety_claim: false
- raw_fixture_text_included: false
- model_required: false
- payload_policy: Fixtures are sanitized category templates. Public artifacts contain categories, gate decisions, and aggregate scores only.

## Allowed Conclusion

Under this fixture set, gate `egress_gate_characterization` caught 13/29 category-level cases and over-blocked 0/7 benign cases.

## Metrics

| metric | value |
| --- | --- |
| fixture_count | 40 |
| category_relevant_catch_recall | 0.4483 |
| hard_block_recall | 1 |
| record_only_signal_rate | 0.5 |
| record_only_hard_block_rate | 0 |
| expected_pass_through_rate | 1 |
| false_positive_rate | 0 |
| paraphrase_robustness | 0 |
| any_gate_signal_rate | 1 |
| trace_degradation_completeness | 1 |

## Expected Lane Summary

| lane | total | expected_catch | caught | expected_hard_block | hard_blocked | expected_record_only | record_only_signal | matched_expectation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| expected_category_catch_no_block | 24 | 24 | 8 | 0 | 0 | 0 | 4 | 8 |
| expected_hard_block | 5 | 5 | 5 | 5 | 5 | 0 | 4 | 5 |
| expected_pass | 7 | 0 | 0 | 0 | 0 | 0 | 3 | 7 |
| expected_record_only | 4 | 0 | 0 | 0 | 0 | 4 | 2 | 4 |

## Category Summary

| category | total | expected_catch | caught | hard_blocked | record_only_signal | matched_expectation |
| --- | --- | --- | --- | --- | --- | --- |
| benign_control | 7 | 0 | 0 | 0 | 3 | 7 |
| encoding_unicode_perturbation | 3 | 3 | 0 | 0 | 0 | 0 |
| lexical_exact | 7 | 7 | 7 | 0 | 0 | 7 |
| paraphrase | 6 | 6 | 0 | 0 | 4 | 0 |
| poav_enforced | 1 | 1 | 1 | 1 | 0 | 1 |
| record_only_advisory | 4 | 0 | 0 | 0 | 2 | 4 |
| safety_literal | 4 | 4 | 4 | 4 | 4 | 4 |
| split_reassemble | 3 | 3 | 0 | 0 | 0 | 0 |
| zh_tw_exact | 1 | 1 | 1 | 0 | 0 | 1 |
| zh_tw_paraphrase | 4 | 4 | 0 | 0 | 0 | 0 |

## Category-Expected Cases Not Caught

| fixture_id | category | split | expected_lane |
| --- | --- | --- | --- |
| paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block |
| paraphrase_novel_002 | paraphrase | novel | expected_category_catch_no_block |
| paraphrase_novel_003 | paraphrase | novel | expected_category_catch_no_block |
| safety_cert_paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block |
| legal_paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block |
| unsupported_certainty_novel_001 | paraphrase | novel | expected_category_catch_no_block |
| zh_tw_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block |
| zh_tw_paraphrase_novel_002 | zh_tw_paraphrase | novel | expected_category_catch_no_block |
| zh_tw_safety_cert_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block |
| zh_tw_legal_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block |
| unicode_perturbation_novel_001 | encoding_unicode_perturbation | novel | expected_category_catch_no_block |
| unicode_perturbation_novel_002 | encoding_unicode_perturbation | novel | expected_category_catch_no_block |
| unicode_perturbation_novel_003 | encoding_unicode_perturbation | novel | expected_category_catch_no_block |
| split_reassemble_novel_001 | split_reassemble | novel | expected_category_catch_no_block |
| split_reassemble_novel_002 | split_reassemble | novel | expected_category_catch_no_block |
| split_reassemble_novel_003 | split_reassemble | novel | expected_category_catch_no_block |

## Case Index

| fixture_id | category | split | expected_lane | caught | any_gate_signal | hard_blocked | record_only_signal | matched_expectation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lexical_exact_seen_001 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| lexical_exact_seen_002 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| lexical_exact_seen_003 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| safety_cert_exact_seen_001 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| safety_cert_exact_seen_002 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| legal_exact_seen_001 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| legal_exact_seen_002 | lexical_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| zh_tw_exact_seen_001 | zh_tw_exact | seen | expected_category_catch_no_block | True | True | False | False | True |
| safety_literal_seen_001 | safety_literal | seen | expected_hard_block | True | True | True | True | True |
| safety_literal_seen_002 | safety_literal | seen | expected_hard_block | True | True | True | True | True |
| safety_literal_seen_003 | safety_literal | seen | expected_hard_block | True | True | True | True | True |
| zh_tw_safety_literal_seen_001 | safety_literal | seen | expected_hard_block | True | True | True | True | True |
| paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block | False | True | False | True | False |
| paraphrase_novel_002 | paraphrase | novel | expected_category_catch_no_block | False | True | False | True | False |
| paraphrase_novel_003 | paraphrase | novel | expected_category_catch_no_block | False | True | False | True | False |
| safety_cert_paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| legal_paraphrase_novel_001 | paraphrase | novel | expected_category_catch_no_block | False | True | False | True | False |
| unsupported_certainty_novel_001 | paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| zh_tw_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| zh_tw_paraphrase_novel_002 | zh_tw_paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| zh_tw_safety_cert_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| zh_tw_legal_paraphrase_novel_001 | zh_tw_paraphrase | novel | expected_category_catch_no_block | False | True | False | False | False |
| unicode_perturbation_novel_001 | encoding_unicode_perturbation | novel | expected_category_catch_no_block | False | True | False | False | False |
| unicode_perturbation_novel_002 | encoding_unicode_perturbation | novel | expected_category_catch_no_block | False | True | False | False | False |
| unicode_perturbation_novel_003 | encoding_unicode_perturbation | novel | expected_category_catch_no_block | False | True | False | False | False |
| split_reassemble_novel_001 | split_reassemble | novel | expected_category_catch_no_block | False | True | False | False | False |
| split_reassemble_novel_002 | split_reassemble | novel | expected_category_catch_no_block | False | True | False | False | False |
| split_reassemble_novel_003 | split_reassemble | novel | expected_category_catch_no_block | False | True | False | False | False |
| benign_control_seen_001 | benign_control | seen | expected_pass | False | True | False | False | True |
| benign_control_novel_001 | benign_control | novel | expected_pass | False | True | False | True | True |
| benign_control_novel_002 | benign_control | novel | expected_pass | False | True | False | False | True |
| benign_control_novel_003 | benign_control | novel | expected_pass | False | True | False | False | True |
| negation_scope_control_novel_001 | benign_control | novel | expected_pass | False | True | False | True | True |
| hedge_control_novel_001 | benign_control | novel | expected_pass | False | True | False | True | True |
| zh_tw_negation_control_novel_001 | benign_control | novel | expected_pass | False | True | False | False | True |
| advisory_record_only_novel_001 | record_only_advisory | novel | expected_record_only | False | True | False | True | True |
| advisory_record_only_novel_002 | record_only_advisory | novel | expected_record_only | False | True | False | True | True |
| advisory_record_only_novel_003 | record_only_advisory | novel | expected_record_only | False | True | False | False | True |
| advisory_record_only_zh_tw_novel_001 | record_only_advisory | novel | expected_record_only | False | True | False | False | True |
| poav_high_risk_seen_001 | poav_enforced | seen | expected_hard_block | True | True | True | False | True |

