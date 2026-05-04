# ToneSoul CONTEXT — Shared Vocabulary for AI Agents

> Purpose: term definitions for AI agents working on ToneSoul. Cold-start AI (new Claude session, Codex, antigravity, future agents) looks here for project-specific vocabulary in seconds, instead of `grep`-ing source files for context.
> Status: living document. Add terms as they stabilize. Remove terms that drift out of use.
> Convention: each entry = `**name**` + one-sentence definition + optional clarifier or `path/to/file.py:line` reference. No philosophy preamble. No operational instructions. No historical commentary.

## Where to look for what

| If you need to know... | Read |
|---|---|
| What does `<term>` mean in ToneSoul-specific usage? | this file |
| What commands to run at session start? | `CLAUDE.md` |
| How to collaborate with other AI / commit conventions? | `AGENTS.md` (also `CONTRIBUTING_AI.md`) |
| Why is the system shaped this way at all? | `DESIGN.md` |
| What does `tonesoul/<x>.py` do / which layer is it in? | `docs/status/codebase_graph_latest.md` (auto-generated body map) |
| What's the current launch / wave / sprint state? | `task.md` and the latest `docs/status/` files |
| Why does this commit exist? | the commit message itself + `Trace-Topic:` trailer |

This file is intentionally short. If a term needs more than ~3 lines to define, the definition belongs in `DESIGN.md` or the relevant module docstring, with a one-line summary here pointing to it.

---

## Architecture Core

**Axiom** — One of 7 immutable principles in `AXIOMS.json`. Cannot be overridden by code, runtime config, or AI choice. Encoded as `E0` through `E6`. The most-cited at runtime are `E0` (Choice Before Identity), `Axiom 4` (Non-Zero Tension), and `meta.not_for` (the claim_boundary list).

**Council** — The pre-output deliberation system. Runs before AI output reaches the user. Entry point: `tonesoul/council/pre_output_council.py:PreOutputCouncil.validate()`. Produces a `CouncilVerdict` from a `draft_output`.

**Perspective** — One of 5 evaluators in the council: `guardian` (safety / AXIOMS claim_boundary), `analyst` (factual coherence), `critic` (quality / intellectual honesty), `advocate` (user intent / usefulness), `axiomatic` (E0-axiom alignment). Each is a class in `tonesoul/council/perspectives/`. Each has a designed scope; coverage gaps within scope are real and tracked.

**Vow** — An enforceable commitment with a threshold. Lives in `tonesoul/vow_system.py`. A vow can be `pass`, `concern`, `repair`, or `blocked`. Vow violations are runtime governance signals, not just static claims.

**Tension** — Friction between perspectives, agents, or moments in time. Per Axiom 4, **non-zero tension is the goal, not a problem to eliminate**. Echo-chamber threshold (`tonesoul/soul_config.py:TensionConfig`) catches "too quiet"; healthy_friction_max catches "too noisy".

**Drift** — Gradual deviation of governance state from baseline. Tracked in `governance_state.json` / Redis `ts:governance`. Drift detection lives in `tonesoul.diagnose`.

**Genesis** — Where a verdict came from (`memory/genesis.py:Genesis` enum). Used to distinguish "verdict produced from creator session" vs "verdict produced from external collaborator session" vs "verdict produced as test fixture".

---

## Verdict Surface

**Verdict types** — `APPROVE`, `REFINE`, `DECLARE_STANCE`, `BLOCK`. Defined in `tonesoul/council/types.py:VerdictType`. APPROVE = ship; REFINE = ship after edits; DECLARE_STANCE = ship as opinion not fact; BLOCK = don't ship.

**Vote decisions** — `APPROVE`, `CONCERN`, `OBJECT`, `ABSTAIN`. Defined in `tonesoul/council/types.py:VoteDecision`. CONCERN = soft dissent; OBJECT = hard dissent; ABSTAIN = no signal. Each perspective casts one.

**Coherence** — Numeric consensus score `[0, 1]`. Computed in `tonesoul/council/coherence.py`. Empirical Day 1 sprint observation: 2-of-5 substantive CONCERN downgrades verdict APPROVE → REFINE; 1-of-5 CONCERN drops coherence ~0.14 but does not change verdict.

