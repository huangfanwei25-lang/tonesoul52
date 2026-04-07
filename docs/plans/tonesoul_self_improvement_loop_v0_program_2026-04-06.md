# ToneSoul Self-Improvement Loop v0 Program (2026-04-06)

> Purpose: turn the new self-improvement-loop line into a bounded follow-through program that opens only after the current operator-retrieval short board is landed.
> Status: accepted follow-through program, queued behind `Phase 789`
> Authority: planning aid. Runtime truth remains in code, tests, and accepted architecture contracts.

---

## Why This Program Exists

ToneSoul has crossed a threshold:

- the workspace tier model is now stable enough to improve intentionally
- consumer contracts now exist across Codex-style, Claude-style, dashboard, and observer consumers
- knowledge-layer boundaries now exist, so future lessons have somewhere cleaner to land
- closeout grammar now makes partial/blocked work visible enough that "improvement" can be judged more honestly

That creates a new possibility:

`ToneSoul can now attempt bounded self-improvement without immediately collapsing into magical self-rewrite stories.`

This program exists to keep that possibility disciplined.

---

## Why This Is A New Line, Not Just More Of The Old One

This line is new because it asks a different question.

Previous lines mostly asked:

- how should state be shared?
- how should consumers interpret shared state?
- where should retrieval live?
- how should launch and internal-state claims stay honest?

This line asks:

`once those boundaries exist, how may ToneSoul intentionally improve itself without breaking them?`

So the new line is not "more memory."
It is:

- evaluator discipline
- experiment lineage
- bounded mutation space
- promotion honesty

---

## Why The Program Opens Only After Phase 789

The current short board is still:

`Phase 789: Bounded Operator-Retrieval Query Contract`

That matters because a self-improvement loop without a clean retrieval contract would immediately blur:

- hot coordination
- compiled knowledge
- experimental lessons
- operator-facing retrieval

So this program is intentionally queued **after** Phase 789.

---

## Program Thesis

ToneSoul does not need a giant auto-evolution engine first.

It needs:

1. one bounded evaluator harness
2. one bounded experiment registry story
3. one bounded mutation space
4. one bounded analyzer/distiller flow
5. one or two safe trial families

That is enough for v0.

---

## Workstreams

## Workstream A: Evaluator Harness

Goal:

- define how a candidate is judged before it can be promoted

Why it exists:

- current validation is strong, but not yet organized as an explicit improvement harness

Deliverables:

- evaluator contract
- baseline/candidate result shape
- success/failure/rollback grammar

## Workstream B: Experiment Registry Boundary

Goal:

- define where experiment lineage belongs without reusing hot coordination surfaces

Why it exists:

- R-memory is still hot coordination, not experiment memory

Deliverables:

- experiment-registry boundary
- storage posture
- lineage and retention rule

## Workstream C: Bounded Mutation Space

Goal:

- say clearly what v0 may improve and what remains forbidden or human-gated

Why it exists:

- without a mutation boundary, "self-improvement" turns into authority drift

Deliverables:

- allowed mutation classes
- forbidden mutation classes
- human-gated classes

## Workstream D: Analyzer And Distillation

Goal:

- turn experiment outcomes into reusable lessons instead of one-off patches

Why it exists:

- without analyzer/distillation, the loop can only patch, not learn

Deliverables:

- analyzer closeout shape
- distillation and parking rules
- promotion thresholds

## Workstream E: First Bounded Trials

Goal:

- prove the loop on safe, high-leverage surfaces before touching deeper architecture

Why it exists:

- ToneSoul needs one real bounded win before any broader self-improvement claim is honest

Deliverables:

- one or two trial families
- validation wave
- explicit no-go cases

---

## Proposed Phase Ladder

### Phase 790: Self-Improvement Evaluator Harness Contract

Bounded scope:

- define the minimum evaluator shape for self-improvement candidates
- make baseline, candidate, success metric, failure watch, and rollback path explicit
- keep this bounded to improvement candidates, not general runtime evaluation

