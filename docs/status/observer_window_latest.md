# ToneSoul Observer Window / Low-Drift Anchor

> Generated at `2026-04-02T03:58:46Z`. Advisory only.

**Summary**: `observer_window stable=5 contested=4 stale=1 delta_has_updates=True`

> [!NOTE]
> This observer window is advisory only. Items in 'stable' reflect current bounded posture but do not outrank canonical contracts. Items in 'contested' must not be treated as confirmed. Items in 'stale' should trigger a re-read before leaning on them. Do not promote this readout into canonical governance truth.

## Canonical Center

- Parent surfaces: `task.md, DESIGN.md`
- Canonical anchor references: `AXIOMS.json, DESIGN.md, canonical architecture contracts, task.md.current_short_board`
- Source precedence: `canonical_anchors > live_coordination_truth > derived_orientation_shells > bounded_handoff > working_identity_and_replay`
- Receiver rule: `Treat the canonical center as parent planning truth. Observer/readout children may orient continuation, but they do not override AXIOMS.json, DESIGN.md, canonical contracts, or the accepted short board.`
- Successor correction: `observer stable != execution permission; confirm live_coordination first`
- Correction rule: `Stable observer output is shell-order orientation only. Before shared edits, confirm live_coordination directly: check readiness status, visible claims, and bounded_handoff receiver obligation.`
- Required checks: `readiness.status, claim_view.claims, import_posture.surfaces.compactions.receiver_obligation`
- Current short board visible: `True`
- Current short board:
  - Phase 752: triage the remaining successor/hot-memory sidecar residue so only one active runtime-aligned story remains

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

## Hot-Memory Decay / Compression

- Summary: `operational=canonical_center,live_coordination review_only=low_drift_anchor,working_identity,replay_review quarantine=bounded_handoff`
- Receiver note: `Operational layers may orient immediate work. Review-only layers may inform resumability or context but should not be leaned on as authority. Quarantined layers should be refreshed or resolved before they influence edits.`

- `canonical_center`: `operational`
  - status: `stable`
  - decay_posture: `human_refresh_only`
  - compression_posture: `never_compress`
  - note: Parent truth; successors should re-read when the short board is not visible.
- `low_drift_anchor`: `review_only`
  - status: `stale`
  - decay_posture: `recompute_each_session`
  - compression_posture: `already_compact_do_not_recompress`
  - note: Observer summary should be rebuilt, not carried forward as its own authority.
- `live_coordination`: `operational`
  - status: `stable`
  - decay_posture: `expire_fast`
  - compression_posture: `do_not_compress_live_signals`
  - note: Claims, readiness, and mode hints are only valid for the current coordination moment.
- `bounded_handoff`: `quarantine`
  - status: `contested`
  - decay_posture: `ttl_then_compress`
  - compression_posture: `compress_with_closeout_guards`
  - quarantine_reason: `receiver_obligation=must_not_promote closeout=partial`
  - note: Compactions may orient resumability, but incomplete closeout or promotion hazards require quarantine.
- `working_identity`: `review_only`
  - status: `stable`
  - decay_posture: `slow_decay_with_refresh`
  - compression_posture: `do_not_compress_snapshot`
  - note: Working identity is inheritable but non-canonical; stale or contested identity should not be leaned on.
- `replay_review`: `review_only`
  - status: `stable`
  - decay_posture: `prune_by_cardinality`
  - compression_posture: `preserve_dissent_then_prune_oldest`
  - note: Replay helps context and audit, not authority or execution permission.

## Subsystem Parity

- Summary: `subsystem_parity baseline=3 beta_usable=5 partial=2 deferred=1 launch=collaborator_beta readiness=pass`
- Receiver rule: `Use baseline lanes for normal continuation, beta_usable lanes for guided collaborator-beta work, partial lanes with explicit gap awareness, and deferred lanes as out of current scope.`
- Next focus: `working_style.wave_2_surface_selection` - Shared-edit preflight is now real enough to stop being the shortest board; rotate to the next bounded non-successor bucket instead of reopening hot-memory theory.

- `session_start_bundle`: `baseline`
  - current_signal: `readiness=pass track=feature_track claim=required`
  - strongest_truth: Session-start exposes readiness, task/deliberation hints, import posture, and bounded successor guards.
  - main_gap: Cold successors still need one tighter parity readout for overall subsystem maturity.
  - next_bounded_move: `keep first-hop bundle stable and successor-focused`
  - overclaim_to_avoid: session-start alone captures the whole system
