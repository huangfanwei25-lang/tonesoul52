# ToneSoul Runtime Compaction And Gamification Contract

> Status: architectural contract and prioritization boundary as of 2026-03-26
> Scope: runtime compaction memory, dashboard/world gamification, legacy trace repair, and security sidecar work
> Purpose: decide which ideas from recent multi-agent handoff and thesis discussions belong in ToneSoul's canonical runtime path, which remain experimental, and which must be split into separate workstreams.
> Last Updated: 2026-03-26

## Disclaimer

This document separates:

- mechanisms that belong in the canonical ToneSoul runtime path
- experiments that may enrich the operator experience
- separate workstreams that should not be smuggled into the same implementation batch

It is a prioritization and boundary contract, not a claim that every later-phase feature is already built.

## Compressed Thesis

ToneSoul should promote compaction memory into a non-canonical resumability lane, treat world/dashboard gamification as an operator-facing projection layer, keep security as a separate hardening workstream, and never "repair" append-only trace history in a way that erases audit epochs.

## Input Surfaces

This contract was distilled from:

- `memory/handoff/2026-03-26_codex_task_redis_gamification.md`
- `docs/narrative/TONESOUL_THESIS.md`
- `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`

The handoff note contains valuable momentum, but it mixes:

- canonical runtime concerns
- UI projection ideas
- migration/repair work
- security hardening

ToneSoul must split those concerns before it trusts the proposal.

## A Layer: Mechanism

### 1. Compaction Memory Belongs In A Non-Canonical Lane

The strongest near-term adoption candidate is:

- runtime compaction memory

But it must not go directly into canonical governance posture.

Approved direction:

- `ts:checkpoints:*`
- optional future `ts:compacted`

Approved role:

- resumability
- short handoff summaries
- context-compaction inheritance between sessions or terminals

Forbidden role:

- direct canonical posture mutation
- bypassing `commit()`
- replacing Aegis-protected traces

The correct relationship is:

> compaction memory informs later agents; it does not silently rewrite canonical truth

### 2. World / Dashboard Gamification Is A Projection Layer

The dashboard, world map, or tile-based RPG view may be used as an operator-facing projection surface.

Approved direction:

- render `soul_integral`, `baseline_drift`, `active_vows`, `tension_history`, `aegis` posture, visitors, and claims as visual state
- use `gateway` / `packet` / world-zone artifacts as the source

Forbidden direction:

- making UI the source of truth
- letting presentation semantics override governance semantics
- reading ungoverned raw runtime artifacts instead of the packet/contract surfaces

The correct relationship is:

> the world view may compress governance into a navigable operator shell, but it remains a projection of governed state rather than a replacement for governed state

### 3. Legacy Trace Repair Must Preserve Audit Epochs

The handoff note's instinct to fix compromised legacy traces is valid, but the naive move is dangerous.

Forbidden move:

- rewriting append-only history as if it had always been signed
- silently replacing historical chain semantics

Approved direction:

- preserve a `legacy/pre-aegis` epoch
- add an explicit repair/migration envelope
- record that historical integrity posture changed at a known time
- distinguish:
  - legacy unsigned traces
  - post-repair annotations
  - post-Aegis canonical traces

The correct rule is:

> historical repair may annotate or bridge an epoch boundary, but it must not pretend the earlier epoch always satisfied the later contract

### 4. Security Work Is A Separate Hardening Track

The proposed security ideas have value:

- supply-chain posture
- secret scanning
- agent-trust surfaces

But they should not be smuggled into the same implementation bundle as runtime compaction or gamified world surfaces.

Approved direction:

- separate `security/` module workstream
- explicit trust boundaries
- diagnostics and enforcement linked to R-memory posture where relevant

Forbidden direction:

- coupling security rollout to dashboard work
- coupling secret scanning to semantic-field promotion
- using security rhetoric to imply stronger runtime guarantees than the code enforces

### 5. Canonical Order Of Adoption

The correct implementation order is:

1. canonical commit safety
2. perspective lane
3. checkpoint / compaction lane
4. packet-first operator surfaces
5. world/dashboard gamification
6. field synthesis
7. legacy trace migration plan
8. security sidecar expansion

This order matters.
It protects the nervous system before decorating the body.

## B Layer: Observable Behavior

If this contract is followed, later agents and operators should observe:

- compaction summaries appearing in resumability lanes without changing canonical session counts, vows, or Aegis chain state
- dashboards and world maps becoming more expressive without becoming new authorities
- legacy integrity problems staying visible as historical epoch boundaries rather than disappearing behind rewrites
- security posture appearing as a separate diagnostic/hardening lane instead of contaminating unrelated runtime semantics

If these observations fail, the likely architectural meaning is:

- compaction has leaked into canonical governance mutation
- gamification has started driving semantics instead of projecting them
- migration has erased historical trace boundaries
- security language is smuggling architectural authority it has not earned

## C Layer: Interpretation

The philosophical temptation is to say:

- the world view becomes the lived body of ToneSoul
- compaction memory becomes the inner sediment of memory
- repaired traces restore a continuous soul

Those readings are useful only if they do not smuggle false mechanism.

The defensible interpretation is:

- compaction memory is a resumability sediment layer
- the world/dashboard is a symbolic exteriorization of governed posture
- repair work is an admission of history, not a denial of it
- security is part of ethical posture, but it still requires concrete enforcement

In ToneSoul language:

> let the system become more legible and more alive, but never at the cost of lying about what the repository actually guarantees

## Adoption Decision Matrix

### Promote To Mainline Now

- checkpoint-based compaction memory
- packet-first dashboard consumption
- explicit phase split between canonical runtime and projection layers

### Keep Experimental

- richer world / RPG operator shell
- field-linked mood or atmosphere overlays
- compaction summaries feeding higher-order synthesis

### Delay Until Separate Plan Exists

- legacy trace re-sign / migration bridge
- security package/trust/secret suite as a coherent submodule

### Do Not Allow

- direct compaction-to-canonical mutation
- UI-first truth surfaces
- historical trace rewriting that hides epoch boundaries
- bundled "do everything at once" runtime, world, migration, and security rollout

## Relationship To Other Documents

- `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
  - defines the live memory stack and R-memory role
- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - defines serialized canonical commit vs experimental field synthesis
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`
  - defines current runtime reality and commit-order posture
- `docs/narrative/TONESOUL_THESIS.md`
  - preserves the deeper narrative frame that this contract must not flatten into corporate blandness
- `memory/handoff/2026-03-26_codex_task_redis_gamification.md`
  - source handoff whose ideas are being triaged here rather than copied wholesale

## Canonical Handoff Line

Promote compaction into a governed resumability lane first, let gamification remain a projection layer, keep security as its own hardening track, and treat legacy trace repair as epoch-bridging migration rather than silent history rewrite.