Success criteria:

- ToneSoul can judge a candidate improvement without relying on narrative quality or selective memory

Current implementation target:

- one evaluator harness contract
- explicit candidate record
- explicit outcome classes
- no experiment runner yet

### Phase 791: Experiment Registry And Lineage Boundary

Bounded scope:

- define where experiment outputs belong
- keep the registry separate from R-memory and canonical identity
- define what may be stored as raw run, distilled lesson, or promotion-ready result

Success criteria:

- later agents can tell experimental lineage from hot coordination and from compiled knowledge

Current implementation target:

- one experiment-registry boundary contract
- three-way split:
  - raw run
  - distilled lesson
  - promotion-ready result
- no runtime registry backend yet

### Phase 792: Bounded Mutation Space Contract

Bounded scope:

- define exactly which surfaces v0 may mutate
- define forbidden and human-gated mutation classes
- tie the mutation map back to existing governance and identity boundaries

Success criteria:

- a later agent cannot honestly claim "self-improvement" while still mutating vows, identity, or canonical truth

Current implementation target:

- one mutation-space contract
- explicit split:
  - allowed now
  - human-gated
  - forbidden in v0
- no automatic mutator yet

### Phase 793: Analyzer And Promotion Gate

Bounded scope:

- define how experiment closeout becomes analyzer output
- make park/retire/promote decisions explicit
- keep anti-fake-completion and unresolved-item discipline intact

Success criteria:

- ToneSoul can end an improvement trial honestly even when the result is only partial or blocked

Current implementation target:

- one analyzer/promotion-gate contract
- explicit closeout shape
- explicit promote / park / retire / blocked carry-forward rules
- no experiment runner yet

### Phase 794: First Bounded Self-Improvement Trial Wave

Bounded scope:

- run one or two safe trials only
- prefer:
  - operator workspace tier alignment
  - deliberation escalation hint quality
  - cross-consumer parity packaging
  - bounded operator-retrieval cueing
- do not open deeper architecture or identity-facing surfaces

Success criteria:

- ToneSoul produces one explicit promoted lesson or one explicit retired lesson without crossing governance or identity boundaries

Current implementation target:

- `scripts/run_self_improvement_trial_wave.py`
- `tonesoul/self_improvement_trial_wave.py`
- `docs/status/self_improvement_trial_wave_latest.{json,md}`
- one promoted result and one parked result, both with explicit promotion limits and replay rules

### Phase 795: Promotion-Ready Result Surface Contract

Bounded scope:

- define how promoted, parked, retired, and blocked trial outcomes may surface to later agents
- keep the first surfaced result layer in dedicated status artifacts instead of bloating `session-start`, `observer-window`, or packet defaults
- make replay, supersession, and residue posture explicit so trial results do not become a hidden status swamp

Success criteria:

- later agents can read bounded trial outcomes from a dedicated result surface without confusing them with runtime truth or reopening raw trial artifacts first

Current implementation target:

- one promotion-ready result-surface contract
- enriched self-improvement trial-wave status output
- explicit result-surface fields:
  - `surface_status`
  - `replay_rule`
  - `supersession_posture`
  - `residue_posture`
  - `carry_forward_rule`

### Phase 796: Compact Self-Improvement Result Cue Design

Bounded scope:

- decide whether any compact self-improvement result cue belongs in later shells
- keep the status surface primary while designing the smallest possible secondary cue
- avoid bloating `session-start`, `observer-window`, packet, or dashboard Tier 0 / Tier 1 with trial-history storytelling

Success criteria:

- ToneSoul has one explicit compact-cue design that preserves dedicated result surfaces as the parent lane and keeps any later shell cue opt-in and secondary

Current implementation target:

- one compact-cue design note or contract
- no new first-hop payloads yet
- explicit `do_not_default_load` rule for trial-history surfaces

### Phase 797: Dashboard-Only Self-Improvement Cue Pilot

Bounded scope:

