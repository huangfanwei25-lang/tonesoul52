# ToneSoul Non-Creator / External Cycle Pack (2026-04-10)

> Purpose: give Phase 722 one current, bounded, pack-compliant path for recording a real non-creator or external-use governance-aware cycle.
> Scope: docs/status only, with official claim + preflight + session-end residue.
> Status: current execution pack

---

## 1. Why This Pack Exists

Phase 722 no longer needs more abstract wording.

It needs one real cycle that proves a lower-context or non-creator operator can:

1. enter through normal first-hop surfaces
2. understand the current collaborator-beta posture
3. claim and preflight a shared edit honestly
4. leave one bounded status artifact
5. end the session through the official closeout path

The pack is intentionally narrow so the result can be classified honestly.

## 2. What Counts

This pack only counts if the operator:

- is clearly not relying on hidden chat-history reconstruction
- stays inside the bounded docs/status task
- uses the official `run_task_claim.py` and `run_shared_edit_preflight.py` path
- uses the official `end_agent_session.py` path for final closeout

This pack does **not** count if:

- the work silently expands into runtime code
- host rescue becomes the real reason the task succeeded
- closeout falls back to handwritten compaction/checkpoint residue instead of the official command

## 3. Allowed Task Shape

Allowed:

- create or update one `docs/status/phase722_external_operator_cycle_<date>.md` note
- read first-hop orientation surfaces
- run bounded governance-aware inspection commands
- classify the cycle honestly

Not allowed:

- runtime code changes
- launch-language widening
- ontology/domain-core work
- self-improvement trial admission
- hidden manual residue written outside the official closeout path

## 4. Required Reading Stack

The operator should read only these first:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. `task.md`
5. `docs/status/phase726_go_nogo_2026-04-08.md`
6. `docs/status/codex_handoff_2026-04-07.md`
7. this pack
8. `docs/plans/tonesoul_non_creator_external_cycle_note_template_2026-04-10.md`

Do not begin with broad repo archaeology.

## 5. Command Sequence

Use one fresh agent id and one shell.

If Windows/Redis discovery is unreliable in the operator environment, set:

```powershell
$env:TONESOUL_FORCE_FILE_STORE="1"
```

Then run:

```bash
python scripts/start_agent_session.py --agent <your-id> --tier 0 --no-ack
python scripts/run_observer_window.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

Create the evidence target:

```text
docs/status/phase722_external_operator_cycle_<date>.md
```

Claim it:

```bash
python scripts/run_task_claim.py claim phase722-external-operator-cycle --agent <your-id> --summary "Run one bounded non-creator or external-use governance-aware docs cycle." --path docs/status/phase722_external_operator_cycle_<date>.md
```

Then preflight the shared edit:

```bash
python scripts/run_shared_edit_preflight.py --agent <your-id> --path docs/status/phase722_external_operator_cycle_<date>.md
```

Write the note using the template:

```text
docs/plans/tonesoul_non_creator_external_cycle_note_template_2026-04-10.md
```

Verify docs:

```bash
python scripts/verify_docs_consistency.py --repo-root .
```

If the cycle ended cleanly, use the official closeout:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Executed one bounded non-creator or external-use collaborator-beta cycle and left auditable residue." --closeout-status complete --carry-forward "collaborator beta remains CONDITIONAL GO and public launch stays deferred" --evidence-ref docs/status/phase726_go_nogo_2026-04-08.md --evidence-ref docs/status/collaborator_beta_preflight_latest.md --evidence-ref docs/status/phase722_external_operator_cycle_<date>.md --release-task phase722-external-operator-cycle
```

If the cycle could not close cleanly, still use the official closeout and say so honestly:

```bash
python scripts/end_agent_session.py --agent <your-id> --mode both --summary "Attempted one bounded non-creator or external-use collaborator-beta cycle." --path docs/status/phase722_external_operator_cycle_<date>.md --next-action "Classify the remaining external-use seam before widening launch claims." --closeout-status partial --release-task phase722-external-operator-cycle
```

## 6. Host Intervention Ledger

The note must say whether host intervention happened.

Allowed host help:

- pointing the operator back to this pack
- clarifying an existing first-hop surface
- confirming which file to write

Disqualifying rescue:

- telling the operator what the result should say
- providing hidden repo history that first-hop surfaces did not expose
- replacing the official closeout path with manual residue while still calling the result clean

## 7. Classification Rules

### Strong external pass

Use this only if:

- the operator was genuinely lower-context or non-creator
- the bounded task completed
- docs validation passed
- official `end_agent_session.py` closeout finished cleanly
- host intervention stayed bounded and non-decisive

### Useful partial

Use this if:

- the operator completed meaningful first-hop/claim/preflight/note work
- but official closeout did not finish cleanly, or host rescue became necessary

### No-count

Use this if:

- the operator never really entered through first-hop surfaces
- the bounded task was not completed
- or the result mainly reflects host/manual fallback instead of the official path

## 8. Overclaims To Avoid

Do not conclude from one successful cycle that:

- public launch is now justified
- external collaboration is solved in general
- runtime authority is broader than it was
- ToneSoul has proven durable multi-operator continuity

The honest result of a successful run is only:

`one real bounded non-creator / external-use cycle completed under the current collaborator-beta guardrails`
