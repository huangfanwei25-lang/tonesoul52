# ToneSoul Operator Walkthrough Pack (2026-04-06)

> Purpose: teach first-hop operator behavior in the dashboard without duplicating CLI/runtime truth or turning `apps/web` into a second control plane.
> Authority: bounded dashboard/operator aid. Runtime truth remains in session-start, observer, packet, and preflight surfaces.

---

## Why This Exists

After the tier model landed, ToneSoul gained:

- `Tier 0 · Instant Gate`
- `Tier 1 · Orientation Shell`
- `Tier 2 · Deep Governance`

That made the workspace clearer.
It also created one new risk:

`a fresh operator can now see the tiers, but still not know when to stop pulling deeper.`

This walkthrough exists to solve that exact problem.

It is not a second runtime.
It is a compact explanation layer that sits under the operator shell.

---

## Design Rule

The walkthrough must teach:

- when `Tier 0` is enough
- when `Tier 1` is justified
- when `Tier 2` is worth opening

It must not:

- restate raw packet JSON
- create new authority labels
- compete with CLI entry or dashboard operator truth

---

## Scenario Pack

### 1. Quick Bounded Change

Default tier:

`Tier 0`

Use when:

- readiness is already pass
- one bounded next move is visible
- the task does not require short-board archaeology or contested continuity review

Escalate only when:

- the next move no longer fits the task
- subsystem context becomes necessary
- the current bounded move may touch broader shared surfaces

### 2. Feature Continuation

Default tier:

`Tier 1`

Use when:

- the short board matters
- parity gaps matter
- closeout interpretation matters before acting

Escalate only when:

- closeout attention is present
- contested continuity changes what can be safely done
- mutation or publish posture becomes active

### 3. Contested Or Risky Work

Default tier:

`Tier 2`

Use when:

- mutation, closeout, publish/push, or contested continuity now materially changes what may happen next

Stay bounded:

- open Tier 2 deliberately
- review only the active trigger group first
- close it again when the trigger is resolved

---

## Public Boundary

This pack belongs to:

- `apps/dashboard`
- operator-facing onboarding

It does not belong to:

- `apps/web` as live operator truth
- public/demo surfaces as a hidden control panel

Public/demo surfaces may explain the tier model.
They must not pretend to run this walkthrough as an operator console.

---

## Outcome

This pack succeeds if:

1. later agents stop over-pulling deep governance by default
2. humans can see the smallest honest tier to use next
3. dashboard stays the operator shell
4. `apps/web` stays educational/demo-first