- if a cue is implemented, keep it dashboard-only and secondary to Tier 0 / Tier 1 runtime truth
- point the cue back to the dedicated status artifact instead of inlining raw trial history
- avoid touching packet, observer buckets, or default `session-start` payloads

Success criteria:

- ToneSoul can test whether a compact cue is useful for operators without flattening trial posture into first-hop runtime truth

Current implementation target:

- one small dashboard-only cue
- collapsed or visually secondary by default
- clear source-path and receiver rule

### Phase 798: Self-Improvement Cue Shell-Exclusion Guard

Bounded scope:

- verify the new cue stays dashboard-only and does not appear in packet, observer-window, or default `session-start` payloads
- add one regression guard so future shells cannot quietly import trial posture into first-hop runtime truth
- keep the wave validation-focused instead of expanding the cue into more surfaces

Success criteria:

- ToneSoul can prove the cue remains secondary and dashboard-local rather than relying on memory or convention

Current implementation target:

- one shell-exclusion validation pass
- one regression check for no first-hop cue creep
- no new user-facing surfaces

### Phase 799: Second Trial Candidate Admission

Bounded scope:

- choose the next safe self-improvement candidate after the first trial wave and cue-visibility hardening
- keep admission inside already-allowed mutation classes
- require explicit baseline, rollback posture, and overclaim warning before any second trial opens

Success criteria:

- ToneSoul has one admitted next candidate that is specific enough to trial and narrow enough not to reopen governance, identity, or transport mythology

Current implementation target:

- one candidate-admission note
- one recommended next trial family
- one explicit no-go list for what should not enter the second wave

### Phase 800: Second Bounded Trial Wave - Deliberation Hint Packaging

Bounded scope:

- refine `session_start.deliberation_mode_hint` so shells can distinguish active escalation pressure from conditional escalation ladders
- keep the change inside packaging/readout space only
- preserve the current suggested-mode semantics while making lightweight paths easier to trust

Success criteria:

- ToneSoul lands one bounded second-trial implementation for `deliberation_mode_hint_latency_v2`
- blocked, collided, and elevated-risk cases still surface honest escalation pressure
- lightweight paths stop looking artificially heavier than they are

Current implementation target:

- one runtime packaging refinement in `scripts/start_agent_session.py`
- one targeted regression wave in `tests/test_start_agent_session.py`
- one contract refresh for the deliberation-mode hint surface

### Phase 801: Second Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the `deliberation_mode_hint_latency_v2` implementation against the existing evaluator harness
- classify the trial honestly through the analyzer/promotion gate
- register the result without pushing self-improvement history into first-hop shells

Success criteria:

- ToneSoul has one honest second-trial classification for `deliberation_mode_hint_latency_v2`
- the result remains secondary to runtime truth and does not overclaim better reasoning quality
- the registry/result surface remains bounded and supersedable

Current implementation target:

- one evaluator-ready record for the second trial
- one analyzer conclusion (`promote / park / retire / blocked / not_ready_for_trial`)
- one registry/status update without shell creep

### Phase 802: Third Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate after the second trial result is visible in the status surface
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a third trial wave opens

Success criteria:

- ToneSoul has one admitted third candidate with real operator leverage
- the candidate stays narrower than shell redesign, retrieval mythology, or governance semantics
- the admission note is explicit enough that a later agent can run the third trial without improvising scope

Current implementation target:

- one candidate-admission note
- one recommended third-trial family
- one explicit no-go list for what must stay parked

### Phase 803: Third Bounded Trial Wave - Task-Board Parking Clarity

Bounded scope:

- refine `task_board_preflight` and adjacent packaging so shells read `docs_plans_first` as a routing outcome, not a soft suggestion
- preserve already-ratified follow-through into `task.md`
- avoid turning parking helpers into a new permission or promotion system

Success criteria:

- ToneSoul lands one bounded third-trial implementation for `task_board_parking_clarity_v1`
- new idea flows read more clearly as `docs_plans_first`
- ratified follow-through remains narrow and boring

Current implementation target:

