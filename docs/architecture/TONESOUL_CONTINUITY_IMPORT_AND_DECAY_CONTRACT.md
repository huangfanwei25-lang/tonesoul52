# ToneSoul Continuity Import And Decay Contract

> Status: architectural discipline contract
> Purpose: define what a receiving agent may import directly, what remains advisory, what decays, and what requires explicit re-confirmation — per continuity surface
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (shared surface semantics)
>   - docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md (subject snapshot boundaries)
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md (dossier shape)
>   - docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md (readiness states)
>   - docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md (plan delta discipline)
>   - docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md (lifecycle lanes)
>   - docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md (receiver obligations)
> Scope: 16 continuity surfaces classified by import posture, receiver obligation, and decay posture

## How To Use This Document

If you are an AI agent that just received continuity material (from session-start bundle, packet, compaction, or any shared surface):

1. Find the surface in the **Import Classification Table**
2. Check the **import posture** to know what you may do with it
3. Check the **receiver obligation** to know what you must do
4. Check the **decay posture** to know how long the information is reliable
5. Check the **failure mode** to know what goes wrong if you over-import or under-import

## Why This Document Exists

ToneSoul now has ~16 continuity-bearing surfaces. Each surface was designed with a sender in mind: what shape should the data have, how should it be produced, where should it be stored. What was not always specified is the *receiver* side: what may a later agent actually do with this data?

Without receiver-side rules, two opposite failures emerge:

1. **Over-import**: a later agent reads a compaction's `carry_forward` and treats it as canonical truth. A subject snapshot's `decision_preferences` gets applied as if it were a governance directive. An expired claim gets treated as still active.

2. **Under-import**: a later agent ignores the delta feed entirely and re-discovers context that a previous agent already externalized. A checkpoint with clear `pending_paths` gets skipped, causing duplicate work. A subject snapshot is never read because the agent does not know it exists.

This contract defines the middle ground: import what is reliable, note what is advisory, ignore what has decayed, and re-confirm what is ambiguous.

## Compressed Thesis

Not everything that was written for you is true. Not everything that has decayed is worthless. Import posture tells you what to trust. Receiver obligation tells you what to do. Decay posture tells you when to stop trusting. Together they prevent both credulous over-import and wasteful under-import.

---

## Definitions

### Import Posture

| Posture | Meaning | Receiver Action |
|---|---|---|
| `directly_importable` | The surface's content is operationally reliable at read time. The receiver may act on it without re-verification. | Read and apply to current work planning |
| `advisory` | The surface's content is informative but non-authoritative. The receiver should consider it but must not treat it as canonical truth. | Read and factor into judgment; do not treat as hard constraint |
| `ephemeral_until_acked` | The surface exists briefly and becomes stale if not explicitly acknowledged. The receiver must `--ack` or the content is no longer considered current. | Acknowledge if relevant; ignore if stale |
| `manual_confirmation` | The surface's content may only be acted upon after explicit human or operator confirmation. | Read but do not act until confirmed |

### Receiver Obligation

| Obligation | Meaning |
|---|---|
| `must_read` | The receiver is expected to read this surface as part of session-start or task-start. Skipping it risks operational misalignment. |
| `should_consider` | The receiver should read this if available. Skipping it loses context but does not break governance. |
| `must_not_promote` | The receiver may read this but must not promote its content into canonical truth, durable identity, or hard runtime constraints without additional evidence. |

### Decay Posture

| Posture | Expected Lifetime | Examples |
|---|---|---|
| `fast` | Minutes to 2 hours | Active claims (30 min TTL), perspectives (2 hour TTL), session-scoped readiness |
| `medium` | 1-7 days | Compactions (7 day TTL), checkpoints, delta feed entries |
| `slow` | 7-30 days | Subject snapshots (30 day TTL), council dossiers, recent traces |
| `operator_only` | No automatic decay | Governance posture, canonical traces, AXIOMS.json — only human/operator may retire |

---

## Import Classification Table

