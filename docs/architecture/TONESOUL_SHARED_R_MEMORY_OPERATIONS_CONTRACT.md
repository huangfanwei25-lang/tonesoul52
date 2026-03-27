# ToneSoul Shared R-Memory Operations Contract

> Status: operational architecture contract as of 2026-03-27
> Scope: multi-agent shared runtime operations across diagnose, packet, claims, perspectives, checkpoints, compactions, and serialized canonical commit
> Purpose: define what later agents must externalize into shared R-memory, what other agents can actually see there, and which operating order preserves continuity without overclaiming shared cognition.
> Last Updated: 2026-03-28

## Disclaimer

This document turns the current runtime surfaces into an explicit operating contract.

It does not claim that every client automatically syncs private reasoning into shared state.
Only deliberate writes to governed surfaces become visible to other agents.

## Compressed Thesis

ToneSoul's shared R-memory is not telepathy.
It is a governed coordination shell.

Agents share one hot runtime only to the extent that they deliberately read and write:

- session-start posture
- task claims
- perspectives
- checkpoints
- compactions
- accepted canonical commits

## Operational Source Basis

This contract is grounded in the current executable and schema surfaces:

- `tonesoul/runtime_adapter.py`
- `tonesoul/diagnose.py`
- `scripts/run_r_memory_packet.py`
- `scripts/run_task_claim.py`
- `scripts/save_perspective.py`
- `scripts/save_checkpoint.py`
- `scripts/save_compaction.py`
- `spec/governance/r_memory_packet_v1.schema.json`
- `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
- `docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md`
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`

If later prose disagrees with executable runtime behavior, `tonesoul/runtime_adapter.py` and the packet schema win until this contract is updated.

## A Layer: Mechanism

### 1. Shared Visibility Begins At Externalization, Not Thought

Another agent may see only what has been written to governed shared surfaces.

Visible after explicit write:

- `ts:footprints`
- `ts:governance`
- `ts:traces`
- `ts:locks:*`
- `ts:perspectives:{agent_id}`
- `ts:checkpoints:*`
- `ts:compacted`
- `GET /packet`

Not visible by default:

- private chain-of-thought
- local client context window
- unwritten task state
- local draft notes
- unstaged or uncommitted intent
- any conclusion that has not been externalized into a governed surface

The core rule is:

> if it was not written into the governed shell, another agent cannot be expected to inherit it from R-memory

Default collaboration posture:

> every collaborative AI session starts with diagnose + packet + claim inspection, and ends by externalizing checkpoint or compaction before releasing any shared claim

### 2. Session Start Handshake

Every agent session should begin with:

1. `python -m tonesoul.diagnose --agent <your-id>`
2. `python scripts/run_r_memory_packet.py` or `GET /packet`
3. inspect active claims before touching shared work

Use `python scripts/read_governance_state.py` only when you need a lighter posture read and do not need the fuller shared-runtime picture.

### 3. Task Claim Protocol

If more than one terminal or agent may touch the same task or path family, claim first.

Supported surfaces:

- `python scripts/run_task_claim.py claim <task_id> --agent <name> --summary "..."`
- `POST /claim`
- `python scripts/run_task_claim.py list`
- `GET /claims`
- `python scripts/run_task_claim.py release <task_id> --agent <name>`
- `POST /release`

Rules:

- claims are advisory task-ownership signals
- claims reduce collisions, but they do not replace canonical commit serialization
- a claim does not grant permission to bypass Aegis, AXIOMS, or commit review
- claims should name the task clearly enough that later agents know whether to wait, coordinate, or choose another surface

### 4. Perspective Protocol

Use `write_perspective()` when your current line of work is materially relevant to another agent before final commit.

Supported surfaces:

- `python scripts/save_perspective.py --agent <name> --summary "..." --stance "..." --tension "..."`
- `write_perspective()`

Correct contents:

- provisional stance
- unresolved tension
- candidate drift or vow changes
- evidence refs
- partial interpretation awaiting review

Incorrect use:

- treating the perspective lane as canonical truth
- writing abstract theory and then acting as if runtime has already adopted it

### 5. Checkpoint Protocol

Use `write_checkpoint()` when work is interrupted but should remain resumable inside the active operational window.

Supported surfaces:

- `python scripts/save_checkpoint.py --checkpoint-id <id> --agent <name> --summary "..." --path "..."`
- `write_checkpoint()`

Typical times to checkpoint:

- before a context reset
- before closing a terminal
- before switching to another file family
- when a partial implementation has clear pending paths and a clear next action

Checkpoint semantics:

