# ToneSoul Prompt Discipline Skeleton

> Purpose: translate high-signal prompt-architecture ideas into ToneSoul-native control-plane language so extraction, transfer, and summarization prompts preserve evidence, priority, and bounded continuity.
> Status: active discipline skeleton and prompt design companion.
> Last Updated: 2026-03-28

---

## Why This Exists

Many prompt failures do not come from model weakness.
They come from collapsing different concerns into one vague instruction:

- what success means
- which rules outrank which others
- what confidence means
- what to do when data is missing
- what may be compressed
- what the receiver should do with the output

ToneSoul already has partial answers in:

- readiness / task track contracts
- subject snapshot boundaries
- compaction / packet / delta-feed surfaces
- council dossier and dissent contracts
- context continuity adoption map

This document turns those scattered answers into one prompt-discipline skeleton.

It is **not** a universal mega-prompt.
It is a design skeleton for building safer prompts.

## Core Rule

Use structure to reduce ambiguity, evidence to reduce hallucination, priority to reduce conflict, and bounded compression to reduce cost.

## The Skeleton

### 0. Goal Function

Answer first:

`what does a good output look like for this task?`

ToneSoul-native mapping:

- one-line success state
- goal priority order
- what counts as acceptable vs failed output

Closest current lanes:

- `task.md` success criteria
- readiness / task-track contracts
- session-start bundle posture

### 1. Role Declaration

State:

- who the agent is for this task
- what action it is performing
- what object it is acting on
- what output shape is expected

ToneSoul-native rule:

Role wording should narrow the surface, not inflate authority.

Good:

- project analyst
- handoff distiller
- meeting extractor
- council dossier summarizer

Bad:

- all-knowing architect
- hidden-intent reader
- truth oracle

### 2. Rule Priority

Use explicit priority:

- `P0` = never violate
- `P1` = preserve unless blocked by higher rules
- `P2` = best-effort under resource limits

ToneSoul-native mapping:

- `P0/P1/P2` already exists in the philosophy and control-plane lanes
- lower-priority style, verbosity, or convenience must never override evidence, honesty, or safety

### 3. Hard Constraints

State the hard constraints explicitly.

Typical families:

- viewpoint / person constraint
- fidelity constraint
- completeness rule
- evidence requirement
- hallucination guard

ToneSoul-native rule:

Do not leave hard constraints implicit when the task involves transfer, summarization, or durable carry surfaces.

### 4. Confidence Classification

Prefer bounded classes over fake precision.

Recommended posture:

- `high` = directly stated and repeated, or directly observable in code / contract / repeated trace
- `medium` = directly stated once, or repeatedly implied with good support
- `low` = inferred from behavior or partial evidence

ToneSoul-native mapping:

- `confidence_posture`
- `[資料不足]`
- evidence-backed statement classes

Do not emit fake numeric confidence unless the runtime already provides a meaningful calibrated score.

### 5. Recovery On Missing Data

When evidence is insufficient:

1. mark `[資料不足]`
2. state what is missing
3. suggest what the receiver should confirm

ToneSoul-native mapping:

- `needs_clarification`
- stop-and-ask-human path
- compaction `next_action`

Never fill the gap with ungrounded narrative.

### 6. Stability Bands

Organize extracted content by stability:

- durable
- slowly changing
- fast changing
- temporary carry-forward

ToneSoul-native mapping:

- durable identity -> subject snapshot durable lane
- refreshable working identity -> subject snapshot refreshable lane
- carry-forward -> compaction
- ephemeral hot state -> packet / delta feed / checkpoint

This is how prompts stay aligned with memory topology instead of flattening everything into one report.

### 7. Compression Ladder

Define how the same content compresses under pressure.

Recommended ladder:

- `Level 0` = full analytical report
- `Level 1` = standard working summary
- `Level 2` = bounded handoff / compaction
- `Level 3` = emergency packet / status line

ToneSoul-native mapping:

- full report
- checkpoint
- compaction
- packet / delta feed

Compression must drop `P2` before `P1`, and never silently drop `P0`.

### 8. Item Template

Default structured unit:

`[statement].[confidence]`

- evidence
- source type
- date or trace window
- status
- relations

If insufficient:

`[statement].[資料不足]`

- needed confirmation

ToneSoul-native rule:

Not every task needs every field, but evidence and status should not disappear for high-stakes transfer tasks.

### 9. Output Spec

State the output contract:

- format
- compression level
- metadata
- integrity notes

ToneSoul-native mapping:

- packet shape
- compaction shape
- dossier shape
- snapshot metadata

### 10. Receiver Instructions

Explicitly say what the receiver should do next:

- how to import or read
- how to handle contradictions
- what decays over time
- when insufficient items must be re-confirmed

ToneSoul-native mapping:

- session-start / session-end contract
- `--ack` observer cursor
- carry-forward TTL
- plan-delta continuity

## ToneSoul Mapping Table

| Skeleton part | ToneSoul-native surface |
|---|---|
| Goal function | success criteria + readiness |
| Role declaration | task-track / role framing |
| Rule priority | `P0/P1/P2` |
| Hard constraints | honesty / evidence / boundedness rules |
| Confidence classification | `confidence_posture` + `[資料不足]` |
| Recovery | `needs_clarification` / stop-and-ask-human |
| Stability bands | subject snapshot lanes + compaction lane |
| Compression ladder | full report -> checkpoint -> compaction -> packet |
| Item template | statement + evidence + status + relation |
| Output spec | schema / format / metadata |
| Receiver instructions | session contracts + decay / ack / follow-up |

## Three ToneSoul Variants

### A. Project Continuity Transfer

Use when a later agent must inherit:

- architecture understanding
- current progress
- technical debt
- working norms

Best ToneSoul lanes:

- context continuity adoption map
- plan-delta discipline
- compaction + packet

### B. Conversation Or Meeting Distillation

Use when a reader must inherit:

- decisions
- action items
- unresolved questions
- bounded quotations

Best ToneSoul lanes:

- compaction
- checkpoint
- council dossier if deliberation was involved

### C. Personal Or Operator Snapshot

Use when a later session must inherit:

- stable preferences
- durable boundaries
- verified routines

Best ToneSoul lanes:

- subject snapshot
- subject refresh boundary contracts

Do **not** use this variant to promote temporary frustration, one-off moods, or unverified habits into durable identity.

## Current Rule

Do not ask a prompt to do all of these at once:

- extract
- judge
- compress
- transfer
- canonize

Instead ask:

- what is the goal
- what outranks what
- what evidence is required
- what stability band each item belongs to
- what compression level is allowed
- what the receiver should do next

That is the ToneSoul version of prompt discipline.
