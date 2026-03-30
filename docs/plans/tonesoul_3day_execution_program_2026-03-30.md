# ToneSoul 3-Day Execution Program (2026-03-30)

> Purpose: give the next agent a concrete 3-day continuation plan that can be executed from current repo truth instead of chat memory.
> Scope: continuation after collaborator-beta baseline and launch-honesty work.
> Status: active successor plan
> Starting Point: branch `codex/r-memory-compaction-lane-20260326`, guided collaborator beta open, public-launch maturity still deferred.

---

## 0. Current Baseline

Before starting this program, assume these are already true:

- collaborator beta is open in a guided, file-backed posture
- public-launch maturity claims remain blocked
- session-start / packet / diagnose already share bounded receiver posture
- council realism, working-style continuity, and evidence posture already have readouts
- the next shortest board is no longer launch wording

The next bucket is:

`low-drift anchor / observer-window baseline`

## 1. Program Goal

Over the next 3 days, move ToneSoul from:

`strong bounded entry + continuity surfaces`

to:

`a later-agent observer window that can show stable vs contested vs stale center-of-gravity state without re-reading the whole stack`

while keeping:
- public-claim honesty
- collaborator-beta posture
- advisory-vs-canonical boundaries

## 2. Program Guardrails

- Do not widen public-launch claims.
- Do not promote advisory continuity surfaces into law or identity.
- Do not reopen finished prompt-adoption waves unless a real regression appears.
- Prefer one bounded observer/readout seam over multiple new conceptual lanes.
- Keep validation live and repeated, not purely documentary.

## 3. Day 1: Observer Window And Low-Drift Anchor Baseline

### Target

Create the first minimal observer-facing center that answers:
- what is stable
- what is contested
- what is stale
- what changed since last seen

without asking a fresh agent to reconstruct it manually.

### Work Items

1. Define the observer-window contract in ToneSoul-native terms.
2. Derive a bounded `low_drift_anchor` from current visible surfaces:
   - posture
   - readiness
   - task track hint
   - active threads
   - evidence posture
   - realism caution
   - working-style summary
3. Add one runtime readout surface only if it stays advisory and testable.
4. Keep the output small:
   - `stable`
   - `contested`
   - `stale`
5. Add regression tests for:
   - clean stable case
   - conflicting continuity case
   - stale carry-forward case

### Outputs

- one contract doc if needed
- one bounded runtime/readout addition
- refreshed packet/session-start/diagnose exposure only if the same shape can stay aligned

### Stop Conditions

Stop and reassess if:
- the anchor starts depending on hidden interpretation
- `subject_snapshot` or `compaction` are being silently promoted
- the observer window becomes another long prose dump

### Success Criteria

A fresh agent can see a compact observer center and tell:
- what it may trust as the current center of gravity
- what is under conflict
- what is too old to lean on

## 4. Day 2: Repeated Validation Against The Observer Window

### Target

Prove that the new observer-window readout helps real handoff instead of only looking elegant.

### Work Items

1. Run at least one bounded fresh-agent validation wave.
2. Vary states deliberately:
   - clean state
   - contested dossier
   - stale compaction
   - claim collision or claim-recommended state
3. Record where the fresh agent still misreads:
   - stable vs contested
   - advisory vs promotable
   - current tier vs next target
4. Fix only the highest-friction misunderstanding.

### Outputs

- one new or refreshed validation artifact under `docs/status/`
- one small bounded fix if repeated confusion is visible

### Stop Conditions

Stop and reassess if:
- validation requires broad repo scanning to succeed
- the observer window starts hiding important disagreement
- fixing friction requires changing canonical governance semantics

### Success Criteria

A lower-context agent can use the normal entry stack plus the observer window and still classify the system center correctly in repeated scenarios.

## 5. Day 3: Rotation Checkpoint And Successor Packaging

### Target

Close the observer-window bucket at baseline if it is good enough, then rotate cleanly instead of over-optimizing it.

### Work Items

1. Review whether the observer window now meets baseline:
   - discoverable
   - bounded
   - tested
   - used in validation
2. If yes, freeze that bucket and rotate.
3. Refresh successor materials:
   - `task.md`
   - handoff/status note
   - any launch or entry docs affected by the new readout
4. Name the next shortest board explicitly.

### Candidate Next Bucket

Only if the observer-window bucket reaches baseline, consider rotating to one of:
- broader collaborator-beta validation under more varied task shapes
- more explicit operator health / freeze posture
- another non-launch generic runtime seam that still lacks bounded prompt/readout adoption

### Stop Conditions

Do not rotate if:
- validation is still thin
- the observer window still confuses stable vs advisory state
- the next bucket is chosen by novelty instead of shortest-board logic

### Success Criteria

The next agent can open the repo, read the handoff and plan, and know both:
- what is now baseline-complete
- what the next shortest board is

## 6. Daily Command Baseline

Use these before claiming that the current continuation is healthy:

```bash
python scripts/start_agent_session.py --agent <your-id> --no-ack
python scripts/run_r_memory_packet.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
```

For beta-facing checks:

```bash
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

For docs/runtime verification after bounded changes:

```bash
python scripts/verify_docs_consistency.py --repo-root .
python scripts/verify_protected_paths.py --repo-root . --strict ...
python -m pytest <targeted tests>
python -m ruff check <touched files>
```

## 7. What Not To Touch Casually

Do not mix private or local residue into this wave:
- `CLAUDE.md`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- `OpenClaw-Memory`
- `.claude/` permission-locked residue

Do not widen claims about:
- calibrated council quality
- mature live shared memory
- public-launch readiness

## 8. Compressed Thesis

The next 3 days should not invent a new philosophy lane.
They should make the current stack easier for later agents to enter, read, and continue honestly.
