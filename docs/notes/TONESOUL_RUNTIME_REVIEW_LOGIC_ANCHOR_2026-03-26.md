# ToneSoul Runtime Review Logic Anchor (2026-03-26)

> Purpose: preserve the runtime-review logic, priority order, and failure heuristics that recently guided ToneSoul audit and hardening work, so later agents can reuse the same judgment instead of re-inventing it.
> Last Updated: 2026-03-26

## Why This Exists

When ToneSoul work shifts from philosophy into runtime seams, the hardest part is no longer "what sounds right."
It is:

> what logic should dominate when state authority, UI behavior, memory boundaries, and model-facing claims start disagreeing

This anchor records the judgment spine that proved useful during the runtime-adapter / world-map / Redis review pass.

It should be treated as a review-memory anchor, not as a replacement for the canonical architecture documents.

## The Dominance Order

When multiple concerns conflict, prefer them in this order:

1. **State authority**
   - the same surface that is written should be the surface that is later read and rendered
   - avoid split-brain between Redis, files, and generated artifacts
2. **Safety before mutation**
   - blocked or invalid input must be rejected before it changes governance posture
   - do not "partially reject" if the state was already mutated
3. **One cause → one effect**
   - one commit should not trigger duplicate writes, duplicate pub/sub events, or repeated rebuild cascades
4. **Observable honesty**
   - dashboards and summaries must reflect the real backend in use
   - if a fallback is active, show fallback truthfully instead of pretending full capability
5. **Boundary hygiene**
   - runtime artifacts, test data, and private memory must not silently contaminate public or canonical state
6. **Script-level reality**
   - if the real operator path is a script or standalone server, it needs direct tests
   - package-level tests are not enough if they bypass the actual entrypoint
7. **UI polish**
   - visual richness matters only after authority, safety, and boundary logic are coherent

## Review Heuristics That Should Repeat

### 1. Follow the authoritative state all the way through

For any runtime path, trace this chain explicitly:

- who writes the state
- where it is stored
- who reads it back
- which UI or report renders it

If the chain changes backend midway, assume a bug until proven otherwise.

### 2. Treat "blocked but already merged" as a serious failure

If a filter, gate, or shield says "blocked," the mutation must not already have landed in:

- governance state
- trace logs
- drift baselines
- counters
- visualizations

Blocked means blocked at the mutation boundary, not "blocked after side effects."

### 3. Watch for self-triggering loops

If a watcher observes an artifact that the same process rewrites, inspect it for:

- infinite refresh loops
- redundant rebuilds
- repeated pub/sub storms
- silent CPU churn

ToneSoul review should be suspicious of any path where the system watches its own outputs.

### 4. Prefer semantic parity across backends

If Redis and FileStore both exist, the question is not only "do both run."
The real question is:

> do they mean the same thing under load, rendering, and replay

A fallback is acceptable.
A semantic split is not.

### 5. Keep runtime artifacts and tests separate

A synthetic or partial trace should not quietly become part of:

- public history
- world counts
- latest status artifacts
- operator-visible continuity

Runtime surfaces are narrative surfaces.
Once polluted, later agents will infer false continuity from them.

### 6. Do not confuse adjacent tests with direct coverage

If a new path is introduced through:

- `scripts/*.py`
- a custom HTTP server
- a watcher thread
- a WebSocket flow

then nearby tests do not count unless they exercise that exact surface.

## What Recently Proved Correct

These judgments were recently validated in the runtime-adapter / world-map hardening pass:

- Aegis-style blocking must happen before governance state mutation
- world-map rebuilds must use the active backend, not a stale parallel artifact lane
- file watchers must not watch artifacts they themselves rewrite
- long-lived WebSocket connections require a threaded server or equivalent concurrency seam
- zone registry rebuilding should not overwrite valid timestamps with empty ones
- explicit test paths should write all derived artifacts into the same temporary lane, not back into repo-root state
- new UI panels such as visitors / Aegis should degrade honestly on FileStore, not show fake "unknown" status when a real audit is available

## How Another AI Should Use This

When auditing or extending ToneSoul runtime behavior:

1. read the canonical architecture anchors first
2. then use this note to decide which concern should dominate
3. only then change code, tests, or UI

This note is especially relevant when touching:

- `tonesoul/runtime_adapter.py`
- `tonesoul/zone_registry.py`
- `tonesoul/store.py`
- `tonesoul/backends/*`
- `scripts/launch_world.py`
- `scripts/gateway.py`
- runtime-facing dashboard or world-map surfaces

## What This Anchor Is Not

This is not:

- proof of model selfhood
- a philosophical manifesto
- permission to bypass canonical architecture docs
- justification for storing more raw memory in the repo

It is simply the currently most reliable review logic for ToneSoul runtime seams.

## One-Sentence Handoff

When ToneSoul runtime and UI paths become ambiguous, let authoritative state flow, safety-before-mutation, and one-cause-one-effect dominate before aesthetics or abstraction.
