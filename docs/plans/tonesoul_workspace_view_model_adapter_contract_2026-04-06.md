# ToneSoul Workspace View-Model Adapter Contract (2026-04-06)

> Purpose: define the bounded adapter shapes that a future workspace should use for Tier 0 and Tier 1 rendering, instead of binding UI components directly to raw runtime JSON.
> Authority: completed short-board contract candidate. It is implementation guidance for the workspace lane, not canonical runtime truth.

---

## Design Rule

The frontend should not consume raw runtime JSON as if it were already a visual model.

Runtime surfaces are optimized for:

- machine continuity
- successor safety
- bounded receiver posture

The workspace needs a second layer:

`runtime surface -> view-model adapter -> panel component`

Without that layer, the UI will recreate hierarchy ad hoc and eventually collapse boundaries.

---

## Adapter Families

### 1. Tier-0 Start Strip Adapter

Input:
- `readiness`
- `task_track_hint`
- `deliberation_mode_hint`
- `hook_chain`
- compact `mutation_preflight`

Output shape:

```json
{
  "readiness_chip": { "status": "pass", "summary": "..." },
  "track_chip": { "track": "feature_track", "depth": "bounded" },
  "deliberation_chip": { "mode": "lightweight_review", "why": "..." },
  "hook_badges": [
    { "name": "shared_edit_path_overlap", "status": "active" }
  ],
  "next_action_card": {
    "summary": "...",
    "command": "python ...",
    "receiver_rule": "..."
  }
}
```

Why:
- Tier 0 should feel like a start strip, not a JSON tree

Must not include:
- prose from observer window
- raw source lists
- packet detail

### 2. Canonical-Center Card Adapter

Input:
- compact or full `canonical_center`

Output shape:

```json
{
  "short_board_card": {
    "summary": "...",
    "present": true
  },
  "successor_correction_card": {
    "summary": "...",
    "risk": "observer_stable_is_execution_permission"
  },
  "precedence_card": {
    "summary": "...",
    "top_order": [
      "canonical_anchors",
      "live_coordination_truth",
      "derived_orientation_shells"
    ]
  }
}
```

Why:
- `canonical_center` is semantically strong, but visually too dense as a single block

Must not do:
- treat source precedence as a decorative tooltip
- hide successor correction under expansion-only UX

### 3. Subsystem-Parity Card Adapter

Input:
- `subsystem_parity`

Output shape:

```json
{
  "counts": {
    "baseline": 0,
    "beta_usable": 0,
    "partial": 0,
    "deferred": 0
  },
  "family_cards": [
    {
      "name": "session_start_bundle",
      "status": "baseline",
      "current_signal": "...",
      "main_gap": "...",
      "next_move": "...",
      "overclaim_to_avoid": "..."
    }
  ]
}
```

Why:
- parity is already one of the strongest successor-facing readouts
- the UI only needs card grouping and status normalization, not new semantics

Must not do:
- merge `main_gap` and `overclaim_to_avoid`
- reduce every status to green/yellow/red without keeping the original maturity class

### 4. Observer-Shell Card Adapter

Input:
- `observer_shell`

Output shape:

```json
{
  "summary_card": { "summary": "...", "receiver_note": "..." },
  "count_strip": { "stable": 0, "contested": 0, "stale": 0 },
  "headline_groups": {
    "stable": ["..."],
    "contested": ["..."],
    "stale": ["..."]
  },
  "repo_state_card": {
    "classification": "...",
    "summary": "...",
    "misread_risk": true
  },
  "hot_memory_card": {
    "summary": "...",
    "layers": [
      { "layer": "canonical_center", "status": "operational" }
    ]
  }
}
```

Why:
- Tier 1 needs the observer shell as grouped orientation, not as raw nested JSON

Must not do:
- visually promote stable headlines above `closeout_attention`
- drop `misread_risk`

### 5. Mutation-Preflight Action Card Adapter

Input:
- compact `mutation_preflight`

Output shape:

```json
{
  "summary_card": {
    "summary": "...",
    "receiver_rule": "..."
  },
  "context_card": {
    "readiness_status": "pass",
    "task_track": "feature_track",
    "deliberation_mode": "lightweight_review",
    "claim_conflict_count": 0
  },
  "followup_card": {
    "target": "task_board.parking_preflight",
    "classification": "existing_runtime_hook",
    "command": "python ...",
    "reason": "..."
  }
}
```

Why:
- the raw shape is already bounded
- the UI just needs operator-card separation

Must not do:
- turn `followup_card` into a hidden secondary action
- drop `claim_conflict_count`

---

## Shared View-Model Rules

All adapter output should preserve:

- `label_class`
  - `canonical`
  - `operational`
  - `advisory`
  - `descriptive`
  - `preflight`
- `panel_tier`
  - `0`
  - `1`
  - `2`
- `raw_source`
  - source runtime surface name

This allows the frontend to:
- style safely
- sort correctly
- keep traceability

without inventing new semantics.

---

## What The Adapter Must Not Do

- infer new permissions
- convert descriptive readouts into correctness signals
- collapse closeout and summary into one card
- merge canonical and advisory items into one generic "important" card
- hide the CLI-equivalent command path

The adapter is a translation layer, not a policy layer.

---

## First Implementation Target

Use this contract first in:

`apps/dashboard/frontend/pages/workspace.py`

Why:
- already operator-oriented
- already has side panels and workspace structure
- lower risk than rewriting `apps/web`

---

## Bounded Next Move

The next safe phase is:

`Phase 769: Dashboard Operator Shell Adoption`

That phase should:

1. add a Tier-0 start strip
2. add a Tier-1 orientation region
3. keep council and memory as secondary panes
4. leave Tier-2 as an explicit pull, not default layout
