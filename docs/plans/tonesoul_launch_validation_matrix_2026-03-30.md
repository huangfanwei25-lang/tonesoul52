# ToneSoul Launch Validation Matrix (2026-03-30)

> Purpose: define the minimum validation and decision surfaces for moving from internal alpha toward collaborator beta.
> Companion: `docs/plans/tonesoul_launch_maturity_program_2026-03-30.md`

## 1. Launch Levels

| Level | Meaning | What must be true |
|---|---|---|
| Internal alpha | trusted internal operators can use the system | bounded continuity works, docs are discoverable, claims stay honest |
| Collaborator beta | a small external collaborator group can use it with guidance | repeated validation exists, launch operations are clear, backend story is honest |
| Public launch | public-facing claims can be made without major maturity drift | overclaim boundaries are explicit, operations are stable, validation is broader |

## 2. Validation Matrix

| Surface | Current expectation | Evidence type | Launch level required |
|---|---|---|---|
| Session-start / packet / diagnose parity | same bounded receiver story across all three | tested + live validation | collaborator beta |
| Claim / checkpoint / compaction continuity | handoff survives repeated real use | tested + repeated live validation | collaborator beta |
| Working-style continuity | advisory-only, non-promoting, validated | tested + live validation | collaborator beta |
| Coordination backend | one honest default mode | runtime-present + explicit decision | collaborator beta |
| Council dossier / realism readout | descriptive only, not calibrated | tested + bounded wording | collaborator beta |
| Evidence readout posture | later agents can see tested/runtime/document-backed split | tested | collaborator beta |
| Launch operations / rollback | one current operator story exists | document-backed + command-backed | collaborator beta |
| Public launch claim set | launch wording is bounded by evidence | document-backed + review | public launch |

## 3. Minimum Commands And Checks

These are the current minimum checks that should stay in the launch path for this maturity program.

### Repo-Side Checks

```bash
python -m pytest tests/test_start_agent_session.py tests/test_runtime_adapter.py tests/test_diagnose.py -q
python -m ruff check tonesoul scripts tests
python scripts/verify_docs_consistency.py --repo-root .
python scripts/verify_protected_paths.py --repo-root . --strict ...
```

### Entry-Surface Checks

```bash
python scripts/start_agent_session.py --agent <agent-id> --no-ack
python scripts/run_r_memory_packet.py --agent <agent-id>
python -m tonesoul.diagnose --agent <agent-id>
```

### Validation-Wave Checks

These are not one commands-only. They require repeated runs under different states:
- clean handoff
- claim conflict
- stale compaction
- contested dossier

## 4. Go / No-Go Questions

Before collaborator beta, answer these questions explicitly:

1. Can a fresh agent enter through the normal entry stack and choose a sane next step without hidden chat history?
2. Is the default coordination mode stated honestly?
3. Can the system explain what is tested vs runtime-present vs descriptive-only without long rereads?
4. Does one current launch operations posture exist?
5. Are remaining blockers explicit rather than socially ignored?

If any answer is "no", beta should stay closed.

## 5. Blocking Conditions

The following should block collaborator beta:
- repeated live validation still produces the same unaddressed receiver failures
- the launch-default coordination mode is still ambiguous
- public wording still overclaims calibrated council quality or continuity effectiveness
- rollback / operator posture is still spread across historical docs only

## 6. Non-Blocking Imperfections

These should not block collaborator beta by themselves:
- Redis is not yet the default
- public launch is still deferred
- some philosophical contracts remain descriptive-only
- not every prompt family has been normalized

## 7. Review Cadence

Recommended cadence:
- after Phase 721: refresh the maturity estimate
- after Phase 722: decide whether the current short board moved
- after Phase 724: run a beta go/no-go review

## Compressed Thesis

Do not ask:
"does ToneSoul look advanced enough to launch?"

Ask:
"can a fresh operator or agent enter, act, stay honest, and recover safely under current evidence?"
