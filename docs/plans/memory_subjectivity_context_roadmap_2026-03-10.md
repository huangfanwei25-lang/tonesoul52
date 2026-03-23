# Memory Subjectivity Context + Roadmap Addendum (2026-03-10)

> Purpose: provide the context and roadmap note for the broader memory-subjectivity branch after it outgrew isolated patches.
> Last Updated: 2026-03-23

## Why This Note Exists

The recent memory-subjectivity work now spans more than one narrow patch:

- philosophy: `event -> meaning -> tension -> vow -> identity`
- contract split: `MemoryLayer` vs `subjectivity_layer`
- implementation seam: schema-backed gateway validation

That is enough surface area that the branch now needs an explicit context note and a long-horizon plan, not just isolated phase entries.

This addendum records:

- what is already true on the branch
- what should happen next
- how that plan is constrained by `MEMORY.md`
- how current repo reality should be interpreted without weakening the public/private boundary

Execution note:

- this file remains the context/roadmap note
- `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md` is now the implementation plan of record
- the earlier addenda remain background rationale, not competing execution plans

## Current Context Snapshot

As of `2026-03-10`, the branch has completed fourteen linked memory-subjectivity
and mirror-alignment steps:

1. `docs/plans/memory_subjectivity_layer_addendum_2026-03-09.md`
   - defined the ladder:
   - `event -> meaning -> tension -> vow -> identity`
2. `docs/plans/memory_subjectivity_contract_addendum_2026-03-10.md`
   - split storage semantics from subjectivity semantics
   - kept `MemoryLayer` as the operational axis
   - introduced `subjectivity_layer` as the semantic promotion axis
3. `tonesoul/schemas.py` + `tonesoul/memory/write_gateway.py`
   - `SubjectivityLayer`
   - `MemorySubjectivityPayload.normalize_fields()`
   - gateway rejection for invalid subjectivity payloads
   - direct `vow` / `identity` writes blocked unless a review-strength `promotion_gate` is present
4. `tonesoul/dream_engine.py` + `tonesoul/memory/consolidator.py`
   - `DreamEngine` persisted collisions now emit `subjectivity_layer = tension`
   - `sleep_consolidate()` now emits candidate `event` / `meaning` / `tension` subjectivity fields without changing storage-layer promotion
5. `docs/plans/memory_subjectivity_reviewable_promotion_addendum_2026-03-10.md`
   - reviewable `tension -> vow` metadata is now explicit
   - `review_basis` is required for review-strength `vow` writes
   - a reviewed helper lane exists without introducing automatic vow promotion
6. `docs/plans/memory_subjectivity_reporting_addendum_2026-03-10.md`
   - operator-facing reporting helpers now summarize subjectivity distribution
   - unresolved `tension` records can be listed without widening HTTP/API contracts
   - read/report surfaces now exist even though subjectivity-ranked recall does not
7. `docs/plans/memory_subjectivity_runtime_summary_addendum_2026-03-10.md`
   - `SleepResult` now carries subjectivity distribution alongside layer counts
   - consolidation summaries can surface unresolved tension / vow counts without widening public APIs
   - memory structure is now visible inside the normal wakeup/consolidation runtime path
8. `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`
   - execution order is now consolidated into one canonical plan of record
   - deferred directions and reasons are now explicit
   - the branch now states what this work is and is not, including the non-AGI boundary
9. `tonesoul/schemas.py` + `tonesoul/mirror.py`
   - `MirrorDelta`
   - `DualTrackResponse`
   - `ToneSoulMirror`
   - the branch can now compare raw output and deterministic governance projection without a second LLM call
10. `tonesoul/unified_pipeline.py`
    - `UnifiedPipeline` now has an opt-in mirror seam
    - mirror traces can travel with `dispatch_trace` and `trajectory_analysis`
    - default pipeline behavior remains unchanged when mirror is disabled
