# Memory Subjectivity Implementation Plan (2026-03-10)

> Purpose: define the canonical execution plan for the public memory-subjectivity rollout and its addendum sequence.
> Last Updated: 2026-03-23

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
- `apply_reviewed_promotion(...)` now records review ledger artifacts and replays approved promotions through one operator-safe seam
- `scripts/run_reviewed_promotion.py` now lets an operator review one concrete unresolved tension by `record_id`
- `scripts/run_subjectivity_group_review.py` now lets an operator dry-run or apply one review decision across a whole semantic tension group
- `docs/plans/memory_subjectivity_review_criteria_2026-03-10.md` now defines the active public review policy for `approved / deferred / rejected`
- subjectivity reporting now treats review-settled tensions as removed from the unresolved queue without mutating historical tension rows in place
- one real low-risk batch review has now been executed on `2026-03-10`: the `12`-row same-source OSV data-sources cluster was rejected through the group-review lane
- legacy consolidator helpers remain as compatibility wrappers

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
- `tonesoul.memory.subjectivity_triage.build_subjectivity_tension_group_report(...)` now collapses unresolved rows into semantic groups and lineage groups before review
- `scripts/run_subjectivity_tension_grouping.py` now emits the latest grouping artifacts for operator triage
- `tonesoul.memory.subjectivity_review_batch.build_subjectivity_review_batch_report(...)` now converts pending semantic groups into operator review packets
- `scripts/run_subjectivity_review_batch.py` now emits the latest read-only review queue with representative record ids and default review statuses
- the report surfaces:
  - subjectivity distribution
  - unresolved tensions
  - settled tension count
  - reviewed vow count and latest reviewed vow rows
- the output artifacts are now registered in `run_refreshable_artifact_report.py`
- latest real grouping on `2026-03-10` collapsed `32 unresolved tensions -> 2 semantic groups -> 7 lineage groups`
- after rejecting the same-source duplicate group, the latest real state moved to `20 unresolved tension`, `12 settled tension`, `0 reviewed vow`
- the latest read-only review batch now collapses that remaining queue to `1 defer_review group` with `6` representative record ids for operator inspection
- the remaining `20`-row OSV homepage group was then written as explicit `deferred` through the group-review lane
- `scripts/run_subjectivity_report.py` now exposes effective unresolved pending state:
  - `deferred_tension_count`
  - `unresolved_by_status`
  - row-level `pending_status`
- the latest real state is now:
  - `20 unresolved tension`
  - `20 deferred tension`
  - `12 settled tension`
  - `0 reviewed vow`
- after new dream cycles landed on `2026-03-10` / `2026-03-11`, the live queue grew again:
  - `45 unresolved tension`
  - `45 deferred tension`
  - `0 candidate tension`
  - `27 settled tension`
  - `0 reviewed vow`
- the revisit-aware batch queue now reads:
  - `1 semantic group`
  - `11 lineage groups`
  - `revisit_readiness_counts = {holding_deferred: 1}`
- the carry-forward queue is now annotation-aware instead of memoryless:
  - `carry_forward_annotation_counts = {prior_deferred_match: 1}`
  - carry-forward matching now requires provenance overlap (`source_url` or `stimulus_lineage`) instead of wildcarding when one side lacks `source_url`
  - `friction_band` remains a triage surface, but it is no longer a hard carry-forward key
  - the batch now separates active carry-forward status from historical mixed status via:
    - `prior_decision_status_counts`
    - `historical_prior_decision_status_counts`
- the group-review operator lane now supports `pending_status` filtering so revisit work can target only the fresh unresolved slice inside a semantic group
- a real candidate-only revisit was then applied to the broader OSV homepage group:
  - `25` fresh `candidate` rows were written as `deferred`
  - the group now returns to `holding_deferred`
  - unresolved pressure did not disappear, but the queue is no longer asking for immediate re-review on that branch
