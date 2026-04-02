# ToneSoul Hot-Memory Decay And Compression Map

> Purpose: explain how ToneSoul's current hot-memory ladder should decay, compress, or stay quarantined across successor-facing surfaces.
> Last Updated: 2026-04-02
> Authority: runtime-aligned architecture aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.

---

## Why This Exists

ToneSoul now exposes a live `hot_memory_ladder` and `hot_memory_decay_map`.

That means later agents can already see:

- which layer is parent truth
- which layer is operational
- which layer is review-only
- which layer is quarantined

What this document adds is the design explanation behind those readouts, so later agents do not re-invent a second decay story from old sidecar notes.

---

## Runtime-Aligned Ladder

Current runtime uses six hot-memory layers:

| Layer | Meaning | Primary Surfaces |
|---|---|---|
| `canonical_center` | parent planning truth | `task.md.current_short_board`, `DESIGN.md` |
| `low_drift_anchor` | current orientation shell | posture, launch claim posture, coordination mode, readiness |
| `live_coordination` | current-session coordination state | readiness, claims, track hint, deliberation hint |
| `bounded_handoff` | resumability and handoff state | compactions, checkpoints, delta feed, recent traces |
| `working_identity` | inheritable but non-canonical continuity | subject snapshot, working-style anchor/playbook |
| `replay_review` | replay, audit, and long-tail context | recent traces, council dossier, validation artifacts |

This is the only active hot-memory ladder story.

Earlier drafts that used a separate L0-L6 ladder are now subordinate to this runtime-aligned map.

---

## Decay And Compression Posture

### 1. `canonical_center`

- `use_posture`: `operational`
- `decay_posture`: `human_refresh_only`
- `compression_posture`: `never_compress`

Meaning:

- parent truth should be re-read, not compressed into child summaries
- if the current short board is missing, successors should reopen `task.md`, not invent a replacement

---

### 2. `low_drift_anchor`

- `use_posture`: `operational` when stable, `review_only` otherwise
- `decay_posture`: `recompute_each_session`
- `compression_posture`: `already_compact_do_not_recompress`

Meaning:

- the observer-style anchor is already a bounded shell
- do not carry it forward as if it were its own authority
- rebuild it from current parent surfaces each session

---

### 3. `live_coordination`

- `use_posture`: `operational` when stable, `review_only` otherwise
- `decay_posture`: `expire_fast`
- `compression_posture`: `do_not_compress_live_signals`

Meaning:

- claims, readiness, and mode hints are only valid for the current coordination moment
- if they go stale, re-run session-start or the relevant coordination surface instead of summarizing them

---

### 4. `bounded_handoff`

- `use_posture`: `review_only` when stable, `quarantine` when contested
- `decay_posture`: `ttl_then_compress`
- `compression_posture`: `compress_with_closeout_guards`

Meaning:

- compactions may orient resumability, but they are never parent truth
- incomplete closeout, promotion hazards, or `must_not_promote` obligation should force quarantine
- the most important fields are the ones that prevent fake completion

Must remain explicit whenever present:

- `closeout.status` when not `complete`
- `stop_reason`
- `unresolved_items`
- `human_input_required`

---

### 5. `working_identity`

- `use_posture`: `review_only`
- `decay_posture`: `slow_decay_with_refresh`
- `compression_posture`: `do_not_compress_snapshot`

Meaning:

- subject snapshot and working-style continuity may help successors inherit bounded habits
- they must never become permission, policy, or identity law
- stale working identity should be refreshed or ignored, not compressed into smoother prose

---

### 6. `replay_review`

- `use_posture`: `review_only`
- `decay_posture`: `prune_by_cardinality`
- `compression_posture`: `preserve_dissent_then_prune_oldest`

Meaning:

- replay is for context and audit, not execution permission
- if replay must be pruned, preserve dissent and decision-shaping context before trimming older entries

---

## Compression Rules That Matter Most

### Never Compress

- canonical center
- axioms
- design invariants
- unresolved closeout signals

### Recompute Instead Of Compress

- low-drift anchor
- observer shells
- live coordination

### Compress Only With Guards

- compactions and checkpoints
- only when newer handoff supersedes older handoff
- never if unresolved or human-gated state would disappear

### Prune, Do Not Mythologize

- replay/review surfaces
- old traces
- descriptive council summaries

These should age out by bounded pruning, not become pseudo-canonical memory.

---

## Most Dangerous Decay Mistakes

| Mistake | Why It Fails |
|---|---|
| treating compaction as a timeless master summary | hides unresolved work and closeout reality |
| recompressing low-drift anchor into another child shell | multiplies summaries instead of rebuilding from parents |
| carrying working-style habits across sessions without reinforcement | turns workflow aid into fake identity |
| letting replay dictate current execution | confuses audit context with present authority |

---

## Runtime Reflection

Current runtime already reflects this map through:

- `hot_memory_ladder`
- `hot_memory_decay_map`
- `observer_window`
- `canonical_center`

This document exists to explain those surfaces, not to create a second competing ladder.

---

## Receiver Line

If a later agent is unsure what to trust:

1. reopen parent truth
2. use live coordination for current-session action
3. use bounded handoff only for resumability
4. use working identity only as advisory continuity
5. use replay only for review

That is the current hot-memory discipline ToneSoul actually uses.
