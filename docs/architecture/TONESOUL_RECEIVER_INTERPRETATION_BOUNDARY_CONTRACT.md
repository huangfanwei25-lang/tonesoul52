# ToneSoul Receiver Interpretation Boundary Contract

> Status: architectural discipline contract
> Purpose: define what a receiving agent is and is not allowed to do after reading continuity surfaces — focusing on agent behavior rather than surface classification
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md (surface classification)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (shared surface semantics)
>   - docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md (opacity classification)
>   - docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md (identity refresh boundaries)
> Scope: 3 receiver actions, 7 interpretation rules, 5 silent-override hazards

## How To Use This Document

If you are an AI agent that has just read a continuity surface (packet, compaction, checkpoint, snapshot, dossier, delta feed):

1. Determine which **receiver action** you are performing: `ack`, `apply`, or `promote`
2. Check the **Interpretation Rules** to know what you may and may not infer
3. Check the **Silent-Override Hazards** to avoid common dangerous misinterpretations

## Why This Document Exists

The Continuity Import And Decay Contract classifies *surfaces*: what each surface's import posture, decay rate, and risk profile looks like. This companion contract classifies *agent behavior*: what a receiving agent is allowed to do after reading those surfaces.

The distinction matters because the same surface can be handled three different ways:

- **ack**: I read it and noted it. My cursor advanced. I may or may not use it.
- **apply**: I read it and used it to influence my current work — my planning, exploration, or decision-making.
- **promote**: I read it and elevated it into a more durable or more authoritative surface — e.g., from compaction into task.md, or from advisory guidance into a hard constraint.

The three actions have very different risk profiles. `ack` is always safe. `apply` is usually safe for advisory surfaces. `promote` is dangerous without explicit authorization.

## Compressed Thesis

Reading is not importing. Importing is not applying. Applying is not promoting. A receiver that confuses these three actions will either over-trust stale context (treating every compaction as a work order) or under-use good context (reading a checkpoint but ignoring its pending paths). The boundary is in what the receiver *does* with what it reads, not in the surface itself.

---

## Three Receiver Actions

### ack (acknowledge)

**What it does**: the receiver has read the surface. The observer cursor advances (`--ack`). The receiver is aware of the content but has not committed to using it.

**When to use**: always. Every continuity surface should be acknowledged when read. Ack is the minimum receiver action.

**What it does NOT do**: ack does not mean agreement, adoption, or intent to act. It means "I saw this."

**Runtime surface**: `ts:observer_cursors:{agent_id}` — the `--ack` flag on packet read.

### apply (influence current work)

**What it does**: the receiver uses the surface's content to influence its current work. This may mean adjusting exploration depth, considering a carry_forward item, noting a previous agent's approach, or factoring a dossier verdict into a similar decision.

**When to use**: for `directly_importable` and `advisory` surfaces that are within their TTL and relevant to the current task.

**Constraints**:
- Apply does not change canonical state. It influences the receiver's judgment, not the governance posture.
- Apply should be recorded: if the receiver acted on a compaction's carry_forward, the receiver's own compaction should note "applied carry_forward from session X."
- Apply is reversible: the receiver may later decide the applied context was stale and discard it.

### promote (elevate to higher authority)

**What it does**: the receiver takes content from a non-canonical surface and moves it into a more durable or more authoritative surface. Examples:

- Compaction carry_forward item → new Phase objective in task.md
- Subject snapshot decision_preference → hard coding convention
- Council dossier minority_report → new governance constraint
- Checkpoint pending_path → committed work plan

**When to use**: rarely, and only with explicit justification.

**Constraints**:
- Promote from `advisory` to `canonical` requires human confirmation (per Subject Refresh Boundary Contract and Plan Delta Contract)
- Promote from `ephemeral` to `advisory` is acceptable with evidence (e.g., a repeated checkpoint pattern becoming a compaction carry_forward)
- Promote must be recorded: the receiving agent's compaction or session trace must note what was promoted and why

**Hard rule**: a receiver must never silently promote. Silent promotion is the most dangerous continuity failure mode.

---

## Interpretation Rules

### Rule 1: ack ≠ agree

Acknowledging a continuity surface does not mean the receiver agrees with its content, endorses the previous agent's approach, or commits to continuing the previous agent's work. It means the receiver has seen it.

If the receiver reads a compaction whose `next_action` says "implement feature X" and decides feature X is wrong, the receiver should note the disagreement in its own compaction — not silently ignore the previous agent's work.

### Rule 2: apply ≠ adopt

Applying a continuity surface to current work means the surface influenced the receiver's judgment. It does not mean the receiver adopted the surface's content wholesale.

**Correct**: "I read the previous checkpoint and noted its pending_paths. I chose to continue path A and defer path B based on current evidence."
**Incorrect**: "I imported all pending_paths from the checkpoint as my work plan."

### Rule 3: promote requires explicit justification

Every promotion must answer: *why is this content reliable enough to move to a more durable or authoritative surface?*

Acceptable justifications:
- The content has been confirmed by multiple independent sources (compaction + checkpoint + trace all agree)
- The content has been explicitly authorized by a human or operator
- The content describes a pattern that has repeated across 3+ sessions