- one packaging refinement in `tonesoul/task_board_preflight.py`
- one follow-through alignment pass in adjacent shell-facing readouts
- one targeted regression wave for parking clarity without shell sprawl

### Phase 804: Third Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the `task_board_parking_clarity_v1` implementation against the existing evaluator harness
- classify the trial honestly through the analyzer/promotion gate
- register the result without pushing task-board improvement history into first-hop shells

Success criteria:

- ToneSoul has one honest third-trial classification for `task_board_parking_clarity_v1`
- the result remains secondary to runtime truth and does not overclaim better planning quality
- the registry/result surface remains bounded and supersedable

Current implementation target:

- one evaluator-ready record for the third trial
- one analyzer conclusion (`promote / park / retire / blocked / not_ready_for_trial`)
- one registry/status update without shell creep

### Phase 805: Fourth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate after the third trial result is visible in the status surface
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a fourth trial wave opens

Success criteria:

- ToneSoul has one admitted fourth candidate with real operator leverage
- the candidate stays narrower than shell redesign, retrieval mythology, or governance semantics
- the admission note is explicit enough that a later agent can run the fourth trial without improvising scope

Current implementation target:

- one candidate-admission note
- one recommended fourth-trial family
- one explicit no-go list for what must stay parked

### Phase 806: Fourth Bounded Trial Wave - Shared-Edit Overlap Clarity

Bounded scope:

- refine `shared_edit_preflight` packaging so later agents can distinguish other-agent overlap pressure from self-claim-gap pressure
- preserve the current bounded decision set and recommended-command posture
- keep the change inside packaging/readout space only: no new permission layer, no auto-claiming, no path-lock story

Success criteria:

- ToneSoul lands one bounded fourth-trial implementation that lowers shared-edit ambiguity without widening mutation authority

Current implementation target:

- one shared-edit packaging refinement
- one new probe or regression proving overlap-versus-gap separation stays visible
- no shell redesign and no change to readiness or claim truth

### Phase 807: Fourth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the shared-edit overlap clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready fourth-trial result and clear promotion limit for shared-edit packaging

Current implementation target:

- one evaluator-ready record for the fourth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 808: Fifth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the fourth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a fifth trial wave opens

Success criteria:

- ToneSoul has one admitted fifth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended fifth-trial family
- one explicit no-go list for what must stay parked

### Phase 809: Fifth Bounded Trial Wave - Publish/Push Posture Clarity

Bounded scope:

- refine `publish_push_preflight` packaging so later agents can distinguish hard block reasons, review cues, and launch-honesty cues
- preserve the current bounded decision set and recommended-command posture
- keep the change inside packaging/readout space only: no deployment automation, no release authority expansion, no launch-tier rewrite

Success criteria:

- ToneSoul lands one bounded fifth-trial implementation that lowers publish/push ambiguity without widening outward-facing authority

Current implementation target:

- one publish/push packaging refinement
- one new probe or regression proving review-versus-honesty separation stays visible
- no shell redesign and no change to launch truth

### Phase 810: Fifth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the publish/push posture clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready fifth-trial result and clear promotion limit for publish/push packaging

Current implementation target:

- one evaluator-ready record for the fifth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 811: Sixth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the fifth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a sixth trial wave opens

Success criteria:

- ToneSoul has one admitted sixth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended sixth-trial family
- one explicit no-go list for what must stay parked

### Phase 812: Sixth Bounded Trial Wave - Mutation Follow-Up Routing

Bounded scope:

- refine `mutation_preflight.next_followup` so it routes to the current narrowest bounded hook instead of always pointing at one static target
- preserve the existing hook set and recommended-command posture
- keep the change inside packaging/readout space only: no new hook family, no planner, no permission-system story

Success criteria:

- ToneSoul lands one bounded sixth-trial implementation that lowers successor-routing ambiguity without widening mutation authority

Current implementation target:

- one mutation-followup routing refinement
- one new probe or regression proving dynamic hook selection stays visible
- no shell redesign and no change to governance truth

