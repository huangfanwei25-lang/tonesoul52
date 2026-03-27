# ToneSoul R-Memory Stack Recommendation

> Purpose: define how Redis-backed "R-memory" should fit into ToneSoul as the live shared runtime memory layer, what it should and should not dominate, and which external repositories are the best fit for this role.
> Last Updated: 2026-03-26

Companion contract:

- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - use this when the question is not only "what is R-memory" but also "how many agents may share it, what must stay serialized, and where semantic-field ideas stop being evidence-backed"
- `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
  - use this when the question is not only "what is shared state" but "what another agent can actually see, when to claim/checkpoint/compact, and what must be externalized on purpose"

## Core Thesis

`R-memory` is a useful ToneSoul term for:

> the Redis-backed live shared runtime memory layer that sits between transient model compute and longer-lived file / graph / vector memory

It is a good term because it is short, memorable, and operationally clear.

But it must not be confused with:

- model weights
- hidden latent state
- true subjective experience
- permanent long-term memory

The right claim is:

> R-memory is the hot coordination layer that allows multiple agents and sessions to inherit posture, presence, recent events, and governance continuity without pretending that the model itself became persistent.

## Why ToneSoul Needs This Layer

ToneSoul already has:

- governance contracts
- state artifacts
- vows / vetoes / drift concepts
- retrievable architecture anchors

What it still lacks in everyday operation is a stable live layer that all agents can read and write while they work.

Without that layer:

- every agent rereads docs instead of inheriting hot state
- dashboards reconstruct continuity from files after the fact
- multi-agent coordination feels delayed and brittle
- the same repo can drift into parallel local truths

R-memory is the missing seam between:

- `stateless model session`
- `persistent governance architecture`

## What R-Memory Is Good At

Redis is a good fit when the need is:

- low-latency shared state
- append-only event streams
- short-lived coordination data
- presence and footprints
- pub/sub fanout
- locks and checkpoints
- lightweight counters and TTL-backed caches

In ToneSoul terms, this means R-memory is well-suited for:

- current governance posture
- recent session traces
- active vow surface
- recent Aegis veto surface
- world / zone registry surface
- recent visitors / footprints
- in-flight task ownership
- runtime event fanout for dashboards and agents

## What R-Memory Is Not Good At

Redis should not become the only memory layer.

It is not ideal for:

- canonical philosophy
- rich narrative documents
- public audit prose
- durable graph reasoning over evolving relationships
- raw private vault storage
- model-distillation source governance by itself

That means ToneSoul should not collapse everything into Redis.

R-memory should remain the hot operational layer, not the whole cognitive stack.

## The Dominance Order Inside Live Compute

The user's deeper question is not only "where is memory stored."
It is:

> once all this context is loaded into live compute, which logic should dominate

For ToneSoul, the dominance order should be:

1. **Hard constraints**
   - system/developer rules
   - protected-path rules
   - explicit safety gates
2. **Canonical governance contracts**
   - AXIOMS
   - A/B/C firewall
   - L7 / L8 contracts
   - documented runtime boundaries
3. **Current task objective**
   - what the agent is actually trying to complete now
4. **R-memory posture**
   - current governance state
   - recent traces
   - active vows
   - vetoes
   - footprints
5. **Retrieved long-term memory**
   - graph memory
   - vector memory
   - selected file artifacts
6. **Loose prose background**
   - large docs
   - old notes
   - narrative context

This matters because R-memory should strongly influence:

- continuity
- coordination
- current operational posture

But it must not outrank:

- hard constraints
- canonical governance doctrine

Otherwise the hot layer would start overriding the constitution.

## Recommended ToneSoul Memory Stack

### L0: Model Working Memory

This is the immediate compute memory during a single inference:

- prompt context
- active token sequence
- KV cache / transient internal state

Properties:

- fast
- temporary
- opaque
- cannot be trusted as durable continuity

### L1: R-Memory (Redis Live Runtime Layer)

This is the new hot shared state layer.

Recommended surfaces:

- `ts:governance`
  - current governance posture
- `ts:traces`
  - append-only session trace stream
  - accepted traces should be Aegis-protected before append: content-filtered, signature-bound, and hash-chained for Axiom 1 traceability
- `ts:zones`
  - live world / dashboard zone state
- `ts:footprints`
  - recent agent arrivals / activity
- `ts:events`
  - runtime pub/sub fanout
- `ts:aegis:chain_head`
  - integrity-chain live pointer
- `ts:locks:*`
  - optional ownership / anti-collision locks
- `ts:commit_lock`
  - canonical governance commit mutex
- `ts:checkpoints:*`
  - optional workflow checkpoints
- `ts:compacted`
  - bounded non-canonical resumability summaries for later-agent handoff

Properties:

- shared
- low-latency
- good for coordination
- not enough for rich semantic memory alone

### L2: Canonical File Memory

This remains essential.

Examples:

- `governance_state.json`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- architecture docs
- contracts
- status artifacts

Properties:

- auditable
- diffable
- human-readable
- slower than R-memory

This is where ToneSoul preserves formal public truth surfaces.

### L3: Long-Term Semantic Memory

This layer should hold richer, query-oriented memory:

- temporal knowledge graph
- vector retrieval
- durable semantic summaries
- relationship history

This is where Graphiti / OpenClaw-Memory / Mem0 fit.

### L4: Governance and Verification Layer

ToneSoul itself must remain the judge over all memory layers.

This layer decides:

- what may enter memory
- what must be blocked
- what is reviewable but not canonical
- what may be distilled
- what must remain outside model-attached layers

This is where:

- Aegis
- vows
- ABC firewall
- L7 / L8 boundaries
- verifier-first logic

must stay.

## Best-Fit External Repositories

Last checked against public GitHub project pages on 2026-03-26.

### 1. Redis + LangGraph Redis

Repos:

- <https://github.com/redis/redis>
- <https://github.com/redis-developer/langgraph-redis>

Why it fits:

- closest match to `R-memory`
- checkpoint + store abstraction already exists
- natural fit for hot shared state
- supports TTL, store semantics, and checkpoint persistence
- aligns well with multi-agent orchestration

Best ToneSoul role:

- the live shared memory backbone
- session checkpoints
- event fanout
- shared agent presence

Judgment:

> best external base for ToneSoul's Redis-backed hot runtime layer

### 2. Graphiti

Repo:

- <https://github.com/getzep/graphiti>

Why it fits:

- designed for temporally-aware knowledge graphs
- explicitly handles changing relationships over time
- better fit than plain GraphRAG for evolving agent memory

Best ToneSoul role:

- long-term relationship memory
- temporal semantic memory
- higher-order memory over sessions, entities, and evolving commitments

Judgment:

> best graph-oriented companion to ToneSoul once R-memory is stable

### 3. Mem0

Repo:

- <https://github.com/mem0ai/mem0>

Why it fits:

- practical and popular memory layer
- built around agent memory use cases
- useful for fast experimentation and comparison

Limits for ToneSoul:

- not governance-first
- not enough by itself for vow / veto / constitution logic

Best ToneSoul role:

- benchmark or fallback memory layer
- pragmatic personalization / long-term recall experiments

Judgment:

> useful reference and integration candidate, but not the constitutional center of ToneSoul

### 4. RedisVL

Repo:

- <https://github.com/redis/redis-vl-python>

Why it fits:

- allows Redis to stretch beyond key-value state
- useful for metadata + vector retrieval near the hot layer

Best ToneSoul role:

- hybrid retrieval attached to R-memory
- fast semantic lookup near operational state

Judgment:

> useful extension once ToneSoul wants one backend to cover hot state plus lightweight semantic retrieval

### 5. GraphRAG / Neo4j GraphRAG

Repos:

- <https://github.com/microsoft/graphrag>
- <https://github.com/neo4j/neo4j-graphrag-python>

Why they still matter:

- strong for document graph retrieval
- useful for file / knowledge-base structure

Why they are not the center:

- less aligned with the hot shared runtime memory problem
- better as document-knowledge infrastructure than as ToneSoul's main live memory layer

Best ToneSoul role:

- document graph
- repo knowledge map
- large artifact retrieval

Judgment:

> important supporting layer, but not the primary answer to R-memory

## Recommended ToneSoul Position

If ToneSoul wants a coherent stack, the cleanest position is:

- **ToneSoul governance** stays sovereign
- **Redis** becomes R-memory
- **Graphiti / OpenClaw-Memory** handle deeper long-term semantic memory
- **file artifacts** remain the audit surface

In one line:

> ToneSoul should use Redis as the nervous system, not as the soul itself

## Concrete Integration Shape

## First Operational Surface

The first hot-state surface later agents should actually consume is not the whole repo.
It should be a compact `R-memory packet` that exposes:

- current governance posture
- recent traces and visitors
- recent bounded compaction summaries
- dominance order inside live compute
- the real session-end mutation order
- Aegis trace-integrity requirements

Operational entrypoints:

- `python scripts/run_r_memory_packet.py`
- `python scripts/run_task_claim.py`
- `python scripts/save_compaction.py`
- `GET /packet`
- `GET /claims`
- `POST /claim`
- `POST /release`
- `POST /compact`
- `spec/governance/r_memory_packet_v1.schema.json`
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`

