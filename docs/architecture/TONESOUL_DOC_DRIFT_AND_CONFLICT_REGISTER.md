# ToneSoul — Doc Drift And Conflict Register

> Purpose: compare the prior entrypoint cleanup recommendations against the current repo state and classify each as still valid, drifted, already fixed, or invalidated.
> Last Updated: 2026-03-29
> Authority: drift-reconciliation register. Does not outrank runtime code or canonical contracts.
> Status: historical 2026-03-29 reconciliation snapshot. Major entry cleanup landed on 2026-04-14, so this file should be read as lineage, not as the latest unresolved work queue.

---

## Conflict Register

### From Deliverable AD (Audience Routing And Entry Contract)

| AD recommendation | Current repo says | Verdict | Safest correction |
|------------------|-------------------|---------|-------------------|
| AI agents should follow: `AI_QUICKSTART → session start → AI_ONBOARDING as needed` | README.md line 121 presents `AI_ONBOARDING.md`, `docs/AI_QUICKSTART.md`, and `python scripts/start_agent_session.py` as a **simultaneous triad**, not a priority sequence | **drifted** | AD should describe the AI entry as a triad. AI_ONBOARDING is an equal first-hop surface, not a "later reference." The recommendation that AI_ONBOARDING should not be read first should be softened to: "start with the AI Reading Stack table at the top, not the If-wall in the middle." |
| Developer first read is `docs/GETTING_STARTED.md` | README.md line 119 lists `docs/GETTING_STARTED.md` first for developers | **still valid** | No correction needed |
| Researcher first read is `README.md` | README.md line 120 lists `TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md` first for researchers | **drifted** | AD should match: researcher entry starts at the architecture doc, not README.md |
| Curious human first read is `SOUL.md` | README.md line 122 lists `SOUL.md` first | **still valid** | No correction needed |

### From Deliverable AE (Historical Spec And Legacy Surface Map)

| AE claim | Current repo says | Verdict | Safest correction |
|----------|-------------------|---------|-------------------|
| `docs/architecture/` contains "46 files, all contracts" | Actual: 54 files. 20 are `*_CONTRACT.md`, 9 are `*_MAP.md`, 3 are `*_MATRIX.md`, rest are other types | **invalidated** | Use corrected counts from the new `TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md` |
| `README_EN.md` is "older English version, redundant" | `README.md` IS the English version. `README_EN.md` (6.4KB) is smaller and older. | **still valid** | `README_EN.md` remains likely redundant, but final deprecation requires human decision |
| Historical `.txt` files "have mojibake risk" | Files are clean UTF-8 with BOM. No corruption. | **invalidated** | Remove "mojibake risk" language from any future reference to these files |

### From Deliverable AF (Encoding And Mojibake Hazard Register)

| AF claim | Current repo says | Verdict | Safest correction |
|----------|-------------------|---------|-------------------|
| H1: "AI_ONBOARDING If wall is 60 lines, 20+ If-branches, lines 28-87" | Canonical anchor list is lines 28-44 (12 numbered items). If-routing wall is lines 45-87 (43 statements, not 20+). Total is not "60 lines of Ifs" — it is 17 lines of numbered list + 43 lines of If-statements. | **partly true, numerically wrong** | Correct to: "43 If-routing statements on lines 45-87, preceded by a 12-item canonical anchor list on lines 28-44" |
| H2: "AI_ONBOARDING has duplicate Purpose/Last-Updated" | Lines 24-26 do have a second older header block ("Below: Original architecture document index. Purpose... Last Updated: 2026-03-28") below the current header (line 3-6, Last Updated: 2026-03-29) | **still valid** | Clean the second header block |
| H3: "TAE-01 has contradictory Status vs Purpose" | Still reads "Status: Definitive / Audit-Ready" + "Purpose: ...historical specification surface" | **still valid** | Change Status to "Historical / Lineage Reference" |
| H4: "MGGI_SPEC has duplicate Purpose/Last-Updated" | Still has duplicate lines 4-5 and 6-7 | **still valid** | Remove duplicate |
| M2: "docs/INDEX.md vs docs/README.md near-duplicate" | Both still exist at 24.7KB and 19.5KB | **still valid** | Differentiation recommendation remains appropriate |
| M5: "Root .txt files format mismatch" | They are `.txt` with ASCII art headers in a markdown-native repo | **still valid** | Labeling or conversion recommendation remains appropriate, but "mojibake risk" part should be removed |
| Overall "no actual mojibake" conclusion | ✅ Confirmed by byte-level reasoning | **still valid** | Correct diagnosis |

