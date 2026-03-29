# ToneSoul Continuity Surface Lifecycle Map

> Status: architectural topology document
> Purpose: organize continuity surfaces into lifecycle lanes with explicit lifetime, refresh triggers, decay triggers, and receiver behavior — so later agents and Codex can manage continuity as a system rather than a flat list
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md (import posture)
>   - docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md (receiver actions)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (surface definitions)
> Scope: 5 lifecycle lanes, 17 continuity surfaces mapped

## How To Read This Document

Each lifecycle lane groups surfaces that share a similar expected lifetime, refresh cadence, and receiver behavior. Lanes are ordered from shortest-lived to longest-lived.

---

## Lane 1: Immediate Coordination

**Expected lifetime**: minutes to 2 hours

**Purpose**: real-time coordination between concurrently active agents or between an agent and its immediate next session.

**Characteristic**: these surfaces exist to prevent collisions and coordinate work *right now*. They are operationally critical but inherently transient.

| Surface | TTL | Refresh Trigger | Decay Trigger | Receiver Behavior |
|---|---|---|---|---|
| `claims` (task claims) | 30 minutes | Agent renews claim or takes new claim | TTL expiry; agent releases claim | `must_read`: check before starting overlapping work |
| `perspectives` (provisional stance) | 2 hours | Agent writes new perspective | TTL expiry | `should_consider` if within TTL; ignore if expired |
| `session-start readiness` | Session-scoped | Recomputed each session start | Session ends | `must_read`: determines whether work may begin |
| `router_telemetry` | Session-scoped | Accumulated during session | Next session start | `should_consider` for routing quality; `must_not_promote` into preferences |

**Lane behavior**: surfaces in this lane should be re-read before critical decisions. A claim that was valid 20 minutes ago may have expired. A perspective that was written an hour ago may no longer reflect the agent's stance.

**Failure mode if treated as durable**: expired coordination signals cause false collision avoidance (claims) or stale stance attribution (perspectives).

---

## Lane 2: Bounded Handoff

**Expected lifetime**: 1-7 days

**Purpose**: carry context from one agent session to the next. Designed to survive a context reset, a terminal close, or a model switch — but not to persist indefinitely.

**Characteristic**: these surfaces are the primary handoff mechanism in ToneSoul. They bridge the gap between sessions without claiming canonical authority.

| Surface | TTL | Refresh Trigger | Decay Trigger | Receiver Behavior |
|---|---|---|---|---|
| `compactions` | 7 days | Agent writes new compaction | TTL expiry; superseded by newer compaction | `should_consider`: read carry_forward, next_action, pending_paths |
| `checkpoints` | 7 days (implicit) | Agent writes checkpoint during work | Superseded by newer checkpoint or compaction | `should_consider`: read pending_paths for resumability |
| `session-end resumability handoff` | 7 days (aligned with compaction) | End-session bundle writes it | Next session's start-session bundle reads it | `should_consider`: primary resumability surface |
| `delta_feed` (recent changes) | Entries age out over days | New entries added by any agent's writes | Older entries fall off the feed | `must_read`: know what changed since last visit |
| `r_memory_packet` | Refreshed each read | Recomputed on each `GET /packet` or script run | Stale if not re-read | `must_read`: primary operational context surface |
| `r_memory_packet.operator_guidance` | Refreshed with packet | Recomputed with packet | Stale if not re-read | `should_consider`: advisory hints for current task |
| `project_memory_summary` | Refreshed with packet | Recomputed with packet | Stale if not re-read | `should_consider`: aggregated project context |
| `council_dossier_summary` (in compaction) | 7 days (compaction TTL) | Written with compaction | Compaction TTL expiry | `should_consider`: compressed verdict for follow-up decisions |

**Lane behavior**: surfaces in this lane are the workhorses of multi-agent continuity. They should be read at session start and factored into planning. They should NOT be promoted into task.md or governance posture without explicit human authorization.

**Failure mode if treated as canonical**: compaction carry_forward becomes de facto work plan without human approval. Checkpoint pending_paths become committed objectives without review.

**Failure mode if ignored**: agent works blind, re-discovers context, duplicates effort.

---

## Lane 3: Working Identity

**Expected lifetime**: 7-30 days

**Purpose**: preserve durable but non-canonical working identity across many sessions. Slower-changing than handoff surfaces, but not permanent.

**Characteristic**: these surfaces describe *who the agent is operationally* — its preferences, routines, and active concerns. They are explicitly non-canonical: they do not have the authority of governance posture or axioms.

| Surface | TTL | Refresh Trigger | Decay Trigger | Receiver Behavior |
|---|---|---|---|---|
| `subject_snapshot` | 30 days | Agent writes new snapshot when durable identity changes | TTL expiry; superseded by newer snapshot | `should_consider`: inherit stable preferences and routines; `must_not_promote` into canonical identity |
| `subject_refresh` recommendations | Refreshed with packet | Recomputed when packet includes subject refresh summary | Stale if not re-read | `must_not_promote`: advisory only; never auto-apply to snapshot fields |

**Lane behavior**: working identity surfaces should be read when starting a task that benefits from continuity (preferences, routines, boundaries). They should be treated as "this is what previous agents found useful" — a starting point, not a requirement.

