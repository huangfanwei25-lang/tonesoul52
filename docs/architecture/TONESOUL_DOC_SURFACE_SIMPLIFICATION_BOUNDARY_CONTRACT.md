# ToneSoul Doc Surface Simplification Boundary Contract

> Purpose: define which simplification moves are safe when reducing entrypoint complexity, and which moves would flatten authority or hide important depth.
> Last Updated: 2026-03-29
> Authority: documentation boundary aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.
> Measured Snapshot: 2026-03-29 (`docs/architecture/TONESOUL_*_CONTRACT.md=21`, `docs/*=108`, `root *.md=24`)

---

## Why This Contract Exists

ToneSoul documentation is now large enough that naive cleanup can do real damage.
Without explicit rules, a well-intentioned simplification can:

1. **flatten authority** by hiding canonical surfaces behind the same collapsible UI as low-priority surfaces
2. **lose depth** by treating specialist lanes as clutter
3. **break routing** by rewriting the entry triad without preserving current audience flow

This contract defines what may be simplified and what must stay visible.

---

## Simplification Rules

### Rule 1: Long link walls may be grouped and collapsed

Safe when a surface has more than 8 consecutive links or routing branches without grouping.

**Apply by**:
- keeping the top 3-5 highest-priority links visible
- grouping the rest by topic
- using `<details>` for secondary routes

**Direct targets now**:
- `AI_ONBOARDING.md` lines 28-87
- `README.zh-TW.md` routing cascade

**Boundary**: do not collapse the AI Reading Stack or the README audience routing table.

### Rule 2: Deep specialist lanes must remain discoverable

These may be long, but their visibility is part of their value:
- `docs/narrative/TONESOUL_ANATOMY.md`
- `docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md`
- `docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`
- `docs/WHITEPAPER.md`

**Boundary**: internal sections may collapse; index visibility must not disappear.

### Rule 3: Evidence posture must travel with simplified claims

If a simplification makes a system claim easier to read, it must also preserve or link the evidence posture.

Use the evidence ladder labels:
- `E1 test-backed`
- `E2 schema-backed`
- `E3 runtime-present`
- `E4 document-backed`
- `E5 philosophical`

**Boundary**: do not flatten a claim into assertion-only prose.

### Rule 4: AI entrypoints must use operational surfaces, not local collaborator notes

The current public AI entry is the triad:
- `AI_ONBOARDING.md`
- `docs/AI_QUICKSTART.md`
- `python scripts/start_agent_session.py --agent <id>`

Architecture and boundary contracts come after that.

**Boundary**: do not route general AI entry through `CLAUDE.md`, `CODEX_TASK.md`, `CODEX_HANDBACK.md`, or other local companion notes.

### Rule 5: Historical docs may remain linked, but must be labeled as lineage

Safe labels include:
- `(historical lineage)`
- `(earlier spec)`
- `(founding narrative)`

**Boundary**: do not place historical surfaces before their canonical successors in reading order.

### Rule 6: Duplicate index surfaces must be differentiated, not merged blindly

Current safe split:
- `docs/README.md` = guided entry
- `docs/INDEX.md` = comprehensive flat index

**Boundary**: do not merge them into one oversized hybrid file without first choosing a dominant function.

### Rule 7: Quickstarts may be streamlined, but the minimum viable command path must stay visible

For `docs/AI_QUICKSTART.md`, keep the minimum visible sequence:

```text
start_agent_session -> work -> end_agent_session
```

The larger coordination block may go behind `<details>`.

**Boundary**: do not remove the full command reference entirely.

### Rule 8: Root lineage `.txt` files may be labeled, but not silently erased

Safe options:
1. Add a lineage note at the top
2. Convert to `.md` while preserving lineage labeling
3. Move to a dedicated lineage directory only with redirects and updated indexes

**Boundary**: do not silently delete or relocate them without updating the lineage map.

---

## What Must Not Be Simplified

| Surface | Why |
|---------|-----|
| `AXIOMS.json` | Constitutional |
| `AGENTS.md` | Protected |
| README audience routing table | Primary public routing surface |
| AI Reading Stack in `AI_ONBOARDING.md` | Primary AI routing surface |
| README evidence honesty section | Core epistemic posture |
| `docs/architecture/TONESOUL_*` contract substance | Simplification may change indexing, not contract substance |
| `docs/status/*_latest.json` | Generated machine-readable outputs |

---

## Summary Decision Table

| Simplification Move | Safe? | Condition |
|---------------------|-------|-----------|
| Collapse the AI_ONBOARDING "If wall" into grouped `<details>` | Yes | Keep the reading stack and top routes visible |
| Collapse `README.zh-TW.md` routing cascade | Yes | Preserve routing meaning |
| Fix stale metadata and duplicate headers | Yes | Pure hygiene |
| Differentiate `docs/README.md` and `docs/INDEX.md` | Yes | Preserve guided-versus-flat split |
| Streamline the AI quickstart command block | Yes | Keep the minimum command path visible |
| Delete historical root `.txt` files | No | They are lineage surfaces |
| Merge `docs/README.md` and `docs/INDEX.md` blindly | No | Would erase functional differentiation |
| Hide deep-lane documents from indexes | No | Their visibility is part of their value |
| Remove evidence posture to shorten entry docs | No | Violates evidence honesty |
