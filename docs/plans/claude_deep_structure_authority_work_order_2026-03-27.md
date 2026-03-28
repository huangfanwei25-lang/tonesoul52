# Claude Work Order — Deep Structure Authority Distillation (2026-03-27)

> Purpose: give a high-context synthesis agent a bounded documentation workstream that converts repo-scale structural insight into durable authority boundaries for later AI instances.
> Last Updated: 2026-03-27
> Issued By: Codex
> Target Agent: Claude Opus / other long-context synthesis-heavy collaborator
> Priority: high
> Status: primary authority-distillation pass completed; follow-up extension appended for implementation-gap triage

## Why This Workstream Exists

ToneSoul now has a clearer AI entry stack:

- `operational`: quickstart and working reference
- `canonical`: architecture anchors and contracts
- `deep_map`: anatomy-scale system map
- `interpretive`: deeper narrative readings

That is good enough for entry.

What is still missing is a durable answer to a harder question:

> when a term appears in `law/`, `docs/`, `research/`, `tests/`, and narrative prose at the same time, what exactly is its current authority and implementation status?

This is where a long-context synthesis agent is strongest.

## Why This Fits Claude

This work is best done by an agent that is strong at:

- scanning many files without losing global structure
- turning large repo slices into named conceptual planes
- extracting a panoramic map from `law/`, `PARADOXES/`, `tests/`, `scripts/`, and narrative docs together
- writing high-density synthesis without collapsing distinct layers into one

This is not a runtime feature ticket.
It is a structure-and-boundary distillation ticket.

## Current Repo Posture