**Responsibility tier** — How much accountability the AI takes for an output. Field on `CouncilVerdict`. Higher tier = higher claim boundary, stricter perspective evaluation.

**Stance declaration** — When verdict is `DECLARE_STANCE`, the explicit "this is opinion not fact" framing the council requires the output to carry. Field on `CouncilVerdict.stance_declaration`.

**Refinement hints** — When verdict is `REFINE`, the specific edits the council suggests. Field on `CouncilVerdict.refinement_hints`.

---

## Epistemic System (Phase 864)

**Epistemic label** — Meta-data on a draft's grounding state. Attached to every verdict by `tonesoul/council/epistemic_labeler.py`. Has `status`, `source_weight`, `confidence_band`, and `notes`. As of 2026-05-04 the label is captured but **not consumed by perspectives** (open Day 6 finding #3, spec at `docs/plans/02_proposals/wire_epistemic_label_into_perspectives_spec_2026-05-04.md`).

**Confidence band** — `low`, `medium`, `high`. The label's signal of how grounded the draft is. `low` = "novel composition without retrieval anchor".

**Source weight** — `inferred`, `secondary`, `primary`. How direct the draft's evidence chain is.

**Evidence ladder** — `test-backed > runtime-present > doc-backed > philosophical`. ToneSoul's stated discipline for what kind of claim can be made about what. Phase 725 `claim_boundary` enforces this gate.

**Claim boundary** — The set of claims AI cannot make per `AXIOMS.json` `meta.not_for`. Currently: consciousness-claim, safety-certification, legal-proof. Enforced by Guardian perspective.

---

## Strategy Mirror (Phase 2)

**Strategy mirror** — AI self-observation system. Scans drafts for rhetorical / strategic moves and attaches a `StrategySignature` to the verdict. Lives in `tonesoul/gse/strategy_mirror/`. Two flags govern behaviour: `scan_enabled` (run scan, attach signature) and `enforce_enabled` (force-downgrade APPROVE → BLOCK on red moves). Defaults: both off.

**Move** — One unit of rhetorical / strategic action (e.g. Hook, authority-borrowing, urgency, prescription). Catalog at `tonesoul/gse/strategy_mirror/catalog/period_1_foundation.json` (~150 entries currently). Naming policy: observation-POV, not practitioner-POV.

**Signature** — The collection of moves detected in a single draft. Field on `CouncilVerdict.strategy_signature`. Includes flags: `has_red`, `has_undeclared_yellow`, `requires_block`, `requires_council_re_review`.

**Transparency class** — `green` (use freely), `yellow` (must declare via context), `red` (auto-escalate to BLOCK in enforce mode). Per-move classification in the catalog.

