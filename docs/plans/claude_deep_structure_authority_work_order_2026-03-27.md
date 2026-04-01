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

- one bounded implementation-gap triage note for the selected high-gap terms

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

- one small follow-up candidate list if several items truly deserve separate future work tickets

Use this only if several items truly deserve separate future work tickets.
Do not generate a large roadmap.
Keep it to a small candidate list with one paragraph per item.

Historical note:

- the original raw outputs for this extension were later superseded and retired during source-material cleanup
- see `docs/plans/tonesoul_stale_source_material_supersession_review_2026-03-29.md`

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

---

## Follow-Up Extension: Prompt Surface Topology And Adoption Program

This extension exists because ToneSoul now has:

- a prompt discipline skeleton,
- prompt variants,
- prompt starter cards,
- and two live prompt surfaces already adapted by Codex.

What it still lacks is a clean answer to this question:

> across the existing repository, what is the real topology of prompt surfaces, which starter-card lane each one belongs to, which ones should stay specialized, and what adoption order is actually safe?

This is a large documentation-and-topology ticket.
It is not permission to rewrite runtime prompts, touch packet/schema surfaces, or redesign agent personalities.

## Why This Follow-Up Fits Claude

This pass benefits from a long-context synthesis agent because it requires:

- scanning many prompt-bearing files and separating high-frequency surfaces from low-value one-offs
- comparing current prompt shapes against the new prompt discipline skeleton
- deciding which surfaces match project continuity, meeting distillation, operator snapshot, council replay, or session-end resumability
- identifying which surfaces are too risky, too opaque, or too legacy-bound to touch yet
- grouping related prompt surfaces into reusable families instead of judging them one by one without system shape
- producing one adoption program that Codex can execute incrementally without redoing the mapping later

## Follow-Up Objective

Produce a bounded adoption program for **existing prompt surfaces** so later agents can answer:

- which prompts are already aligned enough and should stay as-is?
- which prompts should adopt a starter card next?
- which prompts need only wording cleanup versus structural rewrite?
- which prompts are too specialized or too risky to touch yet?
- which prompt families belong together as one adoption wave?
- where does prompt discipline stop and domain-specific voice begin?

The goal is to reduce four failure modes:

1. **prompt drift**: high-frequency prompts remain vague even after the discipline docs exist
2. **over-application**: every prompt gets forced into the same skeleton, including niche or low-value surfaces
3. **surface mismatch**: a prompt adopts the wrong card and starts carrying the wrong kind of memory or evidence burden
4. **silent priority collapse**: prompt surfaces still mix goal, evidence, confidence, and recovery in one blur

## Mandatory Focus Areas

At minimum, inspect and classify prompt-bearing surfaces across these areas:

- `tonesoul/llm/`
- `tonesoul/memory/`
- `tonesoul/tonebridge/`
- `tonesoul/market/`
- `tonesoul/scribe/`
- `scripts/` where explicit prompt strings or builder helpers exist
- selected prompt-bearing docs only when they clearly act as active operator prompts or reusable task shells

At minimum, classify surfaces against these ToneSoul prompt lanes:

- `project_continuity_transfer`
- `conversation_or_meeting_distillation`
- `operator_or_user_snapshot`
- `council_dossier_replay`
- `session_end_resumability_handoff`
- `no_adoption_yet`

At minimum, group prompt surfaces into topology families such as:

- governance / review prompts
- handoff / resumability prompts
- identity / snapshot prompts
- deliberation / replay prompts
- domain-specialized analysis prompts
- narrative / stylistic prompts that should remain specialized

At minimum, evaluate the current adapted examples as anchors:

- `tonesoul/llm/gemini_client.py`
- `tonesoul/memory/subjectivity_admissibility.py`
- `docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`
- `docs/architecture/TONESOUL_PROMPT_VARIANTS.md`
- `docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md`

## Follow-Up Deliverables

### Deliverable N

Create:

- `docs/architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md`

This should be table-first and classify at least 15-25 meaningful prompt surfaces.

Each row should include at least:

- file / function / prompt surface
- current role
- frequency / importance estimate
- recommended starter-card lane
- adoption status (`already_aligned`, `safe_next`, `defer`, `do_not_touch_yet`)
- main risk if adapted badly
- short rationale

### Deliverable O

Create:

- `docs/architecture/TONESOUL_PROMPT_SURFACE_BOUNDARY_CONTRACT.md`

This should define:

- when a prompt should receive only wording cleanup
- when it deserves full starter-card adoption
- when it must stay specialized
- when hidden/opaque/legacy surfaces should remain untouched for now

The contract should be principle-first, not a giant roadmap.

### Deliverable P

Create:

- `docs/architecture/TONESOUL_PROMPT_SURFACE_TOPOLOGY_MAP.md`

This should organize the repo's prompt surfaces into a small number of meaningful families.

At minimum include:

- topology family
- representative files/functions
- dominant risk
- recommended adoption posture
- why the family should stay unified or split

The goal is to give Codex a map of families, not just a flat spreadsheet of prompts.

### Deliverable Q

Optional, only if clearly justified:

- `docs/plans/tonesoul_prompt_adoption_followup_candidates_2026-03-29.md`

