# ToneSoul Second Trial Candidate Admission (2026-04-07)

> Purpose: admit one next bounded self-improvement candidate after the first trial wave, dashboard-only cue pilot, and shell-exclusion guard have all landed.
> Status: admitted candidate note for `Phase 799`; promoted into active execution for `Phase 800`.
> Authority: planning aid. Runtime truth remains in code, tests, accepted contracts, and the current bounded trial/result surfaces.

---

## Why This Exists

ToneSoul now has:

- one first bounded trial wave
- one promoted result (`consumer_parity_packaging_v1`)
- one parked result (`operator_retrieval_cueing_v1`)
- one bounded result surface
- one dashboard-only visibility cue
- one regression guard proving the cue stays out of first-hop shells

That means the next bottleneck is no longer:

- how to store trial results
- how to keep cue surfaces bounded

It is:

`what is the next specific candidate worth trialing, without reopening retrieval mythology, governance drift, or shell sprawl?`

This note exists to answer that before a second wave opens.

---

## Admission Rule

The next candidate must satisfy all of these:

- fall inside `allowed_now` mutation classes
- produce operator-visible leverage
- preserve consumer parity
- carry an explicit rollback posture
- avoid reopening transport, identity, governance, or retrieval-runtime fantasies

If it cannot satisfy those, it does not enter the second wave.

---

## Chosen Candidate

### `candidate_id`

`deliberation_mode_hint_latency_v2`

### `target_surface`

`session_start.deliberation_mode_hint`

### `target_consumer`

`codex_cli / claude_adapter / dashboard_operator_shell`

---

## Why This Candidate

This is the best next candidate because it sits at the intersection of:

- operator latency
- multi-agent overhead
- tiered workspace routing
- shared consumer interpretation

It is also inside an already-allowed mutation class:

- routing and escalation hints

And it avoids the biggest parked risk from the first wave:

- pretending retrieval is already live enough to optimize

---

## Baseline Story

ToneSoul already moved bounded feature-track work toward:

- `lightweight_review`

That was a strong correction.

But the current surface still carries one remaining friction:

`later agents can still over-read escalation triggers because the hint does not yet distinguish soft review cues from hard escalation conditions clearly enough.`

The result is not catastrophic, but it creates unnecessary latency pressure and can quietly tax normal continuation work.

---

## Candidate Story

The candidate is:

- not a council-runtime rewrite
- not a claim/readiness rewrite
- not a new deliberation mode

It is only a packaging refinement of:

- `deliberation_mode_hint`

The likely direction is:

- preserve the current final mode recommendation
- separate `hard escalation triggers` from `soft review cues`
- make the summary explain why a shell should stay in `lightweight_review` versus escalate

This keeps the candidate narrow and testable.

---

## Proposed Success Metric

The second-wave evaluator should judge this candidate using:

1. regression:
   - `tests/test_start_agent_session.py`
   - dashboard tier-shell tests remain green

2. parity:
   - Codex-style, dashboard, and Claude-compatible consumers still tell the same escalation story

3. operability:
   - bounded feature-track scenarios read more clearly as `lightweight_review`
   - claim collisions, blocked readiness, or contested closeout still escalate honestly

4. honesty:
   - the cue must not imply that lightweight review means "safe forever"

---

## Failure Watch

The main failure watches are:

- under-escalation when real claim conflict or blocked readiness exists
- wording that sounds cheaper but hides risk
- consumer drift where one shell says `lightweight_review` and another sounds closer to `standard_council`
- reintroducing latency through extra explanatory clutter

If any of these dominate, the second wave should end in:

- `park`
- or `retire`

not `promote`.

---

## Rollback Posture

`bounded_restore`

If the trial fails:

- revert hint packaging
- restore current trigger story
- keep the result surface as history only

No deeper rollback is needed because the candidate does not change runtime council semantics.

---

## Overclaim To Avoid

`better deliberation hinting is not better deliberation quality`

This candidate, even if promoted, does **not** prove:

- improved reasoning
- improved council independence
- improved accuracy
- reduced risk in all tasks

It would only prove:

- better bounded escalation packaging

---

## No-Go List For Wave 2

These should **not** enter the second wave:

1. `operator_retrieval_cueing_v1`
   - still parked
   - no live retrieval runner
   - no compiled collection health lane

2. any `session-start` or `observer-window` self-improvement cue expansion
   - `Phase 798` explicitly guards against this

3. council calibration or confidence math changes
   - still human-gated

4. identity, vows, or transport semantics
   - forbidden in v0

5. public/demo surface changes justified by self-improvement momentum alone
   - not the shortest board

---

## Recommended Next Phase

Open:

- `Phase 800: Second Bounded Trial Wave - Deliberation Hint Candidate`

Do **not** open:

- broader shell redesign
- retrieval runtime optimism
- second-wave multi-candidate experimentation

One admitted candidate is enough for the next step.

---

## One-Sentence Summary

`The next safe self-improvement candidate is a bounded refinement of deliberation-mode hinting, because it directly attacks unnecessary multi-agent latency without crossing retrieval, identity, governance, or transport boundaries.`
