# ToneSoul Claude-Compatible Entry Adapter Contract

> Purpose: define one repo-native adapter that lets Claude-style shells cold-start from ToneSoul without drifting away from the same first-hop order used by Codex and dashboard/operator shells.
> Last Updated: 2026-04-07
> Authority: bounded adapter contract. Does not imply official first-party cross-vendor interoperability.

---

## Why This Exists

ToneSoul already has:

- session-start tiers
- observer window
- consumer contract
- bounded mutation and closeout discipline

What external shells still lack is a thin adapter that says:

- read this first
- do not assume this
- only pull deeper when these conditions hold

This contract exists to make Claude-style shells more parity-aligned without pretending vendor-native memory fusion exists.

## Compressed Thesis

The adapter should:

- reuse ToneSoul's existing Tier-1 orientation shell
- preserve the same first-hop order as other compatible consumers
- stay thinner than full packet or full observer detail

The adapter should not:

- invent a second transport layer
- bypass session-start
- claim official first-party Claude interoperability

## Required Shape

The adapter should preserve:

- `first_hop_order`
- `must_read_now`
- `must_not_assume`
- `priority_correction`
- `current_context`
- `closeout_focus`
- `bounded_pulls`

At minimum, the first-hop order should stay:

1. `readiness`
2. `canonical_center`
3. `closeout_attention`
4. `mutation_preflight`

## Pull Discipline

The Claude-compatible adapter is:

- `orientation_first`
- `deep_pull_later`

That means:

- do not start from packet dumps
- do not start from compaction prose
- do not skip closeout and mutate shared state immediately

Deeper packet or observer surfaces should only be pulled when the task is:

- contested
- blocked
- ambiguous
- shared-state heavy

When `closeout_attention` is present, the adapter should preserve one bounded `closeout_focus` with:

- closeout `status`
- `source_family`
- `attention_pressures`
- `operator_action`

This remains orientation-only packaging.
It must not become a planner or a stronger authority lane.

When a `priority_misread_guard` is present, the adapter should also preserve one bounded
`priority_correction` with:

- the current misread `name`
- the `trigger_surface`
- the blocked assumption
- the bounded `operator_action`
- `re_read_now`
- the current `bounded_next_step_target`

This is still orientation-only packaging.
It should help a Claude-style shell recover the same first correction as other consumers,
but it must not become a planner, transport story, or permission system.

## Non-Goals

This adapter is not:

- proof that Codex and Claude now share hidden cognition
- proof that R-memory alone solves cross-agent parity
- a replacement for canonical center or consumer contract

It is just one bounded shell adapter.