- resumability surface
- non-canonical
- mid-session

### 6. Compaction Protocol

Use `write_compaction()` or `scripts/save_compaction.py` when you need a bounded later-agent handoff that survives longer than a short checkpoint but must not mutate canonical posture.

Supported surfaces:

- `python scripts/save_compaction.py --agent <name> --summary "..." --path "..."`
- `write_compaction()`

Compaction fields should answer:

- what was done
- what must carry forward
- which paths remain pending
- which evidence refs matter
- what the next action should be

Compaction semantics:

- bounded handoff memory
- non-canonical
- resumability-oriented

Forbidden move:

- using compaction to smuggle unreviewed canonical changes into later-agent behavior

### 7. Canonical Commit Protocol

Canonical state changes still belong only to `commit()`.

Required posture:

- canonical commit is serialized by `ts:commit_lock`
- accepted traces are Aegis-protected
- governance posture mutates only through accepted commit flow
- derived world/dashboard surfaces update after canonical write, not before

Canonical commit is for:

- accepted session effects
- accepted vow mutations
- accepted tension and posture updates
- append-only trace history

Canonical commit is not for:

- speculative mid-thought state
- multi-agent brainstorming drafts
- resumability notes that have not passed canonical review

### 8. Required Operating Cadence

When multiple agents share one hot runtime, the correct order is:

1. diagnose/load
2. packet read
3. claim shared task if needed
4. work locally
5. externalize perspective when unresolved but coordination-relevant
6. externalize checkpoint when interrupted
7. externalize compaction when handing off across sessions or models
8. canonical commit only for accepted final state mutation
9. release claim

### 9. Shared Surface Table

| Surface | Meaning | Authority | Visibility |
|---------|---------|-----------|------------|
| `ts:footprints` | recent arrivals / reads | operational | shared after load |
| `ts:governance` | current posture | canonical runtime | shared current state |
| `ts:traces` | accepted session traces | canonical runtime | shared append history |
| `ts:locks:*` | task claims | operational | shared immediately after claim |
| `ts:perspectives:{agent_id}` | provisional stance | non-canonical | visible after explicit write |
| `ts:checkpoints:*` | resumability checkpoint | non-canonical | visible after explicit write |
| `ts:compacted` | bounded handoff summary | non-canonical | visible after explicit write |
| `ts:field` | experimental synthesis | experimental | visible if implemented |
| `GET /packet` | aggregated hot-state read surface | operational packet | read-only composite view |

### 10. Failure Modes And Anti-Patterns

Architectural failure signals:

- an agent worked for a long time without claim/checkpoint/compaction, then expected another agent to know its progress
- compaction text changed later-agent posture without canonical evidence
- a task claim was treated as if it granted canonical mutation rights
- packet output was treated as if it were the whole repository history
- perspective language was promoted straight into mechanism without contract support
- an agent skipped diagnose/packet and bulk-read prose while missing current shared posture

## B Layer: Observable Behavior

If this contract is upheld, another agent should be able to observe:

- who recently arrived via footprints
- which shared tasks are actively claimed
- recent canonical traces through packet or trace history
- bounded handoff summaries through compactions
- provisional but explicit per-agent state through perspectives or checkpoints

Another agent should not be expected to observe:

- unwritten reasoning
- silent local file edits
- task intent that was never claimed
- conclusions still trapped inside one client session

## C Layer: Interpretation

The wrong philosophical reading is:

- "all agents are now literally in one mind"
- "shared Redis state means merged hidden cognition"
- "if one agent thought it, the other should already know it"

The defensible reading is:

- ToneSoul externalizes enough governed state to preserve operational continuity
- continuity comes from deliberate shared traces and resumability surfaces
- shared R-memory is a common shell, not a fused latent subject

In ToneSoul language:

> what survives between agents is not raw hidden thought, but the governed residue of choices that were made visible in time

## Relationship To Other Documents

- `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
  - defines what R-memory is and where it sits in the memory stack
- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - defines how far parallel perspectives and field synthesis may go without overclaiming shared state
- `docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md`
  - defines why compaction is non-canonical and why projection surfaces stay projection
- `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`
  - preserves the current commit-order and state-authority logic
- `spec/governance/r_memory_packet_v1.schema.json`
  - defines the compact read surface later agents should prefer over re-reading long prose

## Canonical Handoff Line

Shared R-memory preserves continuity only through governed externalization: diagnose and packet first, claim before collision, use perspective/checkpoint/compaction for non-canonical coordination, and reserve canonical mutation for serialized Aegis-backed commit.
