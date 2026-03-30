# ToneSoul Launch Operations Surface (2026-03-30)

> Purpose: give one current operator-facing launch posture for the present ToneSoul stack.
> Scope: internal alpha and collaborator-beta preparation.
> Status: current operations surface
> Lineage:
>   - `docs/plans/elisa_tonesoul_operational_runbook_2026-02-24.md`
>   - `docs/plans/release_v1.0_go_nogo_2026-02-24.md`
> Companion:
>   - `docs/plans/tonesoul_launch_maturity_program_2026-03-30.md`
>   - `docs/plans/tonesoul_launch_validation_matrix_2026-03-30.md`
>   - `docs/plans/tonesoul_coordination_backend_decision_2026-03-30.md`

## 1. Current Operational Truth

ToneSoul is currently:
- open for a bounded collaborator beta
- not yet ready to claim mature public launch
- not yet ready to blur internal file-backed discipline into mature live shared-memory infrastructure

### Current posture

| Axis | Current truth |
|---|---|
| Launch tier | `collaborator beta` |
| Next target | `public launch` |
| Shared-coordination default | `file-backed` |
| Redis/live shared memory | present as a path, not yet the launch-default story |
| Council confidence | descriptive, not calibrated |
| Public launch language | must remain evidence-bounded |

## 2. What This Surface Is For

This document is for answering:
- what should be run before we say the current branch is safe to use
- what currently blocks collaborator beta
- what counts as freeze / rollback / stop-and-hold
- what is honest to say about the system today

It is not:
- a historical release note
- a marketing page
- a promise that every subsystem is equally mature

## 3. Minimum Pre-Use Check Bundle

Run from repo root.

### Entry-stack checks

```bash
python scripts/start_agent_session.py --agent launch-smoke --no-ack
python scripts/run_r_memory_packet.py --agent launch-smoke
python -m tonesoul.diagnose --agent launch-smoke
```

### One-command collaborator-beta preflight

```bash
python scripts/run_collaborator_beta_preflight.py --agent beta-smoke
```

Use this when the goal is not a full repo healthcheck, but one current answer to:
- is the entry stack alive
- is collaborator-beta still the current tier
- is file-backed still the launch-default story
- is the latest continuity wave still discoverable
- if claim is really required now or only once a shared path will be edited
- whether current `aegis` posture is a visible caution inside the guided-beta story

These confirm that:
- session-start still renders
- packet still renders
- diagnose still matches the same receiver/readout story

### Code / contract checks

```bash
python -m pytest tests/test_start_agent_session.py tests/test_runtime_adapter.py tests/test_diagnose.py -q
python -m ruff check tonesoul scripts tests
python scripts/verify_docs_consistency.py --repo-root .
python scripts/verify_protected_paths.py --repo-root . --strict ...
```

These confirm that:
- core entry surfaces still behave
- the repo does not drift past the current lint baseline
- docs do not point at broken structure
- protected/private paths are not silently mixed into the public lane

## 4. Current Go / No-Go Rules

### GO for current collaborator-beta usage

Proceed only if:
- entry-stack checks are green
- current receiver posture is coherent across session-start / packet / diagnose
- protected-path verification is green
- no new overclaim was introduced in the touched surface

### GO for bounded collaborator beta

Collaborator beta is open only because:
- repeated validation now exists beyond one neat bounded demo
- the launch-default coordination backend is explicit
- one current launch posture is discoverable without rereading historical runbooks
- public-facing claims are explicitly bounded by evidence level

### NO-GO for public launch language

Do not speak as if the following are already mature public truths:
- "ToneSoul has calibrated council accuracy"
- "ToneSoul preserves context across sessions in a proven robust way"
- "ToneSoul has mature live shared memory"
- "ToneSoul is production-hardened in the public infrastructure sense"

## 5. Freeze Conditions

Freeze outward launch movement when any of these becomes true:
- entry-stack surfaces tell conflicting stories
- repeated live validation exposes the same receiver failure and it remains unfixed
- the coordination backend story becomes ambiguous again
- a public-facing document starts speaking above the evidence ladder
- protected/private residues leak into the public path

When frozen:
- do not widen launch claims
- do not open collaborator beta
- keep work limited to blocker reduction or honesty correction

## 6. Rollback / Operator Response

If a launch-facing regression is detected:

1. Stop widening claims.
2. Treat the current branch/posture as frozen.
3. Record:
   - failing surface
   - failing command
   - first bad commit or observed delta
4. Re-run the minimum pre-use check bundle.
5. Decide:
   - bounded patch
   - revert/rollback of the changed surface
   - hold and keep internal-alpha only

This is not a public deploy rollback playbook.
It is the current ToneSoul maturity rollback posture:
`return to the last honest, working baseline before widening scope again.`

## 7. Current Honest Claims

Safe to say now:
- ToneSoul has a strong bounded entry stack for later agents.
- ToneSoul has file-backed continuity with receiver guards.
- ToneSoul can distinguish tested / runtime-present / descriptive-only / document-backed claims.
- ToneSoul can expose council dissent, descriptive confidence decomposition, and suppression risk.

Not yet safe to say now:
- ToneSoul has calibrated council confidence.
- ToneSoul has proven long-horizon continuity under broad real-world load.
- ToneSoul has mature Redis/live coordination as the default shared-memory story.
- ToneSoul is ready for broad public claims of mature launch readiness.

## 8. Historical Lineage

Older docs remain useful as lineage:
- `elisa_tonesoul_operational_runbook_2026-02-24.md`
- `release_v1.0_go_nogo_2026-02-24.md`

But they are not the current default posture for this R-memory / continuity / council-realism stack.

## 9. Compressed Thesis

Current ToneSoul launch operations should be read as:

`internally usable, externally cautious, publicly bounded.`

The next honest target is collaborator beta, not public maturity theater.