Read these first:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `docs/AI_REFERENCE.md`
4. `docs/narrative/TONESOUL_ANATOMY.md`
5. `docs/narrative/TONESOUL_CODEX_READING.md`
6. `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`
7. `AXIOMS.json`
8. `tonesoul/runtime_adapter.py`
9. `tonesoul/diagnose.py`
10. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
11. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`

Important current boundary:

- `AI_QUICKSTART` and `AI_REFERENCE` are operational guides, not constitutions
- `TONESOUL_ANATOMY` is a deep system map, not a runtime contract
- `TONESOUL_CODEX_READING` and the deep-reading anchor are interpretive, not executable truth
- many `law/` terms are real and important, but not all are current `runtime_adapter.py` hard dependencies

## Primary Objective

Produce a source-backed map that tells later agents, for major ToneSoul claims and terms:

- where the claim lives
- what kind of authority it has
- whether it is implemented now, partially implemented, or still theoretical
- whether an operator may rely on it during live engineering work

## Deliverables

### Deliverable A

Create:

- `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`

This should be a table-driven map of the most load-bearing 40-80 claims or terms across:

- `AXIOMS.json`
- `docs/AI_REFERENCE.md`
- `docs/narrative/TONESOUL_ANATOMY.md`
- `law/`
- runtime/code/test surfaces

Each row should include at least:

- term or claim
- authority role
  - `canonical`
  - `operational`
  - `deep_map`
  - `interpretive`
  - `law`
  - `research`
  - `runtime`
  - `projection`
- implementation status
  - `hard runtime`
  - `runtime-adjacent`
  - `test-backed but distributed`
  - `doc-only`
  - `research/theory`
  - `projection-only`
- source files
- can a later agent rely on this for engineering decisions: `yes / only with verification / no`

### Deliverable B

Create:

- `docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md`

This should explicitly classify high-confusion terms from `law/` and related deep prose into:

1. active runtime or audit dependency
2. active governance vocabulary but not current hard runtime dependency
3. theory / research lane
4. projection / narrative / worldview lane

This contract must explicitly cover:

- `YuHun Gate`
- `StepLedger`
- `Lex Lattice`
- `LAR`
- `Isnād`
- `MDL-Majority`
- `Sovereign Freeze`
- `BBPF`
- `Digital Sovereignty Manifesto`
- `PARADOX_006`

### Deliverable C

Optional, only if needed to support A/B:

- `docs/research/tonesoul_anatomy_source_register_2026-03-27.md`

Use this only if the evidence for `TONESOUL_ANATOMY.md` needs an external register instead of cluttering the anatomy file itself.

## Boundaries

Do not do these things in this workstream:

- do not change `tonesoul/runtime_adapter.py`
- do not change Redis schema, gateway behavior, or commit mutex logic
- do not change `AI_ONBOARDING.md`, `docs/AI_QUICKSTART.md`, or `docs/AI_REFERENCE.md` unless a claim is provably wrong and cannot be corrected later by Codex
- do not touch protected files like `AGENTS.md`
- do not push, merge, or rewrite history
- do not hand-maintain repo file counts unless the number is script-generated in the same pass

If you find that a concept is overclaimed:

- downgrade the claim in documentation
- do not silently "promote" code to match the prose

## Non-Goals

This ticket is not asking for:

- prettier prose
- more philosophy for its own sake
- a new runtime feature
- a dashboard redesign
- another grand unified narrative if the authority map is still missing

## Acceptance Criteria

This workstream is successful if:

- a later AI can answer "is this term active runtime, law, theory, or projection?" without rereading the whole repo
- the biggest overclaiming risks between `law/`, `ANATOMY`, and current runtime are explicitly named
- the resulting docs help future agents avoid mistaking deep structure for live implementation
- no protected files or runtime code are touched

## Suggested Method

1. Read the current AI entry stack and authority boundaries first.
2. Extract the top claims from `AI_REFERENCE`, `ANATOMY`, and `law/`.
3. Cross-check each claim against:
   - `tonesoul/runtime_adapter.py`
   - `tonesoul/diagnose.py`
   - relevant tests
   - canonical architecture contracts
4. Downgrade or split any mixed claim instead of smoothing it over.
5. Leave crisp, table-first artifacts rather than a second long essay.

## Handoff Back To Codex

When done, report back with:

- files created or changed
- 5-10 highest-risk overclaims you found
- which terms are now safe for later AI instances to treat as current runtime truth
- which terms must remain explicitly marked as theory, law, or projection

---

## Follow-Up Extension: Implementation-Gap Triage

This extension exists because Deliverables A/B answer:

> what kind of thing is this term?

But a second, narrower question now matters:

> for the biggest gap terms, should ToneSoul downgrade the prose, keep them as theory, or eventually promote them into a real implementation plan?

This is still a documentation and boundary ticket.
It is not permission to implement the missing mechanisms.

## Why This Follow-Up Fits Claude

This next pass again benefits from panoramic structural judgment:

- it requires comparing prose ambition against runtime evidence
- it requires deciding whether a gap is dangerous, harmless, aspirational, or worth future mainline planning
- it benefits from naming a small set of future work candidates without collapsing them into one giant roadmap

## Follow-Up Objective

Produce a bounded triage of the most important "between theory and runtime" terms so later agents stop oscillating between:

- overclaiming them as already active
- or dismissing them as irrelevant when they are actually live design pressure

The goal is to classify each selected gap term into one of four next-step lanes:

1. **Downgrade prose now**
2. **Keep theory-only**
3. **Contract-only wording is enough**
4. **Deserves a future implementation plan**

## Mandatory Focus Terms

At minimum, re-evaluate these:

- `POAV gate enforcement`
- `Risk (R) calculation`
- `Axiom 5 / Mirror Recursion`
- `Axiom 7 / Semantic Field Conservation`
- `ContractObserver` blocking path
- `PainEngine / CircuitBreaker` trigger path
- `BBPF` enforcement path
- `YuHun Gate` as a distributed runtime metaphor vs a missing object

You may add 2-6 more only if they are comparably dangerous or structurally important.

## Follow-Up Deliverables

### Deliverable D

Create:

- `docs/architecture/TONESOUL_IMPLEMENTATION_GAP_TRIAGE_2026-03-27.md`

This should be a table-first triage for the selected high-gap terms.

Each row should include at least:

- term
- where it is currently overclaimed or easily misread
- actual runtime/code/test evidence
- risk if a later agent misunderstands it
- recommended lane
  - `downgrade prose now`
  - `keep theory-only`
  - `contract-only wording`
  - `future implementation plan`
- short rationale

### Deliverable E

Optional, only if clearly justified by Deliverable D:

- `docs/plans/tonesoul_gap_followup_candidates_2026-03-27.md`

Use this only if several items truly deserve separate future work tickets.
Do not generate a large roadmap.
Keep it to a small candidate list with one paragraph per item.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not implement POAV as a new runtime gate
- do not add a new `Risk (R)` engine
- do not modify `runtime_adapter.py`, `unified_pipeline.py`, Redis schema, or gateway behavior
- do not rewrite `AI_ONBOARDING.md`, `AI_QUICKSTART.md`, or `AI_REFERENCE.md` beyond narrow claim downgrades if absolutely necessary
- do not create a giant master roadmap
- do not use `memory/handoff/` as a public-facing output lane

If a gap deserves real code later:

- name it clearly
- bound it clearly
- leave implementation to a separate Codex-owned phase

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell which gap terms should simply be spoken about more carefully versus which deserve actual future work
- the most dangerous half-implemented or over-read concepts get a crisp next-step classification
- the result reduces confusion without promoting missing mechanisms into false truth

## Follow-Up Handoff Back To Codex

When done, report back with:

- which terms should be downgraded in prose immediately
- which terms should remain explicitly theory-only
- which terms are best handled by small future implementation tickets
- whether any one item is urgent enough to deserve the next Codex build phase

---

## Follow-Up Extension: Subject Refresh Heuristics And Promotion Boundaries

This extension exists because ToneSoul now has a live `subject_snapshot` surface,
but the next hard question is not "can we store a snapshot?"

It is:

> what kinds of evidence are strong enough to refresh durable working identity,
> and what must never be auto-promoted from hot-state coordination surfaces?

This is again a bounded synthesis-and-boundary ticket.
It is not permission to mutate the runtime or invent auto-promotion logic in code.

## Why This Follow-Up Fits Claude

This pass is strongest in a panoramic synthesis agent because it requires:

- comparing `subject_snapshot`, `checkpoint`, `compaction`, `claim`, `perspective`, and `posture` as distinct memory lanes
- deciding what kind of evidence is durable enough to shape a later agent's working identity
- separating "refreshable identity" from "temporary heat" without collapsing them together
- naming field-level promotion boundaries before Codex turns them into runtime heuristics

## Follow-Up Objective

Produce a bounded contract for **subject refresh heuristics** so later agents can answer:

- what may refresh a `subject_snapshot`
- what may only influence it indirectly
- what must stay ephemeral
- what requires deliberate operator or human confirmation

The goal is to reduce two future failure modes:

1. **over-promotion**: every hot-state signal starts rewriting identity
2. **under-promotion**: durable patterns never graduate beyond compactions and are repeatedly rediscovered

## Mandatory Focus Areas

At minimum, classify these surfaces and evidence types:

- `subject_snapshot`
- `checkpoint`
- `compaction`
- `perspective`
- `claim`
- `governance posture`
- `risk_posture`
- `router telemetry / misroute signals`
- `recent_traces`
- `delta feed`

At minimum, classify these candidate field families inside `subject_snapshot`:

- stable vows / durable boundaries
- decision preferences
- verified routines
- active threads
- carry-forward items
- anti-patterns / known failure modes

## Follow-Up Deliverables

### Deliverable F

Create:

- `docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md`

This should be a table-first contract that classifies which source surfaces may
refresh which `subject_snapshot` field families, and under what evidence level.

Each row should include at least:

- source surface
- candidate target field family
- allowed action
  - `may refresh directly`
  - `may influence but not promote directly`
  - `manual/operator-only`
  - `must not promote`
- minimum evidence shape
  - `single signal`
  - `repeat pattern`
  - `compaction-backed`
  - `subject-snapshot-only`
  - `human confirmation`
- risk if misapplied
- short rationale

### Deliverable G

Optional, only if it materially clarifies Deliverable F:

- `docs/architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md`

Use this only if the current `subject_snapshot` fields need a compact lane map
such as:

- durable identity
- refreshable working identity
- temporary carry-forward
- never-auto-promote

Do not create this file unless the boundary contract clearly benefits from it.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify `tonesoul/runtime_adapter.py`
- do not modify `tonesoul/risk_calculator.py`
- do not modify `scripts/save_subject_snapshot.py`
- do not modify `scripts/route_r_memory_signal.py`
- do not modify `spec/governance/subject_snapshot_v1.schema.json`
- do not invent auto-refresh code paths
- do not rewrite onboarding or quickstart unless a narrow wording correction is absolutely necessary

If a field or signal deserves future runtime heuristics:

- say so explicitly
- bound it explicitly
- leave implementation to Codex

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell which hot-state surfaces are allowed to shape durable working identity
- the biggest over-promotion hazards are named explicitly
- the result gives Codex a bounded map for Phase 657 heuristics without silently promoting prose into code

## Follow-Up Handoff Back To Codex

When done, report back with:

- which source surfaces are safe to use for direct subject refresh
- which field families must remain operator-only or human-confirmed
- 5-10 highest-risk over-promotion patterns you found
- which one bounded heuristic would be safest for Codex to implement first

---

## Follow-Up Extension: Control Plane Discipline Adaptation

This extension exists because ToneSoul now has a stronger shared-memory handoff surface,
but its next coordination bottleneck is no longer memory structure alone.

It is:

> how should later agents decide whether a task is ready to begin, what track it belongs to,
> and when a plan change deserves a full rewrite versus a bounded delta?

This is again a bounded synthesis-and-boundary ticket.
It is not permission to modify runtime scripts, packet shape, or session-start/session-end code.

## Why This Follow-Up Fits Claude

This pass benefits from a panoramic synthesis agent because it requires:

- comparing current ToneSoul session cadence against missing control-plane discipline
- separating operator ritual from actual readiness
- classifying tasks into bounded tracks without inventing another grand architecture
- naming where plan deltas should exist without forcing Codex to implement them prematurely

## Follow-Up Objective

Produce a bounded contract for **Readiness Gate + Task Tracks + Plan Delta** so later agents can answer:

- is this task ready to start now?
- what kind of task is this really?
- how much exploration is justified?
- when scope shifts, should we rewrite the full plan or append a delta?

The goal is to reduce three failure modes:

1. **false readiness**: the agent has context but not enough authority/evidence to start
2. **track collapse**: every task gets treated like a full-system refactor
3. **plan thrash**: every scope change rewrites the whole plan instead of leaving a bounded delta

## Mandatory Focus Areas

At minimum, classify these control-plane questions:

- `readiness gate`
- `task track`
- `exploration depth`
- `plan delta`
- `session-start bundle`
- `claim requirement`
- `review requirement`
- `human clarification requirement`

At minimum, map these three task tracks:

- `Quick Change`
- `Feature Track`
- `System Track`

At minimum, evaluate these existing ToneSoul surfaces as inputs:

- `AI_ONBOARDING.md`
- `docs/AI_QUICKSTART.md`
- `docs/AI_REFERENCE.md`
- `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
- `tonesoul/runtime_adapter.py`
- `tonesoul/diagnose.py`
- `scripts/start_agent_session.py`
- `scripts/end_agent_session.py`
- `task.md`

