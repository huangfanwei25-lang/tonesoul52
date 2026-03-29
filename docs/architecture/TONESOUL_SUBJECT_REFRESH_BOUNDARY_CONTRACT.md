# ToneSoul Subject Refresh Boundary Contract

> Status: architectural boundary contract
> Purpose: classify which source surfaces may refresh which subject_snapshot field families, and under what minimum evidence standard
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md (field lane assignments)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (source surface semantics)
>   - docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md (term authority context)
>   - spec/governance/subject_snapshot_v1.schema.json (schema definition)
>   - tonesoul/runtime_adapter.py (_build_subject_refresh_summary, lines 1040-1230)
> Scope: 10 source surfaces x 7 target field families = 70 boundary decisions

## How To Use This Document

If you are an AI agent or heuristic considering whether to refresh a subject_snapshot field:

1. Identify the **source surface** providing the evidence (e.g., compaction, checkpoint, perspective)
2. Identify the **target field family** you want to refresh (e.g., active_threads, stable_vows)
3. Look up the intersection in the Boundary Matrix
4. Check the **allowed action** — if it says `must not promote`, stop
5. Check the **minimum evidence shape** — if your evidence is weaker, do not proceed
6. Check the **risk** column — understand what goes wrong if you get this wrong

## Why This Document Exists

ToneSoul's `subject_snapshot` stores an agent's durable working identity: stable vows, behavioral boundaries, decision preferences, verified routines, and active work threads. This identity persists for up to 30 days and shapes how later agents approach their work.

The system now has ten distinct coordination surfaces that generate signals about what the agent is, what it does, and what it cares about. Without a boundary contract, two failure modes emerge:

1. **Over-promotion**: every hot-state signal starts rewriting identity. A 30-minute task claim becomes a permanent vow. A 2-hour perspective tension becomes a durable boundary. Identity inflates until it means nothing.

2. **Under-promotion**: durable patterns never graduate beyond ephemeral compactions and are repeatedly rediscovered. The agent forgets its verified routines every time the compaction TTL expires. Identity never stabilizes.

This contract draws the line between the two by classifying every source-field combination into an explicit allowed action with a minimum evidence requirement.

## Compressed Thesis

Not every signal is strong enough to shape who you are. Task claims are ownership, not selfhood. Perspectives are temporary stances, not permanent boundaries. Checkpoint cadence is resumability, not identity. Only compaction-backed or repeat-pattern evidence may refresh working identity fields, and constitutional commitments (vows, boundaries) require human confirmation regardless of evidence strength.

## Definitions

### Source Surfaces

| # | Surface | TTL | Authority | One-Line Description |
|---|---------|-----|-----------|---------------------|
| 1 | `subject_snapshot` | 30 days | non-canonical | Durable working identity snapshot; the thing being refreshed |
| 2 | `checkpoint` | 1 day | non-canonical | Mid-session resumability point |
| 3 | `compaction` | 7 days | non-canonical | Bounded cross-session handoff summary with carry_forward |
| 4 | `perspective` | 2 hours | non-canonical | Per-agent temporary stance, tensions, and proposed changes |
| 5 | `claim` | 30 minutes | advisory | Task ownership signal for multi-terminal coordination |
| 6 | `governance_posture` | persistent | **canonical** | Soul integral, vows, tensions, drift — the source of governance truth |
| 7 | `risk_posture` | computed | derived | Runtime risk score and level, embedded in posture |
| 8 | `router_telemetry` | 7 days | observational | Routing events, dominant surface, misroute signals |
| 9 | `recent_traces` | persistent | **canonical** | Append-only session traces, Aegis-protected |
| 10 | `delta_feed` | ephemeral | derived | Since-last-seen cursor differences; an observation window, not raw evidence |

### Target Field Families

| # | Field Family | Lane | In Schema? |
|---|-------------|------|-----------|
| 1 | `stable_vows` | Durable Identity | Yes |
| 2 | `durable_boundaries` | Durable Identity | Yes |
| 3 | `decision_preferences` | Refreshable Working Identity | Yes |
| 4 | `verified_routines` | Refreshable Working Identity | Yes |
| 5 | `active_threads` | Refreshable Working Identity | Yes |
| 6 | `carry-forward items` | Temporary Carry-Forward | No |
| 7 | `anti-patterns` | Temporary Carry-Forward | No |

Lane definitions are in `TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md`.

### Allowed Actions

