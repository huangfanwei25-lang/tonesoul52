# Codex Handoff (2026-04-02)

> Purpose: preserve today's working state, what was actually fixed, and the next successor-facing design move without requiring hidden chat history.
> Scope: branch-local continuation handoff after CI cleanup and successor/hot-memory planning.
> Status: current handoff note (supersedes older handoff notes when the task is successor continuity and hot-memory coherence)

---

## 1. Current Branch State

- Branch: `codex/r-memory-compaction-lane-20260326`
- Current honest launch posture:
  - `GO` for guided collaborator beta
  - `NO-GO` for public maturity claims
  - launch-default coordination remains `file-backed`

## 2. What Was Fixed Today

### CI / Workflow closeout

The immediate repair bucket was closed before starting new planning work.

Key fixes:

- merge-ref attribution false positives were removed
- black/lint PR diff failures under shallow checkout were removed
- full suite and blocking tier were both green locally

Most relevant commits from the repair wave:

- `ac9be52` `fix: unblock merge-ref attribution and black gate`
- `6c04025` `fix: format attribution exemption test`

### Current repo-entry cleanup

Repo-local AI entry has now been rewritten cleanly in:

- `.github/copilot-instructions.md`

The new file points successors to:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. `start_agent_session`
5. `run_observer_window`

instead of expecting repo-wide guessing.

## 3. What Was Added Today

### Successor / hot-memory design surfaces

New files:

- `docs/architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md`
- `docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md`
- `docs/plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md`
- this handoff note

Purpose:

- turn scattered continuity wisdom into one successor-facing contract
- translate useful external patterns into ToneSoul-native terms
- make subsystem maturity and overclaim risks legible

## 4. Current Truths The Next Agent Should Not Forget

### Continuity

- packet, session-start, diagnose, and observer-window are real and useful
- none of them are sovereign governance truth
- compaction, subject snapshot, working style, and dossier remain bounded and non-canonical

### Council

- council realism is visible
- confidence is still descriptive, not calibrated
- do not restate agreement or coherence as correctness

### Launch

- collaborator beta is the honest current tier
- public launch is not ready
- file-backed remains the launch-default coordination story

### Task discipline

- `task.md` is protected from speculative ecosystem drift
- external ideas should stay in `docs/plans/` until ratified

## 5. The New Design Pressure

The next design pressure is no longer:

- launch wording
- basic observer window existence
- CI false-positive cleanup

It is:

`make successor collaboration and hot-memory layering easy enough that any later AI can continue safely from repo-native surfaces alone`

## 6. Recommended First 15 Minutes For The Successor

Read, in this order:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. this handoff note
5. `docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md`
6. `docs/plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md`

Then run:

```bash
python scripts/start_agent_session.py --agent <your-id> --no-ack
python scripts/run_observer_window.py --agent <your-id>
python scripts/run_r_memory_packet.py --agent <your-id>
```

Use `diagnose` only if the shorter surfaces leave a real ambiguity.

## 7. What Still Must Not Be Touched Casually

- `AGENTS.md`
- `CLAUDE.md`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- `OpenClaw-Memory`
- `.claude/`

These are not part of the public successor-continuity lane.

## 8. Recommended Next Move

Do not reopen old launch or prompt-adoption buckets.

The best next move is:

1. use the new parity/gap map to ratify the next active short board
2. if activated, push `low-drift anchor / hot-memory ladder` from day-1 observer baseline toward clearer successor coherence

## 9. Compressed Thesis

ToneSoul now has enough continuity surfaces.

The next gain is not more surfaces.
It is making the existing center easier for a successor to reconstruct without mythology, overclaim, or chat-history dependence.