### Phase 813: Sixth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the mutation-followup routing trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready sixth-trial result and clear promotion limit for mutation-followup routing

Current implementation target:

- one evaluator-ready record for the sixth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 814: Seventh Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the sixth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a seventh trial wave opens

Success criteria:

- ToneSoul has one admitted seventh candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended seventh-trial family
- one explicit no-go list for what must stay parked

### Phase 815: Seventh Bounded Trial Wave - Surface Versioning Lineage Clarity

Bounded scope:

- refine `surface_versioning` with one clearer compatibility-posture layer so later agents can see repo-native entry vs bounded-adapter roles without inferring them from multiple fields
- preserve the existing runtime surface list, consumer-shell list, and fallback rule
- keep the change in packaging/readout space only: no new transport layer, no vendor-native interop story, and no authority promotion

Success criteria:

- ToneSoul lands one bounded seventh-trial implementation that improves consumer-lineage readability without reopening transport mythology

Current implementation target:

- one `surface_versioning.compatibility_posture` refinement
- one new probe or regression proving fallback lineage stays shared across consumers
- no packet/schema redesign and no governance-story changes

### Phase 816: Seventh Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the surface-versioning lineage trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready seventh-trial result and clear promotion limit for surface-versioning lineage clarity

Current implementation target:

- one evaluator-ready record for the seventh trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 817: Eighth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the seventh trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before an eighth trial wave opens

Success criteria:

- ToneSoul has one admitted eighth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended eighth-trial family
- one explicit no-go list for what must stay parked

### Phase 818: Eighth Bounded Trial Wave - Launch Health Trend Clarity

Bounded scope:

- refine `launch_health_trend_posture` so it shows what operators may do now, what trend lanes to watch, and why forecast language remains blocked
- preserve the descriptive-vs-trendable-vs-forecast_later split
- keep the change in readout packaging only: no predictive math, no launch-tier rewrite, no stronger deployment authority

Success criteria:

- ToneSoul lands one bounded eighth-trial implementation that improves launch-health honesty and operator clarity without turning posture into fake prediction

Current implementation target:

- one launch-health packaging refinement
- one new probe or regression proving trend-watch cues and forecast blockers stay explicit
- no forecast numbers and no maturity-story inflation

### Phase 819: Eighth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the launch-health clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready eighth-trial result and clear promotion limit for launch-health trend clarity

Current implementation target:

- one evaluator-ready record for the eighth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 820: Ninth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the eighth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a ninth trial wave opens

Success criteria:

- ToneSoul has one admitted ninth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended ninth-trial family
- one explicit no-go list for what must stay parked

### Phase 821: Ninth Bounded Trial Wave - Internal-State Action Clarity

Bounded scope:

- refine `internal_state_observability` so it exposes pressure-watch cues and bounded operator actions without changing the selfhood boundary
- preserve the current pressure taxonomy (`coordination_strain / continuity_drift / stop_reason_pressure / deliberation_conflict`)
- keep the change in readout packaging only: no emotion claims, no selfhood inflation, no hidden-thought story

Success criteria:

- ToneSoul lands one bounded ninth-trial implementation that improves practical handling of visible pressures without turning functional observability into mythology

Current implementation target:

- one internal-state packaging refinement
- one new probe or regression proving pressure-watch cues stay explicit and anti-mythological
- no change to transport semantics or agency claims

### Phase 822: Ninth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the internal-state clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready ninth-trial result and clear promotion limit for internal-state action clarity

Current implementation target:

- one evaluator-ready record for the ninth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 823: Tenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the ninth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a tenth trial wave opens

Success criteria:

- ToneSoul has one admitted tenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended tenth-trial family
- one explicit no-go list for what must stay parked

### Phase 824: Tenth Bounded Trial Wave - Hook-Chain Trigger Clarity

Bounded scope:

- refine `hook_chain` so it exposes `hooks`, `selection_rule`, and one bounded `current_recommendation`
- preserve the current hook family (`shared_edit_path_overlap / publish_push_posture / task_board_parking`)
- keep the change inside packaging/readout space only: no new hooks, no planner, no stronger permission story