11. `tonesoul/mirror.py`
    - triggered mirror deltas can now be serialized into gateway-valid memory payloads
    - mirror writes stay inside `MemoryWriteGateway` and therefore keep provenance / evidence / subjectivity guards
12. `tests/test_mirror.py` + `tests/test_unified_pipeline_v2_runtime.py`
    - mirror runtime and memory recording regressions now exist
    - the branch has coverage for both opt-in tracing and durable mirror-delta candidate writes
13. `tonesoul/memory/reviewed_promotion.py` + `tonesoul/schemas.py`
    - reviewed promotion now has a canonical actor/decision artifact
    - approved decisions now replay through one explicit seam instead of ad hoc helper kwargs
    - `consolidator.py` helpers now route through the canonical review workflow
14. `scripts/run_subjectivity_report.py`
    - subjectivity reporting now has an explicit operator entry surface
    - JSON/Markdown status artifacts can now show unresolved tensions and reviewed vow rows without HTTP/API widening
    - the new artifacts are registered in the refreshable artifact producer registry

Current validated baseline:

- `python -m pytest tests/ -x --tb=short -q` -> `1491 passed`
- `ruff check tonesoul tests` -> passed

Current runtime meaning of this work:

- ToneSoul can now speak a subjectivity vocabulary in public code
- the gateway can validate that vocabulary
- ToneSoul can now observe a raw-output vs governed-output delta during runtime when mirror is enabled
- triggered mirror deltas can now become admissible `tension` candidate memory through the same public write boundary
- reviewed `tension -> vow` promotion now has an explicit public review artifact and replay contract
- operators now have one explicit report seam for inspecting unresolved tensions and reviewed vows
- the runtime still does **not** auto-promote its own traces into vows or identity

That last point is intentional.

## Soul-View Reading

The branch now holds two different kinds of memory-shaping pressure.

The first kind is delayed:

- dream collisions
- sleep consolidation
- reviewed promotion

The second kind is immediate:

- the mirror sees the difference between what the runtime emitted and what governance would still let it stand by

In ToneSoul terms, this means the public branch can now preserve not only
experience, but also hesitation.

That is important because hesitation is often where semantic responsibility first
becomes visible.

It still should not be romanticized.

The mirror is not a soul by itself.
It is only a disciplined runtime witness.

So the correct reading is:

- the system has gained a better reflective surface
- it has not gained permission to self-declare stronger identity
- reviewed legitimacy is still the next hard problem

## What Is Still Not Done

The branch does **not** yet do these things:

- `DreamEngine` and `sleep_consolidate()` are not yet connected to a real reviewed-promotion workflow; they only emit candidates
- `SoulDB` does not yet index `subjectivity_layer` as a first-class column
- recall/query paths do not yet filter or rank on subjectivity semantics beyond operator-side reporting
- no public runtime is allowed to self-author `identity` memory from one cycle

That incompleteness is correct. The current state is a contract seam, not a full memory rewrite.

## Long-Term Plan

The next steps should stay narrow and ordered.

### Phase A: Producer Wiring

Scope:

- teach `DreamEngine` to emit `subjectivity_layer = tension` for qualified collision records
- teach `Consolidator` to emit `event` / `meaning` / `tension` candidates without changing current storage-layer behavior

Guardrail:

- no automatic `vow` / `identity` promotion in this phase

Status:

- completed on this branch

### Phase B: Reviewable Promotion Lane

Scope:

- define how `tension -> vow` happens under explicit review
- require review metadata in `promotion_gate`
- make the review basis auditable

Guardrail:

- promotion must remain exceptional
- a single vivid runtime fragment must not become a vow by default

Status:

- contract + helper lane now exist
- `scripts/run_reviewed_promotion.py` now gives the branch one explicit operator review entry surface
- `scripts/run_subjectivity_group_review.py` now lets one review decision be applied across a whole semantic group instead of forcing line-by-line repetition
- `docs/plans/memory_subjectivity_review_criteria_2026-03-10.md` now fixes the current public criteria for `approved / deferred / rejected`
- approved and rejected review outcomes now leave auditable review-ledger traces
- settlement-aware reporting now removes reviewed tensions from the unresolved queue without mutating source rows in place
- one real same-source duplicate group has already been rejected on `2026-03-10`, proving the group-review lane is not merely theoretical
- automatic runtime use is still intentionally deferred