| # | Surface | Import Posture | Receiver Obligation | Decay Posture | Failure If Over-Imported | Failure If Under-Imported |
|---|---|---|---|---|---|---|
| 1 | `posture` (packet governance posture: soul_integral, baseline_drift, vows, tensions) | `directly_importable` | `must_read` | `operator_only` | None — this is canonical truth | Agent operates without governance context; may violate active vows |
| 2 | `session-start readiness` (pass / needs_clarification / blocked) | `directly_importable` | `must_read` | `fast` (session-scoped) | None — readiness is computed fresh each session | Agent starts work when blocked or when clarification is needed |
| 3 | `claims` (active task claims) | `directly_importable` | `must_read` | `fast` (30 min TTL) | Expired claim treated as active → false collision avoidance | Agent claims same task another agent owns → collision |
| 4 | `delta_feed` (changes since last visit) | `directly_importable` | `must_read` | `medium` (entries age out) | Stale delta entries treated as current → outdated context | Agent misses recent changes by other agents |
| 5 | `r_memory_packet` (aggregated hot-state) | `advisory` | `must_read` | `medium` (refreshed each read) | Packet snapshot treated as complete truth → ignores what packet omits | Agent has no operational context; works blind |
| 6 | `r_memory_packet.operator_guidance` | `advisory` | `should_consider` | `medium` | Guidance treated as hard directive → over-constrains agent | Agent ignores useful operational hints |
| 7 | `project_memory_summary` | `advisory` | `should_consider` | `medium` | Summary treated as current truth → may be stale | Agent lacks project-level context |
| 8 | `compactions` | `advisory` | `should_consider` | `medium` (7 day TTL) | Compaction carry_forward treated as canonical → false authority | Agent rediscovers context a previous agent already externalized |
| 9 | `checkpoints` | `advisory` | `should_consider` | `medium` | Checkpoint pending_paths treated as current work plan → stale resumption | Agent duplicates work another agent checkpointed |
| 10 | `perspectives` | `ephemeral_until_acked` | `should_consider` | `fast` (2 hour TTL) | Perspective stance treated as durable position → it was temporary | Agent ignores provisional stances that could inform current work |
| 11 | `subject_snapshot` | `advisory` | `should_consider` | `slow` (30 day TTL) | Snapshot treated as canonical identity → it is non-canonical | Agent ignores durable working identity and reinvents preferences |
| 12 | `subject_refresh` recommendations | `advisory` | `must_not_promote` | `medium` | Refresh recommendation auto-applied → identity over-promotion | Agent ignores refresh signals → under-promotion of stable patterns |
| 13 | `council_dossier` | `advisory` | `should_consider` | `slow` | Dossier verdict treated as permanent law → it was one decision | Agent ignores past council decisions → repeats resolved deliberations |
| 14 | `council_dossier_summary` (in compaction) | `advisory` | `should_consider` | `medium` (compaction TTL) | Compressed dossier treated as full dossier → dissent may be lost | Agent lacks council context for follow-up decisions |
| 15 | `recent_traces` (session history) | `advisory` | `should_consider` | `slow` | Historical trace treated as current operational state → staleness | Agent lacks historical context for pattern detection |
| 16 | `router_telemetry` | `advisory` | `must_not_promote` | `fast` | Routing statistics treated as decision preferences → false pattern | Agent ignores misroute signals that could improve routing |
| 17 | `session-end resumability handoff` | `advisory` | `should_consider` | `medium` | Handoff treated as binding work plan → original agent's intent may have changed | Next agent cannot resume efficiently |

---

## High-Risk Over-Import Patterns

These are the most dangerous cases where a receiver might over-trust continuity material:

### 1. Compaction carry_forward → canonical truth

A compaction's `carry_forward` list is a *memo*, not a *directive*. It says "the previous agent thought these items should carry forward." It does not say "these items are true" or "you must act on these items."

**Correct**: read carry_forward, verify each item against current state, act only on items that are still relevant.
**Incorrect**: import all carry_forward items as task objectives without checking whether they are still valid.