## Follow-Up Deliverables

### Deliverable H

Create:

- `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`

This should be a table-first contract that defines:

- readiness states
  - `pass`
  - `needs_clarification`
  - `blocked`
- task tracks
  - `quick_change`
  - `feature_track`
  - `system_track`
- minimum required surfaces before starting
- default exploration depth
  - `x0`
  - `x1`
  - `x2`
  - `x3`
- whether claim is required
- whether explicit review is required
- when a human must be asked before continuing

Each row should include at least:

- task pattern
- recommended track
- readiness state
- minimum evidence
- exploration depth
- risk if misclassified
- short rationale

### Deliverable I

Create:

- `docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md`

This should define when later agents should:

- keep the existing plan
- append a bounded delta
- fork a new phase
- stop and ask a human

At minimum, include:

- what counts as a plan delta
- what counts as a plan rewrite
- what belongs in `task.md`
- what belongs only in compaction or checkpoint
- what must not silently overwrite an existing plan

### Deliverable J

Optional, only if clearly justified by H/I:

- `docs/plans/tonesoul_control_plane_followup_candidates_2026-03-28.md`

Use this only if there are 3-5 genuinely bounded future work items.
Do not write a giant roadmap.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify `tonesoul/runtime_adapter.py`
- do not modify `tonesoul/diagnose.py`
- do not modify `scripts/start_agent_session.py`
- do not modify `scripts/end_agent_session.py`
- do not change packet schema
- do not implement a readiness gate in code
- do not implement automatic track assignment
- do not rewrite `AI_ONBOARDING.md` or `docs/AI_QUICKSTART.md` beyond narrow wording corrections if absolutely necessary