Use this only if there are 3-5 genuinely bounded next implementation candidates.
Do not write a sprawling prompt-overhaul roadmap.
If you add this file, organize candidates into 2-3 adoption waves instead of one flat list.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify runtime prompt code
- do not modify packet/schema surfaces
- do not rewrite `tonesoul/tonebridge/personas.py` wholesale
- do not redesign market personas or Scribe voice as a style exercise
- do not treat every string literal as a prompt surface worth triaging
- do not create a universal prompt replacement plan
- do not collapse specialized domain prompts into generic governance language if their domain signal would be lost

If a prompt surface deserves future implementation:

- keep it bounded
- map it to one starter-card lane
- leave runtime adoption to Codex

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell which prompt surfaces deserve adoption next
- high-frequency and low-frequency prompt surfaces are clearly separated
- starter-card lanes are used as classification aids rather than forced templates
- Codex receives one clean short-list of the next safest prompt-surface adoptions
- Codex can see prompt families and execute adoption in waves instead of one-off patches

## Follow-Up Handoff Back To Codex

When done, report back with:

- the 3 safest next prompt surfaces Codex should adapt
- the 3 prompt surfaces that should explicitly stay untouched for now
- the cleanest adoption rule for deciding `wording cleanup` vs `starter-card adoption`
- the cleanest prompt-family split you found in the repo
- which one bounded prompt-surface improvement Codex should implement first

---

## Follow-Up Extension: Continuity Import, Receiver, And Decay Program

This extension exists because ToneSoul now has several continuity-bearing surfaces:

- `r_memory_packet`
- `delta_feed`
- `claims`
- `checkpoints`
- `compactions`
- `subject_snapshot`
- `council_dossier`
- `session-start` / `session-end` bundles

Those surfaces now exist.
What is still under-specified is a harder question:

> when a later agent receives continuity material, what should it import directly, what should remain advisory, what should decay, and what must be explicitly re-confirmed?

This is a documentation-and-boundary program.
It is not permission to change runtime lifecycles, packet schema, or decay heuristics in code.

## Why This Fits Claude

This next pass again benefits from panoramic structural judgment:

- it requires reading continuity docs, packet surfaces, handoff tooling, and prompt-discipline docs together
- it requires distinguishing importable continuity from stale residue
- it requires separating receiver obligations from sender formatting
- it benefits from turning many overlapping continuity surfaces into a small number of lifecycle lanes

## Follow-Up Objective

Produce a bounded map that tells later agents:

- which continuity surfaces are `authoritative`, `advisory`, `ephemeral`, or `manual-confirmation-only`
- what a receiving agent is allowed to do after reading each surface
- which continuity surfaces should decay quickly, slowly, or only by explicit human/operator review
- where silent over-import is dangerous

The goal is to stop future agents from making two opposite mistakes:

1. treating every carried context artifact as durable truth
2. ignoring continuity surfaces so aggressively that handoff value is lost

## Mandatory Focus Surfaces

At minimum, cover these:

- `r_memory_packet.operator_guidance`
- `delta_feed`
- `claims`
- `checkpoints`
- `compactions`
- `subject_snapshot`
- `subject_refresh` recommendations
- `council_dossier` and `council_dossier_summary`
- `project_memory_summary`
- `session-start readiness`
- `session-end resumability handoff`

You may add 3-6 more only if they are structurally equivalent and materially affect continuity import behavior.

## Follow-Up Deliverables

### Deliverable R

Create:

- `docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`

This should define, per continuity surface:

- import posture
  - `directly importable`
  - `advisory only`
  - `ephemeral until acknowledged`
  - `manual confirmation required`
- receiver obligation
  - `must read`
  - `should consider`
  - `must not silently promote`
- decay posture
  - `fast`
  - `medium`
  - `slow`
  - `operator/human-only`
- main failure mode if over-imported or under-imported

### Deliverable S

Create:

- `docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`

This should focus on the receiving agent rather than the sending surface.

At minimum include:

- what it means to `ack` a packet versus `apply` a continuity artifact
- which surfaces may influence action selection directly
- which surfaces may only influence planning or review posture
- which surfaces must never be treated as durable identity without explicit confirmation
- silent-override hazards for later agents

### Deliverable T

Create:

- `docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md`

This should organize continuity surfaces into a small number of lifecycle lanes, for example:

- immediate coordination
- bounded handoff
- working identity
- replay / review memory
- historical residue

For each lane, include:

- representative surfaces
- expected lifetime
- refresh trigger
- decay trigger
- receiver behavior

### Deliverable U

Optional, only if clearly justified:

- `docs/plans/tonesoul_continuity_followup_candidates_2026-03-29.md`

Use this only if you can name 3-5 bounded follow-up candidates that stay documentation-first or helper-level.
Do not create a giant continuity-overhaul roadmap.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify `tonesoul/runtime_adapter.py`
- do not modify packet schema or example JSON
- do not change `start_agent_session.py` or `end_agent_session.py`
- do not invent hidden-memory capture or private-thought replay
- do not reclassify `subject_snapshot` into canonical identity
- do not turn advisory surfaces into hard runtime authority in prose

If you find a surface is easy to over-import:

- tighten the boundary in documentation
- do not silently promote runtime behavior to match the prose

## Follow-Up Acceptance Criteria

This extension is successful if:

- a later agent can answer "what am I allowed to import from this continuity surface?" without rereading the whole repo
- advisory, ephemeral, and durable continuity surfaces are clearly separated
- receiver behavior is documented as distinctly as sender formatting
- the most dangerous silent over-import patterns are explicitly named
- Codex receives one bounded shortlist of future continuity improvements without runtime drift

