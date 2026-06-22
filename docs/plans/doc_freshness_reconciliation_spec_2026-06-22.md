# Spec — Doc-Freshness Reconciliation (work order for Codex)

> Status: bounded work-order spec; **not** ratified into task.md (ratification is an owner act).
> Author: Claude (Opus 4.8), architect lane — **ground-truth numbers verified by Claude** ·
> Implementer: Codex · Reviewer: Claude (cross-AI loop).
> Last updated: 2026-06-22.
>
> **Framing — read first.** This is **stale-reference repair on the project's public-facing
> docs**, not new content. A skeptical AI architect who cross-checks the docs currently hits
> self-contradictions (7 vs 8 axioms, 254 vs 280 modules, ~1,900 vs ~7,800 tests, a Safety
> "rewrite" claim the code contradicts). Contradictions cost trust faster than missing docs. This
> is the recurring **stale-reference family**, now on the outward face. Fix = align to verified
> ground truth; **prefer pointing at a live source over hardcoding a number that rots.**

## Verified ground truth (Claude checked against source 2026-06-22 — do NOT re-derive wrong)

- **Axioms = 8.** `AXIOMS.json` (version 1.2.0) `axioms` is a list of 8. Any "7 axioms" / "seven
  axioms" / "The 7 Axioms" as a *current-tense* claim is stale (Axiom 8 = Memory Sovereignty,
  added 2026-04).
- **Modules ≈ 280.** `docs/status/codebase_graph_latest.md` (auto-generated, current) reports
  **280**; actual `tonesoul/*.py` count is **283**. "254 modules" is stale. **Prefer pointing to
  `codebase_graph_latest.md` over hardcoding any number.**
- **Test count DRIFTS — do not hardcode a bare number.** Local `pytest --collect-only` now = 7,870;
  `README.md` says "7,778 collected / 7,777 passing, 2026-06-16 clean-CI" (dated + sourced = the
  honest pattern). "~1,900+" is a 2026-03 snapshot. Reconcile stale test numbers by **dating +
  sourcing** (point to README's clean-CI line / CI), not by writing a fresh bare number that will
  rot next PR. (Note: README's 7,778 is itself now slightly behind ~7,870 because PRs #159–#164
  added tests; refreshing it needs a real **clean-CI** count, not a local one — watch the
  local-vs-clean pollution issue. Lower priority; it is dated, so honest-as-of.)
- **Safety "rewrite": VERIFY against code, code wins.** `README.md`/`DESIGN.md` say there is **no
  rewrite path**; `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md` has a card
  saying Safety "blocks / rewrites / audits". Check the actual gate code under `tonesoul/`; align
  the doc to whatever the code actually does (almost certainly "no rewrite" → fix the overview).

## Exact edit list (locations Claude grepped — verify each, fix in place)

**"7 axioms" → 8** (current-tense factual claims only):
- `docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md` (~L42, L185, and the header `~363 files /
  ~1900 tests` at L11 — see tests below)
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md` (~L10)
- `docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md` (~L268; also tests below)
- `docs/narrative/TONESOUL_ANATOMY.md` (~L1285)
- `docs/narrative/TONESOUL_CODEX_READING.md` (~L83)
- `docs/design/tonesoul-reference/SKILL.md` (~L28)
- `docs/plans/tonesoul_high_risk_domain_trial_gate_2026-04-08.md` (~L103)
- `docs/TRUTH_STRUCTURE.md` (~L315)
- **DO NOT touch `CHANGELOG.md`** (its "7 → 8" lines are correct *historical record*).
- `docs/visual/_pending_thesis_sync/README.md` L52 tracks "Finding 6 (7 vs 8 axioms): 未動" — once
  reconciled, update that tracking note.

**"254 modules" → point to codebase_graph (280)**:
- `DESIGN.md` (~L8), `docs/design/tonesoul-reference/sources/DESIGN.md` (~L8),
  `docs/CORE_MODULES.md` (~L9), `docs/FILE_PURPOSE_MAP.md` (~L8), `docs/KNOWLEDGE_GRAPH.md` (~L6),
  `docs/design/tonesoul-reference/sources/README.md` (~L156).
  Preferred fix: "~280 modules (see `docs/status/codebase_graph_latest.md`)" rather than a bare 254→280.

**"~1,900+ tests" (2026-03 stale)**:
- `docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md` (~L11),
  `docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md` (~L10, L31).
  Fix by dating + sourcing (point to README clean-CI line / CI); do not hardcode a new bare count.

**Safety "rewrite"**: `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md` — verify
vs code, align (code wins).

**`docs/GETTING_STARTED.md`**: stale (2026-03-23) + off-message (frames the project as a
personality/memory toy — the exact thing DESIGN/POSITIONING disclaim). Refresh to the current
install (`pip install tonesoul52[dev]`) + the honest posture, **or** retire it and redirect to
README/POSITIONING. Your judgment; explain the choice in the PR.

## Disciplines

- **Canonical / code wins.** Where a doc and the code disagree, fix the doc.
- **Prefer a live source over a rotting number** (codebase_graph for modules, README clean-CI line /
  CI for tests). Hardcoded counts are why this drift happened.
- For any dated doc you edit (matrix, topology map carry "Last Updated"), **bump the date + add a
  one-line "counts reconciled 2026-06-22 against AXIOMS.json / codebase_graph" note** so the next
  reader sees it is fresh, not another stale snapshot.
- **Do NOT touch** `CHANGELOG.md` (historical), `AGENTS.md`, `MEMORY.md`, `.env` (protected).
- Encoding clean: UTF-8, no BOM, **LF** (the recurring lesson — verify with `read_bytes`, not
  `read_text`).
- No code/runtime change; docs only.

## Verification (run before reporting)

- `grep` confirms no current-tense "7 axioms" / "seven axioms" / "The 7 Axioms" remain **outside
  CHANGELOG and historical/changelog contexts**.
- `grep` confirms no "254 modules" remain.
- The Safety card matches the actual gate code.
- Every edited file: UTF-8 / no BOM / LF (byte-level check).
- Links still resolve; dated docs have bumped dates + the reconciliation note.
- Report what you changed per file + the grep evidence that the stale claims are gone.

## Hand-off

Codex executes the edits; Claude independently reviews (re-greps for residual stale claims, spot-
checks the Safety-vs-code alignment, byte-level encoding) and lands. **Compute division:** the
verification/judgment is done (above); this is the mechanical multi-doc labor — Codex's lane.
