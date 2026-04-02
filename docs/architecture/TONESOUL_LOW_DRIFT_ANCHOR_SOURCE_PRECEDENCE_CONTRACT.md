# ToneSoul Low-Drift Anchor Source Precedence Contract

> Purpose: define the one source-order story that later agents should use when reading low-drift anchor, canonical center, and observer-window surfaces.
> Last Updated: 2026-04-02
> Authority: successor-orientation boundary aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.

---

## Why This Exists

ToneSoul already exposes several successor-facing shells:

- `session-start`
- `canonical_center`
- `observer_window`
- `hot_memory_ladder`
- `subsystem_parity`

What causes confusion is not the absence of signals.
It is reading those signals in the wrong order.

This contract exists to keep one bounded rule visible:

`child summaries do not outrank parent truth`

---

## The Current Runtime-Aligned Precedence

Later agents should read low-drift anchor inputs in this order:

| Layer | Surfaces | Receiver Meaning |
|---|---|---|
| `canonical_anchors` | `AXIOMS.json`, `DESIGN.md`, canonical architecture contracts, accepted `task.md` short board | highest parent truth |
| `live_coordination_truth` | packet `posture`, `launch_claim_posture`, `coordination_mode`, `readiness` | authoritative for the current session |
| `derived_orientation_shells` | `session_start.import_posture`, `canonical_center`, `observer_window`, `hot_memory_ladder`, `subsystem_parity` | advisory children derived from parent surfaces |
| `bounded_handoff` | `compactions`, `checkpoints`, `delta_feed`, `recent_traces` | resumability and review only; never self-promote |
| `working_identity_and_replay` | `subject_snapshot`, `working_style_anchor`, `working_style_playbook`, `council_dossier` | context only, not authority |

In compressed form:

`canonical_anchors > live_coordination_truth > derived_orientation_shells > bounded_handoff > working_identity_and_replay`

---

## What Changed From The Sidecar Draft

The earlier sidecar draft mixed two different viewpoints:

1. upstream raw sources such as `governance_state.json` and runtime mutation code
2. successor-facing repo-native readouts that agents actually consume first

That was too wide for current runtime truth.

The corrected contract keeps the successor-facing order explicit while still respecting that:

- `AXIOMS.json` is constitutional
- runtime code and tests outrank documentation
- packet/session-start surfaces are derived from deeper state, not equal to it

---

## Anchor Eligibility

### Eligible For Low-Drift Anchor

- canonical anchor facts that remain current
- current launch truth
- current coordination mode
- current readiness / claim posture

### Not Eligible For Low-Drift Anchor

- compaction summaries
- checkpoints
- subject snapshot identity language
- working-style habits
- council agreement metrics

Those surfaces can still help a successor continue work.
They just do not belong in the anchor center itself.

---

## Core Receiver Rules

1. `AXIOMS.json` and canonical design/contract surfaces outrank every advisory shell.
2. Current session posture/readiness outrank observer phrasing.
3. Observer-window `stable` means `currently unchallenged`, not `verified forever`.
4. Compaction can orient resumability, but incomplete closeout or promotion hazards keep it below anchor level.
5. Working style may shape workflow, but it must never become permission, scope, or identity law.

---

## Most Dangerous Misread

The highest-friction misread remains:

`observer stable -> execution permission`

Corrective rule:

- before shared edits, re-check live coordination directly:
  - `readiness.status`
  - `claim_view.claims`
  - `mutation_preflight`
  - `shared_edit_preflight` when paths are known

---

## Runtime Reflection

Current runtime now reflects this contract in bounded form through:

- `canonical_center.canonical_anchor_references`
- `canonical_center.source_precedence`
- `canonical_center.source_precedence_summary`
- `hot_memory_ladder`
- `observer_window`

This keeps the precedence story machine-readable without promoting observer prose into sovereignty.

---

## What Stays Out

This contract does not authorize:

- direct mutation of runtime behavior by documentation alone
- automatic promotion of handoff or identity surfaces
- replacement of tests with prose
- a second competing precedence ladder in sidecar notes

If a future document proposes a different source order, it must either:

1. align to this contract and current runtime readout, or
2. stay outside the active authority lane until reality-checked