- `observer_window`: `baseline`
  - current_signal: `short_board_visible`
  - strongest_truth: Stable/contested/stale observer window exists and is regression-backed.
  - main_gap: Anchor ordering is better than before but still relies on successor discipline.
  - next_bounded_move: `keep observer output bounded to shell-order orientation`
  - overclaim_to_avoid: observer window is canonical truth
- `receiver_posture`: `baseline`
  - current_signal: `ack is safe, apply is bounded, promote requires explicit justification and human confirmation.`
  - strongest_truth: ack/apply/promote ladder is visible across session-start, packet, and diagnose.
  - main_gap: Cold readers can still miss it if they skip first-hop surfaces.
  - next_bounded_move: `keep the ladder concentrated in successor-facing surfaces`
  - overclaim_to_avoid: every agent will interpret the ladder identically
- `packet_hot_state`: `beta_usable`
  - current_signal: `continuity=runtime_present evidence_tested=2`
  - strongest_truth: Packet carries freshness, evidence posture, launch claim posture, and realism notes.
  - main_gap: Too many adjacent readouts still compete for attention.
  - next_bounded_move: `keep canonical-center and parity ordering visible`
  - overclaim_to_avoid: packet equals complete memory
- `compaction_checkpoint_handoff`: `beta_usable`
  - current_signal: `receiver_obligation=must_not_promote closeout=partial`
  - strongest_truth: Bounded resumability, closeout grammar, and promotion hazards are visible.
  - main_gap: Smooth summaries can still be over-read if successors ignore closeout and receiver posture.
  - next_bounded_move: `tighten closeout surfacing where successors actually read first`
  - overclaim_to_avoid: compaction is full task truth
- `subject_working_style`: `partial`
  - current_signal: `validation=sufficient`
  - strongest_truth: Working-style continuity exists with playbook, limits, observability, and validation.
  - main_gap: Successors can still confuse shared style with identity or authority.
  - next_bounded_move: `keep style bounded to advisory workflow habits`
  - overclaim_to_avoid: shared style means shared selfhood
- `council_realism`: `partial`
  - current_signal: `calibration=unknown`
  - strongest_truth: Descriptive-only, dissent, suppression, and realism notes are visible.
  - main_gap: No outcome calibration exists yet.
  - next_bounded_move: `preserve realism warnings without pretending calibrated accuracy`
  - overclaim_to_avoid: council confidence predicts correctness
- `evidence_posture`: `beta_usable`
  - current_signal: `tested=2 runtime_present=1 descriptive_only=1`
  - strongest_truth: Evidence posture separates tested, runtime_present, descriptive_only, and document_backed lanes.
  - main_gap: Operator-facing storytelling still needs to stay aligned with this ladder.
  - next_bounded_move: `keep evidence posture visible in successor surfaces and launch language`
  - overclaim_to_avoid: all current claims are equally proven
- `collaborator_beta_launch`: `beta_usable`
  - current_signal: `current_tier=collaborator_beta public_ready=no`
  - strongest_truth: Guided collaborator beta is current truth and public launch remains deferred.
  - main_gap: External deployment and broader live validation are still thinner than the internal story.
  - next_bounded_move: `continue bounded beta validation without widening claims`
  - overclaim_to_avoid: public launch maturity is ready
- `mutation_preflight_hooks`: `beta_usable`
  - current_signal: `shared_code=claim_before_shared_edits compaction=review_only_handoff task_board=ratified_short_board_only commit=aegis_locked_commit launch_claims=bounded_collaborator_beta_only`
  - strongest_truth: Successor-facing mutation preflight now maps current write/mutate/publish decision points.
  - main_gap: The path-overlap hook is now real, but it remains intentionally narrow and only sees visible claims plus candidate paths.
  - next_bounded_move: `shared_code_edit.path_overlap_preflight`
  - overclaim_to_avoid: shared-edit mutation is now a full permission system
- `external_transport_plugins`: `deferred`
  - current_signal: `not_in_launch_default_story`
  - strongest_truth: External transport, MCP, and plugin packaging are known future-value lanes.
  - main_gap: They are not needed for current collaborator-beta truth.
  - next_bounded_move: `keep parked under external roadmap until current launch-default story is stronger`
  - overclaim_to_avoid: ToneSoul already has a mature transport shell

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

- **recent_traces are 190.8h old (threshold=48.0h)** - `freshness_hours=190.8`
  - source: `import_posture.recent_traces.freshness_hours`

## Delta Since Last Seen

- First observation: `True`
- Has updates: `True`
- New compactions: `3`
- New checkpoints: `0`
- New traces: `2`
