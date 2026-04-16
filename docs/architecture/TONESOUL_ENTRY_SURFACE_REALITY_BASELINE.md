# ToneSoul — Entry Surface Reality Baseline

> Purpose: repo-grounded baseline for current entry surfaces after correcting drift between the prior entrypoint pass and the live repo state.
> Last Updated: 2026-03-29
> Authority: reality-alignment aid. Does not outrank runtime code, tests, `AXIOMS.json`, or canonical architecture contracts.
> Status: historical 2026-03-29 baseline. Use current entry surfaces for live routing, and use this file as a reality-pass record rather than the latest entry policy.

---

## Self-Correction: Where The Prior Pass Under-Verified

### Error 1: Count inflation

| Prior pass said | Actual (re-measured 2026-03-29 after reality-pass deliverables landed) | Error type |
|----------------|------------------------------|------------|
| "46 architecture contracts" | `docs/architecture/*`: **54 files** | Undercount. 54 total files, not 46. |
| (implied) "46 contracts" | `docs/architecture/TONESOUL_*`: **44 files** | Naming confusion. Only 44 have the `TONESOUL_` prefix; 10 others have different prefixes. |
| (implied all were *_CONTRACT.md) | `docs/architecture/TONESOUL_*_CONTRACT.md`: **20 files** | Severe overcount. 20 actual contracts, not 46. The prior pass called all 46 files "contracts" when the directory also contains `*_MAP.md` (9), `*_MATRIX.md` (3), `*_DOCTRINE.md` (1), and other `TONESOUL_*` naming families (12), plus non-TONESOUL files (10). |

**Actual directory composition (54 files):**

| Pattern | Count | Examples |
|---------|-------|---------|
| `TONESOUL_*_CONTRACT.md` | 20 | `TONESOUL_L7_RETRIEVAL_CONTRACT.md`, `TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md` |
| `TONESOUL_*_MAP.md` | 9 | `TONESOUL_AXIOM_FALSIFICATION_MAP.md`, `TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md` |
| `TONESOUL_*_MATRIX.md` | 3 | `TONESOUL_CLAIM_AUTHORITY_MATRIX.md`, `TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md` |
| `TONESOUL_*` (other naming) | 12 | `TONESOUL_ABC_FIREWALL_DOCTRINE.md`, `TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md` |
| non-TONESOUL files | 10 | `DOC_AUTHORITY_STRUCTURE_MAP.md`, `HISTORICAL_DOC_LANE_POLICY.md`, `RFC-003_Lightweight_ToneSoul.md` |

### Error 2: AI entry routing drift

The prior pass described the AI entry as:

> "AI 代理先讀 AI_QUICKSTART → 跑 session start → 有具體問題時才回 AI_ONBOARDING"

This partially matches the live README but missed that the **current README (line 121)** defines the AI entry as a **triad**, not a sequence with AI_QUICKSTART alone:

```
AI Agent | AI_ONBOARDING.md, docs/AI_QUICKSTART.md,
           python scripts/start_agent_session.py --agent <id>
```

The three are presented as a set, not a recommended-reading-order. `AI_ONBOARDING.md` is not a "later reference" — it is one of three parallel entry surfaces in the current live README.

### Error 3: The "If wall" description was structurally correct but numerically wrong

| Prior pass said | Actual |
|----------------|--------|
| "60 lines" | 43 lines (lines 45-87) |
| "20+ If branches" | **43** individual "If..." routing statements |
| "lines 28-87" | Lines 28-44 are the 12-item canonical architecture anchor list. The If-routing wall starts at line 45 and ends at line 87. |

The hazard is **real and even worse** than described — 43 routing statements is more than 20, not less — but the line count was wrong and the boundary between the numbered list and the If-wall was not distinguished.

### Error 4: Encoding assessment was correct but reasoning was display-dependent

The prior pass correctly concluded "no mojibake found" but relied partly on `view_file` output (which auto-transcodes) rather than explicitly separating:
- file-layer encoding truth (UTF-8 content intact)
- terminal rendering artifacts (PowerShell cp950 may show `??` for CJK paths)
- structural readability problems (the actual hazards)

The conclusion was correct. The diagnostic method was insufficiently rigorous.

---

