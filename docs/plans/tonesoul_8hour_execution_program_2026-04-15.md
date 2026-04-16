# ToneSoul 1.0 Eight-Hour Execution Program (2026-04-15)

> Purpose: use one focused 8-hour window to move the current ToneSoul 1.0 launch line from repeated-validation buildup toward a refreshed collaborator-beta review, without reopening 2.0 or theory-side lanes.
> Status: active execution aid for the current repo state. This plan is subordinate to `task.md`, latest `docs/status/*`, code, and tests.
> Scope: `Phase 722 -> Phase 726 -> Phase 724`, with strict stop conditions if the evidence line does not move cleanly.

---

## 1. Current Truth Anchors

Read these first and keep them current during the 8-hour window:

1. [task.md](../../task.md)
2. [docs/status/collaborator_beta_preflight_latest.md](../status/collaborator_beta_preflight_latest.md)
3. [docs/status/codex_handoff_2026-04-15.md](../status/codex_handoff_2026-04-15.md)
4. [docs/status/phase726_go_nogo_2026-04-08.md](../status/phase726_go_nogo_2026-04-08.md)
5. [docs/plans/tonesoul_non_creator_external_cycle_preflight_refresh_pack_2026-04-15.md](tonesoul_non_creator_external_cycle_preflight_refresh_pack_2026-04-15.md)

Do not let older packs, older handoffs, or side plans silently outrank these.

---

## 2. Window Goal

By the end of this 8-hour window, the program should achieve one of two honest outcomes:

### Outcome A

- a third clean bounded `Phase 722` cycle is recorded across a third task shape
- current-truth surfaces are refreshed
- a refreshed `Phase 726` review is published

### Outcome B

- the third cycle does **not** land cleanly
- the blocking seam is named precisely
- current-truth surfaces and the next bounded repair step are refreshed honestly

Either outcome is acceptable.

Only pretending the evidence moved when it did not is unacceptable.

---

## 3. Guardrails

1. Do not widen public claims beyond guided collaborator beta.
2. Do not reopen ontology, domain-core, or 2.0 architecture as active implementation lanes.
3. Do not let runtime seam cleanup steal the window unless a failed `Phase 722` cycle proves it is the direct blocker.
4. Treat generated artifacts as generated artifacts; regenerate them through scripts rather than patching them by hand.
5. If a counted external-validation run stops being honest, classify it as partial or no-count immediately.

---

## 4. Time Blocks

## Block A: `0h-2h`

### Objective

Execute the third bounded `Phase 722` task shape using the preflight-refresh pack.

### Intended work

- run first-hop entry stack
- claim and preflight shared paths
- refresh `collaborator_beta_preflight_latest.{json,md}` through the script
- write one new `Phase 722` evidence note
- verify docs
- attempt official closeout

### Success condition

- one honest classification is recorded:
  - `strong external pass`, or
  - `useful partial`, or
  - `no-count`

### Failure condition

- the run drifts into manual artifact editing, runtime refactor, or uncontrolled scope growth

## Block B: `2h-4h`

### Objective

Refresh current-truth surfaces based on the actual `Phase 722` result.

### Intended work

- refresh latest preflight artifacts if the cycle changed them
- update `task.md` only if the cycle honestly counts as a third clean pass
- publish one fresh handoff/status note that says exactly what changed and what did not

### Success condition

- the next agent can continue from current surfaces without re-deriving the latest truth

## Block C: `4h-6h`

### Objective

Decide whether `Phase 726` can be refreshed now.

### Branching rule

- if Block A produced a clean third pass, publish a refreshed `Phase 726` review
- if Block A did not produce a clean third pass, publish a blocker note instead of pretending review conditions are met

### Success condition

- the repo has one honest current statement of where collaborator-beta readiness stands after this window

## Block D: `6h-8h`

### Objective

Use remaining time only on the shortest honest follow-through.

### If Block C refreshed `Phase 726`

- start `Phase 724` launch-operations surface consolidation
- keep it bounded to one current operations surface

### If Block C published a blocker note

- use the remaining window on the smallest direct seam that would unblock the next `Phase 722` rerun
- do not start unrelated cleanup

### Success condition

- the window ends with either:
  - one new launch-operations surface, or
  - one smaller repair target that is clearly next

---

## 5. Deliverables

Minimum expected outputs from the window:

- one `Phase 722` run result under the preflight-refresh pack
- refreshed current-truth surfaces
- one `Phase 726` refresh or one blocker note
- one end-of-window handoff

Stretch output:

- first bounded `Phase 724` launch-operations surface

---

## 6. Stop Conditions

Stop and narrow scope if any of these happen:

- the `Phase 722` run starts needing host/manual residue to look clean
- generated status artifacts require hand-edit rescue
- the work starts touching runtime modules unrelated to the launch evidence line
- `task.md` would need edits outside the already-bounded launch sections

---

## 7. Honest Read

This 8-hour program does **not** claim the evidence has already moved.

It claims only that the current shortest honest route is now:

1. try to land the third bounded `Phase 722` cycle
2. refresh current truth from the actual result
3. move into `Phase 726` only if the evidence now supports it
