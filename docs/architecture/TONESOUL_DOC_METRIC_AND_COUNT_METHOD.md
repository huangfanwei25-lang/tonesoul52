# ToneSoul — Doc Metric And Count Method

> Purpose: define reproducible counting methods for doc families so later prose no longer casually says "46 contracts" when the actual directory shape means something different.
> Last Updated: 2026-03-29
> Authority: metric hygiene aid. Does not outrank runtime code or canonical contracts.

---

## Why This Exists

The prior entrypoint pass said the repository had "46 architecture contracts in `docs/architecture/`". That number was wrong in three ways:

1. The file count is currently 54, not 46
2. Only 44 of those 54 have the `TONESOUL_` prefix
3. Only 20 of those 44 match `*_CONTRACT.md`

Casual prose that says "46 contracts" smuggles the wrong impression: that the directory is a flat sea of 46 interchangeable documents. It is not. It contains contracts, maps, matrices, doctrines, skeletons, cards, variants, RFCs, and other naming patterns, each with a different information role.

This document defines the exact counting patterns so later agents can quote verified numbers.

---

## Counting Methods

### Metric 1: Total `docs/architecture/*` files

**Pattern**: `Get-ChildItem -Path "docs/architecture/*" -File | Measure-Object`

**What is included**: Every file in the `docs/architecture/` directory, regardless of prefix or extension.

**What is excluded**: Subdirectories (none currently exist).

**Current value (2026-03-29, after the reality-pass deliverables landed)**: **54**

**When to use**: When making a general statement about the size or density of the architecture directory.

**Correct prose**: "The `docs/architecture/` directory contains 54 files as of 2026-03-29."

**Incorrect prose**: ~~"There are 54 architecture contracts."~~ (Not all files are contracts.)

---

### Metric 2: Total `docs/architecture/TONESOUL_*` files

**Pattern**: `Get-ChildItem -Path "docs/architecture/TONESOUL_*" -File | Measure-Object`

**What is included**: Files whose name starts with `TONESOUL_`.

**What is excluded**: 10 files with other naming patterns (`BASENAME_DIVERGENCE_DISTILLATION_MAP.md`, `council_diagrams.md`, `DOC_AUTHORITY_STRUCTURE_MAP.md`, `ENGINEERING_MIRROR_OWNERSHIP_MAP.md`, `HISTORICAL_DOC_LANE_POLICY.md`, `KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`, `PARADOX_FIXTURE_OWNERSHIP_MAP.md`, `PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`, `RFC-003_Lightweight_ToneSoul.md`, `RFC-003-AI-Metacognition.md`).

**Current value (2026-03-29, after the reality-pass deliverables landed)**: **44**

**When to use**: When making a statement about ToneSoul-namespaced boundary documents.

**Correct prose**: "There are 44 `TONESOUL_*` files in the architecture directory as of 2026-03-29."

---

### Metric 3: Total `docs/architecture/TONESOUL_*_CONTRACT.md` files

**Pattern**: `Get-ChildItem -Path "docs/architecture/TONESOUL_*_CONTRACT.md" -File | Measure-Object`

**What is included**: Files whose name matches the full pattern `TONESOUL_*_CONTRACT.md`.

**What is excluded**: Maps (`*_MAP.md`, 13 files), matrices (`*_MATRIX.md`, 2 files), doctrines (`*_DOCTRINE.md`, 1 file), skeletons, cards, variants, and all non-TONESOUL files.

**Current value (2026-03-29, after the reality-pass deliverables landed)**: **20**

**When to use**: When specifically counting boundary contracts.

**Correct prose**: "There are 20 `TONESOUL_*_CONTRACT.md` files as of 2026-03-29."

**Incorrect prose**: ~~"There are 46 architecture contracts."~~

---

### Metric 4: TONESOUL_* naming subtypes

| Suffix pattern | Count | Information role |
|---------------|-------|-----------------|
| `*_CONTRACT.md` | 20 | Boundary contracts with rules and decision tables |
| `*_MAP.md` | 9 | Topology/classification maps |
| `*_MATRIX.md` | 3 | Multi-column claim/evidence matrices |
| `*_DOCTRINE.md` | 1 | ABC Firewall — a named governance doctrine |
| Other TONESOUL_* naming families | 11 | Baselines, registers, skeletons, cards, variants, recommendations, and other non-contract/non-map artifacts |
| **Total TONESOUL_*** | **44** | |

---

### Metric 5: Root markdown entry surfaces

**Pattern**: `Get-ChildItem -Path "*.md" -File | Measure-Object`

**Current value (2026-03-29)**: **24** (includes `task.md` and `walkthrough.md` which are workspace files, not entry documents)

**Effective entry surfaces**: ~22 (excluding `task.md`, `walkthrough.md`)

---

### Metric 6: docs-level files (direct children only)

**Pattern**: `Get-ChildItem -Path "docs/*" -File | Measure-Object`

**Current value (2026-03-29)**: **108**

**What is included**: Direct children of `docs/`. Does **not** include files in subdirectories like `docs/architecture/`, `docs/status/`, `docs/plans/`, etc.

---

## Prose Hygiene Rules

1. **Never say "N contracts"** unless you have verified that all N files match `*_CONTRACT.md`. Maps, matrices, and doctrines are not contracts.

2. **Always specify the count pattern** when quoting a number in an architecture claim. Example:
   - ✅ "There are 20 ToneSoul boundary contracts (`TONESOUL_*_CONTRACT.md`) as of 2026-03-29."
   - ❌ "There are 54 architecture contracts."

3. **Expect these counts to change** as new deliverables are added. Do not embed counts in prose without noting the snapshot date, and prefer citing the counting pattern over treating the number as timeless.

4. **The directory is not flat** in semantic role — even though it is flat in filesystem terms. Contracts, maps, matrices, and doctrines serve different functions and should not be treated interchangeably.