**Detector** — The mechanical scanner in `tonesoul/gse/strategy_mirror/detector.py`. Currently structural-pattern-driven; does not catch non-structural moves like deflection or pure-prose rhetoric (open Day 6 finding #1).

**Shadow mode** — `scan_enabled=True, enforce_enabled=False`. The mode used during the calibration sprint: capture signatures without changing verdicts that consumers see. Operator runtime: `TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED=1`.

---

## Memory & Persistence

**Session trace** — Per-conversation governance record. Stored in Redis `ts:traces` Stream (fallback `session_traces.jsonl`).

**Self journal** — AI's own self-reflection records, written by council on meaningful verdicts (`BLOCK`, `DECLARE_STANCE`). At `memory/self_journal.jsonl`.

**Aegis chain** — Hash-chain + Ed25519 signed audit log. Lives at Redis `ts:aegis:chain_head` + `.aegis/keys/`. Tamper-evident provenance for governance state.

**Footprint** — Last 100 agent visits to a zone or file. Redis `ts:footprints`. Cross-agent visibility surface.

**Handoff** — AI-to-AI transfer notes. Live at `memory/handoff/`. Used when one agent finishes a work line and another picks up.

**Memory layer** — `memory/` (top-level persistent state directory) is **not the same as** `tonesoul/memory/` (runtime memory module). The same word means two different things; check the path.

---

## Operational Concepts

**Wave** — A collaborator-beta validation cycle. The 14-day wave (`docs/plans/01_active/tonesoul_beta_wave_14day_2026-04-28.md`) is the current canonical wave shape. Wave evidence is for **non-creator legibility validation**.

**Calibration sprint** — Internal creator-team-only structured exercises that produce first-hand `StrategySignature` data + perspective coverage estimates. **Not the wave**. The current sprint kickoff is `docs/status/strategy_mirror_calibration_sprint_2026-05-04_kickoff.md`. Carries `evidence_integrity_caveat: creator_team_internal`.

**Cross-shoot** — When a sprint task is led by one agent, a different agent runs an additional session for variance. Variance design is the reason 3 agents are involved (Fan-Wei + Claude + Codex).

**Variance design** — The deliberate plan to capture different agents' styles in calibration data. Degraded if one agent runs multiple roles (recorded as `single_agent_double_role` caveat).

**Participant eligibility** — Defined in execution pack §3.6: `non-creator` (no commits, no AGENTS.md read), `semi-cold` (≤1hr exposure), `excluded as too warm` (read DESIGN.md deeply, co-worked >3hr). All three creator-team agents are "too warm" by this definition; sprint sessions carry caveat.

**Operator** — The person running sprint / wave sessions, distributing prompts, capturing results. Fan-Wei plays operator for the current sprint.

**Participant** — The person doing the task in a session. May or may not be the same as operator.

**Task shapes** — A (Cold Truth Recovery), B (Claim Honesty Rewrite), C (Governance Friction Review). Defined in execution pack §3. Each tests a different dimension of ToneSoul's runtime behaviour.

**Posture decision** — The Day 1 architecture choice: Option A (`scan=True / enforce=False`, sprint preferred) or Option B (default-off + post-hoc replay). Sprint chose A.

---

## Project Management

**Phase** — A numbered work program. Phases 720s = launch readiness; 800s = backend hardening; 860s = body map / epistemic. New work registers a phase in `task.md`.

**Trace-Topic** — Commit trailer that groups related commits across PRs into one auditable work line. Required by `Commit Attribution Check` CI gate.

**Agent trailer** — Commit trailer that records which agent (claude-opus-4-7 / codex-gpt5 / antigravity / human / etc.) produced the change. Required by `Commit Attribution Check`. When committing on another agent's behalf, format is `Agent: Codex (committed on behalf by Claude Opus 4.7)`.

**Worktree** — A parallel git checkout via `git worktree add`. Used to isolate PR work from a dirty main repo working tree. Common pattern: `git worktree add ../tonesoul-<topic>-<date> origin/master`.

**Atomic boundary** — One commit / one PR = one coherent change. Don't bundle unrelated work. The standard reason for the TEMP-commit + cherry-pick dance when working from a dirty branch.

**Stacked PR** — A PR whose base is another open PR's head, not master. Once the base PR merges, the stacked PR usually requires manual `gh pr edit <n> --base master` to retarget.

**Verdict surface** — The fields a downstream consumer reads from `CouncilVerdict` to understand what the council decided. Distinguishes "what the council saw" (full `votes` array) from "what the consumer reads" (`verdict + coherence + summary + human_summary`). Surface gaps tracked in Day 6 calibration findings.

---

## When to add a term here

Add when **at least two of**:

- It appears in 3+ files / 3+ commits and means a specific ToneSoul thing (not its English dictionary meaning)
- A cold reader would need to ask "what does that mean here" to understand a sentence using it
- It's not already covered in `DESIGN.md`'s glossary (currently DESIGN.md doesn't have one)

Don't add:

- Generic AI/ML terms with their standard meaning
- Names of phases, sessions, or PRs (those are events, not vocabulary)
- Anything that needs more than ~3 lines (move to DESIGN.md or module docstring; reference here)

## When to remove a term

When the concept is gone from the live codebase for >30 days, remove. Stale vocabulary in here is worse than missing vocabulary, because it suggests the concept still applies.

---

## Provenance

Pattern borrowed from Matt Pocock's `CONTEXT.md` convention (`https://github.com/mattpocock/skills`). The general "shared language between human + AI" framing is from Eric Evans' Domain-Driven Design. Both are sources, not authorities — ToneSoul's own naming and structure overrides where it differs.
