# ToneSoul Sixth Trial Candidate Admission (2026-04-07)

> Purpose: admit one sixth bounded self-improvement candidate after the fifth trial result is registered.
> Status: admitted candidate note for `Phase 811`.
> Authority: planning aid. Runtime truth remains in code, tests, accepted contracts, and the current bounded trial/result surfaces.

---

## Why This Exists

ToneSoul now has:

- one promoted consumer-parity packaging result
- one parked operator-retrieval cueing result
- one promoted deliberation-hint packaging result
- one promoted task-board parking clarity result
- one promoted shared-edit overlap clarity result
- one promoted publish/push posture clarity result

That means the next bottleneck is no longer:

- whether individual hooks can be packaged more clearly
- whether self-improvement can promote bounded hook/readout refinements honestly

It is:

`how should successors decide which existing bounded hook to run first, without turning helpers into a new authority system?`

---

## Admission Rule

The sixth candidate must satisfy all of these:

- stay inside `allowed_now` mutation classes
- reduce a live successor-routing friction already visible in this repo
- preserve consumer parity across Codex-style, Claude-style, dashboard, and observer-facing shells
- keep rollback posture explicit
- avoid inventing a new permission layer, new hook family, or hidden planner

If it cannot satisfy those, it does not enter the sixth wave.

---

## Chosen Candidate

### `candidate_id`

`mutation_followup_routing_v1`

### `target_surface`

`mutation_preflight.next_followup`

### `target_consumer`

`codex_cli / claude_adapter / dashboard_operator_shell / observer_window`

---

## Why This Candidate

This is the best sixth candidate because it sits at the exact friction point where later agents still risk:

- being pointed to task-board parking even when the real shortest lane is shared-edit overlap
- missing publish/push review as the next bounded action because `next_followup` is static
- reading `mutation_preflight` as if it were a flat checklist rather than a routing shell

It is also firmly inside an already-allowed mutation class:

- packaging and bounded routing readouts

And it avoids the parked temptations:

- no new hook family
- no governance rewrite
- no identity or transport changes

---

## Baseline Story

ToneSoul already has:

- `shared_edit_path_overlap`
- `publish_push_posture`
- `task_board_parking`
- `mutation_preflight.next_followup`

That is already useful.

But one remaining friction is still visible:

`later agents can still receive a static next-followup target even when the current bounded friction is clearly elsewhere.`

That ambiguity does not break the system, but it taxes continuation speed and makes the shell look less honest than it already is.

---

## Candidate Story

The candidate is:

- not a new hook chain
- not a planner
- not a permission system
- not a release or task-board authority upgrade

It is only a packaging refinement of:

- `mutation_preflight.next_followup`

The likely direction is:

- route to `shared_edit_path_overlap` when shared-code pressure is current
- route to `publish_push_posture` when outward-action review is current
- route to `task_board_parking` only when board routing is actually the shortest friction

This keeps the candidate narrow and testable.

---

## Proposed Success Metric

The sixth-wave evaluator should judge this candidate using:

1. regression:
   - `tests/test_mutation_preflight.py`
   - `tests/test_start_agent_session.py`
   - `tests/test_subsystem_parity.py`

2. parity:
   - the new routing remains understandable from Codex-style, Claude-style, dashboard, and observer-facing shells
   - the self-improvement drift wave still stays aligned

3. operability:
   - a later agent can tell which bounded hook is actually next
   - without opening a second prose explanation

4. honesty:
   - the result must not imply that `mutation_preflight` became a permission engine

---

## Failure Watch

The main failure watches are:

- dynamic routing that feels smarter but actually hides authority boundaries
- one shell following the new routing while another still surfaces stale targets
- overfitting to one scenario and regressing another
- adding dynamic movement without reducing actual ambiguity

If these dominate, the sixth wave should end in:

- `park`
- or `retire`

not `promote`.

---

## Rollback Posture

`bounded_restore`

If the trial fails:

- restore the prior static `next_followup`
- keep the result surface as history only
- do not reinterpret the failure as evidence that bounded hooks were a bad idea

---

## Overclaim To Avoid

`better mutation follow-up routing is not better governance`

This candidate, even if promoted, does **not** prove:

- stronger permissions
- better planning quality
- better launch maturity
- broader safe autonomy

It would only prove:

- clearer bounded routing between existing hooks

---

## No-Go List For Wave 6

These should **not** enter the sixth wave:

1. any new hook family
   - outside the current mutation boundary

2. any hidden planner or adaptive orchestration layer
   - too broad for v0

3. governance, identity, vow, or transport changes
   - outside allowed mutation classes

4. retrieval-runtime or compiled-knowledge optimism
   - still parked

5. shell redesign framed as "follow-up routing"
   - too broad for the current phase

---

## Recommended Next Phase

Open:

- `Phase 812: Sixth Bounded Trial Wave - Mutation Follow-Up Routing`

Do **not** open:

- new hook invention
- permission mythology
- planner mythology