| Action | Code | Meaning |
|--------|------|---------|
| May refresh directly | **D** | The source may write this field without additional confirmation |
| May influence but not promote | **I** | The source may suggest a change, but a human or operator must confirm |
| Manual / operator-only | **M** | Only deliberate human or operator action may change this field from this source |
| Must not promote | **X** | This source must never change this field, regardless of evidence |

### Minimum Evidence Shapes

| Shape | Meaning |
|-------|---------|
| `single_signal` | One observation from the source surface |
| `repeat_pattern` | The same pattern observed across >= 2 sessions, checkpoints, or compactions |
| `compaction-backed` | At least one compaction newer than the latest snapshot confirms the pattern |
| `subject-snapshot-only` | Only an existing snapshot may serve as baseline (self-referential inheritance) |
| `human_confirmation` | A human operator must explicitly approve the change |

---

## The Boundary Matrix

Each cell shows: **Action** / **Evidence Shape**.

### Durable Identity Fields

| Source | `stable_vows` | `durable_boundaries` |
|--------|--------------|---------------------|
| subject_snapshot | M / human_confirmation | M / human_confirmation |
| checkpoint | X / — | X / — |
| compaction | X / — | I / compaction-backed |
| perspective | X / — | X / — |
| claim | X / — | X / — |
| governance_posture | M / human_confirmation | M / human_confirmation |
| risk_posture | X / — | I / repeat_pattern |
| router_telemetry | X / — | X / — |
| recent_traces | X / — | X / — |
| delta_feed | X / — | X / — |

**Reading guide**: stable_vows are the most protected field. No hot-state surface can touch them. Even governance_posture (the canonical source of vows) requires manual operator action to sync into the snapshot, because the direction is canonical-to-snapshot, not automatic. durable_boundaries are almost as protected, but compaction-backed evidence and repeated risk elevation may *influence* (not directly change) them.

### Refreshable Working Identity Fields

| Source | `decision_preferences` | `verified_routines` | `active_threads` |
|--------|----------------------|--------------------|--------------------|
| subject_snapshot | D / subject-snapshot-only | D / subject-snapshot-only | D / subject-snapshot-only |
| checkpoint | X / — | I / repeat_pattern | D / repeat_pattern (>= 2) |
| compaction | I / compaction-backed | I / compaction-backed | D / compaction-backed |
| perspective | I / single_signal | X / — | I / single_signal |
| claim | X / — | X / — | I / single_signal |
| governance_posture | I / repeat_pattern | X / — | X / — |
| risk_posture | I / repeat_pattern | X / — | X / — |
| router_telemetry | I / repeat_pattern | I / repeat_pattern | I / single_signal |
| recent_traces | I / repeat_pattern | I / repeat_pattern | I / single_signal |
| delta_feed | X / — | X / — | I / single_signal |

**Reading guide**: active_threads is the most refreshable field. Compaction-backed evidence or >= 2 newer checkpoints may directly refresh it. This aligns with `_build_subject_refresh_summary()` lines 1116-1133. decision_preferences may be influenced by routing behavior and risk patterns but never directly promoted from a single ephemeral source. verified_routines require the strongest evidence among the three: compaction + checkpoint cadence must both be visible to even influence them.

### Temporary Carry-Forward Fields

| Source | `carry-forward items` | `anti-patterns` |
|--------|-----------------------|-----------------|
| subject_snapshot | D / subject-snapshot-only | D / subject-snapshot-only |
| checkpoint | I / single_signal | I / single_signal |
| compaction | D / compaction-backed | I / compaction-backed |
| perspective | X / — | I / single_signal |
| claim | X / — | X / — |
| governance_posture | X / — | I / compaction-backed |
| risk_posture | X / — | I / repeat_pattern |
| router_telemetry | X / — | D / repeat_pattern |
| recent_traces | X / — | I / repeat_pattern |
| delta_feed | X / — | X / — |

**Reading guide**: carry-forward items live naturally in compaction and can be directly inherited from there. They should not be inferred from perspectives or claims. anti-patterns can be directly refreshed from router telemetry repeat patterns (repeated misroutes are direct evidence of a failure mode) but require at least repeat_pattern evidence from all other sources.

---

## Dangerous Over-Promotion Patterns

These are the ten highest-risk promotion mistakes, ordered by severity.

### 1. Claim to stable_vows

A 30-minute task ownership signal ("I claimed the task of not modifying AGENTS.md") becomes a permanent vow ("I vow never to modify AGENTS.md"). Task ownership is coordination, not selfhood. Claims expire in 30 minutes; vows persist for 30 days.

### 2. Perspective tension to durable_boundaries

