# ToneSoul Tiered Agent Workspace Spec (2026-04-02)

> Purpose: define a ToneSoul-native workspace / IDE surface model that presents Tier 0, Tier 1, and Tier 2 as distinct pull layers instead of one flat dashboard.
> Authority: accepted short-board spec. It describes UI-ready panel boundaries, but it does not outrank runtime code, tests, `task.md`, or canonical architecture contracts.

---

## Problem

ToneSoul now has enough machine-readable surfaces that a future agent UI could easily become worse instead of better.

The failure mode is obvious:

- put every surface on one screen
- mix `canonical`, `advisory`, `descriptive`, and `preflight` signals together
- let a later agent read observer prose as execution permission
- let a smooth compaction summary look like completed work

That would make the interface prettier while making successor behavior less safe.

The workspace must therefore follow the same rule as the runtime:

`tiered pull, not monolithic push`

---

## Design Claim

The workspace should not be "an admin dashboard for everything ToneSoul knows."

It should be:

1. a `Tier 0` start panel for instant safe orientation
2. a `Tier 1` orientation shell for bounded continuation
3. a `Tier 2` deep-governance drawer for contested, risky, or system-track work

The UI succeeds when a successor can:

- start quickly on bounded work
- escalate only when needed
- see why escalation happened
- avoid mistaking advisory and descriptive surfaces for authority

---

## Panel Model

### Tier 0: Instant Gate

Purpose:
- answer whether work may safely begin
- expose the first bounded move
- avoid loading the full governance story

Must show:
- `readiness`
- `task_track_hint`
- `deliberation_mode_hint`
- compact `canonical_center`
- `hook_chain`
- compact `mutation_preflight`
- `next_pull`

Must not show by default:
- full `packet`
- full `observer_window`
- full `import_posture`
- `working_style_playbook`
- `working_style_validation`
- `claim_view`
- dossier detail

UI role:
- start panel
- first decision box
- "can I act now?" surface

Operator action types:
- start bounded local work
- run one preflight command
- pull Tier 1
- stop and clarify

### Tier 1: Orientation Shell

Purpose:
- provide enough stable orientation for feature-track continuation
- reveal the shortest-board shape without opening the whole stack

Must show:
- `canonical_center`
- `subsystem_parity`
- `closeout_attention`
- `observer_shell`
- `hook_chain`
- compact `mutation_preflight`
- `readiness`
- `task_track_hint`
- `deliberation_mode_hint`

May summarize but not fully expand:
- low-drift anchor status
- hot-memory ladder
- repo-state awareness
- stable / contested / stale headlines

Must still avoid by default:
- full `packet`
- full `import_posture`
- raw claim lists
- full council dossier interpretation tables
- long continuity prose

UI role:
- orientation workspace
- bounded continuation shell
- "what is stable enough to act on?" surface

Operator action types:
- choose the next bounded move
- decide whether to escalate
- open one deep drawer when the shell shows contest or blockage

### Tier 2: Deep Governance

Purpose:
- expose the full receiver / continuity / council story only when the task has earned the cost

Can show:
- full `packet`
- full `observer_window`
- full `import_posture`
- full `mutation_preflight`
- `publish_push_preflight`
- `task_board_preflight`
- council realism and dossier interpretation
- hot-memory ladder / decay detail
- working-style playbook and validation

Must be pulled only when:
- `readiness != pass`
- claim overlap exists
- closeout is `partial`, `blocked`, or `underdetermined`
- system-track work is active
- council realism meaningfully affects the next move
- publish / task-board / shared-path mutation is in scope

UI role:
- deep-governance drawer
- escalation console
- continuity and council drilldown

Operator action types:
- review contested surfaces
- perform guarded mutation
- decide whether human input is required
- open a deeper audit trail before risky outward action

---

## Required UI Labels

Every surfaced item should carry one of these labels:

- `canonical`
- `operational`
- `advisory`
- `descriptive`
- `preflight`

Why:
- `canonical` means design/load-bearing truth
- `operational` means current executable entry guidance
- `advisory` means useful but not promotable
- `descriptive` means observed/read out, not accuracy-backed
- `preflight` means mutation or outward action boundary

Without these labels, the workspace will silently collapse meanings.

---

## Panel Boundaries That Must Not Collapse

### Boundary 1: Summary Is Not Completion

Do not render a compaction summary card in a way that visually outranks:
- `closeout_attention`
- `closeout.status`
- `stop_reason`
- `unresolved_items`

If those disagree, the closeout surface wins.

### Boundary 2: Stable Is Not Verified

`observer_window.stable` means:
- unchallenged enough to orient from

It does not mean:
- tested
- canonical
- historically calibrated

The UI must not use "stable" as a green proof badge.

### Boundary 3: Working Style Is Not Identity

`working_style_playbook` and `working_style_validation` help a successor work consistently.
They must not be displayed as:
- who the system truly is
- durable selfhood
- permission to promote style into vows or task scope

### Boundary 4: Council Agreement Is Not Accuracy

Any council card showing:
- `coherence`
- `confidence_posture`
- `agreement_score`
- `descriptive_only`

must visually preserve the distinction between:
- descriptive deliberation state
- calibrated correctness

### Boundary 5: Preflight Is Not Governance Truth

`shared_edit_preflight`, `publish_push_preflight`, and `task_board_preflight` should be shown as action guards, not as constitutional law.

They gate the next move.
They do not redefine the architecture.

---

## Escalation Logic For The Workspace

The workspace should not open deeper panels just because more data exists.

Escalate from Tier 0 -> Tier 1 when:
- bounded work is no longer locally obvious
- feature-track continuation needs stable orientation
- mutation hints indicate likely coordination cost

Escalate from Tier 1 -> Tier 2 when:
- the shell shows contested or blocked state
- closeout attention is present
- claim collision exists
- system-track work is active
- a successor is about to perform shared mutation or outward action

Do not auto-open Tier 2 for:
- ordinary quick-change work
- bounded feature work with `readiness=pass`
- descriptive curiosity

---

## Suggested Workspace Layout

This is a panel model, not a visual mandate.

Recommended structure:

1. left rail
   - agent id
   - tier selector
   - readiness chip
   - track / deliberation hint

2. main panel
   - Tier 0 or Tier 1 surface
   - only one active orientation story at a time

3. right drawer
   - escalation / preflight / deep-governance pulls
   - closed by default

4. footer or utility strip
   - executable commands
   - observer / diagnose / packet pull actions

The critical point is not layout style.
It is that the workspace must preserve pull discipline.

---

## Frontend / IDE Translation Rules

If a future frontend is built:

- start from Tier 0 as the default load
- let Tier 1 be one explicit expansion
- make Tier 2 opt-in and visibly "expensive"
- keep command parity visible so the UI never becomes the only way to act
- do not hide the CLI-equivalent pull path

This matters because ToneSoul currently remains:
- CLI-first
- file-backed by default
- governance-bounded

The UI should package that, not replace it with dashboard theater.

---

## Non-Goals

This spec does not:
- redesign the existing web app
- require a dashboard rewrite
- force all current surfaces into one new schema
- claim a frontend is now the shortest board
- authorize runtime changes just because the UI would look cleaner

---

## Bounded Next Move

The next safe phase after this spec is:

`Frontend readiness mapping, not full UI implementation`

That means:
- identify which current surfaces are already panel-ready
- identify which still need a view-model adapter
- keep the next step spec-first unless the frontend truly becomes the shortest board