Success criteria:

- ToneSoul lands one bounded tenth-trial implementation that makes the current hook choice visible without widening mutation authority

Current implementation target:

- one hook-chain packaging refinement
- one live probe proving the recommendation aligns with `mutation_preflight.next_followup`
- no readiness/claim/governance truth rewrite

### Phase 825: Tenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the hook-chain trigger clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready tenth-trial result and clear promotion limit for hook-chain packaging

Current implementation target:

- one evaluator-ready record for the tenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 826: Eleventh Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the tenth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before an eleventh trial wave opens

Success criteria:

- ToneSoul has one admitted eleventh candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended eleventh-trial family
- one explicit no-go list for what must stay parked

---

## Safe First Trial Families

The best v0 candidates are:

1. `workspace/operator shell`
2. `deliberation escalation readouts`
3. `cross-consumer parity packaging`
4. `bounded retrieval/operator cueing`

The wrong first candidates are:

1. `subject identity`
2. `AXIOMS`
3. `vows or permissions`
4. `vendor-native interop claims`
5. `descriptive-to-predictive number inflation`

---

## Relationship To Claude/Codex Interop

The recent interoperability work matters here.

This program assumes:

- Codex and Claude-style shells can share transport
- but they still need consumer parity and explicit adapters

So self-improvement candidates must not be judged inside a single shell story only.

At least some candidates should be validated against:

- repo-native Codex entry
- Claude-compatible adapter
- dashboard/operator shell

If a candidate improves one shell while quietly degrading shared interpretation, it should not be promoted.

---

## Relationship To R-Memory

This program does **not** replace or rewrite R-memory.

Instead:

- R-memory continues to provide hot coordination and current-state orientation
- self-improvement uses R-memory as one input surface
- experiment lineage belongs in a separate, compiled/registry-like lane

This is the key improvement over the current gap:

`shared transport alone does not create shared learning.`

---

## Current Recommendation

The program is now active through `Phase 846`.

Current short board:

- `Phase 847: Eighteenth Trial Candidate Admission`

Recommended discipline:

- keep trial outcomes visible through dedicated status artifacts first
- do not push self-improvement history into `session-start`, `observer-window`, or packet defaults yet
- keep new trials inside already-allowed mutation classes until a compact result-surface design proves stable
- prefer packaging refinements that reduce operator latency, shared-edit ambiguity, outward-action ambiguity, stale follow-up routing, consumer-lineage ambiguity, launch-health honesty, internal-state handling clarity, hook-selection ambiguity, cross-shell misread-correction ambiguity, successor focus ambiguity, anti-fake-completion handling ambiguity, Claude-style correction ambiguity, hot-memory pull-boundary ambiguity, dashboard reference-authority ambiguity, and operator-status readability ambiguity before opening broader retrieval or governance experiments

### Phase 827: Eleventh Bounded Trial Wave - Consumer Misread-Guard Clarity

Bounded scope:

- refine `consumer_contract` so misread guards expose `trigger_surface` and `operator_action`
- add one bounded `priority_misread_guard` that foregrounds the highest-risk correction without inventing a planner
- preserve the current guard set and keep the change inside packaging/readout space only

Success criteria:

- ToneSoul lands one bounded eleventh-trial implementation that reduces cross-shell correction ambiguity without widening permissions, transport claims, or governance semantics

Current implementation target:

- one consumer-contract packaging refinement
- one live probe proving Claude-style and repo-native shells preserve the same first correction
- no new shell family, no new mutation authority, no transport-story widening

### Phase 828: Eleventh Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the consumer misread-guard clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready eleventh-trial result and clear promotion limit for consumer misread correction packaging

Current implementation target:

- one evaluator-ready record for the eleventh trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 829: Twelfth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the eleventh trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a twelfth trial wave opens

Success criteria:

- ToneSoul has one admitted twelfth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended twelfth-trial family
- one explicit no-go list for what must stay parked