### From Deliverable AG (Simplification Boundary Contract)

| AG recommendation | Current repo says | Verdict | Safest correction |
|------------------|-------------------|---------|-------------------|
| Rule 1: "Collapse link walls with >8 consecutive links into `<details>`" | README.md lines 184+ already uses `<details>` for the architecture wall. AI_ONBOARDING does not yet use this pattern. | **still valid** | The rule points in the right direction. Note that README.md already implements this pattern as a reference model. |
| Rule 3: "Evidence posture must be surfaced near claims" | README.md lines 171-180 already implements this with the "Evidence Honesty" section. | **still valid** | Already implemented in README. Should be propagated to other entry surfaces. |
| Rule 5: "Historical docs may remain linked but must be labeled as lineage" | No entry surface currently labels historical docs as such. MGGI_SPEC and TAE-01 are linked in README.zh-TW.md without lineage labels. | **still valid** | Labeling remains needed |
| Rule 6: "Differentiate docs/README.md vs docs/INDEX.md" | Neither has been changed. | **still valid** | Still needed |

### From Deliverable AH (Cleanup Wave Candidates)

| Wave | Prior status | Current status | Verdict |
|------|-------------|----------------|---------|
| Wave 1: Metadata hygiene (TAE-01, MGGI, AI_ONBOARDING, docs/README footer, INDEX counts) | Not started | Nothing in this wave has been done | **still valid** |
| Wave 2: The If Wall | Not started | AI_ONBOARDING If wall unchanged | **still valid** — but line numbers and If-count should be corrected to 43 on lines 45-87 |
| Wave 3: Index differentiation | Not started | docs/README.md and docs/INDEX.md unchanged | **still valid** |
| Wave 4: Quickstart streamlining | Not started | AI_QUICKSTART unchanged | **still valid** |
| Wave 5: Root .txt lineage labeling | Not started | .txt files unchanged | **still valid** — but remove "mojibake risk" language |
| Wave 6: Content sync | Not started | README.zh-TW.md still at 2026-03-22 | **still valid** |

---

## Summary: What Survives This Reality Pass

### Recommendations that should be kept (with corrections noted above):

1. ✅ Wave 1 metadata hygiene — all 5 items remain valid and easy
2. ✅ Wave 2 If-wall grouping — corrected to 43 statements on lines 45-87
3. ✅ Wave 3 index differentiation — unchanged
4. ✅ Wave 4 quickstart streamlining — unchanged
5. ✅ Wave 5 lineage labeling — valid minus "mojibake risk" language
6. ✅ Wave 6 content sync — valid
7. ✅ TAE-01 Status line fix — valid
8. ✅ README.zh-TW.md sync — valid

### Recommendations that should be retired:

1. ❌ "Root .txt files have mojibake risk" — no evidence of any encoding problem
2. ❌ "46 architecture contracts" — the real count is 54 files, of which 20 are contracts
3. ❌ "AI agents should read AI_QUICKSTART first, not AI_ONBOARDING" — the current README presents them as a triad; AI_ONBOARDING is not a secondary reference
4. ❌ "Researcher first-read is README.md" — the current README puts the architecture doc first for researchers

### Recommendations that should be corrected:

1. 🔄 AI entry routing: describe as triad (`AI_ONBOARDING` + `AI_QUICKSTART` + `start_agent_session.py`), not a sequence
2. 🔄 The If wall: correct from "20+ branches on lines 28-87" to "43 statements on lines 45-87"
3. 🔄 All count references: use the patterns defined in `TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md`
