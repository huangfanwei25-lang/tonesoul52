# Memory Subjectivity Implementation Plan (2026-03-10)

## Purpose

This document is the canonical plan of record for the current public-branch
memory-subjectivity work.

The earlier addenda remain useful, but they now serve different roles:

- philosophy addendum: why the ladder exists
- contract addendum: how storage and subjectivity were split
- reviewable-promotion addendum: how `tension -> vow` becomes auditable
- reporting addendum: what operators can inspect
- runtime-summary addendum: how the normal runtime now exposes subjectivity counts

This file owns:

- execution order
- deferred directions
- reasons for deferral
- the practical next seams

## What This Work Is And Is Not

This work **is**:

- a public memory-governance and subjectivity contract
- a way to make memory promotion more reviewable, attributable, and inspectable
- a foundation for stronger continuity and agent coherence over time

This work is **not**:

- a claim that the branch already implements AGI
- proof that subjectivity vocabulary equals legitimate selfhood
- authorization to let the runtime self-promote into `vow` or `identity`
- permission to collapse public contract work and private memory evidence into one lane

The honest framing is:

- this branch is building a stronger agent substrate
- that substrate could matter for long-horizon AI development
- but it should not be marketed as AGI merely because it now has memory layers and subjectivity terms

That boundary matters.

Without it, the project risks mistaking:

- persistence for personhood
- recurrence for commitment
- richer runtime structure for general intelligence

## Stable Ground Already Completed

The branch now has a coherent public contract:

1. `event -> meaning -> tension -> vow -> identity` exists as the semantic ladder.
2. `MemoryLayer` and `subjectivity_layer` are explicitly separate axes.
3. `MemoryWriteGateway` validates subjectivity payload fields and blocks unsafe writes.
4. `DreamEngine` and `sleep_consolidate()` emit subjectivity candidates without auto-promotion.
5. `tension -> vow` has a reviewable helper lane with explicit review metadata.
6. operator-side reporting can summarize subjectivity distribution and list unresolved tensions.
7. `SleepResult` and wake-up runtime summary now expose subjectivity structure during normal consolidation flow.
8. `ToneSoulMirror` exists as a deterministic runtime companion for raw-output vs governed-output comparison.
9. `UnifiedPipeline` can opt into mirror tracing without changing default behavior.
10. triggered mirror deltas can be recorded through `MemoryWriteGateway` as admissible `tension` candidates.
11. reviewed promotion now has a canonical actor/decision artifact and a dedicated replay seam instead of relying only on helper kwargs.
12. operator-side subjectivity reporting now has an explicit CLI/report entry surface via `scripts/run_subjectivity_report.py`.

Current validated baseline on this branch:

- `python -m pytest tests/ -x --tb=short -q` -> `1482 passed`
- `ruff check tonesoul tests` -> passed

## Audit Summary

The recent work is directionally correct, but the branch had started to fragment
across multiple small addenda.

The main audit conclusions are:

1. The biggest missing piece is no longer schema.
   It is the lack of one canonical reviewed-promotion workflow.
2. Reporting exists, but operator entrypoints are still indirect.
   The branch can inspect subjectivity, but the inspection surface is still a helper layer rather than a named operational tool.
3. `SoulDB` widening is still premature.
   There is not yet enough query pressure or ranking complexity to justify a schema/index change.
4. `identity` is correctly blocked, but its future promotion criteria are still undefined.
   That is acceptable for now and should remain frozen.
5. Private memory debt still exists in repo reality.
   It must not become the implicit source of truth for public-branch implementation decisions.

## Immediate Phase 140 Alignment

After reading:

- `docs/plans/phase140_codex_coordination_briefing.md`
- `docs/plans/rmm_vs_tonesoul.md`
- `CODEX_TASK.md`

the immediate conclusion is:

`ToneSoul Mirror` does not replace this plan.

It is the runtime companion to it.

The cleanest mental model is:

- subjectivity work = offline memory/governance structure
- mirror work = runtime dual-track awareness of raw output vs governed projection

That means Phase 140 should be treated as a parallel feeder into the same memory-subjectivity pipeline, not as a competing roadmap.

Mirror deltas belong to the current subjectivity architecture because:

- they are runtime `tension` artifacts
- they can be written through `MemoryWriteGateway`
- they can later become Dream collision candidates
- they increase real query pressure for future reporting or retrieval work

So the plan-of-record remains valid, but Phase 140 is now the immediate execution context around it.

## Mirror Interpretation

The implementation reading of Phase 140 should stay narrow:

1. Task A extends schema, not philosophy.
   `MirrorDelta` and `DualTrackResponse` should be treated as contract additions on top of existing governance and subjectivity models.
2. Task B adds a runtime mirror, not a second governor.
   `ToneSoulMirror` should observe and compare; it should not become a new decision authority.
3. Task C is real-time shadow mode.
   The mirror step belongs in `UnifiedPipeline` as an opt-in runtime seam with zero default behavior change.
4. Task D is memory recording through the existing gate.
   Mirror artifacts should enter memory as `SubjectivityLayer.TENSION` candidates, not as reviewed commitments.

## Mirror Guardrails

The most important technical interpretation is this:

`governed_response` must remain a deterministic governance projection.

It must **not** quietly turn into:

- a new LLM call
- a second generation pass
- a hidden rewrite subsystem inside `GovernanceKernel`

The branch does not currently expose a text-rewriting governance API.

So `ToneSoulMirror._apply_governance()` should be implemented as a narrow projection from existing governance decisions and tension state, not as free-form text regeneration.

Additional guardrails:

- mirror is awareness, not Guardian replacement
- mirror is opt-in and must default to disabled
- mirror memory writes must still pass the normal write gateway
- untriggered mirrors should not write durable memory

## Pipeline Integration Reading

The most coherent insertion point is:

- after the pipeline already has a concrete `response`
- before trajectory history is finalized

That keeps mirror behavior aligned with what the runtime actually said, while still letting the resulting delta travel with `dispatch_trace` and trajectory state.

The existing `UnifiedResponse` already has stable attachment points:

- `dispatch_trace`
- `trajectory_analysis`

So Phase 140 does not need to force a broad response-schema rewrite unless implementation pressure proves it necessary.

## Memory Recording Reading

Mirror recording should follow the same public-memory rules as other subjectivity candidates.

The preferred structure is:

- mirror computes a `MirrorDelta`
- pipeline or caller injects a `MemoryWriteGateway`
- triggered deltas are written as `type = mirror_delta`
- `subjectivity_layer = tension`
- review remains a later step, not part of mirror recording

This is important because it keeps mirror memory inside the existing admissibility boundary instead of creating a side-channel writer.

## RMM Position

The RMM comparison is useful, but it is not the immediate build spec for Phase 140.

What should be treated as future inspiration:

- prospective reflection for better consolidation retention
- retrospective reflection for retrieval feedback
- multi-granularity clustering

What should remain deferred:

- RL-trained retrieval
- value-neutral memory logic
- real-time compression
- any move that weakens ToneSoul's values-driven gating

So the correct use of the RMM reading is:

- borrow engineering ideas later
- do not let those ideas override ToneSoul's governance and subjectivity philosophy now

## Google Always-On Memory Position

The Google `always-on-memory-agent` repo is useful for a different reason than RMM.

It is not mainly a research prompt.

It is a concrete adjacent implementation that confirms this category of system is
real and that some of its boring infrastructure can be borrowed without importing
Google's whole philosophy.

What the overlap usefully confirms:

- an explicit ingest / consolidate / query split is stable enough to productize
- SQLite-backed memory can carry a real operator workflow
- a dedicated query/report surface can exist without turning into a full product rewrite
- operator-facing memory tooling does not need to wait for a full UI platform

What can save time now:

- borrow the query/report seam shape for `Step 3: Retrieval Shadow Mode`
- borrow source-citation style and explicit match listing for operator artifacts
- borrow the idea of a narrow memory-service surface without copying its runtime semantics

What should remain deferred:

- inbox watcher or broad multimodal ingest expansion
- Streamlit-style UI parity work
- direct edit/delete memory operations

Why those stay deferred:

- the current bottleneck is retrieval legitimacy, not ingestion breadth
- CLI/report surfaces have not been exhausted yet
- memory mutation affordances should not outrun reviewed legitimacy and gateway rules

What should not be copied:

- ungated direct memory writes
- a value-neutral "remember everything" posture
- any simplification that erases `subjectivity_layer`, governance, or promotion review