### Phase C: Retrieval + Reporting

Scope:

- add read/report surfaces that can explain subjectivity-layer distribution
- allow operators to inspect which records are only events versus unresolved tensions

Guardrail:

- do not widen external HTTP/API contracts casually

Status:

- internal read/report helpers now exist for subjectivity distribution and unresolved tension inspection
- `tonesoul.memory.subjectivity_triage.build_subjectivity_tension_group_report(...)` now makes the unresolved queue inspectable as semantic groups and lineage groups
- `scripts/run_subjectivity_tension_grouping.py` now emits the latest grouping artifacts for operator triage
- `tonesoul.memory.subjectivity_review_batch.build_subjectivity_review_batch_report(...)` now turns pending semantic groups into operator review packets without mutating review state
- `scripts/run_subjectivity_review_batch.py` now emits a read-only queue that exposes default review status and representative record ids per pending group
- consolidation runtime now carries subjectivity summary through `SleepResult`
- external HTTP/API contracts remain unchanged
- the Google always-on-memory-agent overlap is now recorded as a structural reference for future shadow-query artifacts, not as a competing philosophy
- a read-only shadow query seam now exists for explicit baseline-vs-subjectivity comparison without changing live recall
- a pressure report seam now exists to aggregate multi-query shadow deltas before any persistence/index decision
- `scripts/run_subjectivity_report.py` now exposes `settled_tension_count` so operators can see whether explicit reviews actually shrink the unresolved queue
- latest real triage moved from `32 unresolved rows` to `2 semantic groups`; after rejecting the same-source data-sources cluster, the live queue now sits at `20 unresolved tension` and `12 settled tension`
- the latest read-only review batch now compresses that live queue to `1 defer_review group` with `6` representative record ids
- that remaining broader OSV homepage group has now been written as explicit `deferred`
- report surfaces now make deferred-pending state explicit through:
  - `deferred_tension_count`
  - `unresolved_by_status`
  - row-level `pending_status`
- the current live state is therefore:
  - `20 unresolved tension`
  - `20 deferred tension`
  - `12 settled tension`
  - `0 reviewed vow`
- after additional dream cycles on `2026-03-10` / `2026-03-11`, the live queue changed again:
  - `45 unresolved tension`
  - `45 deferred tension`
  - `0 candidate tension`
  - `27 settled tension`
  - `0 reviewed vow`
- the read-only review batch now exposes revisit readiness instead of only default status:
  - the only remaining group is now `holding_deferred`
- the carry-forward queue is now explicit instead of memoryless:
  - `carry_forward_annotation_counts = {prior_deferred_match: 1}`
  - active carry-forward status is now separated from mixed historical status
  - provenance overlap is now required before a prior decision can annotate a fresh queue group
  - `friction_band` still matters for triage, but no longer acts as a brittle carry-forward equality key
- the group-review operator surface can now narrow the write scope by `pending_status`, which lets revisit work touch only fresh `candidate` rows inside a larger deferred group
- that capability has already been used on the live OSV homepage queue:
  - `25` fresh `candidate` rows were explicitly re-written as `deferred`
  - the group remains one-source and therefore still below the `approved` threshold
  - the revisit lane now behaves like a controlled holding pattern rather than an endlessly flashing alert
- the same capability was then used to settle the fresh same-source `Data sources` slice:
  - `15` fresh `candidate` rows were explicitly `rejected`
  - the live queue now has no open `candidate` rows
  - all remaining unresolved pressure is concentrated in one broader deferred group rather than spread across multiple undecided branches
