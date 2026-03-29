# ToneSoul Council Realism Follow-Up Candidates (2026-03-29)

> Purpose: bounded next implementation candidates for council quality improvement, ordered by safety
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Related Contracts:
>   - docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md
>   - docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md
>   - docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md

---

## Candidate 1: Forced Devil's Advocate In Critic Prompt

Modify `_default_prompt()` in `perspective_factory.py` for the CRITIC perspective type to require at least one substantive objection. Current prompt allows the Critic to approve unanimously — forced dissent prevents silent consensus.

**Scope**: ~10 lines of prompt text change in `perspective_factory.py`.

**No code logic change**: the Critic still produces a `PerspectiveVote`. Only the prompt instructions change.

**Why first**: zero code change, zero schema change, zero cost increase. Directly addresses the most dangerous council failure mode (unanimous approval masking genuine concerns). The Dossier Contract already has a `minority_report` field to capture this output.

---

## Candidate 2: Confidence Decomposition Function

Add `compute_confidence_decomposition()` to `pre_output_council.py` that decomposes the single coherence score into 4 independently assessable dimensions:

```python
{
    "agreement": 0.90,           # perspective vote agreement (from existing coherence)
    "coverage": 0.60,            # count of distinct perspective types that participated
    "evidence_density": 0.40,    # evidence_refs count / total reasoning assertions
    "adversarial_survived": True # Critic vote was not OBJECT
}
```

**Scope**: ~30-40 lines in `pre_output_council.py`. All input data already exists in the council output.

**Why second**: builds on Candidate 1 (Critic's forced objection becomes the `adversarial_survived` signal). Replaces one misleading number with four honest dimensions. No infrastructure dependency.

---

## Candidate 3: Evolution Suppression Visibility Flag

Add `suppressed_perspectives` list to `build_council_summary()` in `runtime.py`. When `CouncilEvolution` has reduced any perspective's weight below 0.7, include it in the list. This makes evolution-induced diversity loss visible in the council output.

**Scope**: ~10 lines in `runtime.py`. Reads existing `CouncilEvolution.get_evolved_weights()`.

**Why third**: directly addresses the conformity bias problem documented in the Independence Contract. Without this flag, evolution can silently downweight the Critic until its objections have no practical effect — and no one notices.

---

## Candidate 4: Honest Confidence Labeling In Dossier Output

Rename confidence-bearing fields in dossier documentation and output formatting:
- `confidence_posture` → `agreement_posture`
- `coherence_score` → `agreement_score`
- Add one-line disclaimer to dossier output: "Agreement metrics describe perspective consensus, not prediction accuracy."

**Scope**: ~15 lines of documentation and output formatting changes.

**Why fourth**: naming is the cheapest and most impactful intervention for preventing miscalibration misuse. But it touches established naming, so it requires care to avoid breaking downstream consumers. Do after Candidates 1-3 which add new surfaces without renaming existing ones.

---

## Candidate 5: Self-Consistency For Elevated Council Mode

Add a `self_consistency_passes` parameter to `elevated_council` deliberation mode. Run `PreOutputCouncil.validate()` 3 times with LLM temperature variation. Report consistency rate alongside primary verdict.

**Scope**: ~50-70 lines in `runtime.py`. Requires elevated_council mode to be distinguishable in the code path (per Adaptive Deliberation Mode Contract).

**Why fifth**: highest-impact improvement for confidence quality, but has a 3x LLM cost multiplier. Should only be applied in elevated_council mode where stakes justify the cost. Depends on deliberation mode selection being implemented first.

---

## Summary

| # | Candidate | Scope | Code Change | Cost Increase |
|---|---|---|---|---|
| 1 | Forced devil's advocate | ~10 lines prompt | Prompt only | None |
| 2 | Confidence decomposition | ~30-40 lines | New function | None |
| 3 | Evolution suppression flag | ~10 lines | Existing weights | None |
| 4 | Honest confidence labeling | ~15 lines | Naming only | None |
| 5 | Self-consistency passes | ~50-70 lines | New code path | 3x LLM (elevated only) |

Candidates 1-4 have zero cost increase and total ~65 lines. Candidate 5 requires cost trade-off and mode selection infrastructure.
