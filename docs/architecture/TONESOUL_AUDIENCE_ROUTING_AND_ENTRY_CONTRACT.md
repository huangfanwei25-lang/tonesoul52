# ToneSoul Audience Routing And Entry Contract

> Purpose: define the cleanest first-hop reading path for each audience so later readers stop mistaking historical, deep, or operational surfaces for the first thing to open.
> Last Updated: 2026-04-14
> Authority: documentation boundary aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.

---

## Audience Routing Table

| Audience | First Surface | Second Surface | Third Surface Or First Command | Avoid Opening First | Most Common Navigation Mistake |
|----------|---------------|----------------|--------------------------------|---------------------|-------------------------------|
| **Developer** | `docs/GETTING_STARTED.md` | `docs/foundation/README.md` | `docs/README.md` | `docs/narrative/TONESOUL_ANATOMY.md` | Opening a deep map before the thin packet, then assuming every philosophical concept is already code |
| **Researcher** | `DESIGN.md` | `docs/foundation/README.md` | `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md` | `TONESOUL_NARRATIVE.txt`, `TONESOUL_PHILOSOPHY.txt` | Treating lineage files as the current spec, then overclaiming what the system has proven |
| **AI Agent** | `docs/AI_QUICKSTART.md` | `python scripts/start_agent_session.py --agent <id>` | `AI_ONBOARDING.md` | bulk-opening `docs/architecture/` before the packet | Widening into contracts before reading `readiness`, `canonical_center`, and the bounded packet |
| **Curious Human** | `README.zh-TW.md` | `SOUL.md` | `LETTER_TO_AI.md` or `README.md` | `docs/SEMANTIC_SPINE_SPEC.md`, `docs/TRUTH_STRUCTURE.md` | Starting with a dense historical spec and concluding the project is impenetrable |

---

## Entry Lane Definitions

### Lane 1: Operational Start

**Surfaces**: `docs/AI_QUICKSTART.md`, `python scripts/start_agent_session.py --agent <id>`, `AI_ONBOARDING.md`, `docs/foundation/README.md`, `docs/GETTING_STARTED.md`

**Purpose**: Get a reader oriented and running within 5 minutes.

**Rule**: These surfaces should make sense before any deep architecture contract is required.

**Current hazard**: widening into `docs/architecture/` before reading the bounded packet still creates drift, even after the first-hop cleanup.

### Lane 2: Canonical Architecture

**Surfaces**: the canonical architecture anchor and the AI Reading Stack surfaced from `AI_ONBOARDING.md`

**Purpose**: Establish what the system actually is before repeating architectural claims.

**Rule**: Canonical architecture documents outrank narrative, philosophical, and interpretive documents when they disagree.

### Lane 3: Working Reference

**Surfaces**: `docs/AI_REFERENCE.md`, `docs/terminology.md`

**Purpose**: Lookup during active work.

**Rule**: These are lookup surfaces, not first-read surfaces.

### Lane 4: Deep Map And Narrative

**Surfaces**: `docs/narrative/TONESOUL_ANATOMY.md`, `TONESOUL_NARRATIVE.txt`, `TONESOUL_PHILOSOPHY.txt`, `TONESOUL_THEORY.txt`

**Purpose**: Understand deeper identity, philosophical foundation, and technical theory after orientation is complete.

**Rule**: These are explanation surfaces, not orientation surfaces.

### Lane 5: Interpretive

**Surfaces**: `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`, `docs/narrative/TONESOUL_CODEX_READING.md`

**Purpose**: Help when the structural map is clear but the load-bearing meaning still feels diffuse.

**Rule**: Never open these before the canonical architecture lane.

### Lane 6: Identity And Philosophical

**Surfaces**: `SOUL.md`, `LETTER_TO_AI.md`, `AXIOMS.json`

**Purpose**: Understand values, identity posture, and constitutional constraints.

**Rule**: `AXIOMS.json` is constitutional. `SOUL.md` and `LETTER_TO_AI.md` are identity/narrative companions and do not share the same authority level.

### Lane 7: Historical And Lineage

**Surfaces**: `docs/SEMANTIC_SPINE_SPEC.md`, `docs/TRUTH_STRUCTURE.md`, `docs/MGGI_MANIFESTO.md`, `.archive/`, `docs/archive/`

**Purpose**: Understand where the system came from, not where it is now.

**Rule**: Never treat these as current architecture. See `TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md` for classification.

---

## First-Read Hazard Summary

| Hazard | Where | Who Gets Hurt | Severity |
|--------|-------|---------------|----------|
| Root lineage `.txt` files look primary | `TONESOUL_NARRATIVE.txt`, `TONESOUL_PHILOSOPHY.txt`, `TONESOUL_THEORY.txt` | Researchers, curious humans | **medium**. High-quality lineage, not current spec |
| `README.zh-TW.md` has a long routing cascade | `README.zh-TW.md` | Chinese-reading developers | **medium**. Harder to scan than the English README |
| Curated gateway versus full registry still gets skipped | `docs/README.md` and `docs/INDEX.md` | All readers | **medium**. Some readers still jump to the full index before the guided gateway |
| historical-spec references can point at dense legacy prose too early | `docs/SEMANTIC_SPINE_SPEC.md`, `docs/TRUTH_STRUCTURE.md` | All readers | **low**. Correct file, wrong first hop still causes overreading |
| Deep packet widening still happens too early | `docs/architecture/*` after session start | AI agents, developers | **medium**. Clean entry exists, but later readers may still skip the bounded packet |

---

## Recommended Entry Sequence

```text
Step 1: Open README.md and use "Choose Your Entry".
Step 2: If you are an AI agent, open docs/AI_QUICKSTART.md.
Step 3: Run python scripts/start_agent_session.py --agent <id>.
Step 4: Open AI_ONBOARDING.md and docs/foundation/README.md.
Step 5: Read task.md.
Step 6: Open deeper contracts only after you have a concrete question.
```
