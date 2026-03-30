# Codex Handoff (2026-03-30)

> Purpose: preserve today's working state, current truths, and next-shortest-board guidance for the next AI without requiring hidden chat history.
> Scope: branch-local continuation handoff after collaborator-beta baseline work.
> Status: current handoff note

---

## 1. Current Branch State

- Branch: `codex/r-memory-compaction-lane-20260326`
- HEAD when this note was written: `e80328c43d243d488e3185fa1a03f69721363037`
- Launch posture:
  - `GO` for guided collaborator beta
  - `NO-GO` for public maturity claims
  - launch-default coordination remains `file-backed`

## 2. What Changed Today

This continuation wave finished the collaborator-beta packaging bucket and left the repo at a clearer handoff baseline.

### Key commits from this wave

- `15cb9c6` `feat: add collaborator beta preflight bundle`
- `14a0347` `feat: clarify collaborator beta entry posture`
- `e80328c` `feat: publish collaborator beta validation surfaces`

### Supporting earlier commits still shaping the current state

- `7e3a246` `docs: open guided collaborator beta posture`
- `2b4b384` `feat: add public-claim honesty gate`
- `471b9d7` `feat: add launch coordination backend posture`
- `b0162fc` `feat: add repeated continuity validation wave`
- `636e6c1` `docs: add launch operations surface`
- `3ea6fcf` `docs: add launch maturity program`

## 3. Current Truths The Next Agent Should Not Forget

### Launch and honesty

- `collaborator_beta` is the current tier
- `public_launch` is only the next target tier, not current readiness
- `public_launch_ready = false`
- `launch_default_mode = file-backed`

### Council and evidence

- council confidence is still descriptive, not calibrated
- council realism, dissent, suppression visibility, and decomposition are visible
- later agents should not restate agreement/coherence as accuracy

### Continuity and receiver posture

- session-start / packet / diagnose are already aligned on `ack / apply / promote`
- working-style continuity is advisory-only
- subject snapshot is not canonical identity
- compaction carry-forward must not be silently promoted

### Current shortest board

The next shortest board is:

`low-drift anchor / observer-window baseline`

Do not reopen launch wording unless the observer-window work exposes a real new launch-facing failure.

## 4. First 15 Minutes For The Successor Agent

Read, in this order:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. this handoff note
5. `docs/plans/tonesoul_3day_execution_program_2026-03-30.md`

Then run:

```bash
python scripts/start_agent_session.py --agent <your-id> --no-ack
python scripts/run_r_memory_packet.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
```

If the task is beta-facing, also run:

```bash
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

## 5. Current Beta-Facing Readouts

The latest bounded beta-facing artifacts are:

- `docs/status/collaborator_beta_preflight_latest.json`
- `docs/status/collaborator_beta_preflight_latest.md`
- `docs/status/collaborator_beta_entry_validation_latest.json`
- `docs/status/collaborator_beta_entry_validation_latest.md`

These are the right surfaces to read before making new collaborator-beta claims.

## 6. What Still Must Not Be Touched Casually

These are not part of the public/canonical continuation wave:

- `CLAUDE.md`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- `OpenClaw-Memory`
- `.claude/` permission-locked local residue

If they are dirty in `git status`, that is expected and not a reason to "clean the repo."

## 7. If Work Starts Going Sideways

If the next agent starts reopening old launch wording, overclaiming maturity, or losing the receiver/evidence boundaries:

1. stop widening claims
2. return to:
   - `DESIGN.md`
   - `docs/plans/tonesoul_launch_maturity_program_2026-03-30.md`
   - `docs/plans/tonesoul_launch_operations_surface_2026-03-30.md`
3. re-run the bounded entry stack
4. resume from the observer-window short board instead of inventing a new architecture lane

## 8. Recommended Next Move

Implement a bounded observer-window / low-drift-anchor readout that can tell a later agent:
- what is currently stable
- what is contested
- what is stale
- what changed since last seen

without forcing a repo-wide reread or silent promotion of advisory surfaces.

## 9. Compressed Thesis

Today ended with ToneSoul in a stronger guided-beta state, but the honest next step is not bigger launch language.

It is:

`make the current center of gravity easier for later agents to see and continue safely.`