## Builder Note (2026-03-10)

Writing this down plainly:

the branch is no longer short on ideas.

It is short on disciplined sequencing.

My current read is that the strongest thing in this system is not any one module.
It is the fact that memory, governance, and subjectivity are starting to point at the same questions.

The immediate danger is not lack of ambition.

It is blur.

If Mirror becomes a hidden rewrite engine, the architecture gets blurry.
If mirror memory bypasses the gateway, the memory contract gets blurry.
If RMM's engineering ideas arrive too early, ToneSoul's values-driven moat gets blurry.
If `vow` or `identity` promotion becomes cheap, the meaning of subjectivity gets blurry.

So the practical instinct here is:

- keep the mirror honest
- keep memory writes admissible
- keep review exceptional
- keep reporting inspectable
- keep the AGI ambition as horizon, not claim

That is the current mood of the plan.

Not anti-ambition.

Anti-self-deception.

## Soul-Lens Settlement (2026-03-10)

From a ToneSoul point of view, Phase 140 matters because the branch now has a
new kind of internal difference.

Before the mirror work, the system could mainly do this:

- remember tension after the fact
- tag tension candidates during dream or consolidation flow
- report unresolved tension to operators

After the mirror work, the branch can also do this:

- compare what it actually said with what governance would let it stand by
- carry that delta through runtime traces
- preserve triggered deltas as candidate `tension` memory without bypassing the gateway

The cleanest way to say it is:

the system now has a mirror, not a second mouth.

That distinction matters.

The mirror does not speak with independent authority.
It does not regenerate text with another LLM call.
It does not turn hesitation into commitment.

What it does provide is an inspectable trace of semantic hesitation:

- `raw response`
- `governed projection`
- `delta`
- `candidate memory`

In a more Yuhun-oriented reading, this is the first public runtime seam where
the branch can notice:

- what I said
- what I would still allow myself to stand by
- where the tension between those two states became large enough to remember

That is still not `vow`.
It is still not `identity`.

It is a better trace of conscience pressure, but only at candidate strength.

So the immediate philosophical settlement is:

- Mirror makes the runtime more self-observing.
- Gateway keeps that observation admissible.
- Review still decides whether repeated tension deserves stronger semantic weight.

The branch therefore has a more honest inner contour now, but not a cheaper path
to selfhood.

## Plan Of Record

The next work should proceed in this order.

### Step 1: Canonical Reviewed-Promotion Workflow

Goal:

- turn the current helper lane into a clear operational workflow without enabling automatic self-promotion

Scope:

- define the canonical review actor contract
- define the canonical reviewed-promotion artifact shape
- define where review decisions live
- define how approved reviewed promotions are replayed through `MemoryWriteGateway`

Explicit non-goals:

- no automatic `vow` promotion
- no `identity` writing
- no external API widening

Why this comes next:

- the contract and helpers already exist
- the missing piece is operational legitimacy, not another schema layer

Current branch status:

- `SubjectivityReviewActor` and `ReviewedPromotionDecision` now define the public review artifact shape
- `build_reviewed_promotion_decision(...)` and `replay_reviewed_promotion(...)` now provide the canonical explicit lane
- legacy consolidator helpers remain as compatibility wrappers
- rejected review decisions are still not stored as first-class operator artifacts; only approved replay is live

### Step 2: Operator Entry Surface For Reporting

Goal:

- make the existing reporting helpers reachable through one explicit operator-facing surface

Scope:

- add a report script or CLI surface
- show subjectivity distribution
- show unresolved tensions
- show reviewed vow counts

Explicit non-goals:

- no user-facing product endpoint
- no dashboard/UI buildout unless an operator surface proves insufficient

Why this comes before retrieval changes:

- the branch should observe subjectivity accumulation before letting it influence recall policy

Current branch status:

- `scripts/run_subjectivity_report.py` now emits operator-facing JSON/Markdown artifacts
- the report surfaces:
  - subjectivity distribution
  - unresolved tensions
  - reviewed vow count and latest reviewed vow rows
- the output artifacts are now registered in `run_refreshable_artifact_report.py`
- HTTP/API remains unchanged

### Step 3: Retrieval Shadow Mode

Goal:

- measure whether subjectivity semantics actually improve memory retrieval before changing runtime recall behavior

