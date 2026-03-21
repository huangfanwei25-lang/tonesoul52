# Subjectivity Review Batch Latest

- generated_at: 2026-03-11T15:55:43Z
- overall_ok: true
- db_path: C:/Users/user/Desktop/倉庫/memory/soul.db
- source: all

## Handoff
- queue_shape: stable_history_only
- requires_operator_action: false
- top_queue_posture: stable_deferred_history
- primary_status_line: stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split

## Summary
- unresolved_row_count: 50
- semantic_group_count: 1
- lineage_group_count: 12
- review_group_count: 1

## Default Status Counts
- deferred: 1

## Revisit Readiness Counts
- holding_deferred: 1

## Carry-Forward Annotations
- prior_deferred_match: 1

## Queue Postures
- stable_deferred_history: 1

## Duplicate Pressure Counts
- high: 1

## Producer Follow-Up Counts
- upstream_dedup_candidate: 1

## Operator Follow-Up Counts
- read_only_density_compaction_candidate: 1

## Admissibility Gate Counts
- admissibility_not_yet_clear: 1

## Admissibility Focus Counts
- authority_and_exception_pressure: 1

## Status Lines
- stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split

## Admissibility Status Lines
- admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity

## Operator Lens
- A distributed vulnerability database for Open Source (`stable_deferred_history`)
  - summary: stable deferred history; 50 row(s) compress to 12 lineage(s) / 30 cycle(s); density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1; no new rows since latest review.
  - revisit_trigger: Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.

## Review Groups
- A distributed vulnerability database for Open Source (`defer_review`, default=deferred, rows=50, lineages=12, cycles=30`)
  - revisit_readiness: holding_deferred
  - carry_forward_annotation: prior_deferred_match
  - queue_posture: stable_deferred_history
  - duplicate_pressure: high
  - producer_followup: upstream_dedup_candidate
  - operator_followup: read_only_density_compaction_candidate
  - revisit_trigger: Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.
  - revisit_trigger_code: second_source_context_or_material_split
  - operator_lens_summary: stable deferred history; 50 row(s) compress to 12 lineage(s) / 30 cycle(s); density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1; no new rows since latest review.
  - operator_status_line: stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split
  - density: rows_per_lineage=4.17, rows_per_cycle=1.67
  - history_density_summary: 50 row(s) across 30 cycle(s) / 12 lineage(s) from 2026-03-10T05:08:05Z to 2026-03-11T08:08:13Z; same-source loop; no new rows since latest review.
  - lineage_density: repeated_lineages=11, dense_lineages=10, singleton_lineages=1, max_rows_per_lineage=5
  - lineage_record_histogram: 1=>1, 2=>1, 3=>1, 4=>1, 5=>8
  - duplicate_pressure_reason: One source loop is reopening the queue with repeated collision rows across many cycles and lineages.
  - density_compaction_reason: 50 deferred row(s) are concentrated into 12 lineage(s); 11 lineage(s) repeat, 10 lineage(s) carry 3+ rows, and the deepest lineage carries 5 row(s).
  - basis: A distributed vulnerability database for Open Source recurred across 50 unresolved row(s), 12 lineage(s), and 30 cycle(s), but direction `governance_escalation` is still dominated by one source loop and should be revisited later rather than promoted now; admissibility under existing P0/P1 constraints is not yet strong enough to assert.
  - admissibility: admissibility_not_yet_clear / authority_and_exception_pressure
  - admissibility_status_line: admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity
  - admissibility_risk_tags: cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity
  - admissibility_prompt: Before approving `A distributed vulnerability database for Open Source`, explicitly answer the admissibility questions and confirm that the direction does not violate existing P0/P1 constraints.
  - pending_status_counts: deferred=50
  - latest_review_timestamp: 2026-03-11T10:07:11Z
  - latest_row_timestamp: 2026-03-11T08:08:13Z
  - rows_after_latest_review: 0
  - prior_decision_status_counts: deferred=50
  - latest_matched_review_timestamp: 2026-03-11T10:07:11Z
  - latest_review_status: deferred
  - latest_review_actor: operator (operator)
  - latest_review_basis: Directional governance pressure persists across cycles and lineages, but it is still confined to one source loop (osv.dev); defer rather than promote until a second source context or materially different governance setting corroborates it.
  - latest_review_notes: Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.
  - representative_record_ids: e3852e6b-fefe-472b-8822-a951a7149b46, 92f9fe80-15c3-4248-8fe7-35b07c738bc4, 2a124f8b-4c9e-4f5e-a89f-7a4eabdb3a77, 551941cc-f25c-4089-8524-67d62b04b684, 70ea9b23-3cb5-4f9d-8afd-128b38a4b999, bcb0066f-5849-4914-a21f-850c376a0f89