## Follow-Up Handoff Back To Codex

When done, report back with:

- the 3 continuity surfaces most safe to import directly
- the 3 continuity surfaces most dangerous to over-import
- the cleanest distinction you found between `ack`, `apply`, and `promote`
- the most useful lifecycle-lane split you found
- which one bounded continuity improvement Codex should implement first without changing packet schema

---

## Follow-Up Extension: Council Realism, Calibration, And Adversarial Deliberation Program

This extension exists because ToneSoul now has:

- council dossier extraction
- dissent preservation contracts
- adaptive deliberation mode contracts
- replayable dossier carry surfaces

What is still under-specified is a harder question:

> how close is ToneSoul's current council to a real multi-perspective deliberation system, and what should be improved first so the council does not become a polite pseudo-debate with uncalibrated confidence?

This is a large documentation-and-boundary program.
It is not permission to mutate council runtime, voting logic, evolution weights, packet schema, or frontend behavior.

## Why This Fits Claude

This next pass benefits from long-context structural synthesis because it requires:

- comparing current council code and contracts against the deeper weaknesses already surfaced
- separating "already replayable" from "actually independent"
- naming which deliberation improvements are academically or industrially grounded versus merely attractive
- turning multiple partially related ideas into a bounded adoption map instead of a giant speculative roadmap

## Follow-Up Objective

Produce a source-backed map that tells later agents:

- where the current council is genuinely strong
- where it is only simulating plurality without real independence
- which known improvement families are safe, bounded next steps
- which improvements require infrastructure that ToneSoul does not yet have

The goal is to stop future agents from making two opposite mistakes:

1. overstating the current council as already equivalent to real debate / calibrated ensemble deliberation
2. dismissing the current council as fake when it already has valuable structure worth preserving

## Mandatory Focus Problems

At minimum, analyze these:

- pseudo-debate risk: all perspectives reading the same draft/context and only differing by prompt voice
- evolution weight suppression: dissent-heavy roles being downweighted for disagreeing
- uncalibrated confidence: perspective confidence having no historical grounding
- mode mismatch: quick-change tasks and system-track tasks receiving similar deliberation depth
- verdict flattening risk: final outcome surviving while dissent detail disappears downstream

## Mandatory Improvement Families

At minimum, classify these:

- forced adversarial / devil's advocate protocols
- self-consistency / repeated independent council passes
- pre-mortem / failure-backward reasoning
- competing-hypotheses style evidence elimination
- calibrated confidence / post-hoc confidence correction
- outcome-tracking or impact-backed council learning

You may add 3-6 more only if they are comparably bounded and materially relevant.

## Follow-Up Deliverables

### Deliverable V

Create:

- `docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`

This should define:

- which parts of the current council are truly independent
- which parts are perspective-voiced but not independent
- which failure modes arise from that gap
- which claims later agents must avoid making about current council realism

### Deliverable W

Create:

- `docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`

This should define:

- the current confidence surfaces in council outputs
- where confidence is descriptive versus calibrated
- what evidence would be needed to call council confidence "calibrated"
- which calibration approaches are plausible now versus infrastructure-blocked

### Deliverable X

Create:

- `docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md`

This should organize bounded next-step improvement families into lanes such as:

- safe prompt-level additions
- safe evaluation-surface additions
- helper-level additions requiring small code changes
- infrastructure-blocked ideas
- ideas ToneSoul should explicitly defer

For each lane include:

- representative methods
- why they fit or do not fit current ToneSoul
- the smallest credible next step
- the main distortion risk if adopted badly

### Deliverable Y

Optional, only if clearly justified:

- `docs/plans/tonesoul_council_realism_followup_candidates_2026-03-29.md`

Use this only if you can produce 3-5 bounded candidates with clear safety ordering.
Do not create a sprawling "next generation council" manifesto.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify `tonesoul/council/runtime.py`, `tonesoul/unified_pipeline.py`, or evolution-weight code
- do not change council packet/schema surfaces
- do not redesign frontend deliberation views
- do not invent hidden-thought capture, secret chains-of-thought, or pseudo-private debate transcripts
- do not claim academic methods are "implemented" unless the code path actually exists

If you find a current council claim is too strong:

- downgrade the prose or boundary wording
- do not silently promote implementation status

## Follow-Up Acceptance Criteria

This extension is successful if:

- a later agent can answer "how real is ToneSoul's council right now?" without reading the whole repo
- confidence, dissent, and independence are clearly separated rather than smoothed together
- at least one safe family of bounded next improvements is named without runtime overreach
- blocked ideas are explicitly marked as blocked by missing infrastructure, not just "nice to have"
- Codex receives a high-signal shortlist of what to implement first if council quality becomes the next mainline focus

## Follow-Up Handoff Back To Codex

When done, report back with:

- the single clearest gap between current council plurality and real independent deliberation
- the 3 safest improvement families to consider next
- the 3 ideas that are most attractive but still infrastructure-blocked
- the cleanest distinction you found between descriptive confidence and calibrated confidence
- which one bounded council-quality improvement Codex should implement first without redesigning the whole council

---

## Follow-Up Extension: Evidence Topology, Test Backing, And Claim Verifiability Program

