# Claude Work Order — Deep Structure Authority Distillation (2026-03-27)

> Purpose: give a high-context synthesis agent a bounded documentation workstream that converts repo-scale structural insight into durable authority boundaries for later AI instances.
> Last Updated: 2026-03-27
> Issued By: Codex
> Target Agent: Claude Opus / other long-context synthesis-heavy collaborator
> Priority: high
> Status: ready for execution

## Why This Workstream Exists

ToneSoul now has a clearer AI entry stack:

- `operational`: quickstart and working reference
- `canonical`: architecture anchors and contracts
- `deep_map`: anatomy-scale system map
- `interpretive`: deeper narrative readings

That is good enough for entry.

What is still missing is a durable answer to a harder question:

> when a term appears in `law/`, `docs/`, `research/`, `tests/`, and narrative prose at the same time, what exactly is its current authority and implementation status?

This is where a long-context synthesis agent is strongest.

## Why This Fits Claude

This work is best done by an agent that is strong at:

- scanning many files without losing global structure
- turning large repo slices into named conceptual planes
- extracting a panoramic map from `law/`, `PARADOXES/`, `tests/`, `scripts/`, and narrative docs together
- writing high-density synthesis without collapsing distinct layers into one

This is not a runtime feature ticket.
It is a structure-and-boundary distillation ticket.

## Current Repo Posture

Read these first:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `docs/AI_REFERENCE.md`
4. `docs/narrative/TONESOUL_ANATOMY.md`
5. `docs/narrative/TONESOUL_CODEX_READING.md`
6. `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`
7. `AXIOMS.json`
8. `tonesoul/runtime_adapter.py`
9. `tonesoul/diagnose.py`
10. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
11. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`

Important current boundary:

- `AI_QUICKSTART` and `AI_REFERENCE` are operational guides, not constitutions
- `TONESOUL_ANATOMY` is a deep system map, not a runtime contract
- `TONESOUL_CODEX_READING` and the deep-reading anchor are interpretive, not executable truth
- many `law/` terms are real and important, but not all are current `runtime_adapter.py` hard dependencies

## Primary Objective

Produce a source-backed map that tells later agents, for major ToneSoul claims and terms:

- where the claim lives
- what kind of authority it has
- whether it is implemented now, partially implemented, or still theoretical
- whether an operator may rely on it during live engineering work

## Deliverables

### Deliverable A

Create:

- `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`

This should be a table-driven map of the most load-bearing 40-80 claims or terms across:

- `AXIOMS.json`
- `docs/AI_REFERENCE.md`
- `docs/narrative/TONESOUL_ANATOMY.md`
- `law/`
- runtime/code/test surfaces

Each row should include at least:

- term or claim
- authority role
  - `canonical`
  - `operational`
  - `deep_map`
  - `interpretive`
  - `law`
  - `research`
  - `runtime`
  - `projection`
- implementation status
  - `hard runtime`
  - `runtime-adjacent`
  - `test-backed but distributed`
  - `doc-only`
  - `research/theory`
  - `projection-only`
- source files
- can a later agent rely on this for engineering decisions: `yes / only with verification / no`

### Deliverable B

Create:

- `docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md`

This should explicitly classify high-confusion terms from `law/` and related deep prose into:

1. active runtime or audit dependency
2. active governance vocabulary but not current hard runtime dependency
3. theory / research lane
4. projection / narrative / worldview lane

This contract must explicitly cover:

- `YuHun Gate`
- `StepLedger`
- `Lex Lattice`
- `LAR`
- `Isnād`
- `MDL-Majority`
- `Sovereign Freeze`
- `BBPF`
- `Digital Sovereignty Manifesto`
- `PARADOX_006`

### Deliverable C

Optional, only if needed to support A/B:

- `docs/research/tonesoul_anatomy_source_register_2026-03-27.md`

Use this only if the evidence for `TONESOUL_ANATOMY.md` needs an external register instead of cluttering the anatomy file itself.

## Boundaries

Do not do these things in this workstream:

- do not change `tonesoul/runtime_adapter.py`
- do not change Redis schema, gateway behavior, or commit mutex logic
- do not change `AI_ONBOARDING.md`, `docs/AI_QUICKSTART.md`, or `docs/AI_REFERENCE.md` unless a claim is provably wrong and cannot be corrected later by Codex
- do not touch protected files like `AGENTS.md`
- do not push, merge, or rewrite history
- do not hand-maintain repo file counts unless the number is script-generated in the same pass

If you find that a concept is overclaimed:

- downgrade the claim in documentation
- do not silently "promote" code to match the prose

## Non-Goals

This ticket is not asking for:

- prettier prose
- more philosophy for its own sake
- a new runtime feature
- a dashboard redesign
- another grand unified narrative if the authority map is still missing

## Acceptance Criteria

This workstream is successful if:

- a later AI can answer "is this term active runtime, law, theory, or projection?" without rereading the whole repo
- the biggest overclaiming risks between `law/`, `ANATOMY`, and current runtime are explicitly named
- the resulting docs help future agents avoid mistaking deep structure for live implementation
- no protected files or runtime code are touched

## Suggested Method

1. Read the current AI entry stack and authority boundaries first.
2. Extract the top claims from `AI_REFERENCE`, `ANATOMY`, and `law/`.
3. Cross-check each claim against:
   - `tonesoul/runtime_adapter.py`
   - `tonesoul/diagnose.py`
   - relevant tests
   - canonical architecture contracts
4. Downgrade or split any mixed claim instead of smoothing it over.
5. Leave crisp, table-first artifacts rather than a second long essay.

## Handoff Back To Codex

When done, report back with:

- files created or changed
- 5-10 highest-risk overclaims you found
- which terms are now safe for later AI instances to treat as current runtime truth
- which terms must remain explicitly marked as theory, law, or projection