If a control-plane gap deserves future implementation:

- bound it clearly
- keep it small
- leave runtime implementation to Codex

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell whether a task is truly ready before starting
- later agents can distinguish quick changes from feature work from system work
- later agents can tell when to append a bounded plan delta instead of rewriting everything
- the result reduces coordination drift without inventing a second runtime architecture

## Follow-Up Handoff Back To Codex

When done, report back with:

- the cleanest readiness gate you would recommend for ToneSoul
- the safest default mapping for Quick Change / Feature Track / System Track
- the most dangerous current plan-thrash patterns you found
- which one bounded control-plane improvement Codex should implement first

---

## Follow-Up Extension: Council Dossier And Dissent Adaptation

This extension exists because ToneSoul already has:

- council personas,
- verdicts,
- coherence posture,
- packet/compaction handoff,
- and stronger control-plane discipline.

What it still lacks is a cleaner answer to this question:

> when multiple perspectives deliberate, what should a later agent or human inherit besides the final yes/no verdict?

This is a bounded synthesis-and-contract ticket.
It is not permission to redesign the runtime, replace the council, or rebuild the dashboard.

## Why This Follow-Up Fits Claude

This pass benefits from a long-context synthesis agent because it requires:

- comparing current council/runtime outputs against missing decision-summary structure
- separating final verdict, minority dissent, confidence posture, and change-of-mind evidence
- translating good external multi-agent review patterns into ToneSoul-native naming
- keeping the result legible for both future agents and human operators without overclaiming implementation

