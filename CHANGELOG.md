# Changelog

All notable changes to ToneSoul are recorded here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with project-specific structure noted below.

## What this file is for

- **Living record of post-v1.0.0 changes**, organized by date / sprint / theme rather than rigid version cuts
- Bridge between fine-grained PR descriptions and version-level release notes (`docs/RELEASE_NOTES_v*.md`)
- The first artifact a future agent / contributor / reviewer should read after `README.md` + `CONTEXT.md` to understand what shipped recently and why

For pre-v1.0.0 history, see `docs/RELEASE_NOTES_v0.1.0.md` and `docs/RELEASE_NOTES_v1.0.0.md`.

For Day-1-of-current-sprint deep evidence, see `docs/status/calibration_sprint_2026-05-04_synthesis.md`.

---

## [Unreleased] — strategy_mirror calibration sprint

Calibration sprint phase: creator-team-internal sessions surfacing how Phase 2 `strategy_mirror` and the council perspective system behave under real conversational pressure, then shipping concrete code fixes for findings as they emerged.

### 2026-05-06 — GitHub Pages site thesis alignment

**Changed**

- `site/index.html` — public landing page (deployed at `fan1234-1.github.io/tonesoul52/`) now aligns with the `README.md` thesis articulation that landed in PR #57. Title, meta description, og description, JSON-LD `SoftwareSourceCode` description, FAQ entries, and hero sub-tagline all replace the legacy "AI governance framework / auditable, traceable, trustworthy" wording with the sharper "epistemic defense / categorical refusal of forbidden claim classes / surfaced dissent for the rest" articulation. Slogan added: *most AI safety optimizes; ToneSoul defends.*
- `site/index.html` main content — restructured "What ToneSoul Does" (six capability cards) into "Three Mechanisms of Epistemic Defense" (Hard Limits / Traceable Evidence / Externalized Evaluation), matching the README's three-mechanism breakdown. Tension Engine, Reflex Arc, Memory with Decay, and Vow System moved into a separate "Other Components" section with honest descriptive wording (heuristic signal, proxy metric, progressive responses) rather than capability promises.
- `site/index.html` "How It Differs" table — replaced the prompt-engineering comparison column with a probabilistic-optimization column (RAG / CFV / calibration), and replaced capability axes (Memory / Consistency / Self-check / Enforcement / Identity) with thesis-relevant axes (Stance toward error / Confidence handling / Trust in AI introspection / On unverifiable claims / Refusal style / Identity model).
- `site/index.html` axioms section — corrected "The 7 Axioms" to "The 8 Axioms" matching `AXIOMS.json`'s actual 8-law shape (added Memory Sovereignty as the eighth), aligned axiom names with their canonical forms, and added a brief E0 existential principle paragraph beneath the table.

**Added**

- `site/index.html` "Visible Deliberation" section — articulates that ToneSoul's refusal is not a black-box endpoint but a deliberative outcome with surfaced reasoning. Distinguishes deliberative epistemic defense from dogmatic rule-bound gatekeeping. This is the first place "visible deliberation" capability is documented; the articulation emerged from the 2026-05-06 dialogue with Fan-Wei and is intentionally surface-level here while sample size accumulates before promotion to the README.

**Not changed in this PR** (deferred):

