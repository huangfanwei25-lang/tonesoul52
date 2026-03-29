# ToneSoul Audience Routing And Entry Contract

> Purpose: define the cleanest first-hop reading path for each audience so later readers stop mistaking historical, deep, or operational surfaces for the first thing to open.
> Last Updated: 2026-03-29
> Authority: documentation boundary aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.

---

## Audience Routing Table

| Audience | First Surface | Second Surface | Third Surface Or First Command | Avoid Opening First | Most Common Navigation Mistake |
|----------|---------------|----------------|--------------------------------|---------------------|-------------------------------|
| **Developer** | `docs/GETTING_STARTED.md` | `README.md` | `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` | `docs/narrative/TONESOUL_ANATOMY.md` | Reading the deep map before understanding the runtime pipeline, then assuming every philosophical concept is already code |
| **Researcher** | `README.md` | `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` | `docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md` | `TONESOUL_NARRATIVE.txt`, `TONESOUL_PHILOSOPHY.txt` | Treating philosophical lineage files as the current spec, then overclaiming what the system has proven |
| **AI Agent** | `AI_ONBOARDING.md` | `docs/AI_QUICKSTART.md` | `python scripts/start_agent_session.py --agent <id>` | `AI_ONBOARDING.md` lines 28-87 before the reading stack and first commands | Reading the full "If..." wall before orienting, then opening too many contracts without a concrete question |
| **Curious Human** | `SOUL.md` | `LETTER_TO_AI.md` | `README.zh-TW.md` or `README.md` | `MGGI_SPEC.md`, `TAE-01_Architecture_Spec.md` | Starting with a dense spec and concluding the project is impenetrable |

---

## Entry Lane Definitions

### Lane 1: Operational Start

**Surfaces**: `AI_ONBOARDING.md`, `docs/AI_QUICKSTART.md`, `docs/GETTING_STARTED.md`, `python scripts/start_agent_session.py --agent <id>`

**Purpose**: Get a reader oriented and running within 5 minutes.

**Rule**: These surfaces should make sense before any deep architecture contract is required.

**Current hazard**: `docs/AI_QUICKSTART.md` still contains a long R-memory coordination block that is heavier than a true first-minute entry.

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

**Surfaces**: `MGGI_SPEC.md`, `TAE-01_Architecture_Spec.md`, `.archive/`, `docs/archive/`

**Purpose**: Understand where the system came from, not where it is now.

**Rule**: Never treat these as current architecture. See `TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md` for classification.

---

## First-Read Hazard Summary

| Hazard | Where | Who Gets Hurt | Severity |
|--------|-------|---------------|----------|
| AI_ONBOARDING "If wall" | `AI_ONBOARDING.md` lines 28-87 | AI agents | **high**. Causes read paralysis and contract over-opening |
| Root lineage `.txt` files look primary | `TONESOUL_NARRATIVE.txt`, `TONESOUL_PHILOSOPHY.txt`, `TONESOUL_THEORY.txt` | Researchers, curious humans | **medium**. High-quality lineage, not current spec |
| `README.zh-TW.md` has a long routing cascade | `README.zh-TW.md` | Chinese-reading developers | **medium**. Harder to scan than the English README |
| `docs/README.md` and `docs/INDEX.md` overlap | both docs entry surfaces | All readers | **medium**. Their roles need clearer differentiation |
| `TAE-01_Architecture_Spec.md` metadata overstates currentness | root historical spec | All readers | **low**. Status wording can mislead later agents |
| Quickstart command block is too heavy | `docs/AI_QUICKSTART.md` | New AI agents | **medium**. Too much coordination detail too early |

---

## Recommended Entry Sequence

```text
Step 1: Open README.md and use "Choose Your Entry".
Step 2: If you are an AI agent, open AI_ONBOARDING.md.
Step 3: Read docs/AI_QUICKSTART.md.
Step 4: Run python scripts/start_agent_session.py --agent <id>.
Step 5: Open deeper contracts only after you have a concrete question.
```