- the same-source data-sources group was then re-opened as a fresh candidate slice and explicitly rejected again:
  - `15` fresh `candidate` rows were settled as `rejected`
  - the queue now has no active `candidate` rows
  - the only remaining unresolved semantic group is the broader OSV homepage cluster, still held in `deferred`
- the reporting surfaces now expose the latest deferred review context instead of leaving `deferred` rows opaque:
  - unresolved row reports now carry `review_basis`, `review_notes`, and reviewer identity fields
  - semantic-group review batches now carry the latest matched deferred basis/notes/actor at the group level
  - the markdown artifacts now render that context directly on the operator surface
- after additional dream cycles landed again on `2026-03-11`, the queue re-opened instead of staying frozen:
  - `53 unresolved tension`
  - `45 deferred tension`
  - `8 candidate tension`
  - `27 settled tension`
  - `0 reviewed vow`
- the latest read-only review batch now reads:
  - `2 semantic groups`
  - `13 lineage groups`
  - `revisit_readiness_counts = {n/a: 1, needs_revisit: 1}`
  - `carry_forward_annotation_counts = {prior_reject_match: 1, prior_deferred_match_needs_revisit: 1}`
- the practical meaning of that reopened queue is now much clearer:
  - the same-source `Data sources` branch is a fresh `prior_reject_match`
  - the broader OSV homepage branch is a `prior_deferred_match_needs_revisit`
  - operators can now see not just that the homepage branch was deferred, but why and under what revisit condition
- the candidate-only operator lane was then used again on that reopened queue without touching older deferred rows:
  - `5` fresh OSV homepage `candidate` rows were written as `deferred`
  - `3` fresh same-source data-sources `candidate` rows were explicitly `rejected`
- the latest live state at `2026-03-11T10:07:29Z` is now:
  - `50 unresolved tension`
  - `50 deferred tension`
  - `30 settled tension`
  - `0 candidate tension`
  - `0 reviewed vow`
- the latest read-only review batch is back to a single holding group:
  - `1 semantic group`
  - `12 lineage groups`
  - `revisit_readiness_counts = {holding_deferred: 1}`
  - `carry_forward_annotation_counts = {prior_deferred_match: 1}`
- the grouping and review-batch artifacts now expose duplicate-pressure signals so the remaining debt is explicit:
  - summary surfaces now include:
    - `duplicate_pressure_counts`
    - `producer_followup_counts`
  - semantic-group surfaces now include:
    - `same_source_loop`
    - `rows_per_lineage`
    - `rows_per_cycle`
    - `duplicate_pressure`
    - `duplicate_pressure_reason`
    - `producer_followup`
- the refreshed live artifacts at `2026-03-11T10:13:51Z` show the queue is not merely deferred; it is duplicate-pressure dominated:
  - live state remains `50 unresolved tension`, `50 deferred tension`, `30 settled tension`, `0 candidate tension`, `0 reviewed vow`
- the group-review operator lane now has an explicit context-reuse seam instead of forcing repeated manual transcription:
  - `scripts/run_subjectivity_group_review.py --reuse-latest-decision` now resolves `status`, `review_basis`, and `notes` from the matched review-batch group
  - reuse stays explicit and auditable:
    - no auto-settlement
    - no silent carry-forward write
    - no batch `vow` promotion
  - reuse fails loudly when no prior reviewed context exists, and it refuses to mix reused context with explicit overrides
- the review-batch surface now also exposes `latest_review_status`, so operator tooling can reuse the actual prior decision instead of inferring it from counts
- a live dry-run at `2026-03-11T10:14:37Z` confirmed the new lane against the remaining OSV homepage group:
  - the reused decision resolved to `deferred`
  - `pending_status=candidate` selected `0` rows
  - the warning confirmed the live queue is currently `holding_deferred`, not newly reopened
