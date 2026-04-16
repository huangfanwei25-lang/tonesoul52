# ToneSoul Non-Creator / External Cycle Preflight-Refresh Pack (2026-04-15)

> Purpose: give Phase 722 one third repeated-validation pack that exercises a different bounded task shape by refreshing the canonical collaborator-beta preflight artifacts, leaving one fresh status note, and touching the short board only if the run is honestly clean.
> Scope: one bounded `task.md` touch, one bounded generated current-truth refresh for `collaborator_beta_preflight_latest.{json,md}`, and one fresh `docs/status` note under official claim + preflight + session-end residue.
> Status: next repeated-validation pack

---

## 1. Why This Pack Exists

Phase 722 now has two clean bounded external/non-creator passes across two task shapes.

The next repetition should still stay small, but it should not just replay:

- one status note only, or
- one `task.md` touch plus one fresh status note

This pack exercises a third bounded task shape:

1. recover the current collaborator-beta posture from first-hop surfaces
2. claim and preflight a mixed set of generated and manual shared paths honestly
3. refresh the canonical `collaborator_beta_preflight_latest` artifacts through the official script
4. leave one fresh auditable status note
5. update only the two allowed `task.md` lines if the run honestly counts as clean
6. finish through the official closeout path

If this pack passes cleanly, it strengthens repeated evidence without widening public-launch claims by itself.

## 2. What Counts

This pack only counts if the operator:

- is clearly lower-context or non-creator
- uses the normal first-hop entry stack
- claims and preflights every shared path officially
- refreshes `collaborator_beta_preflight_latest.{json,md}` through `run_collaborator_beta_preflight.py`, not by hand
- keeps `task.md` edits inside the exact bounded sections named below
- completes official `end_agent_session.py` closeout cleanly

This pack does **not** count if:

- the task expands into runtime code or general repo cleanup
- the operator hand-edits the generated preflight artifacts instead of regenerating them
- `task.md` is edited outside the named bounded sections
- host rescue determines the classification
- manual residue replaces official closeout

## 3. Allowed Task Shape

Allowed:

- create `docs/status/phase722_external_preflight_refresh_cycle_<date>.md`
- refresh:
  - `docs/status/collaborator_beta_preflight_latest.json`
  - `docs/status/collaborator_beta_preflight_latest.md`
- update `task.md` only in these two places, and only if the run honestly counts as `strong external pass`:
  - the `Phase 722` line under `Active Program: Launch Readiness And Design Legibility`
  - the `Real-world usage validation` bullet under `Current short board`
- run the official claim, preflight, preflight-refresh, docs-consistency, and session-end commands

Not allowed:

- editing any other `task.md` section
- editing `docs/README.md`, handoff notes, or runtime code during the counted run
- widening launch posture beyond collaborator-beta / public-launch-deferred language
- ontology, domain-core, or self-improvement detours

## 4. Required Reading Stack

