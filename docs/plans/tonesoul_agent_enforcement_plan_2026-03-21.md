# ToneSoul Agent Enforcement Plan

Date: 2026-03-21
Status: draft

## Why

Prompt rules decay across multi-step execution.

If a task has multiple steps, the effective success rate drops multiplicatively.
So the main problem is not only model intelligence. The main problem is lack of
enforcement and verification.

ToneSoul should therefore treat agent collaboration as a governance system:

1. retrieval must be structured
2. risky actions must be blocked at the system boundary
3. output claims must be verified before completion

## Four Layers

### 1. Prompt Layer

Use short, high-signal instruction files.

- keep the core contract short
- move long rationale into linked docs
- do not rely on prose alone for hard safety rules

In ToneSoul terms:

- `AGENTS.md` / `AI_ONBOARDING.md` define posture
- canonical reading order comes from the knowledge graph

### 2. Guard Layer

Move hard constraints out of prose and into executable checks.

Examples:

- block edits to `.env`, `.env.*`, `AGENTS.md`, `MEMORY.md`
- block writes to private-memory payloads
- block dangerous path classes before the tool call succeeds

This is the `PreToolUse` equivalent.

### 3. Normalization Layer

After edits, run bounded normalization automatically.

Examples:

- Python touched -> `ruff check`
- web touched -> `npm --prefix apps/web run lint`
- generated artifacts touched -> regenerate from source script, never hand-edit

This is the `PostToolUse` equivalent.

### 4. Verifier Layer

Before an agent can claim "done", run lightweight verifiers.

Verifier classes:

1. contract verifier
   - did protected paths stay untouched?
2. behavior verifier
   - did targeted tests pass?
3. evidence verifier
   - does the final claim match command output and artifact state?

This is the `Stop Hook` equivalent.

## ToneSoul Mapping

| Collaboration Level | ToneSoul Interpretation | Required Mechanism |
| --- | --- | --- |
| Conversational | Pure prompt-following | none |
| Configured | repo rules in docs | canonical docs + short prompts |
| Automated | rules become executable | guards + post-change checks |
| Orchestrated | specialized lanes and roles | knowledge graph + lane routing |
| Autonomous | agents check agents | stop verifiers + replayable evidence |

## Immediate Application Order

### A. Retrieval first

Agents should open:

1. `docs/status/tonesoul_knowledge_graph_latest.md`
2. the relevant lane
3. authority docs
4. implementation files
5. tests or latest status artifacts

### B. Hard guards next

The first executable guardrail to add should be a protected-path verifier.

Minimum deny set:

- `.env`
- `.env.local`
- `.env.*.local`
- `AGENTS.md`
- `MEMORY.md`
- runtime memory payloads (`memory/*.jsonl`, `.db`, `vectors/`)

### C. Changed-file verifiers

Use changed-file aware verification instead of always running the full repo:

- Python-only change -> targeted `ruff` + relevant pytest
- web-only change -> targeted lint/test
- governance file change -> docs consistency + integrity checks

### D. Stop verifier

The completion gate should reject answers that claim:

- tests passed when they did not
- artifacts updated when they were not regenerated
- no changes were made when protected paths were touched

## Design Rule

Do not encode critical rules only as natural language.

In ToneSoul terms:

- prose defines philosophy
- graph defines retrieval
- verifiers define reality

Without the last layer, governance remains narrative instead of engineering.
