# Corrective-Recall Characterization

generated: True
canonical: False
updated_at: 2026-06-18T00:00:00Z

This status artifact is non-canonical and makes no runtime or relevance claim. It measures the parked error-vector corrective-recall logic with a controlled fake index (no FAISS, no model, no gitignored store).

## Allowed conclusion

Under this fixture set, corrective recall is inert by default with no store (1.0); the pre-recall guard skips on a zero error vector / no-rewrite case (1.0); and given a populated store the recall path fires (1.0) and the planted corrective item is present in the selected subset (1.0). These are structural signals — not a claim about runtime liveness, discrepancy-gated firing, or recall quality.

## Metrics

| metric | value |
|---|---|
| fixture_count | 4 |
| inert_by_default_rate | 1.0 |
| noop_on_zero_vector_rate | 1.0 |
| recall_fires_when_lit_rate | 1.0 |
| returns_planted_item_rate | 1.0 |
| structural_signal_rate | 1.0 |
| degradation_event_count | 0 |

## Cases

| fixture_id | mode | split | signals observed |
|---|---|---|---|
| inert_default_seen_001 | inert_default | seen | inert_by_default |
| noop_zero_vector_seen_001 | noop_zero_vector | seen | noop_on_zero_vector |
| lit_discrepancy_seen_001 | lit_discrepancy | seen | recall_fires_when_lit, returns_planted_item |
| lit_discrepancy_novel_001 | lit_discrepancy | novel | recall_fires_when_lit, returns_planted_item |

