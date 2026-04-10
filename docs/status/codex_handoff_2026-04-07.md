# Codex Handoff (2026-04-07)

> Purpose: preserve the current launch-readiness state, the remaining Phase 722 gap, and the safest next continuation point without requiring hidden chat-history reconstruction.
> Scope: branch-local continuation handoff after PR #5 merged the CI/file-store/dashboard cleanup bundle into `master`.
> Status: current handoff note

---

## 1. Current Branch State

- Branch: `master`
- Current active bucket:
  - `Launch Readiness And Design Legibility`
- Honest current short board:
  - `Phase 722: run repeated live continuity validation waves`
  - Real remaining gap: repeat the external/non-creator cycle under 1-2 different lower-context task shapes before widening any launch claims
  - Immediate next pack: `docs/plans/tonesoul_non_creator_external_cycle_dual_surface_pack_2026-04-10.md`

## 2. What Landed Most Recently

### PR #5 merged into `master`

Merged as:

- `089bbbc` merge commit on `master`

What changed:

- CI lanes are now less noisy:
  - `ToneSoul CI` remains the automatic mainline gate
  - `Pytest CI` is manual focused rerun only
  - legacy `CI` is manual replay only, and `web_api_smoke` is now clearly named `web_api_quality_replay`
- Windows/file-backed closeout behavior is safer:
  - `TONESOUL_FORCE_FILE_STORE=1` now keeps `end_agent_session`, `save_checkpoint`, and `save_compaction` out of Redis auto-detect fallback
  - `save_compaction` no longer drops CLI payloads when `stdin` is a TTY
- Dashboard/operator packaging improved:
  - command shelf now exposes `source / activation / return` cues
  - self-improvement trial wave and tests now agree on the eighteenth promoted candidate

Most relevant surfaces:

- `scripts/run_collaborator_beta_preflight.py`
- `scripts/end_agent_session.py`
- `scripts/save_checkpoint.py`
- `scripts/save_compaction.py`
- `scripts/start_agent_session.py`
- `tonesoul/runtime_adapter.py`
- `tonesoul/store.py`
- `apps/dashboard/frontend/utils/session_start.py`
- `tonesoul/self_improvement_trial_wave.py`

## 3. Current Launch-Readiness Truth

The current safe public story is still:

- `CONDITIONAL GO` for guided collaborator beta
- `NO-GO` for public-launch claims
- file-backed coordination remains the launch-default mode

Most relevant status surfaces:

- `docs/status/phase726_go_nogo_2026-04-08.md`
- `docs/status/collaborator_beta_preflight_latest.{json,md}`
- `docs/status/collaborator_beta_entry_validation_latest.{json,md}`
- `docs/status/launch_continuity_validation_wave_latest.{json,md}`

The most important unresolved evidence gap is still:

- only one clean `non-creator / external-use` governance-aware cycle is currently recorded in canonical status surfaces; repeated varied proof across different task shapes is still thin

## 4. What The Next Agent Should Not Forget

### Launch boundaries

- collaborator beta is the current tier
- public launch remains deferred
- `next_target_tier` is roadmap language, not current permission

### Evidence boundaries

- repeated continuity validation exists
- collaborator-beta preflight exists
- lower-context entry validation exists
- but those do **not** by themselves equal repeated varied external clean-cycle proof

### Runtime boundaries

- the file-backed launch default is intentional for current beta posture
- `TONESOUL_FORCE_FILE_STORE=1` is a Windows/operator compatibility tool, not a new architecture claim
- closeout must use the official `end_agent_session.py` path if the goal is to count as clean external evidence

### Scope boundaries

- self-improvement remains active, but it is not the current center of gravity
- do not reopen ontology/domain-core extraction while Phase 722 still lacks repeated varied external clean-cycle proof
- do not widen launch language just because CI and operator packaging are healthier

## 5. Recommended First 10 Minutes For The Successor

Read:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. `task.md`
5. `docs/status/phase726_go_nogo_2026-04-08.md`
6. this handoff note
7. `docs/plans/tonesoul_non_creator_external_cycle_dual_surface_pack_2026-04-10.md`

Then run:

```bash
python scripts/start_agent_session.py --agent <your-id> --tier 0 --no-ack
python scripts/run_observer_window.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

If the task is Phase 722-facing, continue with the current repeated-validation pack instead of inventing a new validation flow.

## 6. What Still Must Stay Parked

- `.claude/`
- `claw-code-main/`
- `external_research/`
- `docs/plans/tonesoul_ontology_and_central_control_rethink_2026-04-08.md`
- `docs/plans/tonesoul_ontology_and_central_control_dormant_program_2026-04-08.md`

These may be useful later, but they are not the active shortest board while repeated varied external proof is still thin.

## 7. Best Next Move

Do not reopen:

- public-launch wording
- identity/ontology rewrites
- retrieval mythology
- domain-core extraction

The best next move is:

- run the dual-surface repeated-validation pack under one different lower-context or non-creator task shape
- keep the task small enough that the official session-end path can still end as `complete`
- keep the claim conservative: one clean pass exists, but launch claims still need repeated validation rather than one heroic proof

## 8. Compressed Thesis

ToneSoul is now cleaner to operate and easier to verify.

The remaining question is no longer "can the shell start safely?"

It is:

`can a lower-context or non-creator operator complete another honest cycle under a different bounded task shape without hidden rescue or unofficial closeout fallback?`