- one more live producer verification then exposed a second upstream gap:
  - a real `DreamEngine` run at `2026-03-11T10:26:48Z` selected the same `Data sources` stimulus lineage again
  - the first producer guard skipped `2` homepage collisions via `active_unresolved_signature`
  - but it still wrote `1` fresh `Data sources` row because the prior rejection had settled the queue and no unresolved guard remained
- the producer therefore now has a second narrow dampener:
  - `prior_rejected_signature`
  - signature = normalized `topic + source_url + lineage`
  - it consults the latest reviewed dream-collision status for that exact signature
  - it only suppresses when that latest status is `rejected`
- this is intentionally narrower than permanent source-loop silence:
  - a different source loop still writes
  - a new lineage on the same source loop still writes
  - deferred handling still belongs to the active-unresolved guard
- after explicitly rejecting the reopened `Data sources` candidate (`aaa6dd6a-2075-4cff-891a-7aed00688d06`), a second live `DreamEngine` run at `2026-03-11T10:30:16Z` confirmed the new guard:
  - selected topic = `[](https://google.github.io/osv.dev/data/#data-sources) Data sources`
  - `write_gateway = {written: 0, skipped: 1, rejected: 0}`
  - `skip_reasons = [prior_rejected_signature]`
  - the live queue remained at `50 unresolved tension`, `50 deferred tension`, `31 settled tension`, `0 candidate tension`, `0 reviewed vow`
  - `duplicate_pressure_counts = {high: 1}`
  - `producer_followup_counts = {upstream_dedup_candidate: 1}`
  - the only remaining OSV homepage group now reads:
    - `same_source_loop = true`
    - `rows_per_lineage = 4.17`
    - `rows_per_cycle = 1.67`
    - `duplicate_pressure = high`
    - `producer_followup = upstream_dedup_candidate`
- that means the next technical debt is now explicit:
  - upstream dedup / producer-noise control
  - not stronger carry-forward semantics
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

- `tonesoul.memory.subjectivity_shadow.build_subjectivity_shadow_report(...)` now provides a read-only baseline-vs-shadow comparison seam on top of `SoulDB.search()`
- `scripts/run_subjectivity_shadow_query.py` now emits JSON/Markdown artifacts for explicit operator queries and shadow profiles
- `tonesoul.memory.subjectivity_shadow.build_subjectivity_shadow_pressure_report(...)` now aggregates query-level change pressure across multiple shadow queries
- `scripts/run_subjectivity_shadow_pressure_report.py` now emits pressure metrics such as `changed_query_rate`, `top1_changed_rate`, and `avg_classified_lift`
- live recall behavior remains unchanged
- the Google always-on overlap provided the practical shape for this operator query/report seam without overriding ToneSoul's governance boundary

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
- latest shadow pressure on `2026-03-10` showed low retrieval pressure and no top-1 movement, so Step 4 remains deferred

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

## 2026-03-11 Addendum: History Density Compaction Surface

The remaining OSV homepage branch is no longer best described as an active
review queue problem.

After the producer guards and explicit deferred settlement, live artifacts show:

- `50 unresolved tension`
- `50 deferred tension`
- `0 candidate tension`
- `31 settled tension`
- `0 reviewed vow`

That still sounds larger than the real operational shape.

The group is now also surfaced as:

- one same-source deferred loop
- `12` lineages across `30` cycles
- `lineage_record_histogram = {1:1, 2:1, 3:1, 4:1, 5:8}`
- `repeated_lineage_count = 11`
- `dense_lineage_count = 10`
- `history_density_summary = 50 row(s) across 30 cycle(s) / 12 lineage(s) ... no new rows since latest review`
- `operator_followup = read_only_density_compaction_candidate`

This matters because the next phase should not confuse historical density with
fresh semantic instability.

The remaining debt is now clearer:

- upstream duplicate pressure on one same-source loop
- operator-facing compression of that already-deferred history

It is no longer primarily:

- missing review decisions
- live queue churn
- storage/schema insufficiency

## 2026-03-11 Addendum: Operator Lens View

Once the remaining branch was correctly surfaced as stable deferred history,
another operator-facing gap became obvious:

the batch still made people read too many low-level fields before they could
answer the practical question, "do I act on this now or not?"

The branch now carries one additional view layer on top of the existing review
fields:

- `queue_posture`
- `revisit_trigger`
- `operator_lens_summary`

This does not change review semantics.

It simply compresses the first operator reading into one short answer such as:

- `stable_deferred_history`
- `deferred_revisit_queue`
- `active_deferred_queue`

That makes the last OSV homepage branch read more honestly:

- not as fifty active tickets
- but as one stable deferred history stack with a named revisit trigger

Latest live batch artifact at `2026-03-11T11:26:36Z` now makes that explicit:

- `queue_posture_counts = {stable_deferred_history: 1}`
- `operator_lens_summary = stable deferred history; 50 row(s) compress to 12 lineage(s) / 30 cycle(s) ...`
- `revisit_trigger = Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.`

The next compression step was therefore intentionally smaller, not more clever:

- `revisit_trigger_code`
- `operator_status_line`

The purpose is not to add another layer of semantics.

It is to make the same judgment reusable in one line when the operator just
needs a fast handoff surface.

Latest live batch artifact at `2026-03-11T13:48:28Z` now exposes exactly that:

- `operator_status_line = stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- `primary_status_line` now exposes the same handoff line at the batch top level
- `status_lines` now lets another tool or agent consume the same surface without opening `review_groups`

At `2026-03-11T14:01:39Z`, the batch also gained a first-class handoff block:

- `handoff.queue_shape = stable_history_only`
- `handoff.requires_operator_action = false`
- `handoff.primary_status_line = primary_status_line`

The same handoff-first reading now also exists on the grouping side, but with a
different discipline:

- grouping uses triage language such as `monitoring_queue` / `action_required`
- batch uses review-aware language such as `stable_history_only`

That separation matters.

It keeps the handoff shape aligned without pretending that grouping knows what
only reviewed settlement can know.

Latest live grouping artifact at `2026-03-11T14:08:48Z` now states that
discipline clearly:

- `handoff.queue_shape = monitoring_queue`
- `handoff.requires_operator_action = false`
- `primary_status_line = high_duplicate_same_source_loop | A distributed vulnerability database for Open Source | recommendation=defer_review | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | followup=upstream_dedup_candidate`

The last remaining artifact gap was the broad report itself.

That report now also supports a top-level handoff surface in report language:

- `empty_report`
- `observational_only`
- `settled_or_reviewed`
- `deferred_monitoring`
- `action_required`

This keeps the operator story aligned across all three artifact types without
collapsing their distinct semantic layers.

Latest live report artifact at `2026-03-11T14:46:12Z` now makes that broad
surface concrete too:

- `handoff.queue_shape = deferred_monitoring`
- `handoff.requires_operator_action = false`
- `primary_status_line = deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`

Once all three artifacts shared that contract, the next cleanup was no longer a
semantic phase but an implementation one: centralize the handoff plumbing
without collapsing the three semantic altitudes.

The branch now has one shared utility layer for:

- status-line normalization
- `primary_status_line` selection
- top-level `handoff` assembly
- markdown rendering for `## Handoff`
- markdown rendering for `## Status Lines`

And the important guardrail stayed intact:

- report still owns `deferred_monitoring`
- grouping still owns `monitoring_queue`
- batch still owns `stable_history_only`

That made one more read-only lift possible above the artifact layer itself.

`scripts/run_refreshable_artifact_report.py` can now read existing latest JSON
artifacts and surface their compact handoff previews without recomputing
subjectivity semantics.

At `2026-03-11T15:05:33Z`, the live refreshable report now exposes:

- `summary.handoff_preview_count = 3`
- report preview: `deferred_monitoring`
- grouping preview: `monitoring_queue`
- batch preview: `stable_history_only`

So the higher-level artifact lane no longer only answers "can this be
regenerated?" It now also answers "what queue posture will I see when I open
it?"

The next read-only lift above that was the worktree settlement layer.

`scripts/run_worktree_settlement_report.py` now reuses the refreshable lane's
existing handoff previews and attaches them to the `refreshable_artifacts`
settlement lane instead of treating that lane as pure cleanup abstraction.

At `2026-03-11T15:14:08Z`, the live settlement artifact now exposes:

- `summary.refreshable_handoff_preview_count = 3`
- refreshable settlement preview: report -> `deferred_monitoring`
- refreshable settlement preview: grouping -> `monitoring_queue`
- refreshable settlement preview: batch -> `stable_history_only`

So even the branch-movement settlement layer now carries a truthful glimpse of
the subjectivity queue without pretending to become the subjectivity engine.

That same mirror now reaches the repo-governance settlement layer too.

`scripts/run_repo_governance_settlement_report.py` now reads the existing
`worktree_settlement_latest.json` preview surface and mirrors it in governance
language without recomputing subjectivity state.

At `2026-03-11T15:15:54Z`, the live governance settlement artifact now exposes:

- `worktree_settlement.refreshable_handoff_preview_count = 3`
- governance mirror: report -> `deferred_monitoring`
- governance mirror: grouping -> `monitoring_queue`
- governance mirror: batch -> `stable_history_only`

So the subjectivity queue is now visible all the way up the governance ladder
while each layer still keeps its own honest boundary.

## 2026-03-11 Addendum: Historical Figure Audit

The handoff and review surfaces are now strong enough that the next meaningful
pressure did not need to come from another storage or reporting phase.

It needed to come from history.

The branch now carries a formal historical-figure audit addendum and a reusable
seed corpus:

- `docs/plans/memory_subjectivity_historical_figure_audit_addendum_2026-03-11.md`
- `docs/experiments/historical_viewpoint_audit_seed_2026-03-11.json`

This phase is intentionally audit-only.

It does not:

- promote any figure into runtime persona
- mutate review semantics automatically
- widen schema or change retrieval

What it does is harder:

it pressure-tests the active `tension -> vow` criteria against historically
durable figures whose commitments reveal three distinct risks:

- coherent direction is not the same as legitimate direction
- restraint and witness may be real direction even when they do not look like
  governance defense
- minority truth may begin before context diversity becomes comfortable

The most important finding is a policy gap, not a runtime bug:

the active review criteria are good at detecting semantic maturity, but they do
not yet explicitly require `axiomatic admissibility` before `approved`.

History makes that gap visible because some lines can satisfy:

- directionality
- recurrence
- reviewable basis
- cross-context durability

and still be unfit for commitment weight.

So the likely next strengthening move, if the branch chooses to act on this
audit, is not more plumbing.

It is a future policy clarification:

- `approved` should require semantic maturity
- and admissibility under existing P0/P1 constraints

That clarification has now been applied to the official criteria document
itself.

The branch now explicitly requires `axiomatic admissibility` before
`approved`, and the operator review-batch template now prompts reviewers to
check P0/P1 compatibility before they grant commitment weight.

This still remains policy-first.

The branch has not yet added:

- an automatic admissibility scorer
- a new runtime rejection pipeline
- a new gateway field

So this phase tightens official judgment without pretending that automation
already exists.

## 2026-03-11 Addendum: Review Batch Admissibility Checklist Surface

Once admissibility became official policy, the next question was not whether to
invent another gate.

It was where that gate should first become visible.

This phase resolves that question in favor of the review batch artifact.

That is the right place because batch already answers:

- what deserves manual attention
- what likely stays deferred
- what likely stays rejected

