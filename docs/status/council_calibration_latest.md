# Council Calibration v0a — Realism Baseline

> Generated at `2026-04-16T02:12:21Z`.

- Schema version: `v0a`
- Status: `v0a_realism_baseline`

## Language Boundary

- This is: `internal realism baseline`
- This is NOT: `outcome calibration`
- This is NOT: `predictive accuracy`
- This is NOT: `public-launch blocker resolution`
- Ceiling effect: `none — council_decision_quality stays descriptive_only`
- Maximum honest claim: `council_decision_quality has moved from purely descriptive to 'trackable realism baseline with persistence capability established'`

## Data Sources

- Stress test journal: `C:\Users\user\Desktop\倉庫\memory\stress_test_journal.jsonl` (200 records)
- Council verdict persistence: 8 records

## Metrics

### agreement_stability

- Status: `computed`
- Sample count: `203`
- groups_analyzed: `12`
- mean_dominant_verdict_ratio: `1.0`
- mean_split_half_jsd: `0.0`
- Data source: `council_verdict_persistence(8) + stress_test_journal(200)`
- Measures: `vote distribution consistency for the same input across sessions`
- Does NOT measure: `whether the verdict was correct or appropriate`
- Interpretation: dominant_ratio near 1.0 = highly stable; jsd near 0.0 = low distribution drift across halves

### internal_self_consistency

- Status: `computed`
- Sample count: `179`
- consistent_count: `133`
- inconsistent_count: `46`
- consistency_rate: `0.743`
- Data source: `council_verdict_persistence(8) + stress_test_journal(200)`
- Measures: `alignment between internal signals (tension, objection, coherence) and verdict direction`
- Does NOT measure: `outcome calibration or predictive accuracy`
- Interpretation: consistency_rate near 1.0 = internal signals align with verdict direction; low rate suggests the council produces contradictory signal-verdict pairs

### suppression_recovery_rate

- Status: `computed`
- Sample count: `1`
- minority_events: `1`
- recovery_events: `0`
- recovery_rate: `0.0`
- Data source: `council_verdict_persistence(8) + stress_test_journal(200)`
- Measures: `rate at which suppressed minority positions later become the dominant verdict`
- Does NOT measure: `whether the minority position was correct`
- Interpretation: recovery_rate near 0.0 = minority positions never recover; moderate rate suggests the council can self-correct on repeated input

### persistence_coverage

- Status: `computed`
- Sample count: `8`
- field_completeness:
  - record_id: `1.0`
  - schema_version: `1.0`
  - recorded_at: `1.0`
  - agent: `1.0`
  - input_fingerprint: `1.0`
  - verdict: `1.0`
  - coherence: `1.0`
  - vote_profile: `1.0`
  - minority_perspectives: `1.0`
  - grounding_summary: `1.0`
- overall_field_coverage: `1.0`
- Data source: `council_verdict_persistence_lane`
- Measures: `field completeness of persisted council verdict records`
- Does NOT measure: `council quality or correctness`
- Interpretation: overall near 1.0 = all required fields present in all records; gaps indicate persistence schema drift or partial writes

## v0a Exit Criteria

- Baseline metrics stable: `True`
- Persistence operational: `True`
- Verdict records accumulating: `True`

## v0b Prerequisites (not in V1.1 scope)

- verdict_outcome_alignment N>=20: `False`
- Two consecutive stable waves: `False`
- Note: `v0b is not in scope for V1.1; these fields track forward readiness only`

## Receiver Rule

> These metrics describe internal realism baseline, not outcome calibration. They cannot be used to downgrade claim ceilings or justify public-launch language. council_decision_quality remains descriptive_only until v0b verdict-outcome alignment is established.