Read these first and stop there unless the pack itself requires more:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. `task.md`
5. `docs/status/collaborator_beta_preflight_latest.md`
6. `docs/status/phase726_go_nogo_2026-04-08.md`
7. `docs/status/phase722_external_operator_cycle_2026-04-10.md`
8. `docs/status/phase722_external_dual_surface_cycle_2026-04-14.md`
9. this pack
10. `docs/plans/tonesoul_non_creator_external_cycle_preflight_refresh_note_template_2026-04-15.md`

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
docs/status/phase722_external_preflight_refresh_cycle_<date>.md
```

Claim all shared paths:

```bash
python scripts/run_task_claim.py claim phase722-external-preflight-refresh-cycle --agent <your-id> --summary "Run one repeated Phase 722 preflight-refresh external-use validation cycle." --path task.md --path docs/status/collaborator_beta_preflight_latest.json --path docs/status/collaborator_beta_preflight_latest.md --path docs/status/phase722_external_preflight_refresh_cycle_<date>.md
```

Preflight all shared edits:

```bash
python scripts/run_shared_edit_preflight.py --agent <your-id> --path task.md --path docs/status/collaborator_beta_preflight_latest.json --path docs/status/collaborator_beta_preflight_latest.md --path docs/status/phase722_external_preflight_refresh_cycle_<date>.md
```

Refresh the canonical preflight artifacts:

```bash
python scripts/run_collaborator_beta_preflight.py --agent <your-id> --json-out docs/status/collaborator_beta_preflight_latest.json --markdown-out docs/status/collaborator_beta_preflight_latest.md
```

Write the note using:

```text
docs/plans/tonesoul_non_creator_external_cycle_preflight_refresh_note_template_2026-04-15.md
```

If the run honestly classifies as `strong external pass`, update only the two allowed `task.md` lines so they say, in plain language:

- three clean external/non-creator bounded cycles now exist across three different task shapes
- public launch still stays deferred and launch claims stay bounded
- the next meaningful move is a refreshed `Phase 726` review / current-truth go-no-go check, not automatic widening

If the run does **not** classify as `strong external pass`, leave `task.md` unchanged.

Verify docs:

```bash
python scripts/verify_docs_consistency.py --repo-root .
```

If the cycle ended cleanly, use the official closeout:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Executed one preflight-refresh non-creator or external-use collaborator-beta cycle and left auditable residue." --closeout-status complete --carry-forward "Phase 722 now has three clean bounded cycles across three task shapes; refresh Phase 726 review before any claim widening." --evidence-ref docs/status/phase726_go_nogo_2026-04-08.md --evidence-ref docs/status/collaborator_beta_preflight_latest.md --evidence-ref docs/status/phase722_external_dual_surface_cycle_2026-04-14.md --evidence-ref docs/status/phase722_external_preflight_refresh_cycle_<date>.md --release-task phase722-external-preflight-refresh-cycle
```

If the cycle could not close cleanly, still use the official closeout and say so honestly:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Attempted one repeated preflight-refresh non-creator or external-use collaborator-beta cycle." --path task.md --path docs/status/collaborator_beta_preflight_latest.json --path docs/status/collaborator_beta_preflight_latest.md --path docs/status/phase722_external_preflight_refresh_cycle_<date>.md --next-action "Classify the remaining repeated-validation seam before widening launch claims." --closeout-status partial --release-task phase722-external-preflight-refresh-cycle
```

## 6. Host Intervention Ledger

The note must record whether host intervention happened.

Allowed host help:

- pointing back to this pack or already-recorded Phase 722 evidence notes
- clarifying which `task.md` sections are in scope
- confirming the generated preflight command and target paths

Disqualifying rescue:

- dictating the classification
- rewriting the `task.md` conclusion for the operator
- hand-editing generated preflight artifacts while still calling the run clean
- replacing official closeout with handwritten residue while still calling the run clean

## 7. Classification Rules

### Strong external pass

Use this only if:

- the operator was genuinely lower-context or non-creator
- the new note was completed
- the bounded preflight-refresh command completed and wrote the canonical artifacts
- the bounded `task.md` update landed and stayed inside the allowed sections
- docs validation passed
- official `end_agent_session.py` closeout finished cleanly
- host intervention stayed bounded and non-decisive

### Useful partial

Use this if:

- meaningful first-hop / claim / preflight / generated-refresh / note work completed
- but `task.md` stayed untouched, generated artifacts failed to refresh cleanly, drifted out of scope, or official closeout did not finish cleanly

### No-count

Use this if:

- the operator never really entered through first-hop surfaces
- the run depended mainly on host/manual fallback
- the generated artifacts were hand-patched instead of regenerated
- or the shared-edit discipline stopped being honest

## 8. Overclaims To Avoid

Do not conclude from this pack that:

- collaborator beta is now equivalent to public launch
- three clean bounded cycles mean repeated validation is "done"
- preflight-refresh evidence alone proves runtime maturity
- launch wording should widen automatically without a fresh Phase 726 review

The honest result of a clean run is only:

`a third clean external/non-creator bounded cycle completed under a new task shape that refreshed canonical preflight truth without widening launch claims`
