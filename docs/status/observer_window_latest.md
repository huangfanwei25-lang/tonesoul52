# ToneSoul Observer Window / Low-Drift Anchor

> Generated at `2026-04-01T23:30:41Z`. Advisory only.

**Summary**: `observer_window stable=5 contested=4 stale=1 delta_has_updates=True`

> [!NOTE]
> This observer window is advisory only. Items in 'stable' reflect current bounded posture but do not outrank canonical contracts. Items in 'contested' must not be treated as confirmed. Items in 'stale' should trigger a re-read before leaning on them. Do not promote this readout into canonical governance truth.

## Canonical Center

- Parent surfaces: `task.md, DESIGN.md`
- Receiver rule: `Treat the canonical center as parent planning truth. Observer/readout children may orient continuation, but they do not override task.md or DESIGN.md.`
- Successor correction: `observer stable != execution permission; confirm live_coordination first`
- Correction rule: `Stable observer output is shell-order orientation only. Before shared edits, confirm live_coordination directly: check readiness status, visible claims, and bounded_handoff receiver obligation.`
- Required checks: `readiness.status, claim_view.claims, import_posture.surfaces.compactions.receiver_obligation`
- Current short board visible: `True`
- Current short board:
  - Phase 745: map hot-memory decay/compression and quarantine posture once the ladder is legible
  - Phase 746: map mutation-preflight / write-hook chain without reopening launch wording or new ontology lanes

## Hot-Memory Ladder

- Summary: `canonical_center=stable | low_drift_anchor=stale | live_coordination=stable | bounded_handoff=contested | working_identity=stable | replay_review=stable`
- Receiver note: `Read the ladder from canonical_center downward. Parent layers orient or constrain child layers. Child summaries do not outrank parent truth.`

- `canonical_center`: `stable`
  - sources: `task.md.current_short_board, DESIGN.md`
  - receiver_rule: `treat_as_parent_truth`
  - note: Current short board is visible.
- `low_drift_anchor`: `stale`
  - sources: `import_posture.posture, packet.launch_claim_posture, packet.coordination_mode, import_posture.readiness`
  - receiver_rule: `apply_when_stable_review_when_contested`
  - note: observer_window counts: stable=5 contested=4 stale=1
- `live_coordination`: `stable`
  - sources: `readiness, claims, task_track_hint, deliberation_mode_hint`
  - receiver_rule: `must_read_before_shared_edits`
  - note: readiness=pass
- `bounded_handoff`: `contested`
  - sources: `compactions, checkpoints, delta_feed, recent_traces`
  - receiver_rule: `ack_or_review_never_self_promote`
  - note: receiver_obligation=must_not_promote closeout=partial
- `working_identity`: `stable`
  - sources: `subject_snapshot, working_style_anchor, working_style_playbook`
  - receiver_rule: `advisory_only_do_not_promote`
  - note: working_style_status=reinforced
- `replay_review`: `stable`
  - sources: `recent_traces, council_dossier, validation_artifacts`
  - receiver_rule: `review_for_context_not_for_authority`
  - note: Replay surfaces are available without current descriptive-only flags.

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

(4 items)

- **council confidence is descriptive_only; agreement does not equal calibrated accuracy** - `council dossier present but calibration_status not confirmed`
  - source: `import_posture.council_dossier.dossier_interpretation`
- **latest compaction has carry_forward promotion hazard; must_not_promote** - `hazards=1`
  - source: `import_posture.compactions.promotion_hazards`
- **latest compaction closeout is 'partial'; do not read the handoff as completed work** - `status=partial unresolved=0`
  - source: `import_posture.compactions.closeout_status`
- **subject snapshot is advisory; must not be promoted into canonical identity**
  - source: `import_posture.subject_snapshot`

## Stale

(1 items)

- **recent_traces are 186.3h old (threshold=48.0h)** - `freshness_hours=186.3`
  - source: `import_posture.recent_traces.freshness_hours`

## Delta Since Last Seen

- First observation: `True`
- Has updates: `True`
- New compactions: `3`
- New checkpoints: `0`
- New traces: `2`
