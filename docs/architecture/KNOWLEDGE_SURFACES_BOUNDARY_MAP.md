# Knowledge Surfaces Boundary Map

> Purpose: define the authority boundary between `knowledge/`, `knowledge_base/`, and `PARADOXES/` so retrieval stays lane-aware.
> Last Updated: 2026-03-23

This document exists to stop a common retrieval mistake:

> treating every knowledge-like directory in the repository as the same kind of authority.

In ToneSoul, `knowledge/`, `knowledge_base/`, and `PARADOXES/` serve different purposes.
They should not be merged into one mental bucket.

## Quick Rule

If you are an agent trying to understand the repo:

1. read the canonical architecture anchor first,
2. use this boundary map before making assumptions about knowledge surfaces,
3. only then decide which directory is relevant to the task.

## Boundary Table

| Surface | What It Is | What It Is Not | Primary Use |
|---|---|---|---|
| `knowledge/` | human-authored concept, identity, and learning-context notes | not a runtime database, not a test fixture set, not a current source-of-truth by default | orientation, philosophical context, historical mind-model framing |
| `knowledge_base/` | local structured concept store and helper code (`knowledge.db`, initialization utilities) | not the canonical public architecture spec, not a broad narrative corpus | structured concept lookup / prototype persistence |
| `PARADOXES/` | governance and ethical stress-test fixtures expressed as scenario data | not a general knowledge library, not policy text, not user-facing docs | council evaluation, RDD-style adversarial / paradox testing |

## 1. `knowledge/`

### What it contains

Current examples:

- `knowledge/yuhun_identity.md`
- `knowledge/learning_materials_20251208.md`

These files read more like:

- conceptual onboarding,
- identity framing,
- learning references,
- historical mind-model notes.

### How to use it

Use `knowledge/` when you need:

- project self-description history,
- conceptual vocabulary background,
- older framing of YuHun / ToneSoul identity,
- narrative context for why the system was shaped this way.

### How not to use it

Do not treat `knowledge/` as:

- a guaranteed current implementation map,
- a runtime contract,
- a fresh test / CI status surface.

Some files in `knowledge/` are older than the current runtime and may reference legacy paths.

## 2. `knowledge_base/`

### What it contains

Current examples:

- `knowledge_base/knowledge.db`
- `knowledge_base/init_knowledge.py`

This surface is a small structured persistence layer for concepts:

- SQLite-backed,
- schema-driven,
- utility-oriented.

### How to use it

Use `knowledge_base/` when you need:

- concept storage,
- a structured local lookup table,
- a place to persist concise concept definitions with timestamps / source URLs.

### How not to use it

Do not treat `knowledge_base/` as:

- the public canonical knowledge model of ToneSoul,
- the architecture north star,
- the same thing as `memory/`,
- a substitute for docs/spec review.

It is closer to a lightweight concept store than to a full repository ontology.

## 3. `PARADOXES/`

### What it contains

Current examples:

- `PARADOXES/paradox_003.json`
- `PARADOXES/truth_vs_harm_paradox.json`
- `PARADOXES/medical_suicide_paradox.json`

These files are scenario fixtures, not essays.
They encode:

- input prompts,
- tension / risk estimates,
- axiom conflicts,
- expected governance posture.

### How to use it

Use `PARADOXES/` when you need:

- red-team style governance cases,
- ethical conflict fixtures,
- council / guardian regression material,
- RDD-oriented scenario coverage.

### How not to use it

Do not treat `PARADOXES/` as:

- general product knowledge,
- the semantic encyclopedia of the repo,
- user documentation.

It is a test / evaluation surface.

## Adjacent Surfaces That Often Get Confused

| Surface | Role | Why it gets confused |
|---|---|---|
| `memory/` | runtime and journal-like memory surfaces | people assume all repo knowledge is "memory" |
| `memory_base/` | metadata / ingest sidecar surface | naming similarity with `knowledge_base/` |
| `simulation_logs/` | run artifacts / logs | looks knowledge-like, but is operational residue |
| `docs/status/` | current machine-readable status and hand-authored clarifications | mixes generated snapshots with historical notes unless read carefully |

## Recommended Retrieval Order

When the question is about current system behavior:

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
3. `README.md` / `AI_ONBOARDING.md`
4. current status artifacts in `docs/status/`
5. source code under `tonesoul/`, `apps/`, `scripts/`, `tests/`

When the question is about conceptual lineage:

1. `knowledge/`
2. `docs/philosophy/`
3. historical specs such as `docs/SEMANTIC_SPINE_SPEC.md`, `docs/TRUTH_STRUCTURE.md`, and `docs/MGGI_MANIFESTO.md`

When the question is about adversarial governance behavior:

1. `PARADOXES/`
2. `tests/red_team/`
3. `docs/7D_EXECUTION_SPEC.md`
4. `docs/7D_AUDIT_FRAMEWORK.md`

## One-Line Heuristic

- `knowledge/` = conceptual memory
- `knowledge_base/` = structured concept store
- `PARADOXES/` = governance stress fixtures

If a reader collapses those into one category, they will almost certainly over- or under-state the
system.