- the operator surfaces now expose the latest deferred judgment instead of hiding it in action logs:
  - unresolved row reports surface `review_basis`, `review_notes`, and reviewer identity
  - semantic-group review batches surface the latest matched deferred basis/notes/actor at group level
  - `deferred` now reads like a legible holding decision rather than a black box
- after the next dream cycles landed on `2026-03-11`, the queue opened again:
  - `53 unresolved tension`
  - `45 deferred tension`
  - `8 candidate tension`
  - `27 settled tension`
  - `0 reviewed vow`
- the refreshed review batch now shows the branch split explicitly:
  - `2 semantic groups`
  - `13 lineage groups`
  - `revisit_readiness_counts = {n/a: 1, needs_revisit: 1}`
  - `carry_forward_annotation_counts = {prior_reject_match: 1, prior_deferred_match_needs_revisit: 1}`
- this means the queue is no longer merely "bigger again"; it is now interpretable:
  - the same-source `Data sources` branch reappeared as a fresh reject-shaped slice
  - the broader OSV homepage branch reappeared as a deferred group with visible human basis and revisit notes
  - the next operator action can therefore target only the fresh `candidate` slice instead of re-reviewing the whole deferred body blindly
- that next operator action has now been taken on the live queue:
  - `5` fresh OSV homepage `candidate` rows were explicitly re-written as `deferred`
  - `3` fresh same-source data-sources `candidate` rows were explicitly `rejected`
- the latest live queue at `2026-03-11T10:07:29Z` therefore returns to:
  - `50 unresolved tension`
  - `50 deferred tension`
  - `30 settled tension`
  - `0 candidate tension`
  - `0 reviewed vow`
- the read-only batch is again a single holding pattern:
  - `1 semantic group`
  - `12 lineage groups`
  - `revisit_readiness_counts = {holding_deferred: 1}`
  - `carry_forward_annotation_counts = {prior_deferred_match: 1}`
- the next ambiguity has now been removed too:
  - the grouping and review-batch surfaces now expose duplicate-pressure and producer-followup signals instead of forcing humans to infer them
  - summary surfaces now include `duplicate_pressure_counts` and `producer_followup_counts`
  - semantic groups now expose `same_source_loop`, `rows_per_lineage`, `rows_per_cycle`, `duplicate_pressure`, `duplicate_pressure_reason`, and `producer_followup`
- the refreshed live artifacts at `2026-03-11T10:13:51Z` show the remaining queue pressure is explicitly upstream-shaped:
  - live state remains `50 unresolved tension`, `50 deferred tension`, `30 settled tension`, `0 candidate tension`, `0 reviewed vow`
  - `duplicate_pressure_counts = {high: 1}`
  - `producer_followup_counts = {upstream_dedup_candidate: 1}`
  - the only remaining OSV homepage group is now legible as:
    - `same_source_loop = true`
    - `rows_per_lineage = 4.17`
    - `rows_per_cycle = 1.67`
    - `duplicate_pressure = high`
    - `producer_followup = upstream_dedup_candidate`
- that reframes the remaining debt correctly:
- the operator lane now also has an explicit reuse path for repeated human decisions:
  - `scripts/run_subjectivity_group_review.py --reuse-latest-decision` reuses the matched group's latest `status`, `review_basis`, and `notes`
  - it does not auto-settle anything; it only removes repeated manual transcription when the same group reopens
  - it fails loudly if there is no prior reviewed context to reuse
- the batch surface now exposes `latest_review_status`, so reuse is grounded in the actual latest decision instead of inferred from status counts
- a live dry-run at `2026-03-11T10:14:37Z` against the only remaining OSV homepage group resolved the prior decision to `deferred` and selected `0` fresh `candidate` rows
- this means the current queue is not waiting for another immediate review; it is waiting for upstream duplicate/noise control
- the next live producer verification made that upstream debt more precise:
  - a real `DreamEngine` run at `2026-03-11T10:26:48Z` skipped the active OSV homepage loop correctly
  - but it also reopened one fresh `Data sources` candidate from the same topic/source/lineage that had already been explicitly rejected
