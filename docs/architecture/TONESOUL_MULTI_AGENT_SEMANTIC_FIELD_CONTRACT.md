# ToneSoul Multi-Agent Semantic Field Contract

> Status: architectural contract and rollout boundary as of 2026-03-26
> Scope: multi-agent shared runtime memory, perspective lanes, semantic-field synthesis, and canonical commit safety
> Purpose: define what ToneSoul may and may not claim about multi-agent shared state after reviewing current official enterprise and lab evidence.
> Last Updated: 2026-03-26

## Disclaimer

This document contains both executable architectural requirements and higher-order interpretation.

The executable parts govern how ToneSoul should structure shared runtime state, canonical commits, and experimental field synthesis.
The interpretive parts explain why this boundary exists.
Interpretation does not imply that every later-phase mechanism is already implemented.

## Compressed Thesis

ToneSoul may build a governed multi-agent semantic field, but only if parallel perspectives remain non-canonical, canonical governance commits stay serialized, and field synthesis never outranks hard constraints or Aegis-backed traceability.

## Evidence Basis

This contract is grounded in current official enterprise and lab sources last checked on 2026-03-26:

- Anthropic, "How we built our multi-agent research system" (2025-06-13)
- Anthropic, "Effective context engineering for AI agents" (2025-09-29)
- Anthropic, "Managing context on the Claude Developer Platform" (2025-09-29)
- Anthropic, "Effective harnesses for long-running agents" (2025-11-26)
- OpenAI, "New tools for building agents" (2025-03-11)
- OpenAI platform docs, "Agents SDK"
- OpenAI platform docs, "Trace grading"
- OpenAI, "Introducing AgentKit" (2025-10-06)
- Microsoft Research, "AutoGen v0.4" (2025-01-14 / 2025-02-25)
- Microsoft Research, "Magentic-One" (2024-11-04)
- Google Cloud, "How to build a simple multi-agentic system using Google's ADK" (2025-07-02)
- Google Research, "Titans: Learning to Memorize at Test Time" (2025)
- Google Research Blog, "Titans + MIRAS: Helping AI have long-term memory" (2025-12-04)

Inference from those sources:

- frontier practice clearly supports bounded subagents, external memory, checkpoints, handoffs, tracing, and evaluation
- frontier practice does not yet justify letting many agents freely and concurrently mutate one canonical shared semantic center
- test-time memory research is relevant inspiration, but it does not erase the need for explicit external governance and concurrency control in ToneSoul

See the supporting evidence note:

- `docs/research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md`

## A Layer: Mechanism

### 1. Canonical And Experimental Lanes Must Stay Separate

ToneSoul must separate the shared runtime into four distinct lanes.

#### A. Canonical Governance Lane

This lane carries public, auditable, serialized truth surfaces:

- `ts:governance`
- `ts:traces`
- `ts:aegis:chain_head`
- file mirrors such as `governance_state.json` and `memory/autonomous/session_traces.jsonl`

Rules:

- this lane is authoritative
- this lane is append-oriented and traceable
- this lane must not accept uncontrolled concurrent mutation

#### B. Perspective Lane

This lane carries per-agent working perspectives:

- `ts:perspectives:{agent_id}`

Expected contents:

- local tension deltas
- proposed drift adjustments
- candidate vow changes
- agent-local evidence notes
- partial interpretations awaiting synthesis

Rules:

- each agent writes only to its own perspective key
- this lane may be updated concurrently
- this lane is not canonical by itself

#### C. Field Synthesis Lane

This lane carries a governed synthesis of perspective lanes:

- `ts:field`
- optional derived artifacts or dashboards that summarize field posture

Rules:

- this lane is experimental until explicitly promoted
- it may summarize or score perspective convergence/divergence
- it must not directly overwrite canonical governance posture

#### D. Checkpoint Lane

This lane carries mid-session state without pretending to be final truth:

- `ts:checkpoints:*`

Rules:

- checkpoints are resumability surfaces
- checkpoints are not final commits
- checkpoints may later inform synthesis or canonical commit review

### 2. Canonical Commit Must Be Serialized

Any operation that mutates canonical governance state must run inside a dedicated commit critical section.

Required mechanism:

- `ts:commit_lock`

Required lock properties:

- acquire with atomic set-if-not-exists plus expiry
- include an owner token
- release with compare-and-delete semantics
- fail closed or retry if the lock cannot be acquired

Advisory task claims such as `ts:locks:*` are not sufficient for this role.

### 3. Aegis Trace Integrity Is Mandatory

To satisfy ToneSoul's traceability posture and Axiom #1 continuity expectations:

- accepted canonical traces in R-memory must be Aegis-protected
- the canonical append path must bind trace payload, signature, and previous hash
- `ts:aegis:chain_head` update must happen inside the same canonical commit critical section that writes the accepted commit

