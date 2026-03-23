# ToneSoul Runtime Adapter Memory Anchor (2026-03-23)

> Purpose: repo-safe memory anchor for the self-dogfooding runtime-adapter direction and the latest document-governance handoff state.
> Last Updated: 2026-03-23

## Why This Exists

ToneSoul was designed to solve the "AI has no memory" problem through externalized governance, memory, and verification layers.

But the AI agents currently developing ToneSoul are still mostly stateless between conversations.

That creates a structural mismatch:

- ToneSoul runtime assumes persistent state
- Codex / Antigravity development sessions still restart from near-zero unless they reread docs

The next architecture seam is therefore not "make the philosophy bigger."
It is:

> build a lightweight developer runtime adapter so the agents building ToneSoul can start running a minimal ToneSoul governance shell themselves

## Canonical Interpretation

Treat the runtime-adapter direction as:

- observable-shell governance
- local state persistence across sessions
- explicit session traces and vow posture
- externalized state, not latent-state intervention

Do **not** interpret it as:

- direct access to hidden model state
- proof of model selfhood
- permission to store raw private memory in the public repo
- justification for collapsing public and private memory boundaries

The right claim is:

> developer agents should load a small local governance state at session start and write a small session trace at session end

## Current North Star

These remain the primary architecture sources:

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
3. `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
4. `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
5. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`

Runtime-adapter work must stay compatible with those anchors.

## What Was Already Done Before This Anchor

### Architecture and governance stabilization

- ToneSoul was restated as an externalized cognitive operating system
- the older six-layer runtime story was reconciled into the eight-layer convergence map
- L7 retrieval and L8 distillation boundaries were turned into explicit contracts
- the A/B/C firewall doctrine was added so mechanism, observability, and interpretation stop being mixed together

### Documentation convergence program

The repo now has explicit governance for previously confusing documentation surfaces:

- engineering mirror ownership map
- basename divergence distillation map
- paradox fixture ownership map
- private memory shadow boundary map
- historical document lane policy
- document authority structure map
- generated convergence inventory and mermaid/status artifacts

### Repo hygiene already completed

- the current docs-convergence branch was pushed and validated
- PR `#3` is open and green
- stale local/remote branches were pruned down to the active branch plus `master`

### Latest convergence posture at the time of this anchor

- `missing_purpose_count = 138`
- `missing_date_count = 100`

This means the repo is no longer in "structural chaos."
The remaining work is now long-tail cleanup, not architectural confusion.

## Immediate Next Build After This Anchor

### 1. Rewrite RFC-015 into a clean canonical document

`docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md` currently contains the right direction, but it is not yet stable enough to treat as canonical because the file still has encoding damage and draft-level rough edges.

Use it as a source idea, then rewrite it into a clean UTF-8 contract or plan before implementation.

### 2. Build a minimal developer runtime adapter

First version should stay intentionally small:

- one local `governance_state`
- one append-only `session_trace`
- lightweight tension / vow / veto / drift fields
- no attempt to mirror the entire production runtime

### 3. Keep runtime state outside the public repo by default

Preferred posture:

- repo stores contracts, schemas, scripts, and public-safe summaries
- local agent state stays in tool-local storage such as:
  - `C:\Users\user\.codex\memories\...`
  - `C:\Users\user\.gemini\...`

Only public-safe schemas and tooling should live in this repo.

### 4. Add a start/end workflow seam

The minimal adapter should eventually support:

- session start: load local governance state
- session end: write session trace
- optional post-session summary commit to external memory tooling

### 5. Bridge to OpenClaw-Memory only through safe summaries

If OpenClaw-Memory is used, keep the bridge narrow:

- safe summary rows
- public-safe tags
- no raw private vault dump

## Recommended Minimal State Shape

The first adapter does not need full runtime parity.

The smallest useful persistent fields are:

- `soul_integral`
- `recent_tension_events`
- `active_vows`
- `aegis_vetoes`
- `baseline_drift`
- `session_count`

The smallest useful per-session trace fields are:

- `session_id`
- `agent`
- `timestamp`
- `key_decisions`
- `tension_events`
- `vow_events`
- `aegis_vetoes`
- `stance_shift`

## Constraints That Must Stay In Force

- do not modify protected human-managed files just to fake memory continuity
- do not store personal memory payloads in the public repo
- do not claim latent-state control
- do not bypass the L7 retrieval contract or L8 boundary contract
- do not let runtime-adapter language blur into philosophical overclaim

## External Inputs Parked For The Next Research Step

These local files were explicitly deferred for the next architecture-thinking phase:

- `C:\Users\user\.gemini\antigravity\brain\970a6e54-00a8-4344-9947-90267fe8e9d3\asmr_vs_tonesoul_analysis.md.resolved`
- `C:\Users\user\.gemini\antigravity\brain\970a6e54-00a8-4344-9947-90267fe8e9d3\game_studios_and_senticore_analysis.md.resolved`

Do not lose them.
They are part of the next reasoning pass after the current handoff preservation work.

## Reading Order For The Next Agent

1. `docs/notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md`
2. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
3. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
4. `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
5. `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
6. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`
7. `docs/status/doc_convergence_inventory_latest.json`
8. `docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md`

## One-Sentence Handoff

ToneSoul has already stabilized its externalized architecture and document-governance spine; the next major step is to make developer agents run a minimal local ToneSoul governance shell instead of rebuilding context from scratch every session.