An agent expresses temporary anxiety in a 2-hour perspective ("I am uncertain about modifying the Redis schema"), and a later agent hardens this into a permanent boundary ("never modify Redis schema"). Uncertainty is not prohibition.

### 3. Single checkpoint to verified_routines

An agent writes one checkpoint recording its workflow ("I ran diagnose then packet then claim list"), and a later heuristic promotes this one-time behavior into a verified routine. Doing something once does not make it verified. Verification requires repeat evidence across multiple sessions.

### 4. Risk spike to stable_vows

A momentary high-risk computation triggers a new stable_vow to "permanently prevent" the risk. Runtime risk is a continuous score that changes every session. Hardcoding a transient score into a constitutional commitment causes vow inflation and eventually makes the vow system unable to distinguish real commitments from reflexive caution.

### 5. Router misroute to decision_preferences

The router encounters an ambiguous signal and force-routes it to a surface. A later agent reads this forced choice as "the agent prefers this surface" and writes it into decision_preferences. Ambiguity is not preference.

### 6. Compaction carry_forward to stable_vows

A compaction's carry_forward contains vow-like language ("remember not to commit private data"). A later agent copies this directly into stable_vows. Carry-forward is a 7-day handoff memo, not a constitutional declaration. The memo may be outdated, contextual, or overly broad.

### 7. Delta feed volume to active_threads inflation

A delta feed shows many new compactions and checkpoints. An agent adds every mentioned topic to active_threads. High activity volume is not the same as new work direction. Threads should be added only when the topic is genuinely new and not already covered.

### 8. Single trace topic to decision_preferences

One session trace handled a specific type of problem. An agent fixes the handling approach as a permanent decision_preference. One event does not establish a pattern. Preferences require repeat_pattern evidence across multiple sessions.

### 9. Baseline drift numeric change to active_threads

The baseline_drift value for `innovation_bias` shifts from 0.6 to 0.7. An agent infers this means "innovation is now an active thread" and adds it to active_threads. Drift is a continuous governance metric, not a discrete topic declaration. Translating float changes into thread names is over-interpretation.

### 10. No snapshot + compaction-only to durable_boundaries

No subject_snapshot exists yet. An agent reads compaction evidence_refs and directly sets durable_boundaries in the first snapshot. Seed snapshots should only populate the safest fields (active_threads from focus topics). Durable boundaries require deliberate human review, especially in a first snapshot where there is no prior baseline to compare against.

---

## Safe Direct Refresh Paths

These are the source-field combinations where `may refresh directly` is the allowed action. Each has a specific trigger condition.

| Source | Target Field | Trigger Condition | Runtime Alignment |
|--------|-------------|-------------------|-------------------|
| subject_snapshot (self) | decision_preferences | Inheriting from previous snapshot | Self-referential baseline |
| subject_snapshot (self) | verified_routines | Inheriting from previous snapshot | Self-referential baseline |
| subject_snapshot (self) | active_threads | Inheriting from previous snapshot | Self-referential baseline |
| subject_snapshot (self) | carry-forward items | Inheriting from previous snapshot | Self-referential baseline |
| subject_snapshot (self) | anti-patterns | Inheriting from previous snapshot | Self-referential baseline |
| compaction | active_threads | >= 1 compaction newer than latest snapshot, with focus topics not already in existing threads | `runtime_adapter.py:1122-1127` |
| checkpoint | active_threads | >= 2 checkpoints newer than latest snapshot, with persistent work focus | `runtime_adapter.py:1128-1133` |
| compaction | carry-forward items | Compaction carry_forward field contains items not yet in snapshot | Compaction is the natural carry-forward surface |
| router_telemetry | anti-patterns | misroute_signal_count >= 3 across recent routing events (repeat_pattern) | `runtime_adapter.py:1154-1156` (hazard registered) |
| (no snapshot exists) | active_threads | Any compaction or checkpoint exists with focus topics available | `runtime_adapter.py:1116-1121` (seed snapshot path) |

---

## Alignment With Existing Runtime Code

The `_build_subject_refresh_summary()` function in `runtime_adapter.py` (lines 1040-1230) already implements most of this contract's logic for five field families. This section maps each runtime decision to its contract counterpart.

### Field Guidance Alignment