## Follow-Up Objective

Produce a bounded contract for **Council Dossier + Dissent Preservation + Adaptive Deliberation Modes** so later agents can answer:

- what was the final decision?
- how confident was the system?
- which perspective disagreed, and why?
- did the deliberation mode match the task risk/track?
- what should be replayable later without pretending hidden reasoning was fully captured?

The goal is to reduce four failure modes:

1. **verdict flattening**: only the final answer survives, and all useful dissent is lost
2. **false consensus**: a later agent assumes "council approved" means everyone agreed
3. **mode mismatch**: trivial tasks get heavyweight deliberation or risky tasks get shallow deliberation
4. **replay confusion**: later agents cannot tell what is genuinely recoverable versus what remained opaque

## Mandatory Focus Areas

At minimum, classify these output/deliberation questions:

- `final_verdict`
- `confidence_posture`
- `minority_report`
- `dissent_preservation`
- `change_of_position`
- `evidence_refs`
- `deliberation_mode`
- `replayable_summary`

At minimum, evaluate these existing ToneSoul surfaces as inputs:

- `docs/COUNCIL_RUNTIME.md`
- `spec/council_spec.md`
- `tonesoul/unified_pipeline.py`
- `tonesoul/council/runtime.py`
- `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`
- `docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md`
- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
- `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
- `docs/status/claim_authority_latest.json`

At minimum, propose bounded ToneSoul-native deliberation modes such as:

- `lightweight_review`
- `standard_council`
- `elevated_council`

You may rename them if a better ToneSoul-native vocabulary emerges.

## Follow-Up Deliverables

### Deliverable K

Create:

- `docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`

This should be a table-first contract that defines:

- what fields belong in a future ToneSoul decision dossier
- which dissent must be preserved
- what counts as a minority report
- what counts as confidence posture
- what later agents may safely replay from a deliberation
- what remains opaque even after a good dossier

Each field or row should include at least:

- field or concept
- purpose
- source surface
- authority posture
- whether it is required / optional / forbidden
- risk if omitted or overclaimed
- short rationale

### Deliverable L

Create:

- `docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md`

This should define when ToneSoul should conceptually prefer:

- lightweight review
- standard council
- elevated council

Map the modes against:

- task track
- readiness posture
- risk posture
- claim collision
- human clarification requirement

Do not implement mode selection.
Define only the contract and decision boundary.

### Deliverable M

Optional, only if clearly justified by K/L:

- `docs/plans/tonesoul_council_followup_candidates_2026-03-28.md`

Use this only if there are 3-5 genuinely bounded future work items.
Do not write a giant roadmap.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify `tonesoul/unified_pipeline.py`
- do not modify `tonesoul/council/runtime.py`
- do not modify packet schema
- do not redesign dashboard/frontend
- do not invent hidden-thought capture
- do not rewrite `docs/COUNCIL_RUNTIME.md` beyond narrow factual corrections if absolutely necessary
- do not convert dissent into a new constitutional authority surface

If a council-output gap deserves future implementation:

- bound it clearly
- keep it small
- leave runtime implementation to Codex

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell what a good ToneSoul decision dossier should contain
- later agents can preserve dissent without pretending disagreement disappeared
- later agents can classify when deliberation should stay light versus become elevated
- the result improves replayability and human legibility without overclaiming access to hidden reasoning

## Follow-Up Handoff Back To Codex

When done, report back with:

- the minimal safe shape of a ToneSoul council dossier
- which dissent fields must survive even when the final verdict is clear
- the safest default deliberation-mode mapping for quick/feature/system work
- which one bounded council-surface improvement Codex should implement first