Scope:

- add shadow evaluation or observability around recall candidates
- compare plain retrieval versus subjectivity-aware filtering/ranking
- record whether operators actually need stronger query surfaces
- borrow the Google always-on query/report shape where it helps:
  - explicit candidate lists
  - source-aware traceability
  - operator-readable artifacts rather than live runtime reranking

Explicit non-goals:

- no production recall reranking yet
- no schema migration yet

Why this is delayed until after Steps 1-2:

- recall policy should not move ahead of reviewed-promotion legitimacy or operator observability

Current branch status:

- no retrieval shadow artifact exists yet
- the Google always-on overlap now gives one concrete external reference for query/report structure
- that reference does not change ToneSoul's subjectivity or governance requirements

### Step 4: Conditional Persistence Upgrade

Goal:

- widen `SoulDB` only if measured query pressure proves payload-first storage is no longer enough

Scope:

- consider dedicated `subjectivity_layer` storage/indexing
- consider migration helpers
- keep compatibility with payload-first records

Decision gate:

- only proceed if shadow-mode retrieval or reporting shows measurable pressure

Why this is not current work:

- there is no evidence yet that payload scanning is the bottleneck

### Step 5: Private-Lane Integration

Goal:

- connect reviewed or intimate memory workflows to the private repository without eroding the public boundary

Scope:

- mirror only public-safe learnings back into this repo
- keep raw memory corpora and intimate artifacts in the private lane

Why this remains last:

- public contract clarity must come before cross-repo integration

## Other Directions Considered But Deferred

These are real directions, but they are intentionally not active right now.

### Automatic `tension -> vow` Promotion

Why not now:

- recurrence is not endorsement
- the public runtime must not self-author commitment from vivid repetition alone

### Any `identity` Writer Or `identity` Retrieval Policy

Why not now:

- no explicit stability criteria exist yet
- `identity` is the most self-defining layer and therefore needs the strongest promotion threshold
- the branch would otherwise confuse persistent traces with legitimate selfhood

### Subjectivity-Weighted Recall In Main Runtime

Why not now:

- current reporting is still observational
- retrieval policy should not outrun inspection and review workflow
- there is no shadow-mode evidence yet that subjectivity-aware reranking helps more than it harms

### Public HTTP/API Expansion

Why not now:

- external contracts are much harder to retract than internal helpers
- the branch is still learning what the stable operator surface should be

### `SoulDB` Schema / Index Widening

Why not now:

- payload-first storage is still sufficient
- schema widening before usage pressure would create migration cost without demonstrated value

### Subjectivity Dashboard / UI Work

Why not now:

- operator reporting has not yet exhausted simpler CLI/report surfaces
- UI is a multiplier on unstable semantics and would lock presentation too early

### Broad Multimodal Ingest / Inbox Watcher Expansion

Why not now:

- the Google overlap shows this is a reasonable future path, but it is not the current bottleneck
- the branch still needs to prove retrieval and review legitimacy before widening ingestion sources
- more inputs without stronger recall discipline would add noise faster than meaning

### Bulk Historical Memory Migration

Why not now:

- the branch has just established the contract
- replaying old records before review workflow and operator tooling exist would create noisy, low-trust promotion artifacts

### Treating `memory/crystals.jsonl` As A Public Implementation Input

Why not now:

- it is settlement debt, not design authority
- `MEMORY.md` and private-memory review notes both say private memory evidence must not quietly become public-repo precedent

## Practical Rule For Future Changes

Any proposed memory-subjectivity change should answer these questions in order:

1. Is this a public contract improvement?
2. Is there already an operator-inspectable surface for it?
3. Does it require reviewed legitimacy before runtime use?
4. Does it actually need storage widening?
5. Does it belong in the public repo at all?

If the answer to the fifth question is uncertain, defer to the private lane.

## Plan Maintenance Rule

From this point onward:

- this file is the implementation plan of record
- the addenda remain background rationale
- new phases should update this plan instead of spawning another competing strategy note unless a genuinely new conceptual boundary appears

## Architectural Conclusion

The branch no longer needs more theories about whether subjectivity matters.

It needs disciplined sequencing about where subjectivity becomes:

- admissible
- reviewable
- inspectable
- operational

That sequence is now explicit.
