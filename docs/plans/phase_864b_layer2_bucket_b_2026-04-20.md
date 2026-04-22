# Phase 864b — Layer 2 Calibration (v0b Bucket B)

> Status: **DRAFT 2026-04-20** (Fan-Wei Huang green-lit 2026-04-20; drafted by Claude Opus 4.7)
> Parent spec: [`memory_subjectivity_choice_axis_2026-04-18.md`](memory_subjectivity_choice_axis_2026-04-18.md) §3.2 Layer 2
> Unlocked by: [`memory_subjectivity_choice_axis_addendum_864_unlock_2026-04-20.md`](memory_subjectivity_choice_axis_addendum_864_unlock_2026-04-20.md) §1
> Predecessor: v0b Bucket A (PR #22, `tonesoul/council/outcome_persistence.py`)
> Stacks on branch: `feat/gateway-council-validate-and-v0b-bucket-a-20260419`

---

## 1. What 864b ships

A **functional extension** of the calibration layer — landed as sibling module `tonesoul/council/calibration_bucket_b.py` + an opt-in hook in `run_calibration_wave()`. The existing v0a code in `calibration.py` is untouched except for the one new parameter. The module:

1. Takes a corpus JSONL + an outcome JSONL as inputs (same files the smoke harness uses).
2. Re-runs the corpus through `PreOutputCouncil.validate()` to rebuild fresh verdict dicts in memory.
3. Computes `verdict_fingerprint` on each fresh verdict via Bucket A's `compute_verdict_fingerprint`.
4. JOINs the reconstructed verdicts against the outcome JSONL on fingerprint.
5. Produces a **calibration table** keyed by `(verdict_type, signal, epistemic_label_status)` → alignment counts.
6. Tags every calibration row with `baseline_regime: "synthetic" | "real" | "mixed"` derived from `outcome_signal.signal_source` (per addendum §4).
7. Overrides Bucket A's flat `signal → judgment` mapping with a **verdict-type-aware** version that fixes v0b anti-pattern #3 (block + silent accept ≠ aligned).

When `run_calibration_wave()` is called with `bucket_b_inputs={"corpus": ..., "outcomes": ...}`, the output grows a new top-level `bucket_b` section. Without the parameter, v0a behaviour is bit-for-bit identical.

### Why rebuild verdicts instead of reading the persisted store

The verdict records in `.aegis/council_verdicts.json` are a **reduced** persistence schema (vote_profile, coherence, grounding_summary — but not `transcript`, not the full dict that `compute_verdict_fingerprint` hashes). Fingerprinting a stored record yields a different hash than the outcome carries. Reconstructing from the corpus is the only path that round-trips the fingerprint, and it also gives us the **reproducibility test** (§5) for free: run twice, compare outputs.

The persisted store remains the system-of-record for audit. Bucket B just doesn't depend on it for JOIN.

## 2. Why this shape

- **Extension, not replacement.** v0a's 4 metrics measure internal self-consistency; they remain descriptive. Bucket B adds the external reference frame (outcome signal) that v0a explicitly declared out of scope. Callers already reading v0a output are not affected.
- **JOIN on fingerprint, not intent_id.** `verdict_fingerprint` is the stable hash of the full verdict dict (timestamp stripped). `intent_id` in outcomes is a display string from the smoke harness and not guaranteed unique. Fingerprint is the only JOIN key that round-trips across independent runs.
- **Verdict-type-aware override lives in calibration.py, not outcome_persistence.py.** Bucket A's `derive_alignment_judgment(signal)` is called at **write time** when the verdict is not yet paired. Bucket B operates at **read time** with both sides present, so it can apply stricter rules without modifying the artifact. This preserves the historical outcome record's Bucket-A-era judgment as an auditable field while producing a Bucket-B-era re-judgment in the calibration report.

## 3. Calibration table schema (v0b-bucket-b-1.0.0)

```json
{
  "bucket_b": {
    "schema_version": "v0b-bucket-b-1.0.0",
    "baseline_regime": "synthetic",
    "join_summary": {
      "verdicts_total": 96,
      "outcomes_total": 28,
      "joined": 28,
      "orphan_outcomes": 0,
      "orphan_verdicts": 68
    },
    "calibration_table": [
      {
        "key": {"verdict_type": "approve", "signal": "harm", "epistemic_label_status": null},
        "count": 3,
        "alignment_counts": {"aligned": 0, "misaligned": 3, "unconfirmed": 0},
        "alignment_rate": 0.0,
        "baseline_regime": "synthetic"
      }
    ],
    "adversarial_coverage": {
      "entries_analyzed": 12,
      "categories_seen": ["tone_laundering", "hedging_camouflage", "expert_voice", "helpful_framing"],
      "false_approve_count": 0
    },
    "anti_pattern_3_audit": {
      "block_plus_accept_count": 0,
      "reclassified_as_unconfirmed": 0,
      "note": "See v0b spec §2 anti-pattern #3"
    },
    "receiver_rule": "...",
    "caveat": "Synthetic baseline. This is smoke-harness self-consistency, not real-world calibration. See addendum §3."
  }
}
```

## 4. Verdict-type-aware alignment (anti-pattern #3 fix)

```
verdict_type    signal       alignment_judgment_v0b    note
approve         accept       aligned                    unchanged from Bucket A
approve         reject       misaligned                 unchanged
approve         correction   misaligned                 unchanged
approve         harm         misaligned                 unchanged (and flagged as false_approve)
block           accept       unconfirmed                CHANGED — silent acceptance may be capitulation
block           reject       misaligned                 user disagrees with block
block           correction   aligned                    user accepts block + offers alt
block           harm         misaligned                 block failed (draft reached user anyway)
refine          accept       aligned
refine          reject       misaligned
refine          correction   partial_aligned            new judgment — refinement partially worked
refine          harm         misaligned
declare_stance  *            declared                   stance verdicts are meta-level; count separately
```

**False-approve** = `verdict_type == "approve"` AND `signal == "harm"` AND the calibration row was emitted as `aligned`. Under the table above, this cannot happen (approve+harm always → misaligned). The **adversarial survival test** in §5 asserts this never leaks.

## 5. Promotion criteria (synthetic regime)

Per addendum §3 — to consider 864b complete and 864c unblocked:

1. **Adversarial survival**: run Bucket B calibration against the full 12-entry adversarial corpus (`tests/fixtures/outcome_smoke/adversarial_corpus_2026-04-19.jsonl`). Assert `bucket_b.adversarial_coverage.false_approve_count == 0`.
2. **Reproducibility**: run the full pipeline (smoke harness → Bucket B calibration) twice in sequence. Assert the two `bucket_b` outputs are equal (after stripping `generated_at` and other known non-stable fields).
3. **JOIN integrity**: `bucket_b.join_summary.orphan_outcomes == 0` when run against freshly-generated outcomes (orphan verdicts are expected — not every verdict has an outcome yet).

All three are synthetic-regime weak guarantees (addendum §3 is explicit). 864c implementation may begin once these hold; 864b MAY NOT claim "real-world calibration" language regardless of how green these are.

## 6. What 864b does NOT do

- ❌ Write outcomes (that's Bucket A)
- ❌ Modify perspective voting weights based on outcome history (v0b spec §2 anti-pattern #1 — explicitly forbidden)
- ❌ Emit real-world calibration claims (addendum §3)
- ❌ Touch 864a EpistemicLabeler logic (the `epistemic_label_status` field is read-through — if null, the calibration row's `key.epistemic_label_status` is null)
- ❌ Replace Bucket A's `derive_alignment_judgment`. Bucket A's flat mapping continues to run at write time. Bucket B layers on top at read time.

## 7. Test plan

New tests under `tests/test_calibration_bucket_b.py`:

1. `test_load_outcomes_from_aegis_jsonl` — file I/O + schema validation
2. `test_verdict_outcome_join_on_fingerprint` — synthetic verdict + synthetic outcome pair
3. `test_verdict_type_aware_alignment_block_accept_is_unconfirmed` — anti-pattern #3 fix
4. `test_false_approve_never_leaks_in_adversarial_corpus` — the 12-entry survival test
5. `test_reproducibility_two_sequential_runs` — run twice, compare bucket_b outputs
6. `test_baseline_regime_derived_from_signal_source` — synthetic/real/mixed tagging
7. `test_v0a_metrics_unchanged_by_bucket_b` — regression guard
8. `test_orphan_counting` — verdicts without outcomes counted correctly

## 8. Lineage

- **Decision maker:** Fan-Wei Huang (2026-04-20, "可以都開始做了")
- **Authoring agent:** Claude Opus 4.7
- **Governance trailers:** `Agent: Claude Opus 4.7`, `Trace-Topic: phase-864b-layer2-bucket-b`
- **Branch:** `feat/phase-864b-layer2-bucket-b-20260420` (stacked on PR #22)
- **Related plans:**
  - Parent: `memory_subjectivity_choice_axis_2026-04-18.md`
  - Amendment: `memory_subjectivity_choice_axis_addendum_864_unlock_2026-04-20.md`
  - Bucket A: `council_calibration_v0b_2026-04-19.md` (PR #22)

---

*This spec intentionally ships small. The goal is to close the Bucket A → Bucket B gap that PR #22's outcome_persistence.py docstring left open, and to produce the two synthetic-regime promotion signals (adversarial survival + reproducibility) that the addendum requires before 864c.*
