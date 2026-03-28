# ToneSoul Subject Snapshot Field Lanes

> Status: companion to TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md
> Purpose: classify subject_snapshot fields into four lanes by their refresh tolerance so the boundary contract matrix is readable at a glance
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Depends On:
>   - spec/governance/subject_snapshot_v1.schema.json
>   - tonesoul/runtime_adapter.py (_build_subject_refresh_summary, lines 1040-1230)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md

## Why This Document Exists

The subject_snapshot schema carries seven candidate field families whose refresh tolerance ranges from "almost never" (stable_vows) to "freely refreshable from compaction evidence" (active_threads). Without an explicit lane map, the 10x7 boundary matrix in the companion contract is difficult to scan and easy to misapply.

This document assigns each field family to exactly one of four lanes so later agents and heuristics can check a field's lane before deciding whether a source signal is strong enough to refresh it.

## Four Lanes

| Lane | Meaning | Refresh Tolerance | Typical TTL Analogy |
|------|---------|-------------------|---------------------|
| **Durable Identity** | Constitutional commitments and persistent behavioral boundaries. These define who the agent is, not what it is currently doing. | Human confirmation only. No hot-state signal may auto-promote into this lane. | Months to permanent |
| **Refreshable Working Identity** | Operational preferences, verified workflows, and current work focus. These define how the agent works and what it is working on. | Compaction-backed or repeat-pattern evidence. A single ephemeral signal is not enough. | Days to weeks |
| **Temporary Carry-Forward** | Cross-session items that should survive handoff but decay naturally. Useful context, not identity. | Single signal with bounded TTL is acceptable, but the item must not be confused with durable identity. | Hours to days |
| **Never-Auto-Promote** | Fields or surfaces whose content must never be inferred from hot-state coordination residue. Promotion requires deliberate human or operator action and is never triggered by heuristic. | Forbidden for automatic heuristics. | N/A |

## Field Lane Map

| Field Family | Lane | In Schema? | Rationale |
|---|---|---|---|
| `stable_vows` | **Durable Identity** | Yes | Vows are constitutional commitments. The canonical source is `governance_state.json` `active_vows`. The snapshot copy is a shadow, not a source of truth. Changing a vow is a governance event, not a refresh event. |
| `durable_boundaries` | **Durable Identity** | Yes | Boundaries constrain what the agent must not do. They require deliberate review because a wrongly added boundary restricts capability permanently until manually removed. |
| `decision_preferences` | **Refreshable Working Identity** | Yes | Preferences describe how the agent tends to approach work. They can shift when repeated evidence (routing patterns, compaction themes) shows a consistent new pattern. A single ephemeral signal is not enough. |
| `verified_routines` | **Refreshable Working Identity** | Yes | Routines describe workflows the agent has performed reliably. "Verified" requires repeat evidence: at minimum, compaction-backed and checkpoint-backed confirmation that the routine was executed more than once without failure. |
| `active_threads` | **Refreshable Working Identity** | Yes | Threads describe what the agent is currently working on. This is the most refreshable field family. Compaction-backed evidence or repeated newer checkpoints are sufficient to add new threads. |
| `carry-forward items` | **Temporary Carry-Forward** | **No** | Items that should survive handoff (e.g., "remember to check X next session") but are not identity. Currently best expressed inside compaction `carry_forward` rather than as a snapshot field. |
| `anti-patterns / known failure modes` | **Temporary Carry-Forward** | **No** | Observed failure patterns (e.g., "routing misroutes tend to happen when...") are valuable context but are not selfhood. They should decay unless reinforced by repeated evidence. |

## Fields Not In Schema: Assessment

### carry-forward items

Currently, cross-session carry-forward lives in compaction (`carry_forward` field, TTL 7 days). This is the right place for now. Adding a dedicated `carry_forward` field to subject_snapshot would risk promoting temporary handoff notes into 30-day durable identity. If a carry-forward item proves persistent across multiple compactions, it should be manually promoted to `active_threads` or `decision_preferences` instead.

**Recommendation**: do not add to schema yet. Let compaction remain the primary carry-forward surface.

### anti-patterns / known failure modes

Anti-patterns are observed, not declared. They emerge from repeated misroute signals, tension spikes, or aegis vetoes. Adding them to subject_snapshot is defensible if:

1. The anti-pattern has been observed across >= 3 sessions or compactions
2. The entry decays (TTL or refresh-signal-gated) rather than persisting indefinitely
3. The field is explicitly labeled as advisory, not prescriptive

**Recommendation**: consider adding to schema in a future phase, but only with an explicit decay mechanism. Until then, record anti-patterns in compaction `carry_forward` and let the boundary contract treat them as Temporary Carry-Forward.

## Relationship To Boundary Contract

This document is a prerequisite for reading `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md`. The boundary matrix uses lane assignments from this table to determine default allowed actions:

- **Durable Identity** fields default to `must not promote` or `manual/operator-only`
- **Refreshable Working Identity** fields default to `may influence` and can reach `may refresh directly` with sufficient evidence
- **Temporary Carry-Forward** fields default to `may influence` from most sources and `may refresh directly` from compaction
- **Never-Auto-Promote** is a lane constraint, not a field family — it marks source/field combinations where the lane itself forbids automatic action regardless of evidence strength