Operationally, ToneSoul should treat accepted canonical traces as:

> Aegis-chained traces: content-filtered, signature-bound, and hash-linked

Perspective and checkpoint lanes may record provisional material, but only accepted canonical traces may advance the chain head.

### 4. Current Session-End Order Must Follow Runtime Reality

As of 2026-03-26, the operational source of truth is:

- `tonesoul/runtime_adapter.py::commit()`

The current canonical order is:

1. build trace candidate
2. run Aegis gate
3. if blocked, do not merge tension/vow/drift/session-count effects into canonical posture
4. if accepted, merge accepted trace effects into governance posture
5. persist updated governance posture
6. append the accepted protected trace
7. rebuild derived world/dashboard surfaces

If future prose disagrees with runtime code, runtime code wins until the contract is updated.

### 5. Field Synthesis May Inform Review, Not Override Doctrine

The semantic field may be used to:

- highlight convergence or disagreement between agents
- recommend review intensity
- suggest candidate checkpoints or follow-up tasks
- provide a richer operator-facing picture than a single last-write-wins posture

The semantic field may not:

- override hard constraints
- override AXIOMS
- override the A/B/C firewall
- bypass Aegis
- directly replace serialized canonical commit

### 6. Promotion Gate Before Canonical Influence

No semantic-field-derived signal may influence canonical posture until it passes an explicit evaluation gate.

The promotion gate must check at least:

- trace integrity
- evidence sufficiency
- field stability across replay
- disagreement visibility
- regression impact against current canonical behavior

Until that gate exists, `ts:field` remains an experimental synthesis surface.

## B Layer: Observable Behavior

If this contract is upheld, operators and later agents should be able to observe:

- multiple agents contributing separate perspective records without overwriting one another
- a canonical governance surface that changes through serialized commits rather than last-write-wins races
- an Aegis chain head that advances linearly rather than forking
- checkpoints that preserve progress without pretending to be final truth
- a field synthesis surface that shows disagreement rather than hiding it
- traces, evals, or graders that can detect whether semantic-field promotion improved or degraded outcomes

If these observations fail, the likely architectural meaning is:

- duplicated or missing canonical effects imply commit serialization is broken
- multiple accepted traces pointing at the same `prev_hash` imply canonical chain integrity is broken
- field summaries changing canonical posture without trace/eval evidence imply synthesis has overreached its contract

## C Layer: Interpretation

The right philosophical reading is not:

- "many models share one latent mind"
- "Redis becomes collective consciousness"
- "the field proves a shared subject"

The defensible reading is:

- ToneSoul is externalizing parallel viewpoints into a governed runtime
- those viewpoints may be synthesized into an interpretable field
- the field is an observable-shell coordination construct, not evidence of merged hidden cognition

In ToneSoul language:

> the semantic field is a governed interference map over externalized perspectives, not a claim about direct latent-state fusion

## Allowed Claims

ToneSoul may claim:

- it supports bounded multi-agent perspective lanes
- it supports shared R-memory for hot coordination state
- it supports governed field synthesis as an experimental layer
- it requires serialized canonical commit for governance state
- it uses trace-backed evaluation before promoting new multi-agent behavior

## Forbidden Claims

ToneSoul must not claim:

- that multiple agents share one real hidden semantic state
- that Redis-backed shared state is equivalent to model-internal memory research
- that frontier labs have already validated free concurrent mutation of one canonical semantic center
- that semantic-field language itself proves safety, continuity, or correctness
- that experimental field synthesis already outranks AXIOMS, Aegis, or canonical traceability

## Rollout Order

### Phase 1: Canonical Commit Safety

- add dedicated commit mutex
- protect Aegis chain-head advancement inside the same critical section
- keep canonical posture serialized

### Phase 2: Perspective And Checkpoint Lanes

- add `ts:perspectives:{agent_id}`
- add `ts:checkpoints:*`
- preserve per-agent viewpoint isolation

### Phase 3: Experimental Field Synthesis

- add `ts:field`
- compute governed synthesis from perspective lanes
- expose disagreement and convergence explicitly

### Phase 4: Promotion Gate

- evaluate field-assisted behavior against trace/eval criteria
- only then allow limited field-derived recommendations to influence canonical review

## Relationship To Other Documents

- `docs/research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md`
  - official-source evidence map behind this contract
- `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
  - R-memory stack, dominance order, and memory-layer roles
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`
  - current runtime review logic and commit-order posture
- `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`
  - honesty boundary for mechanism vs observability vs interpretation
- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - higher-level north star for keeping governance, memory, and distillation externalized

## Canonical Handoff Line

Treat multi-agent semantic field work as a governed experimental synthesis layer around ToneSoul's canonical core, not as permission to let many agents freely co-write one shared truth surface.
