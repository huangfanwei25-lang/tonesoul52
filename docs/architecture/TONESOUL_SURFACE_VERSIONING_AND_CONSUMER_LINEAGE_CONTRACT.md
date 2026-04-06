# ToneSoul Surface Versioning And Consumer Lineage Contract

> Purpose: keep `session-start`, `observer-window`, dashboard tier shells, and Claude-style entry adapters aligned as more consumers appear.
> Scope: repo-native consumer parity only. This is not a new transport layer or a vendor-integration story.

---

## Why This Exists

ToneSoul now has multiple valid consumers for the same bounded runtime truth:

- CLI / `session-start`
- `observer-window`
- dashboard operator shell
- Claude-compatible entry adapter

Without an explicit lineage rule, those consumers drift in two predictable ways:

1. a derived shell starts sounding like parent truth
2. a consumer keeps reading an old shape and silently misinterprets new fields

This contract exists to stop that drift before it turns into memory-interop confusion.

---

## Core Rule

Consumer surfaces may differ in shape and emphasis, but they must stay explicit about:

- which parent surface they derive from
- which versioned shape they expect
- which fallback surface outranks them when fields are missing or mismatched

---

## Current Runtime Surfaces

1. `session_start:tiered_v1`
   - role: bounded runtime entry
   - outranks: dashboard shell and Claude-style adapter
   - fallback: `observer_window:anchor_window_v1`

2. `observer_window:anchor_window_v1`
   - role: bounded runtime orientation
   - outranks: prose summaries and consumer-specific walkthrough shells
   - fallback: `r_memory_packet:packet_v1`

3. `r_memory_packet:packet_v1`
   - role: deeper runtime detail
   - use only after bounded entry/orientation is not enough

---

## Current Consumer Shells

1. `codex_cli:cli_entry_v1`
   - derives from `session_start:tiered_v1`

2. `dashboard_operator_shell:dashboard_shell_v1`
   - derives from `session_start:tiered_v1`
   - may render Tier 0 / 1 / 2 differently, but must not outrank parent runtime surfaces

3. `claude_style_shell:claude_entry_v1`
   - derives from `session_start:tiered_v1`
   - remains a repo-native adapter, not official first-party interop

---

## Compatibility Posture

`surface_versioning` may expose one bounded `compatibility_posture`.

It may clarify:

- which consumers are repo-native entries
- which consumers are bounded adapters
- which shared fallback chain preserves parity

It must **not** imply:

- stronger transport semantics
- vendor-native shared cognition
- authority promotion for a consumer shell

This posture exists only to make lineage and fallback easier to read.

---

## Fallback Rule

If a consumer shell is missing fields, looks stale, or conflicts with another consumer:

1. fall back to `Tier 1 session-start`
2. then fall back to `observer-window`
3. only then pull `r_memory_packet`

Do not jump directly from a mismatched shell to smooth prose or compaction summaries.

---

## Non-Goals

- creating a new packet schema family
- inventing vendor-specific memory transport
- promising cross-model shared understanding by transport alone
- turning version tags into predictive or authority scores