### 2. Subject snapshot → governance authority

A subject snapshot captures durable working identity (preferences, routines, boundaries). It is non-canonical. It does not have the authority of packet `posture` or `AXIOMS.json`.

**Correct**: treat snapshot as "this is what the previous agent found useful" — a suggestion, not a rule.
**Incorrect**: treat `stable_vows` from a snapshot as equivalent to canonical vows in governance state.

### 3. Expired claim → active ownership

Claims have a 30-minute TTL. A claim that was active when the packet was generated may have expired by the time the receiver reads it.

**Correct**: check claim TTL before treating a claim as active.
**Incorrect**: avoid a task because a claim existed in the last packet read, without checking expiry.

### 4. Council dossier → permanent law

A council dossier records one deliberation's outcome. The Critic's objection was valid at that moment, with that evidence, for that draft. It is not a permanent legal precedent.

**Correct**: use dossier as context for similar decisions; re-deliberate if circumstances changed.
**Incorrect**: cite a previous dossier verdict as binding authority for a new, different task.

### 5. Perspective stance → durable position

A perspective has a 2-hour TTL. It captures a provisional stance during active work. After TTL expiry, the stance is no longer current.

**Correct**: if perspective is within TTL, consider the stance. If expired, treat as historical.
**Incorrect**: cite an expired perspective as "the previous agent's position" without noting it has decayed.

---

## High-Risk Under-Import Patterns

These are cases where receivers commonly ignore valuable continuity:

### 1. Delta feed ignored → duplicate discovery

The delta feed shows what changed since the receiver's last visit. Ignoring it means the receiver may spend time discovering changes that are already documented.

### 2. Checkpoint pending_paths ignored → duplicate work

A checkpoint's `pending_paths` lists work that was started but not finished. Ignoring it means the receiver may restart work from scratch.

### 3. Subject snapshot ignored → preference re-discovery

If a subject snapshot exists with `verified_routines`, ignoring it means the receiver will rediscover those routines through trial and error — wasting time and potentially choosing different (worse) approaches.

---

## Decay And Freshness Rules

### Rule 1: Check TTL Before Importing

For surfaces with explicit TTL (claims: 30 min, perspectives: 2 hours, compactions: 7 days, subject snapshots: 30 days), check whether the TTL has expired before treating the content as current.

### Rule 2: Packet Is A Snapshot, Not A Stream

`r_memory_packet` is computed at read time. It reflects state at that moment. If significant time passes between reading the packet and acting on it, re-read the packet.

### Rule 3: Canonical Surfaces Do Not Decay

`posture`, `canonical traces` (Aegis-sealed), and `AXIOMS.json` do not decay automatically. They change only through canonical commit or human action. A receiver may always trust their current values.

### Rule 4: Advisory Surfaces Decay Toward Staleness, Not Toward Falsehood

A 5-day-old compaction is stale — its context may no longer apply. But it is not *false*. It accurately describes what the previous agent knew and did at that time. The receiver should discount its operational relevance, not its honesty.

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines the surfaces this contract classifies; this contract adds receiver-side rules |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Defines which source surfaces may refresh subject_snapshot; this contract adds import discipline |
| `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` | Defines dossier shape; this contract defines how a receiver should import a dossier |
| `TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md` | Readiness gate reads continuity surfaces; this contract clarifies what readiness may import |
| `TONESOUL_PLAN_DELTA_CONTRACT.md` | Plan delta decisions use compaction and checkpoint data; this contract clarifies their import posture |
| `TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md` | Companion: this contract classifies surfaces; receiver contract classifies agent behavior |
| `TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md` | Companion: this contract classifies import; lifecycle map organizes surfaces into temporal lanes |

---

## Canonical Handoff Line

Continuity is not telepathy. What a previous agent externalized is valuable — but it is valuable as context, not as command. Import what is reliable, note what is advisory, check what has decayed, and re-confirm what is ambiguous. The receiver's job is not to blindly inherit; it is to import with discipline.
