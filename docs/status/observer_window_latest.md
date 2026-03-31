# ToneSoul Observer Window / Low-Drift Anchor

> Generated at `2026-03-30T16:14:20Z`. Advisory only.

**Summary**: `observer_window stable=5 contested=3 stale=1 delta_has_updates=True`

> [!NOTE]
> This observer window is advisory only. Items in 'stable' reflect current bounded posture but do not outrank canonical contracts. Items in 'contested' must not be treated as confirmed. Items in 'stale' should trigger a re-read before leaning on them. Do not promote this readout into canonical governance truth.

## Stable

(5 items)

- **governance posture is directly importable**
  - source: `import_posture.posture`
- **launch tier is collaborator_beta; public_launch_ready=false**
  - source: `packet.project_memory_summary.launch_claim_posture`
- **coordination backend is file-backed (launch default)**
  - source: `packet.coordination_mode.launch_default_mode`
- **evidence_readout_posture is present and bounded**
  - source: `packet.project_memory_summary.evidence_readout_posture`
- **session readiness surface is computed and directly importable**
  - source: `import_posture.readiness`

## Contested

(3 items)

- **council confidence is descriptive_only; agreement ≠ calibrated accuracy** — `council dossier present but calibration_status not confirmed`
  - source: `import_posture.council_dossier.dossier_interpretation`
- **latest compaction has carry_forward promotion hazard; must_not_promote** — `hazards=1`
  - source: `import_posture.compactions.promotion_hazards`
- **subject snapshot is advisory; must not be promoted into canonical identity**
  - source: `import_posture.subject_snapshot`

## Stale

(1 items)

- **recent_traces are 131.1h old (threshold=48.0h)** — `freshness_hours=131.1`
  - source: `import_posture.recent_traces.freshness_hours`

## Delta Since Last Seen

- First observation: `True`
- Has updates: `True`
- New compactions: `3`
- New checkpoints: `0`
- New traces: `2`
