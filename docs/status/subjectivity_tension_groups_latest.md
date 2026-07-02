# Subjectivity Tension Groups Latest

- generated_at: 2026-07-02T07:34:22Z
- overall_ok: true
- db_path: C:/Users/user/Desktop/codex_worktrees/stale-regen-20260702/memory/soul.db
- source: all

## Handoff
- queue_shape: multi_group
- requires_operator_action: false
- top_group_shape: same_source_loop_monitor
- primary_status_line: same_source_loop_monitor | A distributed vulnerability database for Open Source | recommendation=reject_review | rows=1 lineages=1 cycles=1 | density=1r x1

## Summary
- unresolved_row_count: 2
- semantic_group_count: 2
- lineage_group_count: 2
- multi_direction_topic_count: 0

## Recommendation Counts
- reject_review: 2

## Duplicate Pressure Counts
- low: 2

## Status Lines
- same_source_loop_monitor | A distributed vulnerability database for Open Source | recommendation=reject_review | rows=1 lineages=1 cycles=1 | density=1r x1
- same_source_loop_monitor | [](https://google.github.io/osv.dev/data/#data-sources) Data sources | recommendation=reject_review | rows=1 lineages=1 cycles=1 | density=1r x1

## Semantic Groups
- A distributed vulnerability database for Open Source (`governance_escalation`, `low`, rows=1, lineages=1, cycles=1, sources=1`)
  - recommendation: `reject_review`
  - group_shape: same_source_loop_monitor
  - reason: Same-source repetition without context diversity does not justify commitment weight.
  - duplicate_pressure: low
  - producer_followup: none
  - density: rows_per_lineage=1.0, rows_per_cycle=1.0
  - lineage_density: repeated_lineages=0, dense_lineages=0, singleton_lineages=1, max_rows_per_lineage=1
  - lineage_record_histogram: 1=>1
  - duplicate_pressure_reason: No dominant same-source duplicate loop is visible at the current grouping level.
  - source_urls: https://osv.dev/
  - stimulus_lineages: 835bc5df-0609-4409-bb65-fb1a4cb6c43a
- [](https://google.github.io/osv.dev/data/#data-sources) Data sources (`governance_escalation`, `low`, rows=1, lineages=1, cycles=1, sources=1`)
  - recommendation: `reject_review`
  - group_shape: same_source_loop_monitor
  - reason: Same-source repetition without context diversity does not justify commitment weight.
  - duplicate_pressure: low
  - producer_followup: none
  - density: rows_per_lineage=1.0, rows_per_cycle=1.0
  - lineage_density: repeated_lineages=0, dense_lineages=0, singleton_lineages=1, max_rows_per_lineage=1
  - lineage_record_histogram: 1=>1
  - duplicate_pressure_reason: No dominant same-source duplicate loop is visible at the current grouping level.
  - source_urls: https://google.github.io/osv.dev/data/
  - stimulus_lineages: 153a7b6f-29be-4e9f-b097-8085551ec480

## Topics With Multiple Directions
- None

## Lineage Groups
- 835bc5df-0609-4409-bb65-fb1a4cb6c43a (`A distributed vulnerability database for Open Source`, rows=1, cycles=1)
- 153a7b6f-29be-4e9f-b097-8085551ec480 (`[](https://google.github.io/osv.dev/data/#data-sources) Data sources`, rows=1, cycles=1)