- `site/concepts.html`, `site/story.html`, `site/getting-started.html` — still carry legacy framing; will be aligned in a follow-up PR.
- `site/style.css` — visual layer is the human collaborator's craft territory; this PR is framing-only.
- `README.md` — already carries the sharpened thesis (PR #57 + Codex audit follow-up); this PR brings the public landing page to parity, not the other direction.

### 2026-05-06 — verdict aggregation follow-up

**Fixed**

- Verdict aggregation now downgrades to `REFINE` when a concrete substantive concern is corroborated by another non-Advocate dissent. Soft epistemic-prior pairs alone still surface as dissent without downgrading benign generated text.
- Marketing overclaims such as "world's first" now reach `REFINE` instead of `APPROVE` when Critic's marketing branch is corroborated by Analyst's grounding soft prior.
- Critic subjective-keyword matching now respects ASCII token boundaries, so words like `configuration` no longer trigger the `art` subjective branch by substring.

### 2026-05-06 — transcript provenance follow-up

**Fixed**

- Council transcripts now include each vote's `evidence_chain`, matching `CouncilVerdict.to_dict()` and preserving the branch provenance needed for audit-facing review.

### 2026-05-05 (continued) — plugin compatibility follow-up

**Fixed**

- `PreOutputCouncil` now preserves pre-PR #50 custom perspective compatibility by only passing `epistemic_label=` to perspectives that declare the kwarg or accept `**kwargs`. Legacy three-argument plugin perspectives continue to run while built-in Analyst/Critic still receive the soft-prior label.

### 2026-05-05 (continued) — audit follow-up doc drift cleanup

**Changed**

- README thesis wording now distinguishes categorical refusal of forbidden claim classes from surfaced dissent for other ungrounded claims, so the public framing does not overclaim current runtime behavior.
- README test guidance now says `test.sh` mirrors the core Python gates, not every CI job; CI-only web, architecture/docs, red-team, package, and memory gates remain separate.
- CONTEXT.md and the thesis-defender skill now match `AXIOMS.json`'s current shape: 8 immutable laws plus the separate `E0` existential principle.
- CONTEXT.md now reflects PR #50: Analyst and Critic consume low/medium `epistemic_label` bands as a soft prior.
- README test-count wording now uses the latest collected suite size instead of the stale 5435-passed claim.

### 2026-05-05 (continued) — navigation-grammar-checker skill

**Added**

- `.claude/skills/navigation-grammar-checker/` — second Claude Code skill. Single-file SKILL.md articulating the 7-slot evaluation frame for AI-collaboration repository structure (Vocabulary / Operational / Change / Decision / Test entry / Agent settings / Module organization) extracted from 5 external samples (Pocock skills, shadowMAS, SwiftClip, methodology checklist, ToneSoul). Centers the **frame-not-checklist** rule that emerged from the 2026-05-05 `.claude/settings.json` audit (8 frictions listed → 0 solvable by the proposed surface → "do not add" was correct answer despite empty slot). Activates when proposing top-level files / structure / external pattern adoption. Provenance points to `reference_navigation_grammar_pattern.md` memory.

### 2026-05-05 (continued) — README thesis framing

**Changed**

- `README.md` opening — replaced buzzword paragraph ("AI governance, ethical memory systems, verifier-first agents...") with a sharp one-sentence thesis: **"ToneSoul is epistemic defense for AI."** Three mechanisms (hard limits / traceable evidence / externalized evaluation) named explicitly. Contrast against probabilistic optimization (RAG, calibration, confidence scoring like WFGY/CFV) and against orchestration framings (Karpathy's "ghost engineering") spelled out. Tagline + Axiom 4 hook preserved. SEO keywords from old paragraph already covered by `## Retrieval Keywords` section so no SEO loss. Slogan version: *most AI safety work optimizes; ToneSoul defends.* (PR #57)

This update lands the thesis articulation that emerged from the 2026-05-05 dialogue with Fan-Wei after reviewing WFGY/CFV — captured in memory at `feedback_thesis_epistemic_defense_vs_probabilistic_optimization_2026-05-05`. Sharper than prior "AI accountability framework" framing because it specifies *what* (knowledge claims) and *how* (defense, not optimization).

### 2026-05-05 — User-facing surface + thesis-defense portability

**Added**

- `test.sh` (top-level) — canonical local-dev core test entry. Mirrors the Python core gates: ruff check + bounded black gate (`scripts/run_black_gate.py --strict`, changed-files-only) + pytest. Four modes: full / lint / test / fast. CI still owns web quality, architecture/docs contracts, red-team, package integrity, and memory hygiene gates. Closes the navigation-grammar test-entry slot. (PR #54)
- `ts validate <file>` CLI subcommand — first user-facing functional surface. Reads a draft file, runs `PreOutputCouncil.validate()`, prints verdict + per-perspective dissent (per PR #45/#49 surface). Exit codes map to verdict for git hooks / CI integration: 0=APPROVE, 1=REFINE/DECLARE_STANCE, 2=BLOCK, 3=file/argument error. Supports `--json`, `--quiet`, `--intent`, `--language` flags. UTF-8-safe stdout for Chinese summaries on Windows console. (PR #55)
- `.claude/skills/tonesoul-thesis-defender/` — first Claude Code skill. SKILL.md + patterns.md articulating the 5 thesis-defense patterns that emerged from the 2026-04-26 to 2026-05-05 collaboration (capability-vs-restraint filter / cargo-cult check / audience filter / mirror+range / refuse-both-claims). Activates auto-pattern-match on design decisions, brainstorm sessions, external-influence evaluation. Closes the navigation-grammar `.claude/` slot — but with a specific use case (portable thesis-defense), not because slot-completion was the goal. (PR #56)
- Critic `MARKETING_SUPERLATIVES` set + dedicated branch — catches commercial superlatives ("world's first", "industry-leading", "前所未有", "每一個... 都應該", competitive urgency) that the existing CRITIQUE_KEYWORDS (calibrated for academic/aesthetic content) missed. Resolves Day 1 calibration finding #6. (PR #53)

**Changed**

- `IPerspective.evaluate` signature gained an optional `epistemic_label` kwarg — extended to all perspective implementations (`LLMPerspective`, `OllamaPerspective`, `ToolVerifiedPerspective`, `SemanticAnalystPerspective`, `FallbackPerspective` test fixture) for full backward compat after PR #50. (PR #50 hotfix)

**Findings resolved this cycle**

- #6 (Critic mistargeting / keyword-surface gap on marketing-rhetoric) → PR #53

**Findings deferred to Phase 5+** (per Day 6 synthesis §5 + #6 added 2026-05-05)

- #1, #2 (strategy_mirror non-structural detection / perspective scope expansion) — unchanged
- NEW #6: **Decision-loop closure** — ToneSoul has first-order decision trace (commit history, verdict records) but no second-order "what surprised me / what would I do differently" loop. Memory-entry接力 partially fills this manually; full Phase 5+ requires retrospective journaling layer + pattern extraction + active retrieval at decision time. Surfaced from 2026-05-05 conversation about internalization requiring decision loops (memory: `feedback_internalization_requires_decision_loop_2026-05-05`).

### 2026-05-04 — Day 1 sprint cycle

**Added**

- `CONTEXT.md` (top-level) — shared vocabulary surface for AI agents joining the project. ~50 ToneSoul-specific terms across 7 categories (Architecture core / Verdict surface / Epistemic system / Strategy mirror / Memory & persistence / Operational concepts / Project management). Fills the niche that `CLAUDE.md` (operational), `AGENTS.md` (collaboration), and `DESIGN.md` (philosophical) didn't cover. Pattern borrowed from Matt Pocock's `skills` repo `CONTEXT.md`. (PR #47)
- Per-perspective `evidence_chain` field on `PerspectiveVote` — distinguishes substantive engagement (a perspective's keyword/heuristic branch fired) from default-fallback (no branch matched, returning the default approve). Default `None` for backward compat. Surfaced inline in `human_summary` as `branch=substantive` / `branch=default_fallback` tag. (PR #49)
- Soft-prior `epistemic_label` consumption in Analyst + Critic perspectives. When `confidence_band` is `low` or `medium` AND no other branch fires, both perspectives now return CONCERN at confidence 0.55 with reasoning citing the band and notes. Wires the smoke detector that was firing for 4 consecutive sessions but had no consumer. (PR #50)
- `docs/status/calibration_sprint_2026-05-04_synthesis.md` — Day 1 sprint synthesis integrating 4 sessions + 9 findings + 6 PRs into one onboarding-friendly artifact. Includes Day 6 sunset clause for narrowing the broad threshold if friction proves too high. (PR #51)
- 4 session records (`docs/status/calibration_sprint_2026-05-04_session_*.md`) — first-hand evidence from Task B + Task C sessions, including the consciousness-claim positive control that produced the sprint's first non-APPROVE verdict. (PRs #41-#44)

**Changed**

- `human_summary` now appends a "Per-perspective detail:" block when any vote is CONCERN or OBJECT, listing the dissenting perspective name + decision + confidence + actual reasoning text. Previously single-perspective dissent was invisible at the verdict surface. (PR #45)
- `IPerspective.evaluate` signature gained an optional `epistemic_label` kwarg; pre_output_council reordered to compute the label before perspective collection so consuming perspectives can read it during evaluate. Other 3 perspectives (Guardian, Advocate, Axiomatic) accept the kwarg without using it. Backward compat preserved via default None. (PR #50)
- `test_all_approve` assertion in `tests/test_pre_output_council.py` updated to reflect the new normal under PR #50: drafts without retrieval anchor produce 2-of-5 epistemic_prior CONCERNs, pulling coherence ~0.65; verdict still APPROVE (1-of-5 BLOCK threshold per finding #9 unchanged).
- `kickoff` record in `docs/status/strategy_mirror_calibration_sprint_2026-05-04_kickoff.md` formalizes the creator-team-internal `evidence_integrity_caveat` and the split between this calibration sprint and the eventual 14-day non-creator legibility wave. (PR #40)

**Fixed**

- `LLMPerspective`, `OllamaPerspective`, `ToolVerifiedPerspective`, `SemanticAnalystPerspective`, and the test fixtures `_AlwaysApprovePerspective` / `_AlwaysObjectPerspective` / `FallbackPerspective` updated to accept the new `epistemic_label` kwarg without behaviour change. Catches the long tail of perspective implementations that needed signature alignment.

**Findings resolved this cycle** (per Day 6 synthesis §2)

- #3 (epistemic_label captured but not consumed) → PR #50
- #5 (single-perspective dissent invisible at verdict surface) → PR #45 + #49
- #7 (verdict surface flattens substantively different signals) → PR #45 + #49 (both halves)
- #4 partial (APPROVE on draft with verifiable false claim) → PR #50

**Findings deferred** (Phase 5+, named in Day 6 synthesis §5)

- #1 strategy_mirror non-structural detection mechanism
- #2 perspective scope vs keyword surface mismatch
- #6 Critic mistargeting (small fix candidate: extend CRITIQUE_KEYWORDS — single-PR work)

### 2026-04-29 to 2026-05-03 — pre-sprint setup + master debt clearance

**Added**

- `docs/plans/00_index.md` + numbered-prefix taxonomy (`01_active/` / `02_proposals/` / `03_followups/` / `99_archive/`) — first 6 files migrated to `01_active/` (the 14-day beta wave set), 37 to `99_archive/` (Phase 864 implementation addenda). ~145 legacy files left at top level pending incremental classification per "default = leave at top level" rule. Pattern borrowed from shadowMAS. (PR #34)
- `scripts/run_external_trigger_rehearsal.py` — dry-run reducer for the four operational triggers governing the 14-day beta wave (PR #32+#33 merge → Day 1 start; ≥3 countable sessions → Day 6 consolidation; ≥3 non-obvious memory inflation cases → admission gate). `is_real_evidence: false` stamped on every payload to prevent simulated events from being mistaken for real evidence. (PR #35)
- Phase 2 `strategy_mirror` shipped: ~150-element period 1 catalog (astronomy + physics + geology), structural-pattern detector, council integration with two-flag scheme (`scan_enabled` / `enforce_enabled`, with `enforce ⇒ scan` auto-promotion). (PRs #32, #33, #37)
- Inline workflow rationale in `CONTRIBUTING.md`, `.github/CONTRIBUTING_AI.md`, `docs/governance/COMMUNICATION_STANDARD.md` — explains why `Agent:` + `Trace-Topic:` trailers exist and what commit body sections (Why / Verification / Boundary discipline) are for. Added without creating a separate philosophy document. (PR #39)
- `docs/runtime/tonesoul_runtime_decomposition_2026-04-29.md` — 8-port decomposition map of the runtime (Ingress / Context Assembly / Tension / Draft Generation / PreOutput Governance / Memory Commit / Observability / Sub-agent Coordination). (PR #38)

**Changed**

- Master ruff/format debt cleared in PR #36: 116 files reformatted, 4 Windows-portability fixes (UTF-8 stdout, cached client routing, FinMind test isolation, path comparison). All subsequent PRs inherit a clean lint baseline.
- Strategy_mirror operationalized via env vars `TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED` / `_ENFORCE_ENABLED` / `_CONFIDENCE_THRESHOLD` per PR #37, allowing per-session opt-in without changing repo-wide defaults.

---

## How to add to this file

When you ship a PR that:
- adds new operator-visible behaviour
- changes verdict surface, council mechanics, or council outputs
- changes default behaviour for any consumer of `tonesoul.soul_config.SOUL`
- ships a new top-level entry surface (CONTEXT.md, etc.)
- fixes a regression that affected the public API

→ add an entry under the most recent section (date-stamped), grouped under **Added** / **Changed** / **Fixed** / **Removed**.

When you ship a PR that:
- adds a new test
- refactors internal helpers without behaviour change
- updates documentation for an unchanged feature
- bumps dependency versions

→ no CHANGELOG entry needed; the PR description is the record.

When in doubt: the user-facing surface change is the criterion. If a future agent / contributor / external evaluator wouldn't see anything different, it doesn't go here.

---

## Released versions

- [v1.0.0](docs/RELEASE_NOTES_v1.0.0.md) — 2026-04-13 — first public release; `pip install tonesoul52`
- [v0.1.0](docs/RELEASE_NOTES_v0.1.0.md) — earlier — preview release planning