### Phase 830: Twelfth Bounded Trial Wave - Subsystem-Parity Focus Clarity

Bounded scope:

- refine `subsystem_parity.next_focus` so it exposes `source_family`, `focus_pressures`, and `operator_action`
- preserve the current family list, count structure, and bounded target resolution
- keep the change inside successor-facing packaging only: no planner story, no governance widening, no stronger permissions

Success criteria:

- ToneSoul lands one bounded twelfth-trial implementation that improves successor orientation without turning subsystem parity into a planner or authority lane

Current implementation target:

- one subsystem-parity packaging refinement
- one cross-shell probe proving Codex-style, Claude-style, and dashboard shells preserve the same next-focus family
- no shell redesign and no change to mutation/governance truth

### Phase 831: Twelfth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the subsystem-parity focus clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready twelfth-trial result and clear promotion limit for subsystem-parity focus packaging

Current implementation target:

- one evaluator-ready record for the twelfth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 832: Thirteenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the twelfth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a thirteenth trial wave opens

Success criteria:

- ToneSoul has one admitted thirteenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended thirteenth-trial family
- one explicit no-go list for what must stay parked

### Phase 833: Thirteenth Bounded Trial Wave - Closeout-Attention Action Clarity

Bounded scope:

- refine `closeout_attention` so it exposes `source_family`, `attention_pressures`, and `operator_action`
- preserve the current closeout lift, anti-fake-completion meaning, and bounded handoff status semantics
- keep the change inside successor-facing packaging only: no planner story, no governance widening, no stronger permissions

Success criteria:

- ToneSoul lands one bounded thirteenth-trial implementation that improves closeout handling across observer, Claude-style, and dashboard shells without turning closeout attention into a planner or authority lane

Current implementation target:

- one closeout-attention packaging refinement
- one cross-shell probe proving observer, Claude-style, and dashboard shells preserve the same closeout handling story
- no shell redesign and no change to closeout truth or mutation authority

### Phase 834: Thirteenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the closeout-attention action-clarity trial using the existing evaluator harness and analyzer gate
- classify the result honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the outcome in the bounded status surface without leaking it into first-hop shells

Success criteria:

- ToneSoul has one honest registry-ready thirteenth-trial result and clear promotion limit for closeout-attention packaging

Current implementation target:

- one evaluator-ready record for the thirteenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 835: Fourteenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the thirteenth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a fourteenth trial wave opens

Success criteria:

- ToneSoul has one admitted fourteenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended fourteenth-trial family
- one explicit no-go list for what must stay parked

### Phase 836: Fourteenth Bounded Trial Wave - Claude Priority-Correction Clarity

Bounded scope:

- refine `claude_entry_adapter` so it exposes one bounded `priority_correction`
- preserve the same first-hop order and consumer-contract priority guard
- keep the change inside Claude-style shell packaging only

Success criteria:

- ToneSoul lands one bounded fourteenth-trial implementation that improves Claude-style recovery discipline without widening transport claims, permissions, or governance semantics

Current implementation target:

- one `priority_correction` packet
- one live probe proving re-read order and bounded next-step target stay explicit
- no planner story, no stronger vendor interop story

### Phase 837: Fourteenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the fourteenth-trial candidate against the existing evaluator harness
- classify it honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the result in the bounded status surface only

Success criteria:

- ToneSoul has one honest fourteenth-trial result classification and registry-ready record for the Claude-style correction packet

Current implementation target:

- one evaluator-ready record for the fourteenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 838: Fifteenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the fourteenth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a fifteenth trial wave opens

Success criteria:

- ToneSoul has one admitted fifteenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended fifteenth-trial family
- one explicit no-go list for what must stay parked

### Phase 839: Fifteenth Bounded Trial Wave - Hot-Memory Pull-Boundary Clarity

Bounded scope:

- refine `hot_memory_ladder` so it exposes one bounded `current_pull_boundary`
- preserve current layer ordering and parent-child authority boundaries
- keep the change inside latency/readout packaging only