This extension exists because ToneSoul now has:

- claim-authority matrices
- law / runtime boundary contracts
- council dossier and dissent contracts
- continuity import / decay contracts
- a large live test suite and many narrative claims about what that suite proves

What is still under-specified is a harder question:

> which system claims are actually backed by tests, which are only code-backed or document-backed, and how should later agents describe ToneSoul's evidence posture without overclaiming?

This is a large documentation-and-boundary program.
It is not permission to rewrite tests, mutate runtime, inflate implementation status, or declare that every claim already has full empirical backing.

## Why This Fits Claude

This next pass benefits from long-context structural synthesis because it requires:

- reading across tests, docs, contracts, and runtime surfaces at once
- separating "there is code" from "there is evidence" from "there is repeated validation"
- classifying strong, partial, weak, and missing evidence without collapsing everything into one score
- turning many scattered assertions into a bounded evidence topology rather than another sprawling manifesto

## Follow-Up Objective

Produce a source-backed map that tells later agents:

- which ToneSoul claims are strongly test-backed
- which are runtime-backed but thinly tested
- which are document / philosophy / narrative claims with little or no direct verification
- how to speak honestly about the system's evidence posture without underselling or mythologizing it

The goal is to stop future agents from making two opposite mistakes:

1. treating every well-written claim as if it has equivalent empirical support
2. dismissing the value of existing tests because they do not cover every philosophical layer

## Mandatory Focus Areas

At minimum, analyze these evidence families:

- governance posture and runtime packet surfaces
- council / dossier / dissent surfaces
- continuity / handoff / subject snapshot surfaces
- risk / readiness / claim / checkpoint / compaction coordination surfaces
- AXIOMS / law / philosophy / manifesto style claims
- frontend / projection / dashboard style claims only if they materially affect what later agents say is "observable"

At minimum, analyze these evidence modes:

- direct automated test backing
- helper-level or schema-level validation
- runtime-path existence without strong test depth
- document-only or narrative-only support
- blocked or currently unverifiable claims

## Follow-Up Deliverables

### Deliverable Z

Create:

- `docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md`

This should cover a bounded but substantial set of high-value claims or surfaces, for example 40-80 rows.
For each row include at least:

- claim / surface name
- claim family
- current authority level
- evidence level
- strongest backing source
- weakest link or gap
- safest phrasing later agents should use

Do not turn this into a giant file inventory.
Prefer high-value system claims over exhaustive enumeration.

### Deliverable AA

Create:

- `docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md`

This should define a small number of evidence levels, for example:

- test-backed
- schema / helper backed
- runtime-present but thinly verified
- document-backed
- philosophical / narrative only
- blocked / unverifiable for now

For each level include:

- what later agents may and may not claim
- what kind of language is honest at that level
- what common overclaiming pattern to avoid
- what kind of upgrade would move a claim to the next level

### Deliverable AB

Create:

- `docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md`

This should organize the repo's validation surfaces into a small number of lanes, such as:

- critical runtime protections
- coordination and continuity
- council and deliberation
- memory / subject / handoff
- projection / surface / interface
- narrative or doctrine without direct verification

For each lane include:

- representative tests or validation tools
- what kind of confidence that lane really buys
- what it still does not prove
- the most dangerous false inference later agents might make from that lane

### Deliverable AC

Optional, only if clearly justified:

- `docs/plans/tonesoul_evidence_followup_candidates_2026-03-29.md`

Use this only if you can produce 3-5 bounded candidates with clear evidence-ordering.
Do not create a giant "prove everything" roadmap.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not modify tests, runtime code, packet schema, or frontend code
- do not inflate weak evidence into stronger categories because the prose sounds compelling
- do not restate philosophical claims as if they were empirically verified mechanisms
- do not collapse document-backed and test-backed into one generic "supported" bucket
- do not claim outcome calibration or real-world production validation unless the repo actually contains it

If you find current docs overstate evidence:

- tighten the prose or evidence classification
- do not silently promote implementation or validation status

## Follow-Up Acceptance Criteria

This extension is successful if:

- a later agent can answer "how strongly is this claim actually backed?" without reading the whole repo
- evidence strength and authority strength are clearly separated rather than blended
- at least one strong warning exists against equating narrative elegance with runtime proof
- tests, schema checks, runtime-path existence, and philosophy are all visibly distinct lanes
- Codex receives one bounded shortlist of future evidence improvements without drifting into a giant verification manifesto

## Follow-Up Handoff Back To Codex

When done, report back with:

- the single clearest difference between authority and evidence in ToneSoul
- the 3 claim families most strongly backed today
- the 3 claim families most likely to be overstated if later agents are careless
- the cleanest evidence-ladder split you found
- which one bounded evidence-surface improvement Codex should implement first without starting a full verification overhaul

---

## Follow-Up Extension: Entrypoint Simplification, Historical Surface, And Encoding Recovery Program

This extension is intentionally larger than the earlier follow-ups.
It is a documentation-architecture program, not a one-note contract ticket.

Its purpose is to answer a repo-wide usability question that still remains open:

> how should a human or later AI move through ToneSoul's public document surfaces without getting lost in legacy specs, authority collisions, mojibake-corrupted notes, or giant undifferentiated link walls?

This is the kind of work that can easily absorb 6+ focused hours if done seriously.

## Why This Fits Claude