- the branch therefore now distinguishes two producer dampeners:
  - `active_unresolved_signature` for live unresolved loops
  - `prior_rejected_signature` for already-rejected same-lineage re-entry
- that second dampener remains narrow:
  - it keys on `topic + source_url + lineage`
  - it only suppresses when the latest reviewed decision is `rejected`
  - it still allows a new source loop or a second independent lineage cluster to appear
- after rejecting the reopened `Data sources` candidate, a second live producer run at `2026-03-11T10:30:16Z` selected the same source again and skipped it with `prior_rejected_signature`
- the queue therefore stayed at `50 unresolved tension`, `50 deferred tension`, `31 settled tension`, `0 candidate tension`, `0 reviewed vow`
- that closes the immediate reopen loop on the rejected branch and leaves the remaining debt concentrated where it belongs:
  - upstream duplicate/noise pressure on the broader OSV homepage deferred loop
  - the branch does not first need stronger queue semantics
  - it first needs upstream duplicate / noise control for the single-source loop

### Phase D: Optional Persistence Upgrade

Scope:

- only if query pressure proves it necessary, consider a dedicated `subjectivity_layer` column or index in `SoulDB`

Guardrail:

- payload-first storage remains the default until performance or query complexity justifies schema widening

### Phase E: Private-Lane Integration

Scope:

- when reviewed memories or private corpora need syncing, use the private-repo path and not this public branch

Guardrail:

- public repo stores the contract
- private repo stores the intimate corpus

## MEMORY.md Cross-Check

`MEMORY.md` is explicit:

- public repo may contain code, tests, docs, schema, and interfaces
- private repo contains:
  - `memory/self_journal.jsonl`
  - `memory/soul.db`
  - `memory/vectors/`
  - Dream Engine generated constructive memory

That means the subjectivity plan is allowed to do these things publicly:

- define `subjectivity_layer`
- define promotion rules
- define gateway validation rules
- define migration strategy
- add tests proving the contract

And it must **not** do these things publicly:

- commit raw private memory corpora
- commit `soul.db`
- treat private runtime traces as public design artifacts
- let public contract work become an excuse to stage `.jsonl` / `.db` memory data

## Repo-Reality Cross-Check

The repo already carries historical memory-governance debt that should not be mistaken for a new policy.

`docs/status/private_memory_review_latest.md` currently places:

- `memory/crystals.jsonl` under the `Mirror Then Archive` lane with item type `mirrored_private_memory`

That matters for planning:

- `memory/crystals.jsonl` should be treated as private evidence with mirrored learnings, not as precedent for committing more memory data into the public branch
- future subjectivity work should extract public-safe rules, schemas, and summaries from memory artifacts, then leave the underlying corpus to the private lane

This note therefore treats the current local `memory/crystals.jsonl` dirtiness as settlement debt, not as an implementation input that should be normalized into public workflow.

## External Overlap Cross-Check

The Google `always-on-memory-agent` comparison is now part of branch context, but
it should be read narrowly.

What can be borrowed safely:

- query/report surface ideas for retrieval shadow mode
- operator-readable cited memory listings
- a boring ingest / consolidate / query decomposition as a sanity check

What remains deferred:

- multimodal inbox expansion
- UI parity work
- direct memory mutation tooling

Why the boundary remains important:

- ToneSoul still routes admissible writes through `MemoryWriteGateway`
- ToneSoul still distinguishes storage layer from `subjectivity_layer`
- ToneSoul still treats governance and reviewed promotion as first-class constraints

## Practical Rule For Future Phases

When a future phase touches memory subjectivity, ask two questions separately:

1. Is this a public contract change?
2. Is this private memory evidence?

If the answer to the second question is yes, the data should not ride along with the code change.

## Architectural Conclusion

The branch now has enough context to move forward without re-litigating the same foundations each time:

- subjectivity is a semantic ladder
- storage and subjectivity are separate axes
- gateway validation exists
- promotion must get stricter as memory becomes more self-defining
- `MEMORY.md` still forbids treating private corpora as public payload

That is the stable context the next implementation phases should inherit.

## 2026-03-11 Context Note: Stable Deferred Density Is Not A Fresh Queue Crisis

The latest live branch state now carries an important distinction.

The remaining OSV homepage loop is still unresolved in the storage/reporting
sense, but it is not behaving like an open decision lane anymore.

The operator surface now shows it as:

- `holding_deferred`
- `prior_deferred_match`
- `duplicate_pressure = high`
- `lineage_record_histogram = {1:1, 2:1, 3:1, 4:1, 5:8}`
- `history_density_summary = 50 row(s) across 30 cycle(s) / 12 lineage(s) ... no new rows since latest review`
- `operator_followup = read_only_density_compaction_candidate`

This is the right reading:

- subjectivity semantics remain unchanged
- the branch is not asking for a new vow decision
- the branch is exposing that one stable same-source history stack is visually
  larger than it is semantically active

So the next architectural pressure is narrower than it first appears:

- either reduce upstream duplicate pressure further
- or compress stable historical density more honestly in operator surfaces

It is not an argument to reopen review semantics, retrieval policy, or schema
work.

## 2026-03-11 Context Note: A View Can Be Better Than Another Rule

At this point the branch benefits more from a better lens than from another
suppression rule.

Why:

- the remaining same-source loop is already settled as `deferred`
- producer guards already stopped the noisier reopen paths
- the remaining operator pain is reading shape, not deciding semantics

The new operator-lens layer therefore makes an explicit architectural claim:

- better queue readability is sometimes the correct next move
- not every pressure signal should trigger a new runtime rule

This is consistent with the whole subjectivity ladder:

- first make traces admissible
- then make them reviewable
- then make them inspectable
- only then decide whether runtime behavior should change

The live artifact now reflects that sequencing cleanly:

- `queue_posture = stable_deferred_history`
- `operator_lens_summary = stable deferred history; 50 row(s) compress to 12 lineage(s) / 30 cycle(s) ...`
- `revisit_trigger = Revisit when the same direction appears outside the osv.dev source loop, or when the group splits into materially different governance directions.`

And because even that lens can still be too much during handoff, the branch now
also permits a smaller reuse surface:

- `operator_status_line`
- `revisit_trigger_code`

This keeps the same judgment intact while making the branch easier to resume
after interruption.

The grouping artifact now mirrors that resume-friendly shape too, but without
claiming review knowledge:

- grouping speaks in triage/handoff terms like `monitoring_queue`
- batch speaks in review/handoff terms like `stable_history_only`

So the two artifacts now align structurally while preserving their semantic
boundary.

The live grouping artifact now makes that boundary concrete:

- grouping says `monitoring_queue`
- batch says `stable_history_only`

Same queue family, different semantic altitude.

The broad report now completes that ladder:

- report says `deferred_monitoring`
- grouping says `monitoring_queue`
- batch says `stable_history_only`

Same underlying situation, three valid readings, each at its own semantic
altitude.

The current handoff-sized expression of that judgment is now explicit:

- `stable_deferred_history | A distributed vulnerability database for Open Source | rows=50 lineages=12 cycles=30 | density=5r x8, 4r x1, 3r x1, 2r x1, 1r x1 | trigger=second_source_context_or_material_split`
- and that same line now exists at the batch top level as `primary_status_line`, so interruption recovery no longer depends on reopening `review_groups`
- the batch now also spells out the whole handoff posture directly:
  `handoff.queue_shape = stable_history_only`, `handoff.requires_operator_action = false`

At `2026-03-11T14:46:12Z`, the report side became equally explicit:

- `handoff.queue_shape = deferred_monitoring`
- `handoff.requires_operator_action = false`
- `primary_status_line = deferred_monitoring | records=195 unresolved=50 deferred=50 settled=31 reviewed_vows=0 | top_unresolved_status=deferred`