### Session start

Agent:

1. loads canonical instructions
2. reads governance posture from R-memory
3. reads recent footprints / active locks
4. optionally retrieves long-term semantic context
5. begins work

### During work

Agent:

- updates checkpoints
- records presence
- publishes key state changes
- does not yet write canonical conclusions too early

### Session end

Agent:

1. builds session trace
2. runs Aegis / verifier gates
3. merges accepted trace effects into governance posture
4. persists updated governance posture into R-memory and/or file state
5. appends the accepted protected trace into the trace stream
6. rebuilds derived world/dashboard surfaces
7. optionally writes safe summaries into long-term semantic memory

This ordering must follow runtime reality.
At the time of this recommendation, `tonesoul/runtime_adapter.py::commit()` is the operational source of truth:

- blocked traces do **not** mutate posture fields such as tension, vows, drift, or session count
- blocked traces only record an Aegis veto on the governance side
- accepted traces are Aegis-processed before they are appended
- canonical multi-agent commits should be serialized behind a dedicated commit mutex rather than relying on advisory task claims

## What Must Stay Outside R-Memory

Do not treat Redis as the universal sink.

Keep these out unless deliberately summarized:

- raw private journals
- unfiltered personal memory
- whole markdown corpora
- arbitrary long narrative blobs
- distillation-forbidden surfaces
- human-only protected files

