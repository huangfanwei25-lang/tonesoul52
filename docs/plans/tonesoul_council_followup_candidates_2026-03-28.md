# ToneSoul Council Follow-Up Candidates (2026-03-28)

> Purpose: bounded future work items identified during the Council Dossier And Dissent Adaptation work order
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Related Contracts:
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md
>   - docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md

## Recommended Implementation Order

1 (safest) → 5 (most complex)

---

## Candidate 1: Dossier Extraction Helper

Add a `build_dossier()` function that extracts the 12 dossier fields from a `CouncilVerdict` object according to the Dossier Contract. Currently the verdict contains all the raw data but no extraction logic exists — each consumer (session trace, compaction, dispatch trace) assembles its own subset of fields ad hoc.

**Scope**: ~80 lines in a new `tonesoul/council/dossier.py` module. Pure function: takes `CouncilVerdict` + optional `dissent_ratio` from role council, returns a dict matching the dossier shape. No schema changes, no new dependencies.

**Why first**: zero behavioral change. Every existing code path continues to work. The helper just makes dossier production available for callers that want it. Compaction and session trace producers can opt in later.

---

## Candidate 2: Minority Report Extraction

Add extraction logic that filters `CouncilVerdict.votes` for dissenting votes (CONCERN or OBJECT) and produces the `minority_report` list shape defined in the Dossier Contract. This is a prerequisite for any consumer that wants to surface dissent explicitly.

**Scope**: ~30 lines, likely inside the `build_dossier()` function from Candidate 1. Could also be a standalone `extract_minority_report(votes)` utility.

**Why second**: builds on Candidate 1. The minority report shape is defined in the contract; this just implements the extraction. Low risk because the data already exists in votes — this is reshaping, not new computation.

---

## Candidate 3: Deliberation Mode Selection Function

Add a `select_deliberation_mode()` function that reads task track, risk posture, claim state, and readiness state and returns one of `lightweight_review`, `standard_council`, or `elevated_council` per the Adaptive Deliberation Mode Contract's matrix.

**Scope**: ~60 lines in a new helper module or as an extension of `_resolve_council_decision()` in `unified_pipeline.py`. The function returns a mode string; it does not change council behavior. Callers decide whether to act on the recommendation.

**Why third**: requires the Task Track & Readiness Contract to be active (at least as advisory classification). The function itself is simple — it is a lookup table — but its value depends on task classification being available at the deliberation decision point.

---

## Candidate 4: Change-Of-Position Tracking In Adaptive Deliberation

Add position tracking across rounds in `tonesoul/deliberation/adaptive_rounds.py`. Currently the adaptive debate runs multiple rounds and tracks tension per round, but does not explicitly record when a perspective (Muse/Logos/Aegis) changes its stance between rounds.

**Scope**: ~40 lines in `adaptive_rounds.py` — compare each perspective's stance in round N vs round N-1 and record changes in the `RoundResult` or a new `position_changes` list. Feed the result into the dossier's `change_of_position` field.

**Why fourth**: requires touching deliberation internals. The change is small but the deliberation engine has multiple code paths (gravity-based synthesis, persona track record, adaptive rounds). Testing all paths with position tracking adds integration complexity.

---

## Candidate 5: Evolution Suppression Flag

Add a check in `CouncilEvolution.evolve_weights()` that flags when any perspective's weight has dropped below 0.6 (40% reduction from baseline 1.0). Surface the flag in the evolution summary and in the dossier.

**Scope**: ~15 lines in `evolution.py` + integration with dossier extraction. Tiny code change, but the semantic question is significant: what should the system do when it detects that dissent is being systematically suppressed by weight evolution?

**Why fifth**: the flag itself is trivial, but the response to the flag (should elevated_council be forced? should weights be reset?) is a policy decision that needs human input. Implement the detection first; leave the response to a later phase.
