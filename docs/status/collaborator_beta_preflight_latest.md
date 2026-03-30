# ToneSoul Collaborator-Beta Preflight

> Generated at `2026-03-30T11:37:26Z`.

- Overall status: `go`
- Current tier: `collaborator_beta`
- Next target: `public_launch`
- Launch-default backend: `file-backed`
- Scope posture: `guided collaborator beta only; file-backed remains launch default and public launch stays deferred`
- Target reading: `next_target_tier names the next maturity target, not current readiness or public-launch permission.`
- Claim trigger: `claim when you are about to edit a shared path; read-only inspection can stay unclaimed`
- Aegis posture: `compromised` / `Treat aegis_compromised as a visible caution in the current beta posture, not as an implicit public-launch stop or a reason to ignore the rest of the bounded receiver checks.`

## Entry Stack

| Surface | Status | Key detail |
|---|---|---|
| session-start | ok | readiness=pass track=feature_track claim=required mode=standard_council |
| packet | ok | current=collaborator_beta next=public_launch backend=file-backed |
| diagnose | ok | [ToneSoul] file | SI=0.45 | vows=3 tensions=0 | R=0.03/stable | coord=file-backed | traces=2 claims=0 compactions=3 subjects=1 zones=9 | git=15cb9c6/dirty=10 | aegis=compromised | agent=beta-smoke (aegis=compromised) |

## Validation Wave

- Scenario count: `4`
- Max receiver alerts: `4`
- Contested dossier visible: `True`
- Stale compaction guarded: `True`

## Claim Posture

- Summary: `launch_claims=current:collaborator_beta public_launch:deferred blocked=continuity_effectiveness,council_decision_quality,live_shared_memory`

### Blocked Overclaims
- `continuity_effectiveness` = `runtime_present`
- `council_decision_quality` = `descriptive_only`
- `live_shared_memory` = `not_launch_default`

## Blocking Findings

- none
