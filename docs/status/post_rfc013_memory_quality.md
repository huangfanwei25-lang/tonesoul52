# Post RFC-013 Memory Quality Check

- Date (UTC): 2026-03-02T02:17:02Z
- Command: python scripts/run_memory_quality_report.py
- Overall OK: True

## Key Metrics

- entry_count: 10843
- failure_case_count: 10833
- learning_sample_count: 10833
- invalid_json_line_count: 0

## Quality Signals

- failure_case_rate: 0.9991
- provenance_coverage_rate: 0.7548
- divergence_coverage_rate: 1.0
- contract_coverage_rate: 0.1811
- contract_evidence_coverage_rate: 0.0

## Result

- Gate check: PASS (invalid_json_line_count == 0)
- No new integrity regression detected in memory journal parsing.
