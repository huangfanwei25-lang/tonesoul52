# AI Onboarding Guide

> Purpose: route later AI agents into the right entry lane without making them bulk-read the repo.
> Last Updated: 2026-04-14
> Status: active AI routing map. Operational work starts in `docs/AI_QUICKSTART.md`; deeper lanes open only after session start and the bounded project packet.

---

## Clean First-Hop Route

1. Open `docs/AI_QUICKSTART.md`.
2. Run `python scripts/start_agent_session.py --agent <your-id>`.
3. Read `readiness`, `canonical_center`, and `hook_chain`.
4. Open `docs/foundation/README.md`.
5. Read `task.md`.
6. Only then widen into `DESIGN.md`, `docs/README.md`, `docs/architecture/`, or code.

Tiered entry options:

- `--tier 0` = instant gate for quick bounded work
- `--tier 1` = orientation shell for feature continuation
- default / `--tier 2` = full bundle for deeper governance

Do not:

- treat observer prose as execution permission
- treat compaction summary as completed work
- promote outside ideas into `task.md` before task-board parking preflight

## Entry Stack

| Lane | Owner | Use When | Not This |
|---|---|---|---|
| Operational Start | `docs/AI_QUICKSTART.md` | first minute of work | not a deep architecture lane |
| Session Handshake | `python scripts/start_agent_session.py --agent <your-id>` | you need live `readiness`, `canonical_center`, and `hook_chain` | not a docs replacement |
| Routing Map | `AI_ONBOARDING.md` | you need the next lane after the handshake | not the canonical architecture itself |
| Thin Project Packet | `docs/foundation/README.md` | you need the current project center and short board | not the whole-system guide |
| Design Center | `DESIGN.md` | you need the architectural why and non-drift invariants | not runtime truth |
| Curated Docs Gateway | `docs/README.md` | the lane is still unclear after first hop | not exhaustive browsing |
| Full Registry | `docs/INDEX.md` | you intentionally need wider inventory coverage | not a first-hop packet |

## Canonical Questions And Next Surface

- architecture or runtime shape: `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
- readiness, task track, or scope mutation: `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`
- continuity, packet, compaction, or handoff: `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
- knowledge, retrieval, or residue boundaries: `docs/architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md` and `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
- evidence posture or overclaim risk: `docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md`
- whole-system explanation: `DESIGN.md` then `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md`
- docs routing or mirror confusion: `docs/README.md` first, `docs/INDEX.md` only if needed
- historical or interpretive reading: open only after the canonical lane is already clear

## Minimal Session Commands

```bash
python scripts/start_agent_session.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_r_memory_packet.py --agent <your-id> --ack
python scripts/run_task_claim.py list
```

## Preflight Commands

Run only when the work needs them:

```bash
python scripts/run_shared_edit_preflight.py --agent <your-id> --path <repo-path>
python scripts/run_publish_push_preflight.py --agent <your-id>
python scripts/run_task_board_preflight.py --agent <your-id> --proposal-kind external_idea --target-path task.md
```

- shared-edit preflight: before touching shared paths
- publish/push preflight: before outward actions
- task-board preflight: before promoting outside ideas into `task.md`

## Session End

```bash
python scripts/end_agent_session.py --agent <your-id> --summary "<short summary>" --path "<path>"
```

If you claimed a task, release it after the handoff path is complete.

## Source Anchors

- `docs/AI_QUICKSTART.md`
- `docs/foundation/README.md`
- `task.md`
- `DESIGN.md`
- `docs/README.md`
- `docs/INDEX.md`

## Canonical Handoff Line

If an AI agent starts widening into contracts before finishing quickstart, session-start, and the bounded packet, it is reading out of order.