| Runtime Field Guidance | Contract Matrix Cell | Match? |
|----------------------|---------------------|--------|
| `stable_vows`: action=`must_not_auto_promote`, evidence=`human_confirmation` (line 1066-1072) | stable_vows column: all X except subject_snapshot and governance_posture (M) | Yes |
| `durable_boundaries`: action=`manual_operator_only`, evidence=`human_confirmation` (line 1073-1081) | durable_boundaries column: all X except subject_snapshot and governance_posture (M), compaction and risk (I) | Yes — contract adds two I cells the runtime does not yet model |
| `decision_preferences`: action varies by routing_total (line 1082-1092) | decision_preferences column: multiple I cells from routing, compaction, traces | Yes — contract expands to more sources |
| `verified_routines`: action varies by compaction+checkpoint+misroute (line 1093-1113) | verified_routines column: I from compaction+checkpoint+router+traces | Yes |
| `active_threads`: action varies by snapshot presence and evidence (line 1116-1149) | active_threads column: D from compaction, D from checkpoint (>=2), I from others | Yes — exact match |

### Promotion Hazard Alignment

| Runtime Hazard | Contract Hazard # | Match? |
|---------------|-------------------|--------|
| "Do not promote active claims into durable identity" (line 1152-1153) | #1 (claim to stable_vows) | Yes |
| "Do not promote routing ambiguity or forced routes" (line 1154-1156) | #5 (router misroute to decision_preferences) | Yes |
| "Elevated runtime risk should not auto-promote into stable vows or durable boundaries" (line 1158-1161) | #4 (risk spike to stable_vows) | Yes |
| "Checkpoint-only evidence is too weak for durable identity promotion" (line 1162-1164) | #3 (single checkpoint to verified_routines) | Yes |
| "Do not infer durable identity from traces alone" (line 1166-1168) | #8 (single trace topic to decision_preferences) | Yes |

### What This Contract Adds Beyond Runtime

The runtime function covers 5 field families and 5 hazards. This contract extends to:

- 2 additional field families (carry-forward, anti-patterns) not yet in schema
- 5 additional source surfaces the runtime does not yet evaluate (perspective, governance_posture, risk_posture, recent_traces, delta_feed as distinct sources)
- 5 additional hazard patterns (#2, #6, #7, #9, #10) not yet in runtime code
- Explicit "safe direct refresh paths" table that the runtime only implies through conditional logic

---

## Future Heuristic Implementation Candidates

These are bounded heuristics that Codex may implement in future phases based on this contract. Ordered from safest to most complex.

### 1. active_threads compaction-backed auto-refresh (recommended first)

The runtime already has 90% of the logic in `_build_subject_refresh_summary()` lines 1116-1147. What remains is a thin execution layer:

- Read the refresh summary
- If `status == "refresh_candidate"` and `active_threads.action == "may_refresh_directly"`
- Execute `write_subject_snapshot()` updating only active_threads, inheriting all other fields from the latest snapshot
- Estimated scope: < 50 lines of new code in a script or adapter extension

### 2. anti-patterns from router misroute telemetry

When `misroute_signal_count >= 3` across recent routing events, record the dominant misroute pattern as an anti-pattern entry. Requires:

- Adding an `anti_patterns` field to the subject_snapshot schema (schema change)
- A decay mechanism (TTL or refresh-signal gating)
- Estimated scope: schema change + ~30 lines of heuristic code

### 3. decision_preferences from dominant routing surface

When `routing_total > N` and a `dominant_surface` is clearly established, suggest (but do not auto-write) a decision_preference reflecting the routing pattern. This should remain `may_influence_only` — the heuristic produces a recommendation, not an automatic write.

### 4. verified_routines from repeated checkpoint + compaction cadence

When both `newer_compactions > 0` and `newer_checkpoints > 0` and `misroute_signal_count == 0`, the checkpoint+compaction cadence suggests a stable workflow. This could prompt the agent to explicitly name verified routines, but should not auto-promote unnamed patterns.

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md` | Prerequisite — defines the four lanes used in this contract's matrix |
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines the operational semantics of each source surface |
| `TONESOUL_CLAIM_AUTHORITY_MATRIX.md` | Provides term-level authority context; this contract operates at the field-family level |
| `TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md` | Classifies law/ terms; this contract classifies runtime coordination surfaces |
| `tonesoul_stale_source_material_supersession_review_2026-03-29.md` | Records that the earlier implementation-gap triage draft was a source-material step later superseded by current runtime and authority surfaces |
| `subject_snapshot_v1.schema.json` | Defines the schema fields this contract governs |

---

## Canonical Handoff Line

A later agent refreshing a subject_snapshot must check this contract's matrix before writing any field. If the source-field intersection says `must not promote`, the write is forbidden regardless of how compelling the evidence looks. If it says `may refresh directly`, the minimum evidence shape must still be met. Identity is not heat.
