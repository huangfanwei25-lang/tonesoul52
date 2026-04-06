# ToneSoul Public / Demo Surface Alignment (2026-04-06)

> Purpose: decide what part of the tier model belongs in `apps/web` without turning the public/demo site into a second operator console.
> Authority: bounded execution plan for `Phase 771`. Runtime/operator truth still lives in CLI, dashboard workspace, and accepted contracts.

---

## Decision

`apps/web` may expose:

- educational explanation of `Tier 0 / Tier 1 / Tier 2`
- explicit routing that says the operator shell lives in dashboard workspace and CLI entry
- bounded copy that prevents public/demo readers from confusing summaries with operator authority

`apps/web` may not expose:

- live session-start bundles
- raw `packet`, `import_posture`, `claim_view`, or `observer_window` payloads
- mutation, publish/push, or task-board preflight results
- full council dossier or deep-governance drawer content

This keeps `apps/web` demo-first and explanation-first.
It does not turn it into the canonical operator console.

---

## Why This Is The Right Boundary

ToneSoul now has a real tier model:

- `Tier 0` = instant gate
- `Tier 1` = orientation shell
- `Tier 2` = deep governance pull

If `apps/web` renders live operator surfaces directly, three failure modes appear immediately:

1. public/demo UI starts competing with dashboard workspace
2. descriptive surfaces start looking like permissions or verified truth
3. response latency goes up because the public surface now pulls operator-grade state

So the correct public move is:

`teach the tier model`

not:

`embed the operator shell`

---

## Allowed Public Render Pattern

### Home / App Surface

Allowed:

- one compact cue that says this page is demo-first
- one short explanation that `Tier 0 / 1 / 2` exist
- one link to the docs explanation

Not allowed:

- live orientation cards
- subsystem parity counts
- closeout attention cards
- hook-chain/preflight results

### Docs Surface

Allowed:

- one full explanatory section for `Tier 0 / 1 / 2`
- one clear rule that dashboard workspace and CLI remain operator-truth surfaces
- one explanation of why `Tier 2` is explicit pull only

Not allowed:

- live runtime JSON
- current claim or readiness state
- any copy that implies `/docs` is the operator dashboard

---

## Concrete Implementation Shape

### Public Cue Component

Use one shared component for `apps/web`:

- `compact` variant for `app/page.tsx`
- `full` variant for `app/docs/page.tsx`

Shared invariant:

`This surface explains the tier model but does not execute or reveal live operator state.`

### Copy Discipline

Must say:

- `demo-first`
- `operator shell lives in dashboard workspace and CLI`
- `deep governance is explicit pull only`

Must avoid:

- `verified`
- `authoritative control center`
- `live operator console`

---

## Follow-On Short Board

After this phase lands, the next workspace bucket should be:

`Dashboard Deep-Governance Drawer Implementation`

Reason:

- the public/demo boundary will be clear
- the next real value is not more public copy
- the next real value is turning the already-defined Tier-2 drawer budget into a bounded dashboard pull path

---

## Success Condition

This phase succeeds when:

1. `apps/web` teaches the tier model without pretending to be the operator console
2. public readers are routed toward docs/CLI/dashboard instead of mistaking demo UI for governance truth
3. no live operator payload is added to `apps/web`
