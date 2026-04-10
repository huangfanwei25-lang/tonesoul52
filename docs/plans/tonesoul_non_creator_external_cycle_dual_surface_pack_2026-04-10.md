# ToneSoul Non-Creator / External Cycle Dual-Surface Pack (2026-04-10)

> Purpose: give Phase 722 one repeated-validation pack that uses a genuinely different bounded task shape after the first clean external pass.
> Scope: one bounded canonical short-board touch in `task.md` plus one fresh `docs/status` note, both under official claim + preflight + session-end residue.
> Status: next repeated-validation pack

---

## 1. Why This Pack Exists

Phase 722 already has one clean external/non-creator pass.

The next repetition should not simply recreate the same single-note move.

This pack exercises a different bounded task shape:

1. recover the current collaborator-beta posture from first-hop surfaces
2. handle a multi-path shared-edit claim honestly
3. update one tightly bounded canonical surface
4. leave one fresh auditable status note
5. finish through the official closeout path

If this pack passes cleanly, the result is stronger than another one-note replay, but it still does **not** justify widening launch claims.

## 2. What Counts

This pack only counts if the operator:

- is clearly lower-context or non-creator
- uses the normal first-hop entry stack
- claims and preflights both shared paths officially
- keeps `task.md` edits inside the exact bounded sections named below
- completes official `end_agent_session.py` closeout cleanly

This pack does **not** count if:

- the task expands into runtime code or general repo cleanup
- `task.md` is edited outside the named bounded sections
- host rescue determines the final wording
- manual residue is used instead of official closeout

## 3. Allowed Task Shape

Allowed:

- create `docs/status/phase722_external_dual_surface_cycle_<date>.md`
- update `task.md` only in these two places:
  - the `Phase 722` line under `Active Program: Launch Readiness And Design Legibility`
  - the `Real-world usage validation` bullet under `Current short board`
- run the official claim, preflight, docs-consistency, and session-end commands

Not allowed:

- editing any other `task.md` section
- editing `docs/status/codex_handoff_2026-04-07.md`, `docs/README.md`, or runtime code
- widening launch posture beyond collaborator-beta / conditional-go language
- ontology, domain-core, or self-improvement detours

## 4. Required Reading Stack

Read these first and stop there unless the pack itself requires more:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. `task.md`
5. `docs/status/phase726_go_nogo_2026-04-08.md`
6. `docs/status/codex_handoff_2026-04-07.md`
7. `docs/status/phase722_external_operator_cycle_2026-04-10.md`
8. this pack
9. `docs/plans/tonesoul_non_creator_external_cycle_dual_surface_note_template_2026-04-10.md`

Do not begin with broad repo archaeology.

## 5. Command Sequence

Use one fresh agent id and one shell.

If Windows/Redis discovery is unreliable in the operator environment, set:

```powershell
$env:TONESOUL_FORCE_FILE_STORE="1"
```

Then enter through the normal first-hop stack:

```bash
python scripts/start_agent_session.py --agent <your-id> --tier 0 --no-ack
python scripts/run_observer_window.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

Create the new evidence target:

```text
docs/status/phase722_external_dual_surface_cycle_<date>.md
```

Claim both shared paths:

```bash
python scripts/run_task_claim.py claim phase722-external-dual-surface-cycle --agent <your-id> --summary "Run one repeated Phase 722 dual-surface external-use validation cycle." --path task.md --path docs/status/phase722_external_dual_surface_cycle_<date>.md
```

Preflight both shared edits:

```bash
python scripts/run_shared_edit_preflight.py --agent <your-id> --path task.md --path docs/status/phase722_external_dual_surface_cycle_<date>.md
```

Write the note using:

```text
docs/plans/tonesoul_non_creator_external_cycle_dual_surface_note_template_2026-04-10.md
```

If the run honestly classifies as `strong external pass`, update only the two allowed `task.md` lines so they say, in plain language:

- two clean external/non-creator bounded cycles now exist across two different task shapes
- launch claims still stay bounded
- at least one more varied lower-context cycle is still recommended before any widening

If the run does **not** classify as `strong external pass`, leave `task.md` unchanged.

Verify docs:

```bash
python scripts/verify_docs_consistency.py --repo-root .
```

If the cycle ended cleanly, use the official closeout:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Executed one repeated dual-surface non-creator or external-use collaborator-beta cycle and left auditable residue." --closeout-status complete --carry-forward "collaborator beta remains CONDITIONAL GO and public launch stays deferred" --evidence-ref docs/status/phase726_go_nogo_2026-04-08.md --evidence-ref docs/status/phase722_external_operator_cycle_2026-04-10.md --evidence-ref docs/status/phase722_external_dual_surface_cycle_<date>.md --release-task phase722-external-dual-surface-cycle
```

If the cycle could not close cleanly, still use the official closeout and say so honestly:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Attempted one repeated dual-surface non-creator or external-use collaborator-beta cycle." --path task.md --path docs/status/phase722_external_dual_surface_cycle_<date>.md --next-action "Classify the remaining repeated-validation seam before widening launch claims." --closeout-status partial --release-task phase722-external-dual-surface-cycle
```

## 6. Host Intervention Ledger

The note must record whether host intervention happened.

Allowed host help:

- pointing back to this pack or the already-recorded first clean external cycle
- clarifying which `task.md` sections are in scope
- confirming the target note filename

Disqualifying rescue:

- dictating the classification
- rewriting the `task.md` conclusion for the operator
- replacing official closeout with handwritten residue while still calling the run clean

## 7. Classification Rules

### Strong external pass

Use this only if:

- the operator was genuinely lower-context or non-creator
- the new note was completed
- the bounded `task.md` update landed and stayed inside the allowed sections
- docs validation passed
- official `end_agent_session.py` closeout finished cleanly
- host intervention stayed bounded and non-decisive

### Useful partial

Use this if:

- meaningful first-hop / claim / preflight / note work completed
- but `task.md` stayed untouched, drifted out of scope, or official closeout did not finish cleanly

### No-count

Use this if:

- the operator never really entered through first-hop surfaces
- the run depended mainly on host/manual fallback
- or the shared-edit discipline stopped being honest

## 8. Overclaims To Avoid

Do not conclude from this pack that:

- collaborator beta is now equivalent to public launch
- repeated validation is "done" in general
- task-board updates prove runtime maturity
- multi-operator continuity is durable under broad task shapes

The honest result of a clean run is only:

`a second clean external/non-creator bounded cycle completed under a different task shape, with launch claims still intentionally constrained`