R-memory should carry posture and coordination, not dump everything.

## Suggested Build Order

### Phase A: Stabilize the runtime adapter

- finish Redis/file parity
- clean event semantics
- add direct tests for script entrypoints

### Phase B: Promote Redis into the official R-memory layer

- presence
- checkpoints
- locks
- event routing
- world/dashboard fanout

### Phase C: Add semantic memory companion

Preferred order:

1. OpenClaw-Memory if the repo-specific direction is already active
2. Graphiti if temporal graph memory becomes the next frontier
3. Mem0 as a comparison or fallback layer

### Phase D: Distillation boundary enforcement

- only public-safe summaries move beyond memory
- no direct private-memory-to-adapter shortcut
- keep L8 governance explicit

## Recommended Near-Term Decision

The best next step is not to add five memory systems at once.

It is:

1. explicitly name Redis as `R-memory`
2. finish hardening the Redis-backed runtime path
3. define what belongs in R-memory vs file memory vs graph memory
4. only then connect Graphiti or Mem0

This keeps ToneSoul readable and avoids premature memory sprawl.

## Final Position

Yes, this concept can meaningfully elevate how AI agents operate inside ToneSoul.

Not because Redis grants consciousness.

But because it gives the system a real shared live layer where:

- continuity can persist
- coordination can happen in real time
- posture can survive across sessions
- later reasoning can inherit more than raw prose

If ToneSoul already has a constitution, contracts, and memory doctrine,
then R-memory is the missing live substrate that lets those things actually run together.

## One-Sentence Handoff

Use Redis as ToneSoul's R-memory hot layer, keep governance above it, keep audit surfaces beside it, and let deeper graph/vector memory attach only after the live runtime seam is stable.
