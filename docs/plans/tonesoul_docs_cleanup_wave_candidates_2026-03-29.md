# ToneSoul Docs Cleanup Wave Candidates (2026-03-29)

> Purpose: bounded cleanup sequence derived from the audience-routing, lineage, encoding, and simplification aids so cleanup can happen in realistic waves instead of one giant pass.
> Last Updated: 2026-03-29
> Measured Snapshot: `docs/architecture/*=55`, `docs/architecture/TONESOUL_*=45`, `docs/architecture/TONESOUL_*_CONTRACT.md=21`, `docs/*=108`, `root *.md=24`

---

## Wave 1: Metadata Hygiene

**Goal**: Remove contradictory or duplicate metadata that misleads later agents.

| Task | File | What To Do |
|------|------|-----------|
| 1a | `TAE-01_Architecture_Spec.md` | Change the status to historical lineage and remove duplicate purpose/date lines |
| 1b | `MGGI_SPEC.md` | Remove duplicate purpose/date lines |
| 1c | `AI_ONBOARDING.md` | Remove the second header block |
| 1d | `docs/README.md` | Remove stale footer date |
| 1e | `docs/INDEX.md` | Update subdirectory counts (`architecture=55`, `notes=6`) |

**Risk**: None. Pure metadata correction.

---

## Wave 2: The If Wall

**Goal**: Turn `AI_ONBOARDING.md` from one flat conditional wall into grouped, navigable sections.

| Task | File | What To Do |
|------|------|-----------|
| 2a | `AI_ONBOARDING.md` | Group the routing wall into topic sections with headers and `<details>` while keeping the most-used routes visible |
| 2b | `README.zh-TW.md` | Apply the same grouping pattern to the Chinese routing cascade |

**Risk**: Medium. Preserve all links; change structure, not meaning.

---

## Wave 3: Index Differentiation

**Goal**: Stop `docs/README.md` and `docs/INDEX.md` from behaving like near-duplicates.

| Task | File | What To Do |
|------|------|-----------|
| 3a | `docs/README.md` | Keep it as guided entry and add a clear pointer to `INDEX.md` for the flat listing |
| 3b | `docs/INDEX.md` | Keep it as the comprehensive flat index and point back to `README.md` for guided reading |

**Risk**: Low. This is role clarification, not authority mutation.

---

## Wave 4: Quickstart Streamlining

**Goal**: Make `docs/AI_QUICKSTART.md` feel like a real 60-second entry.

| Task | File | What To Do |
|------|------|-----------|
| 4a | `docs/AI_QUICKSTART.md` | Keep the minimum command path visible and move the longer coordination block behind `<details>` |

**Risk**: Low. No content removed.

---

## Wave 5: Root Lineage Labeling

**Goal**: Make root `.txt` lineage documents recognizable without silently erasing them.

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Label only | Lowest risk | Root still looks crowded |
| B | Convert to `.md` | Better rendering | Changes the original format |
| C | Move to a lineage directory | Cleanest root | Requires redirect and citation verification |

**Recommendation**: Option A is safest. Option C is cleanest but requires extra verification.

---

## Wave 6: Companion Sync

**Goal**: Sync lagging companion entry surfaces.

| Task | File | What To Do |
|------|------|-----------|
| 6a | `README.zh-TW.md` | Sync evidence honesty and current grouped entry structure |
| 6b | `README_EN.md` | Decide whether to deprecate or redirect it |

**Risk**: Medium. Public-facing translation quality matters.

---

## What Not To Do

- Do not mutate `AXIOMS.json`
- Do not mutate `AGENTS.md`
- Do not rewrite runtime code, packet schema, or session scripts as part of docs cleanup
- Do not hide canonical deep lanes from the index
- Do not delete historical documents
- Do not merge `docs/README.md` and `docs/INDEX.md` blindly
