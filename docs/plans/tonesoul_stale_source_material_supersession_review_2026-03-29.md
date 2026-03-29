# ToneSoul Stale Source-Material Supersession Review (2026-03-29)

> Status: cleanup review
> Purpose: record which leftover raw source-material drafts have already been absorbed, superseded, or invalidated by current ToneSoul runtime and documentation
> Scope: 4 stale drafts left outside the authority lanes after the README, prompt-topology, and PATH cleanup waves

---

## Why This Review Exists

Several untracked drafts were still sitting in the worktree even though their useful ideas were already absorbed into newer ToneSoul-native contracts, runtime phases, or entry surfaces.

Leaving those raw drafts in place creates three avoidable problems:

1. later agents mistake superseded analysis for pending authority
2. stale implementation gaps get cited after runtime work already closed them
3. mojibake-heavy source material competes with clean current-state docs

This review keeps the useful decisions and removes the stale wrappers.

---

## Supersession Table

| Raw Draft | Current Status | Why It Is Stale | Superseded By |
|---|---|---|---|
| `docs/architecture/TONESOUL_IMPLEMENTATION_GAP_TRIAGE_2026-03-27.md` | superseded, do not integrate | It still treats POAV gate, Risk (R), and ContractObserver blocking as open gaps, but those were already implemented in later Codex phases. | `task.md`, `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`, `docs/status/claim_authority_latest.md`, current runtime code and tests |
| `docs/plans/tonesoul_gap_followup_candidates_2026-03-27.md` | superseded, do not integrate | It proposes future tickets for gaps that are no longer gaps or are already closed enough to belong in current-state docs rather than old follow-up notes. | `task.md`, current runtime phases, `docs/status/claim_authority_latest.md` |
| `docs/plans/borrowable_prompt_patterns_from_industry_2026-03-29.md` | absorbed then retired | The draft is mojibake-heavy and was only useful as source material. The useful adoption decisions already landed in ToneSoul-native prompt-discipline docs and prompt-surface adoption work. | `docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`, `docs/architecture/TONESOUL_PROMPT_VARIANTS.md`, `docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md`, `docs/architecture/TONESOUL_PROMPT_SURFACE_*` lane |
| `docs/plans/readme_restructure_plan_2026-03-29.md` | superseded by live entrypoint rewrite | The draft still routes AI readers toward `CLAUDE.md` and contains stale structure assumptions. The public README and entry-cleanup lane already replaced it with the correct AI entry triad and grouped architecture map. | `README.md`, `docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md`, `docs/architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md` |

---

## Detailed Notes

### 1. Implementation-Gap Triage

This draft was useful when the repo still needed a clean separation between "runtime now" and "future implementation plan."

It is now stale because it predates several later runtime phases:

- bounded POAV gate enforcement
- runtime risk posture / `Risk (R)` surface
- ContractObserver critical blocking
- drift alert guidance

The right current truth is no longer "what should we maybe build?" but:

- what is already implemented
- what evidence backs it
- what remains documentary versus runtime-present

That truth now lives in the claim-authority and evidence lanes, not in this old triage memo.

### 2. Gap Follow-Up Candidates

This file is just the implementation-gap draft compressed into ticket paragraphs.

Once the corresponding runtime phases shipped, the candidate list stopped being a useful planning artifact and became a source of duplicate roadmaps.

Current planning authority should come from:

- `task.md`
- current runtime surfaces
- current evidence / authority docs

not from a stale candidate list generated before those phases completed.

### 3. Borrowable Prompt Patterns From Industry

This file served as external-source rough notes. It should not survive as a worktree document because:

- it contains visible mojibake noise
- it uses foreign framing instead of ToneSoul-native naming
- its useful ideas were already translated into:
  - prompt discipline skeleton
  - prompt variants
  - prompt starter cards
  - prompt topology / adoption docs

The useful outcome is already kept. The raw extraction layer no longer adds value.

### 4. README Restructure Plan

This draft was useful before the README rewrite landed. It is now stale because:

- the public README already has the 30-second map
- grouped system areas already replaced the link wall
- AI entry is now `AI_ONBOARDING -> AI_QUICKSTART -> start_agent_session`
- the draft still points AI toward `CLAUDE.md`, which is not the public canonical AI entry

The right place to understand entry structure now is the live README plus the audience-routing and simplification contracts.

---

## Cleanup Decision

Action taken for these 4 drafts:

- keep no raw file as authority
- keep no raw file as pending integration item
- preserve useful decisions only through already-landed ToneSoul-native docs
- remove the stale raw drafts from the worktree

---

## What Still Remains Open

This review does **not** claim that ToneSoul has no remaining short boards.

It only says these 4 specific raw drafts are no longer the right place to track them.

Short-board planning should continue through:

- `task.md`
- current authority lanes
- current evidence lanes
- current runtime / packet / session-start surfaces

---

## Relationship To Other Cleanup Reviews

- `docs/plans/tonesoul_path_theory_adoption_review_2026-03-29.md`
  - source-material distillation for PATH-derived theory notes
- this document
  - source-material distillation for stale gap, prompt-source, and README-source drafts

Together they reduce the number of raw external or pre-integration notes competing with current ToneSoul-native contracts.
