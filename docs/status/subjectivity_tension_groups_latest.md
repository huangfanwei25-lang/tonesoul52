# Subjectivity Tension Groups Latest

- generated_at: 2026-03-11T14:46:12Z
- overall_ok: true
- db_path: C:/Users/user/Desktop/倉庫/memory/soul.db
- source: all

## Handoff
- queue_shape: monitoring_queue
- requires_operator_action: false
- top_group_shape: high_duplicate_same_source_loop
- primary_status_line: high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate

## Summary
- unresolved_row_count: 50
- semantic_group_count: 1
- lineage_group_count: 12
- multi_direction_topic_count: 0

## Recommendation Counts
- defer_review: 1

## Duplicate Pressure Counts
- high: 1

## Producer Follow-Up Counts
- upstream_dedup_candidate: 1

## Status Lines
- high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate

## Semantic Groups
- A distributed vulnerability database for Open Source (`governance_escalation`, `medium`, rows=50, lineages=12, cycles=30, sources=1`)
  - recommendation: `defer_review`
  - group_shape: high_duplicate_same_source_loop
  - reason: Cross-cycle repetition exists, but it is still dominated by one source loop and weak directionality.
  - duplicate_pressure: high
  - producer_followup: upstream_dedup_candidate
  - density: rows_per_lineage=4.17, rows_per_cycle=1.67
  - lineage_density: repeated_lineages=11, dense_lineages=10, singleton_lineages=1, max_rows_per_lineage=5
  - lineage_record_histogram: 1=>1, 2=>1, 3=>1, 4=>1, 5=>8
  - duplicate_pressure_reason: One source loop is reopening the queue with repeated collision rows across many cycles and lineages.
  - source_urls: https://osv.dev/
  - stimulus_lineages: 07173cbb-d751-48c2-933e-cffcd239058f, 165f6d95-3845-4f4e-a63d-d3020f1a499d, 298346a8-53e0-4d93-b572-5aef0dd7ba0e, 5d5719a4-7890-4b6b-a404-3c667bcd9b2a

## Topics With Multiple Directions
- None

## Lineage Groups
- 9b2d5754-190c-41e1-96bd-7a0e6ff967cc (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 165f6d95-3845-4f4e-a63d-d3020f1a499d (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 90638411-5557-4055-ad09-bc925901d19b (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- a9ed1014-7e52-46d5-b486-41ce436aa2e7 (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 298346a8-53e0-4d93-b572-5aef0dd7ba0e (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 5d5719a4-7890-4b6b-a404-3c667bcd9b2a (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 70d4c11a-9ddb-4717-a82a-c22fba255639 (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- c223a657-d4c8-4765-9be9-1587dafe72fd (`A distributed vulnerability database for Open Source`, rows=5, cycles=5)
- 938da88c-3cf0-4377-bd96-4d23ece4661f (`A distributed vulnerability database for Open Source`, rows=4, cycles=4)
- ccb61719-9c1f-4316-8d58-0c1ae98236e0 (`A distributed vulnerability database for Open Source`, rows=3, cycles=3)
- 07173cbb-d751-48c2-933e-cffcd239058f (`A distributed vulnerability database for Open Source`, rows=2, cycles=2)
- fca70fc9-9e86-48f3-be1e-8f9eea526755 (`A distributed vulnerability database for Open Source`, rows=1, cycles=1)