So the branch now exposes `axiomatic_admissibility_checklist` on each
`review_group`, plus top-level summary counts for:

- admissibility gate posture
- admissibility focus

And the markdown artifact now renders those surfaces directly.

The important boundary is that this remains reviewer aid.

The branch still does not:

- persist admissibility as replay metadata
- auto-score admissibility
- expand batch group review into an approval seam

So policy and operator surface are now aligned, while runtime authority remains
deliberately unchanged.

## 2026-03-11 Addendum: Admissibility Status Line Surface

Once the checklist existed, the next pressure was not semantic.

It was operational readability.

The batch artifact already knew how to say:

- full admissibility checklist
- per-group risk tags
- operator prompt

But interruption recovery still benefited from a smaller surface.

So the branch now also exposes:

- `admissibility_status_line` on each review group
- `admissibility_primary_status_line` at the batch top level
- `admissibility_status_lines` as a reusable list

This mirrors the earlier queue-posture work:

- keep the full structure
- add one compact resumable line

The live branch now states that its one remaining deferred group is blocked by:

- `admissibility_not_yet_clear`
- focus `authority_and_exception_pressure`

That is a better restart surface than reopening the full checklist every time.

## 2026-03-12 Addendum: Admissibility Preview Mirror

The compact admissibility line is now useful enough that it should not stay
trapped inside review batch.

This phase mirrors it upward through the existing preview chain:

- refreshable artifact report
- worktree settlement
- repo governance settlement

The crucial guardrail is that none of those layers recompute admissibility.

They only mirror the already-existing field:

- `admissibility_primary_status_line`

That keeps the architecture honest.

Review batch remains the semantic owner.

The higher layers only become better mirrors of its state.

Focused validation is complete:

- `10 passed`
- `ruff check` passed
- `black --check` passed

And the live upward mirror now reads as:

- refreshable: `handoff_preview_count = 3`, `admissibility_preview_count = 1`
- worktree settlement: `refreshable_handoff_preview_count = 3`, `refreshable_admissibility_preview_count = 1`
- repo governance settlement: `refreshable_handoff_preview_count = 3`, `refreshable_admissibility_preview_count = 1`

So the branch no longer requires an operator to reopen review batch just to
recover the current admissibility blocker. The higher mirrors now show both:

- queue posture
- admissibility posture

## 2026-03-12 Addendum: Subjectivity Focus Preview Card

Once both axes reached the higher mirrors, the next remaining operator cost was
not missing truth but scan effort.

There were still three subjectivity previews to read:

- report
- grouping
- batch

Yet only one preview actually carried the branch's decisive unresolved line:

- the stable deferred queue posture
- the still-open admissibility blocker

So this phase adds one explicit focus card:

- `subjectivity_focus_preview`

It is still mirror-only. It selects from already mirrored preview objects and
prefers the one that already carries `admissibility_primary_status_line`.

The live focus card now resolves to:

- `docs/status/subjectivity_review_batch_latest.json`
- `stable_history_only`
- `admissibility_not_yet_clear | focus=authority_and_exception_pressure | tags=cross_cycle_persistence, exception_pressure, externalized_harm_check, low_context_diversity`

So interruption recovery at the higher mirrors no longer depends on scanning
the whole preview list to discover which subjectivity line still matters most.

## 2026-03-12 Addendum: Requires-Operator-Action Preview Mirror

The next missing truth was smaller but still important:

the higher mirrors still did not carry the leaf artifact's own answer to:

- does this queue currently require operator action?

That answer already existed as `handoff.requires_operator_action`.

So this phase mirrors that field upward without recomputing it.

The live branch now says, at refreshable, worktree settlement, and repo
governance heights, that the current subjectivity focus preview is:

- `stable_history_only`
- `requires_operator_action = false`
- still blocked by `admissibility_not_yet_clear`

So the higher mirrors now carry not only posture and blocker, but also the
leaf artifact's own declared action stance.
