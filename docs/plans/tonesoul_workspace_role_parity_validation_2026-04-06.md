# ToneSoul Workspace Role-Parity Validation (2026-04-06)

> Purpose: confirm that `apps/dashboard` and `apps/web` now expose clearly different roles after the tier-model landing.
> Authority: bounded validation note for `Phase 773`. This is a parity check, not a new UI redesign.

---

## Validation Goal

After `Phase 771` and `Phase 772`, ToneSoul now has:

- a public/demo tier cue in `apps/web`
- an operator shell plus Tier-2 drawer in `apps/dashboard`

The next risk is not missing features.
The next risk is:

`role drift`

That failure would look like:

- `apps/web` slowly re-growing into an operator console
- `apps/dashboard` flattening back into a mixed packet browser
- later agents no longer knowing which surface is authoritative for what

---

## Current Role Matrix

### apps/dashboard

Role:

- operator workspace
- CLI-adjacent shell
- bounded governance surface

Expected visible traits:

- `Tier 0 · Instant Gate`
- `Tier 1 · Orientation Shell`
- `Tier 2 · Deep Governance`
- explicit drawer pull for mutation / closeout / contested continuity

Must not drift into:

- raw packet browser
- generic status soup without tier hierarchy

### apps/web

Role:

- public/demo conversation surface
- educational explanation surface

Expected visible traits:

- `TierModelPublicCue`
- explanation of the tier model
- explicit routing toward dashboard workspace and CLI entry flow

Must not drift into:

- session-start runner
- live mutation preflight console
- publish/push or task-board operator surface

---

## What Was Validated

### Dashboard Parity

Validated:

- dashboard workspace still renders `Tier 0 / Tier 1 / Tier 2`
- dashboard uses session-start derived shells instead of inventing a separate operator story
- Tier-2 is still an explicit pull path, not a default packet dump

### Public/Demo Parity

Validated:

- `apps/web` uses a public tier cue instead of live runtime payloads
- docs page teaches the tier model
- public/demo surfaces route readers toward operator-truth surfaces instead of impersonating them

---

## Residual Gap

The biggest remaining workspace gap is now:

`dashboard status panel alignment`

Reason:

- the main workspace shell is tiered now
- public/demo cues are bounded now
- but `apps/dashboard/frontend/components/status_panel.py` still carries older mixed status storytelling and should be re-aligned to the tier model

That is a bounded next move.
It is not a reason to reopen a broad UI rewrite.

---

## Next Short Board Recommendation

Promote:

`Phase 774: Dashboard Status Panel Tier Alignment`

Focus:

- keep status panel subordinate to the operator shell
- reduce mixed authority storytelling
- align its copy and grouping with Tier 0 / Tier 1 / Tier 2 instead of legacy generic status language

---

## Success Condition

This phase succeeds when:

1. dashboard remains the operator shell
2. `apps/web` remains public/demo and educational
3. both surfaces point back to the same CLI/runtime truth instead of inventing competing control planes