Unacceptable justifications:
- "The previous agent said so" (one agent's compaction is not sufficient for promotion)
- "It makes sense" (narrative coherence is not evidence — per Observable Shell Opacity Contract)
- "It was in the packet" (the packet is a snapshot, not an authority)

### Rule 4: stale content should be discounted, not discarded

A continuity surface that has aged past its typical freshness window is stale but not necessarily wrong. The receiver should discount its operational relevance (it may no longer apply) without discarding its historical value (it accurately describes what was true at production time).

**Correct**: "This 5-day-old compaction's carry_forward may no longer apply, but its description of the approach taken is historically accurate."
**Incorrect**: "This compaction is old, so I will ignore it entirely."

### Rule 5: absence of a surface is not evidence of absence

If the receiver reads a packet and finds no subject snapshot, this means no agent has written a snapshot — not that there is no durable working identity. The receiver should not infer "no preferences exist" from "no snapshot was written."

Similarly, if no compaction exists, this means the previous agent did not write one — not that the previous session was uneventful.

### Rule 6: conflicting surfaces require judgment, not precedence

If two continuity surfaces conflict (e.g., a compaction says "approach X is best" and a checkpoint says "approach Y is better"), the receiver must exercise judgment rather than applying a precedence rule.

Factors to consider:
- Which surface is fresher (closer to current time)?
- Which surface has more evidence (evidence_refs, concrete next_action)?
- Which surface was written by the agent working on the same task?

If the conflict cannot be resolved, this is a `needs_clarification` condition per the Task Track & Readiness Contract.

### Rule 7: receiver must not fill gaps with inference

If a continuity surface is missing a field (e.g., compaction has no `next_action`), the receiver must not infer what the next action should be from the compaction's summary. Missing fields mean the previous agent did not externalize that information — the receiver should treat the gap as a gap, not as a puzzle to solve.

This is the receiver-side equivalent of the `[資料不足]` principle from the Prompt Discipline Skeleton.

---

## Silent-Override Hazards

These are the most dangerous cases where a receiver might silently override governance boundaries through continuity import:

### Hazard 1: Compaction carry_forward → task.md objective

A carry_forward item is a memo from one agent to the next. It is not an authorized work objective. If the receiver writes a carry_forward item directly into task.md as a Phase objective, it bypasses the Plan Delta Contract's rules for who may define success criteria.

**Prevention**: carry_forward items that deserve to become Phase objectives must go through the `fork new phase` or `append delta` process, with explicit human authorization for success criteria changes.

### Hazard 2: Subject snapshot preference → coding convention

A subject snapshot's `decision_preferences` captures what one agent found useful. If the receiver treats this as a binding coding convention (e.g., "always use pattern X"), it has promoted non-canonical preference into de facto governance.

**Prevention**: coding conventions should be documented in canonical docs (CLAUDE.md, AI_REFERENCE.md), not silently imported from subject snapshots.

### Hazard 3: Council dossier verdict → permanent precedent

A dossier records one deliberation. If the receiver cites a previous dossier verdict as binding precedent for a new, different task, it has promoted a single decision into case law without human authorization.

**Prevention**: dossier verdicts inform but do not bind. Re-deliberate if circumstances have changed.

### Hazard 4: Operator guidance → hard constraint

`r_memory_packet.operator_guidance` is advisory. If the receiver treats it as a P0 hard constraint, it has promoted advisory content into governance authority.

**Prevention**: operator guidance influences planning; it does not override explicit task objectives or human instructions.

### Hazard 5: Expired perspective → current stance

A perspective with expired TTL is historical. If the receiver attributes it to the previous agent as a current position ("Agent X believes Y"), it has promoted a decayed stance into a live claim.

**Prevention**: always check TTL. Expired perspectives are "Agent X believed Y at time T," not "Agent X believes Y."

---

## Receiver Action Decision Matrix

| Surface Import Posture | ack | apply | promote |
|---|---|---|---|
| `directly_importable` | Always | Safe — content is operationally reliable | Only with explicit justification and human confirmation |
| `advisory` | Always | Safe — content informs judgment | Only with repeated evidence + human confirmation |
| `ephemeral_until_acked` | Required for surface to be considered | Safe if within TTL | Never — ephemeral content must not be promoted |
| `manual_confirmation` | Always | Only after human confirmation | Only after human confirmation + evidence |

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md` | Companion: classifies surfaces; this contract classifies receiver behavior |
| `TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md` | Companion: organizes surfaces by lifetime; this contract governs what receivers do within each lifetime |
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines the surfaces and protocols; this contract adds receiver-side interpretation rules |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Rule 3 (promote requires justification) aligns with "narrative coherence is not evidence" |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Promotion from advisory to durable identity follows the refresh boundary rules |
| `TONESOUL_PLAN_DELTA_CONTRACT.md` | Promotion from carry_forward to task.md follows plan delta rules |
| `TONESOUL_PROMPT_DISCIPLINE_SKELETON.md` | Rule 7 (do not fill gaps with inference) aligns with `[資料不足]` principle |

---

## Canonical Handoff Line

What you read is not what you know. What you apply is not what you adopt. What you promote is not what you may promote silently. The receiver's discipline is in the gaps between these actions: reading without over-trusting, applying without over-committing, and never promoting without explicit evidence and authorization.
