# ToneSoul Workspace Frontend Readiness Map (2026-04-06)

> Purpose: classify which current ToneSoul runtime surfaces are ready for direct UI rendering, which need a view-model adapter, and which must stay behind deeper pull.
> Authority: completed short-board mapping artifact. It is a translation aid for frontend work, not a runtime contract.

---

## Result

The workspace should be built against a four-way render classification:

- `render_direct`
- `adapter_needed`
- `deep_pull_only`
- `defer`

This keeps frontend work from turning runtime truth into one undifferentiated panel wall.

---

## Tier 0 Readiness Map

| Surface | Runtime Source | Classification | Why |
|---|---|---|---|
| `readiness` | `start_agent_session --tier 0` | `render_direct` | already compact, machine-readable, and action-driving |
| `task_track_hint` | `start_agent_session --tier 0` | `render_direct` | bounded classification with clear operator value |
| `deliberation_mode_hint` | `start_agent_session --tier 0` | `render_direct` | already successor-facing and advisory |
| compact `canonical_center` | `start_agent_session --tier 0` | `adapter_needed` | source is strong, but UI needs card-level splits for short board vs successor correction |
| `hook_chain` | `start_agent_session --tier 0` | `render_direct` | already a packaging/readiness surface |
| compact `mutation_preflight` | `start_agent_session --tier 0` | `adapter_needed` | structurally usable, but UI should render state + next command separately |
| `next_pull` | `start_agent_session --tier 0` | `render_direct` | exactly the kind of panel CTA a workspace needs |

Tier-0 rule:

`If it cannot help answer "can I safely start and what is the first bounded move?", it does not belong in Tier 0.`

---

## Tier 1 Readiness Map

| Surface | Runtime Source | Classification | Why |
|---|---|---|---|
| full `canonical_center` | `start_agent_session --tier 1` | `adapter_needed` | should become 2-3 cards, not one prose blob |
| `subsystem_parity` | `start_agent_session --tier 1` | `adapter_needed` | current structure is strong but wants badge + gap-card rendering |
| `closeout_attention` | `start_agent_session --tier 1` | `render_direct` | high-priority successor warning; should stay visually sharp |
| `observer_shell` | `start_agent_session --tier 1` | `adapter_needed` | needs grouping into stable / contested / stale shell headlines |
| `hook_chain` | `start_agent_session --tier 1` | `render_direct` | already a bounded operator support surface |
| compact `mutation_preflight` | `start_agent_session --tier 1` | `adapter_needed` | same reason as Tier 0, with more context available |
| `readiness / track / deliberation` | `start_agent_session --tier 1` | `render_direct` | should persist as top-row orientation chips |

Tier-1 rule:

`If the surface helps orient bounded work without requiring full receiver archaeology, it belongs in Tier 1.`

---

## Tier 2 Readiness Map

| Surface | Runtime Source | Classification | Why |
|---|---|---|---|
| full `packet` | packet / full session-start | `deep_pull_only` | too large and too authority-mixed for default rendering |
| full `import_posture` | full session-start | `deep_pull_only` | useful only for contested import / promotion review |
| full `observer_window` | observer window runner | `deep_pull_only` | important, but only after Tier-1 shell says deeper review is warranted |
| council dossier interpretation | full session-start / packet | `deep_pull_only` | must stay behind deeper governance to avoid over-reading |
| `working_style_playbook` | full session-start | `adapter_needed` | renderable, but only in a bounded drawer and with non-identity labels |
| `working_style_validation` | full session-start | `render_direct` | compact enough for a caution/insufficient/sufficient chip inside Tier 2 |
| `publish_push_preflight` | explicit pull | `render_direct` | should become an action guard card |
| `task_board_preflight` | explicit pull | `render_direct` | same |
| `run_shared_edit_preflight` output | explicit pull | `render_direct` | exact preflight panel candidate |

Tier-2 rule:

`If a surface changes how a successor may mutate, publish, promote, or interpret contested continuity, it belongs in Tier 2.`

---

## Repo UI Target Map

### `apps/dashboard`

Current status:
- best operator-workspace candidate
- already has `workspace.py`, `status_panel.py`, and `memory_panel.py`

Readiness:
- `Tier 0`: `adapter_needed`
- `Tier 1`: `adapter_needed`
- `Tier 2`: mixed; render direct for selected preflight cards, deep pull only for packet/import posture

Why:
- layout is already operator-facing
- currently mixes chat, status, council, and memory without a tier model

### `apps/web`

Current status:
- public/demo conversational surface
- built around `ChatInterface` + `TensionTimeline`

Readiness:
- `Tier 0`: `defer`
- `Tier 1`: `defer`
- `Tier 2`: `defer`, except future bounded educational views

Why:
- wrong default audience for operator workspace
- should not become the canonical multi-agent control surface first

### `apps/council-playground`

Current status:
- specialized council surface

Readiness:
- `Tier 0`: `defer`
- `Tier 1`: `defer`
- `Tier 2`: `render_direct` as a deep-governance auxiliary only

Why:
- good for drilldown
- wrong for first-hop orientation

---

## First Implementation Recommendation

Start in:

`apps/dashboard/frontend/pages/workspace.py`

with this bounded translation:

1. replace the generic top summary area with a `Tier 0` start strip
2. introduce one `Tier 1` orientation panel
3. keep council and memory as secondary panes, not the orientation center
4. add one explicit "pull deeper governance" drawer trigger instead of opening everything by default

---

## What Needs Adapter Work First

These surfaces should not be rendered raw:

- `canonical_center`
- `subsystem_parity`
- `observer_shell`
- compact `mutation_preflight`
- `working_style_playbook`

They need a view-model layer because their current JSON shape is correct for machine continuity, not yet ideal for visual hierarchy.

---

## What Should Stay Out Of The First Workspace Pass

- raw packet dumps
- full observer prose
- full import-posture tables
- long continuity narratives
- public/demo-facing chat UI redesign

These are too costly for the first workspace pass and would reintroduce the monolithic-dashboard problem.

---

## Bounded Next Move

The next safe phase is:

`Phase 768: Workspace View-Model Adapter Contract`

That phase should define:

- the adapter shape for `canonical_center`
- the adapter shape for `subsystem_parity`
- the adapter shape for `observer_shell`
- the operator-card shape for compact `mutation_preflight`