This program requires the same strengths as the earlier deep-structure passes, but across a wider documentation hygiene surface:

- scanning many root and `docs/` surfaces without losing audience distinctions
- recognizing which files are current entrypoints versus historical lineage versus auxiliary reference
- identifying encoding / mojibake hazards that make otherwise-good docs unreadable to later agents
- writing crisp boundary artifacts that help Codex simplify entrypoints without flattening legitimate depth

This is still documentation-only.
It is not permission to rewrite runtime code, packet schema, or protected files.

## Program Objective

Produce a repo-backed simplification and hazard map for ToneSoul's public-facing documentation surfaces so that:

- human developers,
- researchers,
- later AI agents,
- and curious non-operators

can each find the right entry lane quickly without mistaking historical, corrupted, or over-deep surfaces for the first thing to read.

## Mandatory Scope

This program must examine at minimum:

- root entry surfaces
  - `README.md`
  - `README.zh-TW.md`
  - `SOUL.md`
  - `LETTER_TO_AI.md`
- AI/operator entry surfaces
  - `AI_ONBOARDING.md`
  - `docs/AI_QUICKSTART.md`
  - `docs/AI_REFERENCE.md`
  - `docs/README.md`
  - `docs/INDEX.md`
- canonical architecture and runtime companion surfaces
  - `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
  - `docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md`
- historical and legacy spec surfaces
  - `MGGI_SPEC.md`
  - `TAE-01_Architecture_Spec.md`
  - `RFC-015_Self_Dogfooding_Runtime_Adapter.md`
  - older notes that still attract search traffic or link gravity
- generated and status surfaces that affect navigation truth
  - `docs/status/doc_convergence_inventory_latest.json`
  - `docs/status/doc_authority_structure_latest.json`

You may read more, but do not turn this into a blind all-doc dump.

## Program Deliverables

### Deliverable AD

Create:

- `docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md`

This should answer:

- what a developer should open first
- what a researcher should open first
- what a later AI agent should open first
- what a curious human should open first

For each audience define:

- first document
- second document
- third document or first command
- what to avoid opening first
- the most common navigation mistake

Keep it table-first.

### Deliverable AE

Create:

- `docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md`

This should separate:

1. current canonical surfaces
2. active companion surfaces
3. historical-but-useful lineage docs
4. legacy docs that should not be read first
5. deferred or archived surfaces that still create search gravity

For each major historical surface include:

- current role
- why it still exists
- whether later agents may cite it directly
- what current canonical file supersedes or reframes it

### Deliverable AF

Create:

- `docs/architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md`

This should be a hazard register for high-traffic docs with:

- encoding corruption
- garbled headers
- broken section labels
- unreadable mixed-language spans
- likely copy/paste artifacts that would mislead later agents

For each affected file include:

- severity
  - `critical`
  - `high`
  - `medium`
  - `low`
- whether the file is a public entrypoint, an AI entrypoint, a canonical contract, a historical doc, or a low-traffic side lane
- what type of corruption is present
- whether the corruption is merely cosmetic or structurally misleading
- the safest cleanup order

### Deliverable AG

Create:

- `docs/architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md`

This should name the simplification rules Codex may safely apply when reducing entrypoint complexity.

Include rules such as:

- when a long link wall may be collapsed into categories
- when a deep lane must remain visible instead of hidden
- when evidence posture must be surfaced near a claim
- when an AI entrypoint must use operational docs instead of local collaborator notes
- when a historical doc may remain linked but must be explicitly labeled as lineage or non-first-read

This document should help Codex simplify public docs without flattening authority.

### Deliverable AH

Optional, only if clearly justified:

- `docs/plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md`

Use this only if the earlier deliverables naturally imply a bounded cleanup sequence.
If you create it, keep it to 5-8 waves max and phrase them as realistic bounded waves, not a giant perfect-doc manifesto.

## Required Method

Do this in stages.

### Stage 0: Entry surface inventory

List the top public and AI-facing entry surfaces and classify their audience and current authority role.

### Stage 1: Audience routing pass

Determine the cleanest first-hop reading path for:

- developer
- researcher
- AI agent
- curious human

Name the first-read hazards for each.

### Stage 2: Historical and legacy pass

Map the current relationship between canonical architecture, active companions, and historical specs.
Do not treat "older but meaningful" and "obsolete" as the same category.

### Stage 3: Encoding and readability pass

Audit high-traffic docs for mojibake, broken section headers, or unreadable mixed encoding.
Focus on documents that later agents are most likely to open first, not obscure side notes.

### Stage 4: Simplification boundary pass

Decide what Codex may safely compress, collapse, relabel, or move behind `<details>` without harming authority clarity.

### Stage 5: Handoff synthesis

Return one clear recommendation for:

- what should be simplified now
- what should stay visible even if it is long
- what must be repaired before any further simplification

## Program Boundaries

Do not do these things in this extension:

- do not modify `README.md`
- do not modify `docs/README.md`
- do not modify `docs/INDEX.md`
- do not modify `AI_ONBOARDING.md`
- do not modify `docs/AI_QUICKSTART.md`
- do not modify `docs/AI_REFERENCE.md`
- do not change runtime code, packet schema, or session scripts
- do not touch protected files like `AGENTS.md`
- do not silently rewrite history or rename many files

This is a map-and-boundary program.
Codex will own the actual entrypoint rewrites.

## Non-Goals

This extension is not asking for:

- a brand-new philosophy layer
- a frontend redesign
- a giant translation effort
- runtime behavior changes
- speculative cleanup of low-value obscure docs

## Acceptance Criteria

This extension is successful if:

- a later agent can tell which document should be read first for each audience
- canonical, companion, historical, and low-priority legacy surfaces are visibly separated
- mojibake and readability hazards are surfaced in a way that helps cleanup ordering
- Codex can simplify README and entry lanes later without guessing what depth is safe to hide

## Handoff Back To Codex

When done, report back with:

- the single highest-value simplification ToneSoul can safely make now
- the single most dangerous entrypoint mistake later agents currently make
- the 3 highest-severity mojibake or readability hazards
- which historical surfaces still deserve first-page visibility and which should only remain as labeled lineage references
- which one cleanup wave Codex should implement first for maximum reader relief with minimum authority damage

---

## Follow-Up Extension: Reality Alignment, Metric Baseline, And Drift Reconciliation Program

This is a correction-heavy long-context program.
It exists because the previous entrypoint / historical / encoding pass was useful, but its synthesis still had several repo-grounding gaps that later agents must not repeat.

### What Was Insufficient In The Previous Pass

Before starting, explicitly correct for these failure modes:

1. **Count inflation without runtime verification**
   - The previous pass treated `docs/architecture/TONESOUL_*_CONTRACT.md` as "46 architecture contracts".
   - Codex verified the actual current counts are different:
     - `docs/architecture/*` files: 50
     - `docs/architecture/TONESOUL_*` files: 40
     - `docs/architecture/TONESOUL_*_CONTRACT.md` files: 19
   - Do not reuse stale or inferred counts.

2. **Entrypoint drift from the actual current README**
   - The previous pass partially reasoned as if AI routing had a single first-hop document.
   - Codex has already rewritten `README.md` so the current public AI entry is a triad:
     - `AI_ONBOARDING.md`
     - `docs/AI_QUICKSTART.md`
     - `python scripts/start_agent_session.py --agent <id>`
   - Do not recommend a new entry path without first reconciling it to the live README.

3. **Display-layer ambiguity versus file-layer encoding truth**
   - Shell output may display `??` or cp950 noise even when the file content is valid UTF-8.
   - The next pass must distinguish:
     - actual file corruption
     - terminal rendering noise
     - structural readability hazards

4. **Plan-level recommendations that outran current repo reality**
   - Some cleanup recommendations assumed surfaces had not already been improved by Codex.
   - The next pass must separate:
     - already fixed
     - still true
     - partly true but drifted
     - invalid because the repo has changed

This extension is therefore not just another cleanup map.
It is a **reality-alignment and drift-reconciliation program**.

## Program Goal

Produce a repo-grounded baseline that later agents can trust when they ask:

- what the current entry surfaces actually are
- which doc counts are real versus stale prose
- which "hazards" are file-content problems versus terminal-display noise
- which cleanup recommendations still remain valid after Codex's recent rewrites

## Mandatory Scope

You must verify, not infer, at minimum:

- current public entry surfaces
  - `README.md`
  - `README.zh-TW.md`
  - `SOUL.md`
  - `LETTER_TO_AI.md`
- AI/operator entry surfaces
  - `AI_ONBOARDING.md`
  - `docs/AI_QUICKSTART.md`
  - `docs/AI_REFERENCE.md`
  - `docs/README.md`
  - `docs/INDEX.md`
- the previous five deliverables from the entrypoint program
  - `docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md`
  - `docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md`
  - `docs/architecture/TONESOUL_ENCODING_AND_MOJIBAKE_HAZARD_REGISTER.md`
  - `docs/architecture/TONESOUL_DOC_SURFACE_SIMPLIFICATION_BOUNDARY_CONTRACT.md`
  - `docs/plans/tonesoul_docs_cleanup_wave_candidates_2026-03-29.md`
- representative historical and metadata-sensitive surfaces
  - `MGGI_SPEC.md`
  - `TAE-01_Architecture_Spec.md`
  - root `TONESOUL_*.txt` founding documents
- machine-readable inventory and authority outputs
  - `docs/status/doc_convergence_inventory_latest.json`
  - `docs/status/doc_authority_structure_latest.json`

You may inspect more if needed, but do not drift into a blind all-doc dump.

## Program Deliverables

### Deliverable AI

Create:

- `docs/architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md`

This should answer:

- what the current first-hop entry really is for each audience
- which surfaces are currently live in the README path
- which surfaces are companion versus optional follow-up
- which recommendations from the prior pass conflict with the current repo state

Keep it table-first and explicitly mark:

- `current`
- `stale`
- `drifted`
- `requires human choice`

### Deliverable AJ

Create:

- `docs/architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md`

This must define a reproducible counting method for:

- root markdown entry surfaces
- docs-level files
- `docs/architecture/*`
- `docs/architecture/TONESOUL_*`
- `docs/architecture/TONESOUL_*_CONTRACT.md`

For each metric include:

- exact pattern
- what is included
- what is excluded
- why later prose should quote that metric carefully

### Deliverable AK

Create:

- `docs/architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md`

This must explicitly separate:

1. real file corruption
2. terminal rendering / locale noise
3. structural readability hazards
4. metadata drift that only looks like an encoding problem

This document should stop later agents from calling every `??` rendering artifact "mojibake".

### Deliverable AL

Create:

- `docs/architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md`

This should compare:

- current repo state
- the prior entrypoint cleanup recommendations
- Codex's already-applied README and routing changes

For each conflict include:

- what the prior pass claimed
- what the repo currently says
- whether the claim is still valid
- the safest correction

### Deliverable AM

Optional, only if clearly justified:

- `docs/plans/tonesoul_docs_reality_alignment_followup_candidates_2026-03-29.md`

Only create this if the earlier deliverables naturally imply a bounded next-wave sequence.
Do not turn it into a giant rewrite manifesto.

## Required Method

Do this in stages.

### Stage 0: Self-correction pass

Re-open the previous five deliverables and explicitly list where:

- counts were inferred instead of measured
- current README routing was not fully re-verified
- terminal-display noise may have been over-read
- cleanup advice now conflicts with Codex-owned rewrites

### Stage 1: Live entry-surface verification

Verify the actual current path for:

- developer
- researcher
- AI agent
- curious human

Do not restate an audience-routing table until it has been reconciled against the **current** `README.md`.

### Stage 2: Metric methodology pass

Measure the relevant doc families directly and define the pattern logic behind each count.
The purpose is to stop prose from casually saying "46 contracts" when the directory shape means something else.

### Stage 3: Render-layer versus file-layer pass

Where shell output or terminal display shows `??`, verify whether:

- the underlying file is fine
- the file actually contains broken characters
- the problem is structural, not encoding-based

Use this to build the encoding/render boundary contract.

### Stage 4: Drift reconciliation pass

Compare the previous cleanup recommendations against the current repo state and classify each recommendation as:

- still valid
- partially valid
- already fixed
- invalidated by later changes

### Stage 5: Handoff synthesis

Return one clear answer for:

- the single biggest reality-gap later agents still have about the current doc entry stack
- the single most misleading stale metric in the docs
- the single most overused false-positive "mojibake" diagnosis
- which earlier cleanup recommendation Codex should keep
- which earlier cleanup recommendation Codex should discard

## Program Boundaries

Do not do these things in this extension:

- do not modify `README.md`
- do not modify `AI_ONBOARDING.md`
- do not modify `docs/README.md`
- do not modify `docs/INDEX.md`
- do not modify the five previous deliverables
- do not modify runtime code, packet schema, or session scripts
- do not touch protected files
- do not silently "fix" counts by editing inventories yourself

This is a reality-check and correction program.
Codex will own the actual follow-up edits.

## Non-Goals

This extension is not asking for:

- a new README rewrite
- a translation pass
- a runtime behavior change
- a new philosophy layer
- a one-shot cleanup of every stale document

## Acceptance Criteria

This extension is successful if:

- a later agent can tell the difference between measured counts and loose prose
- audience routing reflects the current live README rather than an outdated mental model
- rendering noise and actual encoding corruption are no longer conflated
- Codex can decide which cleanup advice to keep or discard without rereading every prior deliverable

## Handoff Back To Codex

When done, report back with:

- the 3 clearest places where your previous entrypoint pass under-verified the repo
- the corrected current AI entry route in one line
- the corrected count triplet for `docs/architecture/*`, `TONESOUL_*`, and `TONESOUL_*_CONTRACT.md`
- the single highest-value cleanup recommendation that still survives this reality pass
- the single previous recommendation that should now be retired

---

## Follow-Up Extension: Low-Drift Anchor, Observer Window, And Successor Coherence Program

This is a large, multi-stage, documentation-only program intended to absorb at least 6 focused hours.

It exists because ToneSoul now has:

- session-start bundle
- packet / import posture / receiver parity
- observer window
- closeout grammar
- successor/hot-memory program docs

But a deeper question remains open:

> how should a later AI reconstruct the current center of gravity, distinguish stable from merely smooth handoff, and know what is safe to continue without silently mutating the wrong layer?

This extension should not implement runtime behavior.
It should give Codex a repo-grounded, high-resolution map for the next runtime waves.

## Why This Fits Claude

This program benefits from a long-context synthesis agent because it requires:

- comparing many adjacent continuity surfaces without collapsing them together
- tracing parent-child authority between packet, import posture, observer window, compaction, subject snapshot, and docs
- naming recurrent successor misreads before Codex turns them into tighter runtime guards
- writing dense but bounded contracts and scenario maps instead of another philosophy lane

## Program Goal

Produce a successor-coherence map that lets a later AI answer all of these quickly:

1. what is truly low-drift right now
2. what is only advisory or resumability memory
3. what kind of closeout is visible
4. when a smooth handoff is actually incomplete
5. which surfaces may influence continuation
6. which surfaces must never be silently promoted

## Mandatory Scope

You must inspect at minimum:

- `DESIGN.md`
- `AI_ONBOARDING.md`
- `docs/AI_QUICKSTART.md`
- `task.md`
- `docs/architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md`
- `docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md`
- `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
- `docs/architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md`
- `tonesoul/runtime_adapter.py`
- `tonesoul/observer_window.py`
- `scripts/start_agent_session.py`
- `scripts/end_agent_session.py`
- `scripts/save_compaction.py`
- `tests/test_observer_window.py`
- `tests/test_start_agent_session.py`
- `tests/test_end_agent_session.py`
- `docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md`
- `docs/plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md`
- `docs/plans/wfgy_avatar_deep_analysis_2026-04-02.md`

You may inspect more, but do not turn this into a blind full-repo survey.

## Program Deliverables

### Deliverable AN

Create:

- `docs/architecture/TONESOUL_LOW_DRIFT_ANCHOR_SOURCE_PRECEDENCE_CONTRACT.md`

This should define:

- which surfaces are allowed to contribute to a low-drift anchor
- what precedence order they should have
- what disqualifies a surface from anchor use
- what states a candidate anchor item may take
  - `stable`
  - `contested`
  - `stale`
  - `retired`

For each source family include:

- source surface
- authority role
- freshness expectations
- anchor eligibility
- disqualifiers
- promotion risk
- one-line rationale

### Deliverable AO

Create:

- `docs/architecture/TONESOUL_OBSERVER_WINDOW_MISREAD_AND_CORRECTION_MAP.md`

This should be scenario-first.
It must catalog the most likely ways a later AI will misread observer-window and session-start surfaces.

Each row should include:

- misread pattern
- what the agent sees
- what it is likely to incorrectly conclude
- the correct reading
- which parent surface should be checked
- whether Codex should fix this with wording, readout shape, or runtime guard

At minimum include scenarios for:

- descriptive council data read as calibrated truth
- advisory compaction read as completed work
- working-style continuity read as shared identity
- subject snapshot read as canonical selfhood
- observer-window stable bucket read as sovereign truth
- launch tier read as runtime permission

### Deliverable AP

Create:

- `docs/architecture/TONESOUL_SUCCESSOR_MUTATION_BOUNDARY_AND_CLOSEOUT_CONTRACT.md`

This should define the successor-side mutation boundary using current ToneSoul-native terms.

At minimum classify:

- when a successor may continue work directly
- when it must pause and review
- when it must fail-stop
- when human choice is required
- when closeout status should block further mutation

This contract must explicitly align:

- `ack / apply / promote`
- `complete / partial / blocked / underdetermined`
- parent/child non-equivalence
- shell / resolver / execution separation

### Deliverable AQ

Create:

- `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md`

This should map:

- which hot-memory surfaces should decay quickly
- which should remain medium-lived
- which should be treated as long-lived but non-canonical
- which should never be used as compression targets

For each surface include:

- default lifespan expectation
- compression safety
- what can be summarized away
- what must remain explicit
- what should move into local residue instead of shared continuity

### Deliverable AR

Optional, only if clearly justified:

- `docs/plans/tonesoul_successor_hot_memory_followup_candidates_2026-04-02.md`

Only create this if the four mandatory deliverables naturally imply 3-6 bounded future waves.
Do not create a giant perfect-system roadmap.

## Required Method

Do this in stages.

### Stage 0: Current-center reconstruction

Reconstruct the current successor path from the live repo, not from prior memory:

- onboarding
- quickstart
- design center
- session-start
- observer window
- deeper packet / diagnose

Explicitly mark where a successor currently still has to infer too much.

### Stage 1: Source precedence pass

Measure which surfaces are actually carrying low-drift information today, and which only look important because they are smooth summaries.

Do not assume that because a surface is recent, it is anchor-worthy.

### Stage 2: Misread-pattern pass

List the most dangerous successor misreads in current ToneSoul.
Prioritize misreads that would cause:

- false completion
- false authority
- false identity continuity
- false launch maturity

### Stage 3: Mutation-boundary pass

Write the successor mutation boundary using current control-plane language, not foreign names.
Make it explicit where continuation is safe, where it is conditional, and where it is prohibited.

### Stage 4: Decay/compression pass

Map which hot-memory surfaces should decay, which should persist, and which should never be collapsed behind a smooth summary.

### Stage 5: Handoff synthesis

Return one concise high-signal handoff that tells Codex:

- the single most dangerous successor confusion still present
- the single cleanest low-drift anchor rule to implement next
- the single continuity surface most likely to be over-promoted
- the single closeout/mutation boundary that should be made more explicit in runtime next

## Program Boundaries

Do not do these things in this extension:

- do not modify runtime code
- do not modify packet schema
- do not modify `task.md`
- do not modify `README.md`, `AI_ONBOARDING.md`, or `docs/AI_QUICKSTART.md`
- do not modify `DESIGN.md`
- do not rewrite current contracts unless a narrow factual correction is absolutely necessary
- do not invent new foreign naming systems
- do not turn this into a full launch-roadmap rewrite

This is a mapping and boundary program.
Codex owns runtime implementation.

## Non-Goals

This extension is not asking for:

- another philosophy treatise
- another personality ontology
- a hidden-thought transfer design
- a total observer-window redesign
- a new shared-self theory

## Acceptance Criteria

This extension is successful if:

- a later agent can tell which current surfaces truly deserve low-drift treatment
- successor misreads are named in a way Codex can directly act on
- closeout and mutation boundaries are mapped without touching runtime
- hot-memory decay/compression is made explicit enough that future cleanup or compaction does not become accidental amnesia

## Handoff Back To Codex

When done, report back with:

- the single most dangerous successor confusion still present in ToneSoul
- the 3 strongest low-drift anchor candidates today
- the 3 surfaces most likely to be over-promoted by a careless later agent
- the cleanest closeout-status rule Codex should tighten next
- the single bounded runtime follow-up you recommend first