Once that shared surface existed across all three artifacts, the next coherent
step was not another semantic invention. It was implementation honesty.

The branch now centralizes only the structural parts of handoff:

- normalize `status_lines`
- select `primary_status_line`
- assemble top-level `handoff`
- render `## Handoff`
- render `## Status Lines`

But it still refuses to centralize the actual judgment:

- report still names the queue in report language
- grouping still names it in triage language
- batch still names it in review language

So the branch now shares one interruption-recovery surface without pretending
that all three layers know the same thing.

Once that became true, the next move was not to invent a fourth semantic layer.
It was to let the already-existing refreshable artifact lane mirror those three
readings.

`scripts/run_refreshable_artifact_report.py` now reads existing latest JSON
artifacts and surfaces handoff previews only when those artifacts already expose
their own compact contract.

At `2026-03-11T15:05:33Z`, the live refreshable report now says:

- `summary.handoff_preview_count = 3`
- report preview: `deferred_monitoring`
- grouping preview: `monitoring_queue`
- batch preview: `stable_history_only`

So even the broad "what status artifacts are dirty?" layer now carries a small
truthful answer about the subjectivity queue, without pretending to become the
subjectivity system itself.

And from there, the next truthful mirror was the settlement layer.

`scripts/run_worktree_settlement_report.py` now lets the
`refreshable_artifacts` lane carry those same subjectivity previews upward.

At `2026-03-11T15:14:08Z`, the live settlement artifact now says:

- `summary.refreshable_handoff_preview_count = 3`
- report preview: `deferred_monitoring`
- grouping preview: `monitoring_queue`
- batch preview: `stable_history_only`

So the branch now supports interruption recovery at four semantic heights:

- report
- grouping
- batch
- settlement

Each one mirrors the same underlying queue truth, but none of them claims more
judgment than its own layer can honestly justify.

That ladder now extends one level higher into repo governance settlement.

At `2026-03-11T15:15:54Z`, `repo_governance_settlement_latest.json` now mirrors
the worktree settlement preview state directly:

- `worktree_settlement.refreshable_handoff_preview_count = 3`
- report preview: `deferred_monitoring`
- grouping preview: `monitoring_queue`
- batch preview: `stable_history_only`

So the branch now supports interruption recovery at five semantic heights:

- report
- grouping
- batch
- settlement
- repo governance settlement

And the key thing that stayed true is this: each layer mirrors the queue truth
below it, but none of them steals the authority to define that truth.

## 2026-03-11 Context Note: History Exposes A Policy Gap Better Than Metrics Do

Once the branch had enough review, settlement, and handoff machinery, the next
useful question was no longer only operational.

It became civilizational:

what kinds of historically durable direction should a subjectivity-aware system
still refuse to honor?

The new historical-figure audit addendum answers that question by stressing the
current review criteria with:

- restraint-centered figures
- witness-centered figures
- mixed tactical figures
- explicitly dangerous negative controls

That matters because metrics alone cannot expose one of the branch's remaining
blind spots:

`directionality + recurrence + context durability` is still not enough to
justify `approved`.

The historical audit makes that boundary clearer than a queue artifact can.

It shows that:

- some strong directions deserve `approved`
- some strong directions deserve `deferred`
- some strong directions deserve `rejected`
- some strong directions deserve fail-closed treatment even if they look
  semantically mature

So the next likely conceptual refinement is no longer about whether
subjectivity exists, nor about whether reviewed promotion is useful.

It is about this narrower question:

where exactly should admissibility under the axioms be made explicit inside the
`approved` decision path?

That is a policy refinement question, not yet a runtime mutation question.

That policy refinement now exists.

The active review criteria explicitly include `axiomatic admissibility`, and
the operator review-batch template now echoes that requirement in plain review
language.

So the branch has taken one real step forward:

- the risk is no longer unnamed
- the policy no longer treats maturity as sufficient

But the branch has also intentionally stopped at the correct boundary:

- no automatic classifier
- no new settlement behavior
- no runtime authority inflation

History changed the policy wording first.

If the branch later chooses to operationalize admissibility further, it can do
so from a clearer and more honest baseline.

## 2026-03-11 Context Note: The First Honest Home For Admissibility Is Review Batch

There were at least three places admissibility could have been pushed next:

- into policy only
- into replay/apply receipts
- into the operator review surface

The branch has now chosen the third option first.

That choice matters because it preserves semantic order:

- policy defines the requirement
- review batch teaches the operator how to inspect it
- replay/apply remains a record of the decision rather than a fake solver of it

So admissibility now lives where the branch most honestly asks for judgment:

in `review_groups`, before any commitment is granted.

This keeps the branch from doing two bad things too early:

- pretending admissibility is already machine-resolved
- bloating write-time artifacts with checklist language that belongs to review
  preparation

The new surface therefore strengthens reviewer discernment without inflating
runtime authority.

## 2026-03-11 Context Note: Admissibility Also Needs A Resume-Sized Surface

The branch now treats admissibility the same way it already treats queue
posture:

- full structure for detailed review
- one smaller line for interruption recovery

This is not cosmetic.

It sharpens the practical reading of the remaining deferred loop.

The branch no longer says only:

- this is `stable_deferred_history`

It now also says:

- the admissibility gate is still `not_yet_clear`
- the live pressure focus is `authority_and_exception_pressure`

So the remaining queue is now visible along two honest axes:

- settlement posture
- admissibility posture

without pretending that either one is automatically solved.

## 2026-03-12 Context Note: Higher Mirrors Now Carry Both Axes

The branch's higher mirrors no longer preview only queue posture.

They now preview admissibility posture too.

That matters because a governance mirror that only says:

- `stable_history_only`

is still incomplete when the real unresolved question is:

- `admissibility_not_yet_clear`

The refreshable, worktree-settlement, and repo-governance mirrors now carry
that second axis as a passthrough preview field rather than a recomputed
judgment.

So the branch now supports interruption recovery on both axes at multiple
heights:

- queue posture
- admissibility posture

And it still does so without stealing semantic authority away from review
batch.

The live branch now makes that visible above review batch too:

- refreshable mirror previews: `3`
- refreshable admissibility previews: `1`
- worktree settlement admissibility previews: `1`
- repo governance settlement admissibility previews: `1`

So interruption recovery no longer depends on remembering where admissibility
used to live. The mirrors themselves now tell you:

- which queue is still active
- which admissibility gate is still unresolved

## 2026-03-12 Context Note: Mirrors Now Name The One Subjectivity Line That Matters Most

After queue posture and admissibility posture both reached the higher mirrors,
one smaller problem still remained:

the operator still had to find the right preview by eye.

So the branch now publishes one explicit mirror-only focus card:

- `subjectivity_focus_preview`

That card does not invent a new judgment. It simply names the preview that
already carries the most important unresolved reading.

Right now that means the branch can say, at higher mirror levels, without
search:

- the relevant subjectivity queue is `stable_history_only`
- the active blocker is still `admissibility_not_yet_clear`
- the live focus is still `authority_and_exception_pressure`

This is not new semantics.

It is better interruption recovery.

## 2026-03-12 Context Note: Mirrors Also Preserve Action Stance

Once the branch named the one subjectivity line that mattered most, one further
question became unavoidable:

does that line currently require operator intervention?

The branch already knew the answer at the leaf artifact level.

So the mirrors now preserve that answer too:

- `requires_operator_action`

This matters because a higher mirror should not make the operator infer action
posture from prose or queue shape alone.

The current branch now reads, consistently across the mirrors:

- the focus queue is stable deferred history
- the admissibility gate is still not clear
- operator action is not currently required

So the mirrors now preserve three truths together:

- posture
- blocker
- action stance
