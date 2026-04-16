# ToneSoul Historical Spec And Legacy Surface Map

> Purpose: separate current canonical surfaces from historical lineage, active companions, and legacy documents so later agents stop treating old specs as current architecture.
> Last Updated: 2026-04-14
> Authority: documentation boundary aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.
> Measured Snapshot: 2026-03-29 (`docs/architecture/*=55`, `docs/architecture/TONESOUL_*=45`, `docs/architecture/TONESOUL_*_CONTRACT.md=21`, `docs/*=108`, `root *.md=24`)
> Status: partially historical classification map. Older cleanup notes may mention root files such as `MGGI_SPEC.md` and `TAE-01_Architecture_Spec.md`; those files are not present in the current repo snapshot.

---

## Classification System

| Category | Meaning | May Later Agents Cite Directly? | Priority |
|----------|---------|----------------------------------|----------|
| **1. Current Canonical** | Active authoritative surface | Yes, as the primary source of truth | Highest |
| **2. Active Companion** | Supports, extends, or operationalizes a canonical surface | Yes, but subordinate to canonical | High |
| **3. Historical But Useful Lineage** | Older document with valuable origin context | Yes, but label as historical lineage | Medium |
| **4. Legacy / Do Not Read First** | Outdated or superseded and confusing as a first read | Only when explicitly comparing evolution | Low |
| **5. Deferred / Archived** | Deprecated reference-only material | No, treat as archive | Lowest |

---

## Root-Level Surface Classification

### Category 1: Current Canonical

| File | Role | Notes |
|------|------|-------|
| `README.md` | Public entrypoint | Audience routing, evidence honesty, grouped system map |
| `AI_ONBOARDING.md` | AI routing map | Opens after quickstart and session-start; not the operational first-hop owner |
| `AXIOMS.json` | Constitutional axioms | Immutable and constitutional |
| `SOUL.md` | Identity surface | Agent-facing identity and values |
| `AGENTS.md` | Collaboration protocol | Protected file |

### Category 2: Active Companion

| File | Role | Canonical Surface It Supports |
|------|------|-------------------------------|
| `README.zh-TW.md` | Chinese public entry | `README.md` |
| `LETTER_TO_AI.md` | Narrative onboarding | `AI_ONBOARDING.md` |
| `CONTRIBUTING.md` | Contribution guide | `README.md` |
| `AGENT_PROTOCOL.md` | Agent protocol specifics | `AGENTS.md` |
| `CLAUDE.md` | Claude-local entry | Local companion, not public AI entry |
| `CODEX_PROTOCOL.md` | Codex-local protocol | `AGENTS.md` |
| `CODEX_TASK.md` | Codex-local task surface | `task.md` |
| `HANDOFF.md` | Cross-agent handoff | `AI_ONBOARDING.md` |
| `SCRIPTS_README.md` | Script documentation | `docs/GETTING_STARTED.md` |

### Category 3: Historical But Useful Lineage

| File | Why It Still Exists | Current Canonical Successor | Citation Rule |
|------|---------------------|-----------------------------|---------------|
| `TONESOUL_NARRATIVE.txt` | Founding narrative context | `README.md`, `LETTER_TO_AI.md` | Cite as founding narrative |
| `TONESOUL_PHILOSOPHY.txt` | Original philosophical formulation | `AXIOMS.json`, `docs/philosophy/*` | Cite as original formulation |
| `TONESOUL_THEORY.txt` | Original mathematical/technical theory | runtime code plus `spec/` | Cite as original theory |
| `MEMORY.md` | Earlier memory overview | continuity and R-memory contracts | Historical only |
| `RESTART_MEMORY.md` | Earlier restart protocol | `scripts/start_agent_session.py` | Historical only |

### Category 4: Legacy / Do Not Read First

| File | Why It Should Not Be Read First |
|------|---------------------------------|
| `README_EN.md` | Older English surface; `README.md` is the live entry |
| `REPO_CONSOLIDATION.md` | One-time consolidation record |
| `CODEX_VERCEL_MIGRATION.md` | Migration-specific |
| `CODEX_HANDBACK.md` | One-time handback artifact |
| `QA_RECORD_core.md` | Point-in-time QA record |
| `task.md` | Active execution ledger, not documentation |

### Category 5: Deferred / Archived

| Surface | Notes |
|---------|-------|
| `.archive/` | Hard boundary. Never import as current |
| `docs/archive/` | Historical archive lane |

---

## docs/ Surface Classification

### Category 1: Current Canonical

| Surface | Role |
|---------|------|
| `docs/AI_QUICKSTART.md` | Operational first-minute AI entry |
| `docs/AI_REFERENCE.md` | Working reference |
| `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` | Architecture north star |
| `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md` | Layer reconciliation |
| `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Shared R-memory contract |
| `docs/architecture/TONESOUL_*_CONTRACT.md` | Current boundary and discipline contracts (`21` measured current files) |

### Category 2: Active Companion

| Surface | Role |
|---------|------|
| `docs/README.md` | Guided docs entry |
| `docs/INDEX.md` | Comprehensive docs index |
| `docs/narrative/TONESOUL_ANATOMY.md` | Deep map |
| `docs/narrative/TONESOUL_CODEX_READING.md` | Interpretive reading |
| `docs/terminology.md` | Term lookup |
| `docs/core_concepts.md` | Core concept explanations |
| `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md` | Interpretive anchor |

### Category 3: Historical But Useful

| Surface | Why It Still Exists |
|---------|---------------------|
| `docs/SEMANTIC_SPINE_SPEC.md` | Earlier system-structure framing that still helps explain lineage |
| `docs/TRUTH_STRUCTURE.md` | Earlier truth-structure framing |
| `docs/MGGI_MANIFESTO.md` | Earlier governance / manifesto layer |
| `docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md` | Original runtime-adapter direction |
| `docs/WHITEPAPER.md` | Research artifact with older claims |
| `docs/PHILOSOPHY.md`, `docs/PHILOSOPHY_EN.md` | Earlier philosophy surfaces |
| `docs/RFC-009_Context_Engineering_Pivot.md` | Historical pivot |
| `docs/RFC-014_Reflection_Loop_Octopus_Architecture.md` | Earlier reflection architecture |

### Category 4: Legacy / Low Priority

| Surface | Notes |
|---------|-------|
| `docs/ARCHITECTURE_REVIEW.md` | Superseded review |
| `docs/ARCHITECTURE_REVIEW_2026-02-13.md` | Point-in-time review |
| `docs/INTEGRATION_AUDIT_DRAFT.md` | Stub |
| `docs/TECH_ARTICLE_DRAFT_v0.1.0.md` | Old article draft |
| `docs/MOLTBOOK_POST_DRAFT.md` | Old post draft |
| `docs/convergence_audit.md` | Superseded by convergence planning |

### Category 5: Deferred / Archived

| Surface | Notes |
|---------|-------|
| `docs/archive/deprecated_modules/` | Historical archive |
| `docs/chronicles/` | Generated chronicles, not live entry surfaces |

---

## Lineage Rules For Later Agents

1. Start from Category 1, then move to Category 2 only if you need depth.
2. When citing Category 3 material, label it as historical lineage.
3. The three root `.txt` files are founding documents. Respect their lineage value, but do not treat them as current specifications.
4. `docs/README.md` and `docs/INDEX.md` serve different roles: guided entry versus comprehensive index.
5. `.archive/` is a hard boundary. Nothing inside it is current or importable.
