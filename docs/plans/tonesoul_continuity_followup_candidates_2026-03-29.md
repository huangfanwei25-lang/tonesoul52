# ToneSoul Continuity Follow-Up Candidates (2026-03-29)

> Purpose: bounded next implementation candidates for continuity import discipline, minimizing packet-shape churn
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Related Contracts:
>   - docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md
>   - docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md
>   - docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md

---

## Candidate 1: Freshness Indicator In Packet Summary

Add a `freshness` field to key sections of `r_memory_packet` output that shows how old each section's data is relative to now. Currently the packet returns data without indicating when it was produced — the receiver cannot tell if a compaction summary is 2 hours old or 6 days old without reading the raw timestamp.

**Scope**: ~30 lines in `runtime_adapter.py` `r_memory_packet()`. For each section that includes timestamped data (compaction, checkpoint, subject_snapshot, claim), compute `age_hours = (now - timestamp).total_hours` and include it as `freshness_hours` in the section output.

**Schema note**: if `freshness_hours` is added directly onto strict packet section objects, the packet schema will need to grow with it. If schema churn must stay zero, emit freshness in a sidecar summary section instead of mutating existing section objects.

**Why first**: zero behavioral change and a bounded packet-shape change. The receiver already sees the data — this just makes staleness visible without requiring manual timestamp math.

---

## Candidate 2: Import Posture Tag In Session-Start Bundle

Add a one-line `import_posture` summary to the `start_agent_session.py` output that classifies each continuity surface the agent is about to read:

```
import_posture:
  governance: directly_importable
  claims: directly_importable (check TTL)
  compaction: advisory (5 days old)
  snapshot: advisory (12 days old)
  delta_feed: directly_importable
```

**Scope**: ~40 lines in `start_agent_session.py`. Read each surface's timestamp, compute age, map to the Import And Decay Contract's posture classification.

**Why second**: builds on Candidate 1's freshness data. Makes the Import Contract machine-readable at session start instead of requiring the agent to mentally apply the contract.

---

## Candidate 3: Promotion Guard In Compaction Writer

Add a soft warning to `write_compaction()` when the compaction's `carry_forward` contains items that look like they are being promoted from a previous compaction without modification. If a carry_forward item is identical (same text, no new evidence) to a carry_forward item from a previous compaction, add an advisory note: `"[carry-forward recycled without new evidence — consider confirming or dropping]"`.

**Scope**: ~25 lines in `runtime_adapter.py` `write_compaction()`. Compare new carry_forward items against the most recent previous compaction's carry_forward. Flag identical items.

**Why third**: directly addresses the most dangerous over-import pattern (Hazard 1 in the Import Contract). Does not block the write — just adds a visible warning that helps the agent notice stale carry-forward recycling.

---

## Candidate 4: Decay Report In Session-End Bundle

Add a `decay_report` section to `end_agent_session.py` output that lists which surfaces the agent produced during this session and their expected lifetimes:

```
decay_report:
  compaction: written, expected lifetime 7 days
  checkpoint: written, expected lifetime 7 days
  claim: released
  perspective: not written
  snapshot: not written (no durable identity change)
```

**Scope**: ~30 lines in `end_agent_session.py`. Check which surfaces were produced during the session, report their expected lifetimes per the Lifecycle Map.

**Why fourth**: helps the agent (and humans reviewing session output) understand what will survive and what will decay. Currently sessions end without any indication of which context will be available to the next agent.

---

## Candidate 5: Stale-Import Advisory In Packet Reader

Add logic to `run_r_memory_packet.py` that emits a one-line warning when a surface exceeds its lane's expected freshness window:

```
⚠ compaction is 6.2 days old (lane: bounded_handoff, expected: ≤7 days)
⚠ snapshot is 28 days old (lane: working_identity, expected: ≤30 days)
```

**Scope**: ~20 lines in `run_r_memory_packet.py` (output formatting, not runtime logic).

**Why fifth**: useful but lower priority than Candidates 1-4. The freshness indicator (Candidate 1) makes staleness visible in the data; this makes it visible in the console output. Value depends on how agents consume packet output.

---

## Summary

| # | Candidate | Scope | Schema Change | Behavioral Change |
|---|---|---|---|---|
| 1 | Freshness indicator in packet | ~30 lines | Bounded / optional | No |
| 2 | Import posture in session-start | ~40 lines | No | No |
| 3 | Promotion guard in compaction | ~25 lines | No | Advisory warning only |
| 4 | Decay report in session-end | ~30 lines | No | No |
| 5 | Stale-import advisory in packet reader | ~20 lines | No | Advisory warning only |

All candidates are documentation-first or helper-level. None change packet schema, runtime lifecycle, or governance behavior.