Success criteria:

- ToneSoul lands one bounded fifteenth-trial implementation that clarifies where successors should stop pulling without widening authority

Current implementation target:

- one `current_pull_boundary` packet
- one live probe proving observer/session-start/dashboard preserve the same stop layer
- no planner story, no retrieval promotion, no deeper default-pull story

### Phase 840: Fifteenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the fifteenth-trial candidate against the existing evaluator harness
- classify it honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the result in the bounded status surface only

Success criteria:

- ToneSoul has one honest fifteenth-trial result classification and registry-ready record for the hot-memory pull-boundary packet

Current implementation target:

- one evaluator-ready record for the fifteenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 841: Sixteenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the fifteenth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a sixteenth trial wave opens

Success criteria:

- ToneSoul has one admitted sixteenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended sixteenth-trial family
- one explicit no-go list for what must stay parked

### Phase 842: Sixteenth Bounded Trial Wave - Memory-Panel Tier Subordination

Bounded scope:

- refine `dashboard.memory_panel` so it states `auxiliary_only` reference boundaries explicitly
- preserve the panel as reference selection, not operator truth, hot-memory truth, or a second control plane
- keep closeout caution visible when partial work is still active

Success criteria:

- ToneSoul lands one bounded sixteenth-trial implementation that improves dashboard reference discipline without widening retrieval or governance authority

Current implementation target:

- one memory-panel view-model refinement
- one probe proving boundary class, closeout caution, and selected-count summary are explicit
- no retrieval runner, no new control plane, no first-hop shell creep

### Phase 843: Sixteenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the sixteenth-trial candidate against the existing evaluator harness
- classify it honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the result in the bounded status surface only

Success criteria:

- ToneSoul has one honest sixteenth-trial result classification and registry-ready record for the dashboard memory-panel boundary packet

Current implementation target:

- one evaluator-ready record for the sixteenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

### Phase 844: Seventeenth Trial Candidate Admission

Bounded scope:

- choose the next bounded candidate only after the sixteenth trial result is visible
- keep the candidate inside already-allowed mutation classes
- make the no-go list explicit before a seventeenth trial wave opens

Success criteria:

- ToneSoul has one admitted seventeenth candidate with real operator leverage and no new authority mythology

Current implementation target:

- one candidate-admission note
- one recommended seventeenth-trial family
- one explicit no-go list for what must stay parked

### Phase 845: Seventeenth Bounded Trial Wave - Status-Panel Operator Copy Clarity

Bounded scope:

- refine `dashboard.status_panel` so operator-facing copy and telemetry labels are clean and explicit about primary vs secondary surfaces
- preserve the existing Tier 0 / Tier 1 / Tier 2 structure and self-improvement secondary posture
- keep the change inside dashboard packaging only

Success criteria:

- ToneSoul lands one bounded seventeenth-trial implementation that improves operator readability without widening runtime authority or turning the panel into a second control plane

Current implementation target:

- one status-panel view-model refinement
- one live probe proving primary-rule, secondary-rule, and telemetry readability stay explicit
- no runtime-semantic mutation, no new control plane, no shell expansion

### Phase 846: Seventeenth Trial Evaluation And Registry Entry

Bounded scope:

- evaluate the seventeenth-trial candidate against the existing evaluator harness
- classify it honestly as `promote`, `park`, `retire`, `blocked`, or `not_ready_for_trial`
- register the result in the bounded status surface only

Success criteria:

- ToneSoul has one honest seventeenth-trial result classification and registry-ready record for the dashboard status-panel copy packet

Current implementation target:

- one evaluator-ready record for the seventeenth trial
- one analyzer conclusion
- one status-surface update with no shell creep

---

## Compressed Thesis

ToneSoul does not need a giant self-evolution machine next.

It needs a bounded loop that can:

- observe real friction
- test a small change
- analyze the result
- promote honestly

without touching identity, vows, canonical truth, or memory transport semantics.
