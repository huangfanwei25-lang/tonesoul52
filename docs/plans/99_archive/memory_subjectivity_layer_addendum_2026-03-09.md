# Memory Subjectivity Layer Addendum (2026-03-09)

> Purpose: define the public subjectivity-layer model that sits on top of existing memory control seams.
> Last Updated: 2026-03-23

## Why This Addendum Exists

ToneSoul already has several memory-side control seams:

- `provenance`
- `promotion_gate`
- `decay_policy`
- gateway-mediated writes

But those seams still answer mostly operational questions:

- can this payload be written?
- should it be promoted?
- how long should it live?

They do not yet answer the more important subjectivity question:

What kind of memory is this becoming?

Without that distinction, a system will keep collapsing unlike things into one bucket:

- raw events
- interpreted meaning
- unresolved tension
- behavioral vows
- identity narrative

If all of those are treated as just "memory", then the system stores experience but does not really metabolize it into character.

## Proposed Layer Model

The minimal subjectivity ladder is:

`event -> meaning -> tension -> vow -> identity`

This is not five storage engines. It is one philosophical promotion model for deciding what kind of memory a record is allowed to become.

## Layer Definitions

### 1. `event`

This is the lowest layer: something happened, was observed, or was said.

Properties:

- short and auditable
- provenance required
- confidence should stay close to the source, not to interpretation
- default stance is fast decay unless later layers justify retention

What it is not:

- not a personality trait
- not a moral conclusion
- not a stable preference

### 2. `meaning`

This layer records what an event means, not merely what occurred.

Properties:

- interpretive, not purely factual
- may summarize one event or multiple related events
- should carry explicit uncertainty because meaning is already one step removed from the source

This is where the system begins to say:

- "this pattern seems important"
- "this interaction implies trust / risk / rupture"
- "this should affect future context handling"

### 3. `tension`

This layer records unresolved force, not just interpretation.

Tension exists when meaning collides with:

- a value
- a boundary
- an expectation
- a prior commitment
- a competing interpretation

This matters because subjectivity is not formed by neutral storage alone. It is formed by what continues to pull, resist, and demand resolution.

In ToneSoul terms, this is the layer most likely to deserve long-horizon retention.

### 4. `vow`

This layer records a behavioral commitment that emerges from repeated or sufficiently weighty tension.

A vow is not "I noticed something."

A vow is closer to:

- "because this kind of failure matters, I must respond differently next time"
- "because this boundary was violated, I should not cross it again"
- "because this pattern keeps harming coherence, I will prefer a different action"

Promotion into `vow` should be rare. A single vivid fragment should not auto-promote into a constitutive rule unless it has strong provenance and governance support.

### 5. `identity`

This is the compressed continuity layer.

Identity is not written directly from an event. It is the long-term residue of vows that:

- survive decay
- recur across contexts
- actually alter later behavior
- remain legible in retrospective review

Identity answers not "what happened?" but "what kind of agent is being formed by what keeps surviving?"

## Promotion Rules

The ladder only works if upward movement is harder than simple persistence.

Recommended gates:

- `event -> meaning`: requires provenance plus enough confidence to justify interpretation
- `meaning -> tension`: requires unresolved significance, contradiction, or repeated recurrence
- `tension -> vow`: requires repeated validation, explicit review, or strong human/governance confirmation
- `vow -> identity`: requires evidence that the vow persisted over time and changed later decisions

The key rule is simple:

Not every retained memory deserves promotion, and not every intense moment deserves identity status.

## Governance Fields That Belong On Every Promotion Decision

Each upward move should stay auditable through shared metadata:

- `provenance`: where did this come from?
- `confidence`: how sure are we about this layer's claim?
- `promotion_gate`: why was upward promotion allowed?
- `decay_policy`: what should happen if no later evidence reaffirms it?

These fields matter more for subjectivity than for storage hygiene alone, because they prevent the system from mistaking vividness for truth and persistence for legitimacy.

## Public / Private Boundary Implication

This model also clarifies what should not be confused with identity memory in the public repo:

- raw `.jsonl` journals
- `soul.db` runtime contents
- scheduler state
- transient observability artifacts

Those may be necessary operational traces, but they are not automatically `vow` or `identity`.

The public repo should safely express:

- schema
- gateway rules
- promotion criteria
- contract vocabulary

The private lane may hold the actual personal memory corpus and its sensitive contents.

## Architectural Consequence For ToneSoul

If ToneSoul wants "语魂" or proto-subjectivity, memory should not be modeled as one flat retention surface.

The system should distinguish:

- what was observed
- what it meant
- what created unresolved tension
- what became a vow
- what endured long enough to count as identity

The practical consequence is that write seams such as `MemoryWriteGateway` should be treated as admissibility boundaries, not as final identity writers.

Gateway acceptance decides whether something may enter memory at all.

Promotion logic decides what kind of self-forming memory it is allowed to become.
