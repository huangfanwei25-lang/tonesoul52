# ToneSoul Deep-Governance Drawer Budget (2026-04-06)

> Purpose: define the first bounded Tier-2 drawer budget for the dashboard operator shell so deep governance remains available without becoming the default workspace load.
> Authority: completed short-board budget. It is a frontend translation rule, not a runtime permission change.

---

## Design Rule

Tier 2 is not "everything else."

Tier 2 exists for:

- contested mutation
- blocked continuation
- closeout ambiguity
- publish / task-board / shared-edit risk

If the drawer opens like a packet browser, the operator shell loses its point.

---

## Default Drawer Groups

The first drawer pass should expose only these groups:

### Group A: Mutation And Closeout

Show by default when present:

- `closeout_attention`
- compact `mutation_preflight`
- `run_shared_edit_preflight` result
- `publish_push_preflight`
- `task_board_preflight`

Why first:
- these surfaces change what the operator may safely do next

### Group B: Contested Continuity

Show by default only when a trigger exists:

- compaction `receiver_obligation`
- compaction `closeout_status`
- council realism caution
- subject snapshot / working-style non-promotion warning

Why second:
- these surfaces prevent over-promotion and over-reading

---

## Explicit Pull Only

These surfaces must never open by default in the first drawer pass:

- full `packet`
- full `import_posture`
- full `observer_window`
- full council dossier tables
- full `working_style_playbook`
- raw claim lists

These remain:

`deep pull only`

because they are too authority-mixed and too dense for default drawer load.

---

## Trigger Matrix

Open the drawer automatically only when at least one of these is true:

- `readiness != pass`
- `claim_conflict_count > 0`
- `closeout_attention.present == true`
- shared-edit preflight result is not `clear`
- publish/push posture is not `clear`
- task-board preflight is not `clear`

Do not auto-open for:

- bounded local quick-change work
- clean feature-track work with `readiness=pass`
- descriptive curiosity

---

## Card Budget

First drawer pass should cap itself to:

- at most `2` group sections
- at most `5` visible cards before expansion
- no raw JSON blocks in the default view

This keeps Tier 2 as escalation, not a second dashboard home screen.

---

## Card Order

When the drawer opens, use this priority:

1. mutation / closeout blockers
2. contested continuity warnings
3. optional deeper links

Never reverse this order.

The operator must see:

`what blocks the next move`

before:

`what would be interesting to inspect`

---

## Dashboard Translation Rule

For `apps/dashboard/frontend/pages/workspace.py`:

- keep Tier 0 and Tier 1 in the main shell
- place Tier 2 behind one explicit "deep governance" trigger
- let the trigger show:
  - `why it opened`
  - `which group is active`
  - `which deeper pull is available next`

Do not embed raw packet tables beside the chat feed.

---

## Non-Goals

This budget does not:

- change runtime semantics
- reclassify authority
- make `apps/web` an operator console
- require full dossier visualization in the first dashboard pass

---

## Bounded Next Move

The next safe phase is:

`Phase 771: Public / Demo Surface Alignment`

That phase should answer:

- what, if anything, from the tier model belongs in `apps/web`
- what must stay dashboard-only
- how to avoid teaching the public/demo site to impersonate the operator shell
