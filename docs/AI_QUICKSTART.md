# ToneSoul AI Quickstart

> Purpose: give later AI agents the minimum operational entry surface before they read the repo in bulk.
> Last Updated: 2026-04-14
> Status: operational first-hop owner; subordinate to `AXIOMS.json`, executable code, tests, `task.md`, and canonical architecture contracts.
> Use When: first minute of a session, before touching code or making architecture claims.

---

## First 60 Seconds

Run these in order:

```bash
python scripts/start_agent_session.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_r_memory_packet.py --agent <your-id> --ack
python scripts/run_task_claim.py list
```

If you need a smaller first-hop bundle:

```bash
python scripts/start_agent_session.py --agent <your-id> --tier 0
python scripts/start_agent_session.py --agent <your-id> --tier 1
```

Use them like this:

- `tier 0` = instant gate for quick bounded work
- `tier 1` = orientation shell for feature-track continuation
- default / `--tier 2` = full bundle for deeper governance

## Read These Outputs First

- `readiness`
- `canonical_center`
- `hook_chain`
- `mutation_preflight`
- `subsystem_parity`

Then open:

- `docs/foundation/README.md`
- `task.md`

If the task touches compaction, handoff survival, or what may be compressed, open `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md` before inferring a new compression story from observer prose.

## Preflight Chain

Run only when the work needs it:

```bash
python scripts/run_shared_edit_preflight.py --agent <your-id> --path <repo-path>
python scripts/run_publish_push_preflight.py --agent <your-id>
python scripts/run_task_board_preflight.py --agent <your-id> --proposal-kind external_idea --target-path task.md
```

Use them narrowly:

- shared-edit preflight: before touching shared paths
- publish/push preflight: before outward actions
- task-board preflight: before promoting new ideas into `task.md`

## Stop Line

Do not widen into `DESIGN.md`, `docs/README.md`, `docs/INDEX.md`, `docs/architecture/`, or code until you know which concrete question you are trying to answer.

## Session End

```bash
python scripts/end_agent_session.py --agent <your-id> --summary "<short summary>" --path "<path>"
```

If you claimed a task, release it after the handoff path is complete.

## Deeper Routing

- `AI_ONBOARDING.md` = routing map after the operational handshake
- `docs/foundation/README.md` = thin project packet
- `docs/README.md` = curated docs gateway
- `docs/INDEX.md` = exhaustive registry only when needed

## Canonical Handoff Line

This file owns the operational first hop. If a later AI instance reads bulk architecture before finishing this block, it is widening too early.
