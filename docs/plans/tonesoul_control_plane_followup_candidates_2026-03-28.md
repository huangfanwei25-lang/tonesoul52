# ToneSoul Control Plane Follow-Up Candidates (2026-03-28)

> Purpose: bounded future work items identified during the Control Plane Discipline Adaptation work order
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Related Contracts:
>   - docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md
>   - docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md

## Recommended Implementation Order

1 (safest) → 5 (most complex)

---

## Candidate 1: Session-Start Readiness Surface

Add a machine-readable `readiness` section to the `start_agent_session.py` output payload. The section would classify the current state as `pass`, `needs_clarification`, or `blocked` based on claim conflicts, risk level, and delta feed signals. This does not block the bundle output — the agent still sees everything — but the readiness classification becomes visible instead of requiring the agent to apply the Track & Readiness Contract mentally.

**Scope**: ~40 lines in `start_agent_session.py` + schema extension for the bundle output. No changes to `runtime_adapter.py` core.

**Why first**: lowest risk, highest immediate value. The readiness contract already defines the logic; this just surfaces it.

---

## Candidate 2: Track Suggestion From Packet

Add a `task_track_hint` section to `r_memory_packet()` or `project_memory_summary` that suggests a track and exploration depth based on the current claim count, risk posture, compaction `next_action`, and active threads. The hint is advisory — the agent may override it — but it reduces the chance of track collapse by making the classification visible before work begins.

**Scope**: ~60 lines in `runtime_adapter.py` (new helper function) + packet schema extension. Requires careful design to avoid the hint becoming authoritative.

**Why second**: builds on Candidate 1's readiness surface. The track suggestion is more opinionated than readiness and needs more testing to avoid false classifications.

---

## Candidate 3: Plan Delta Tracking In Compaction

Add an optional `plan_delta` field to compaction payloads that records what the agent did to `task.md` during the session: `keep`, `append`, `fork`, or `stop`. Later agents can see in the delta feed whether plan thrash is happening (two consecutive `fork` or `stop` entries from the same agent). This is purely observational — it does not enforce plan delta rules, but it makes thrash detectable.

**Scope**: ~20 lines in `write_compaction()` + optional field in compaction schema. Minimal runtime risk since the field is optional and advisory.

**Why third**: cheapest implementation, but value depends on agents actually recording their plan operations. Should be encouraged by operator guidance, not enforced.

---

## Candidate 4: Track-Aware Claim TTL

Adjust claim TTL based on track classification. Currently all claims use the same 1800-second (30-minute) TTL. Quick changes do not need claims at all. Feature track claims are fine at 30 minutes. System track claims often need longer — 2 hours or explicit renewal — because architecture contracts take more than 30 minutes to produce.

**Scope**: ~30 lines in `claim_task()` (add optional `track` parameter that maps to TTL presets) + script argument. Backward compatible since the default remains 1800 seconds.

**Why fourth**: requires the track classification system to be stable before tying TTL to it. Premature binding of TTL to track could cause unexpected claim expirations.

---

## Candidate 5: Exploration Checkpoint

For x2 and x3 depth tasks, encourage agents to write a checkpoint after exploration but before implementation that records: "I explored these files, I classify this as track X, readiness is pass, my plan is Y." This gives later agents a resumability point that includes the exploration results, and gives humans a review window before implementation begins.

**Scope**: convention change + optional template in operator guidance. No runtime code required — this is a discipline addition, not a feature. Could optionally be enforced by checking for an exploration checkpoint before claim is accepted on system_track tasks.

**Why fifth**: most valuable for system_track tasks, but enforcement is the hardest part. Start as convention, promote to enforcement only after repeated agent adoption proves the pattern.