**Failure mode if promoted**: snapshot preferences become hard conventions. Snapshot vows are treated as canonical governance vows. Temporary patterns get locked into durable identity.

**Failure mode if ignored**: agent reinvents preferences through trial and error. Verified routines are rediscovered. Active threads are re-explored from scratch.

---

## Lane 4: Replay And Review Memory

**Expected lifetime**: weeks to months (effectively permanent until archived)

**Purpose**: provide historical context for review, audit, and pattern detection. Not meant for operational import — meant for understanding what happened and why.

**Characteristic**: these surfaces are backward-looking. They describe what was decided, what was observed, what was committed. They are inputs to review and learning, not to operational planning.

| Surface | TTL | Refresh Trigger | Decay Trigger | Receiver Behavior |
|---|---|---|---|---|
| `council_dossier` (full) | No automatic expiry | Written after each council deliberation | Only if explicitly archived | `should_consider` for similar decisions; do not treat as binding precedent |
| `recent_traces` (session history) | No automatic expiry (Aegis-sealed) | New trace added per session | Only if explicitly archived by script | `should_consider` for pattern detection; do not re-litigate past sessions |

**Lane behavior**: replay surfaces are most useful when the receiver is working on a task similar to a previous one. They provide context ("what did the council decide last time about schema changes?") but not authority ("the council decided X, therefore X is still the rule").

**Failure mode if over-imported**: historical decisions become permanent precedents. Past trace patterns become assumed current state.

**Failure mode if ignored**: agent lacks historical context for recurring decisions. Patterns that emerged across sessions are invisible.

---

## Lane 5: Canonical Foundation

**Expected lifetime**: permanent (no automatic decay)

**Purpose**: define the governance foundation that all other lanes operate within. These surfaces change only through canonical commit or explicit human action.

**Characteristic**: these surfaces are the only `directly_importable` + `operator_only` combination. They are authoritative, they do not decay, and they define the rules that all other lanes follow.

| Surface | TTL | Refresh Trigger | Decay Trigger | Receiver Behavior |
|---|---|---|---|---|
| `posture` (packet governance posture: soul_integral, vows, tensions, drift) | No expiry | Canonical commit | Human/operator action only | `must_read`: defines current governance context |
| `AXIOMS.json` | No expiry | Human edit only | Never (constitutionally protected) | `must_read`: defines inviolable governance rules |
| `canonical traces` (Aegis-sealed) | No expiry | Canonical commit appends | Never (append-only, Aegis-protected) | `should_consider` for audit; immutable historical record |

**Lane behavior**: canonical surfaces are the ground truth. Every other lane operates under the constraints these surfaces define. A receiver may always trust the current values of canonical surfaces.

**Failure mode if not read**: agent operates without governance context, may violate active vows or axioms.

**Failure mode if not respected**: governance drift — the system claims to have governance but agents ignore it.

---

## Visual Lifecycle Map

```
Lifetime:  minutes        hours         days          weeks         permanent
           │              │             │             │             │
Lane 1:    ├──claims──────┤             │             │             │
           ├──perspectives┤             │             │             │
           ├──readiness───┤             │             │             │
           ├──telemetry───┤             │             │             │
           │              │             │             │             │
Lane 2:    │              ├──compaction─┤             │             │
           │              ├──checkpoint─┤             │             │
           │              ├──delta_feed─┤             │             │
           │              ├──packet─────┤             │             │
           │              ├──handoff────┤             │             │
           │              │             │             │             │
Lane 3:    │              │             ├──snapshot───┤             │
           │              │             ├──refresh────┤             │
           │              │             │             │             │
Lane 4:    │              │             │             ├──dossier────┤
           │              │             │             ├──traces─────┤
           │              │             │             │             │
Lane 5:    │              │             │             │             ├──governance
           │              │             │             │             ├──axioms
           │              │             │             │             ├──aegis chain
```

---

## Lane Interaction Rules

### Rule 1: Lower lanes may read higher lanes, not vice versa

Bounded handoff (Lane 2) may reference canonical foundation (Lane 5). Canonical foundation does not reference bounded handoff. The direction of authority flows from permanent to temporary.

### Rule 2: Promotion crosses lane boundaries

When content moves from Lane 2 (handoff) to Lane 3 (working identity) or Lane 5 (canonical), it is a promotion. Promotions require explicit justification per the Receiver Interpretation Boundary Contract.

### Rule 3: Decay is natural within a lane

Content that ages past its lane's expected lifetime is stale. This is normal, not a failure. Stale content should be discounted, not purged — it retains historical value.

### Rule 4: Each lane has one primary receiver action

| Lane | Primary Receiver Action |
|---|---|
| Immediate Coordination | `ack` + `apply` (coordinate now) |
| Bounded Handoff | `apply` (resume and continue) |
| Working Identity | `apply` cautiously (inherit but do not promote) |
| Replay And Review | `ack` + selectively `apply` (learn from history) |
| Canonical Foundation | `must_read` (operate within bounds) |

---

## Canonical Handoff Line

Continuity surfaces are not one flat list — they are five lanes with different lifetimes, different receiver obligations, and different promotion risks. Immediate coordination expires in minutes. Bounded handoff expires in days. Working identity lasts weeks. Replay memory lasts months. Canonical foundation lasts forever. Know which lane you are reading from, and act accordingly.
