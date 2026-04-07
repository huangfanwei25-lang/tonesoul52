# ToneSoul Cross-Agent Memory Consumer Contract

> Purpose: keep Codex-style shells, Claude-style shells, and dashboard/operator surfaces aligned on how they read shared ToneSoul memory surfaces.
> Last Updated: 2026-04-07
> Authority: bounded interpretation contract. Does not outrank runtime code, canonical anchors, tests, or human-managed launch truth.

---

## Why This Exists

ToneSoul already has enough shared surfaces to move state across sessions:

- session-start bundle
- observer window
- packet
- closeout grammar
- mutation preflight

What still drifts is how different shells interpret them.

The problem is not only transport.
It is consumer parity:

- one shell starts from smooth summaries
- another starts from packet detail
- another over-trusts observer `stable`
- another skips closeout and misreads compaction as completion

This contract exists so different agent shells can render different panes without inventing different first-hop truth.

## Compressed Thesis

Cross-agent memory interop should preserve:

- the same first-hop read order
- the same parent/child authority ordering
- the same anti-fake-completion rule
- the same mutation caution

It should not assume:

- hidden shared cognition
- first-party cross-vendor memory fusion
- shell-specific authority inflation

## Compatible Consumers

The current bounded consumer set is:

- `codex_cli`
- `claude_style_shell`
- `dashboard_operator_shell`

This is a rendering/interpreter contract, not a vendor interoperability claim.

## Required First-Hop Read Order

All compatible consumers should preserve this order:

1. `readiness`
   - Decide whether work may safely start before trusting any summary shell.
2. `canonical_center`
   - Recover the accepted short board and source precedence before reading children.
3. `closeout_attention`
   - Read latest closeout state before reusing compaction prose as if work were done.
4. `mutation_preflight`
   - Check bounded preflight before shared edits, publish/push, or task-board promotion.
5. `deep_packet_or_observer_pull`
   - Pull deeper packet or observer detail only when the task is ambiguous, contested, shared-state heavy, or not already `pass`.

## Misread Guards

Every compatible consumer should preserve at least these guards:

- `observer_stable_not_verified`
  - observer `stable` means bounded current orientation, not verified truth
  - trigger surface: `observer_window.stable`
  - operator action: read `readiness` and `canonical_center` before trusting stable headlines
- `compaction_not_completion`
  - compaction summaries remain subordinate to closeout status and unresolved items
  - trigger surface: `closeout_attention + compaction summary`
  - operator action: read closeout status before reusing handoff prose
- `working_style_not_identity`
  - shared working style may influence workflow, but must not be promoted into durable identity or law
  - trigger surface: `working_style continuity + subject_snapshot`
  - operator action: reuse habits only as workflow guidance, not as identity or policy
- `council_agreement_not_accuracy`
  - council agreement and coherence remain descriptive unless separately calibrated by outcome evidence
  - trigger surface: `council_dossier confidence surfaces`
  - operator action: treat confidence as descriptive only unless separate calibrated evidence exists

## Priority Misread Correction

Compatible consumers may rank one guard as the current highest-risk correction, but they must stay inside the same guard set.

Priority rule:

- if latest closeout is not `complete`, surface `compaction_not_completion` first
- else if `readiness != pass`, surface `observer_stable_not_verified` first
- else default to `observer_stable_not_verified`

This is a bounded correction cue, not a planner and not a new authority lane.

## Source Precedence

Cross-agent consumers should preserve this bounded precedence:

`canonical_anchors > live_coordination_truth > derived_orientation_shells > bounded_handoff > working_identity_and_replay`

This means:

- children do not outrank parents
- shells do not outrank canonical anchors
- smooth handoff prose does not outrank closeout grammar

## Runtime Surfaces

The contract should remain visible in:

- `start_agent_session.py`
- `observer_window`
- `r_memory_packet`

It may be rendered differently per shell, but the first-hop order and guards should stay the same.

## What This Contract Is Not

This contract is not:

- a new transport layer
- a new vendor bridge
- proof of shared selfhood
- proof that all shells now understand ToneSoul equally well

It is only a bounded shared reading discipline.