## Current Live Entry Surfaces (Verified Against README.md 2026-03-29)

### README.md "Choose Your Entry" (lines 117-122) — The source of truth

| Audience | README Currently Points To | Status |
|----------|---------------------------|--------|
| **Developer** | `docs/GETTING_STARTED.md` → `docs/README.md` → `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` | `current` |
| **Researcher** | `TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` → `TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md` → `TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md` | `current` |
| **AI Agent** | `AI_ONBOARDING.md` + `docs/AI_QUICKSTART.md` + `python scripts/start_agent_session.py --agent <id>` | `current` — this is a **triad**, not a priority sequence |
| **Curious Human** | `SOUL.md` → `LETTER_TO_AI.md` → `README.zh-TW.md` | `current` |

### AI_ONBOARDING.md internal structure (verified)

| Section | Lines | Content | Status |
|---------|-------|---------|--------|
| AI Reading Stack table | 10-20 | 5-lane routing with authority/use-when/anti-pattern columns | `current` |
| Minimum requirement block | 20 | Session start/end with readiness check | `current` |
| Legacy header (second metadata block) | 24-26 | Old Purpose/Last-Updated below the current one | `stale` — should be cleaned |
| Canonical Architecture Anchor (numbered list) | 28-44 | 12-item reading list for architecture claims | `current` |
| If-routing wall | 45-87 | 43 individual "If..." conditional routing sentences | `current but structurally hazardous` |
| Session Start protocol | 89-115 | Governance state loading instructions | `current` |
| The rest | 116-234 | Core concepts, forbidden actions, directory structure | `current` |

### README.md "Five System Areas" (lines 124-170)

This is a **Codex addition** that already groups the architecture links by topic with 3 links each. The prior pass did not reference this section because it was working from an older mental model. This section is the current best practice for categorized access to architecture documents and already partially solves the "grouping" problem that the prior pass recommended for `AI_ONBOARDING.md`.

### README.md "Evidence Honesty" (lines 171-180)

This section establishes the repo's evidence discipline for public readers. The prior pass recommended keeping this visible. That recommendation is still correct and must not be weakened.

---

## Prior Recommendation Reconciliation

| Prior recommendation | Current repo reality | Status |
|---------------------|---------------------|--------|
| "Restructure AI_ONBOARDING If wall into grouped `<details>` sections" | The If wall (43 lines, L45-87) still exists unchanged. README.md already uses `<details>` + grouped categories for the same architecture links (L184+). | **still valid** — AI_ONBOARDING should be improved to match the pattern already used in README.md |
| "Fix TAE-01 Status line from 'Definitive/Audit-Ready' to 'Historical'" | TAE-01 has not been changed. | **still valid** |
| "Remove duplicate Purpose/Last-Updated in MGGI_SPEC, TAE-01, AI_ONBOARDING" | None have been changed. | **still valid** |
| "Differentiate docs/README.md vs docs/INDEX.md" | Neither has been changed. | **still valid** |
| "Collapse AI_QUICKSTART R-memory command block into `<details>`" | AI_QUICKSTART has not been changed. | **still valid** |
| "docs/architecture contains 46 contracts" | **incorrect** — 54 files total, of which only 20 are `*_CONTRACT.md`. The prior pass inflated both the total and the naming. | **invalidated** — must use corrected counts |
| "AI entry sequence: AI_QUICKSTART first → then session start → then AI_ONBOARDING as needed" | **drifted** — README.md presents the AI entry as a simultaneous triad, not a priority sequence. AI_ONBOARDING is a first-read surface alongside AI_QUICKSTART, not a later reference. | **drifted** — routing recommendation should be reconciled to the triad |
| "Root .txt files have mojibake risk" | **already correct** — no actual mojibake found. But the prior pass raised it as a "risk" when verification showed it was clean. | **retired** — should not appear as a risk in future reports |
| "README.zh-TW.md not synced with Evidence Honesty section" | README.zh-TW.md still says "Last Updated: 2026-03-22" while README.md says 2026-03-29. The Evidence Honesty section has not been translated. | **still valid** |
| "Remove stale 'Last updated' footer from docs/README.md" | docs/README.md line 311 still says "Last updated: 2026-03-22". | **still valid** |
