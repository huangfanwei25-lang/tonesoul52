# Engineering Mirror Ownership Map

> Purpose: declare the canonical owner, mirror lane, and sync direction for the duplicated engineering document family.
> Status: active ownership map for convergence cleanup.
> Last Updated: 2026-03-22

---

## Contract

- Canonical owner root: `docs/engineering/`
- Mirror root: `law/engineering/`
- Sync direction: `docs/engineering/` -> `law/engineering/`
- Read order:
  1. open `docs/engineering/` for current engineering content
  2. treat `law/engineering/` as the mirrored normative lane
  3. if the two disagree, prefer the canonical owner until the mirror is resynced

## Why This Boundary Exists

The engineering family currently exists in two lanes because the repository has
both a documentation surface and a law/governance surface.

That duplication only remains safe if the repo names one owner and one mirror.
Without an explicit owner, later edits land in different places and AI readers
incorrectly treat two similar files as parallel truth sources.

## Current Policy

1. `docs/engineering/` owns the editable engineering text.
2. `law/engineering/` mirrors the same material for the law/governance lane.
3. New engineering clarifications should land in `docs/engineering/` first.
4. Mirror drift should be corrected by syncing from `docs/engineering/`, not by
   hand-diverging both copies.
5. Canonical-only files are allowed when the content is operational rather than
   part of the mirrored engineering book set.

## Current Pairing

| Relative Path | Canonical Owner | Mirror Lane | Expected Posture |
|---|---|---|---|
| `README.md` | `docs/engineering/README.md` | `law/engineering/README.md` | role-scoped pair |
| `OVERVIEW.md` | `docs/engineering/OVERVIEW.md` | `law/engineering/OVERVIEW.md` | exact mirror |
| `APPENDIX_ENGINEERING.md` | `docs/engineering/APPENDIX_ENGINEERING.md` | `law/engineering/APPENDIX_ENGINEERING.md` | exact mirror |
| `VOLUME_I_ENGINEERING_FOUNDATION.md` | `docs/engineering/VOLUME_I_ENGINEERING_FOUNDATION.md` | `law/engineering/VOLUME_I_ENGINEERING_FOUNDATION.md` | exact mirror |
| `VOLUME_II_ENGINEERING_DYNAMICS.md` | `docs/engineering/VOLUME_II_ENGINEERING_DYNAMICS.md` | `law/engineering/VOLUME_II_ENGINEERING_DYNAMICS.md` | exact mirror |
| `VOLUME_III_ENGINEERING_RESPONSIBILITY.md` | `docs/engineering/VOLUME_III_ENGINEERING_RESPONSIBILITY.md` | `law/engineering/VOLUME_III_ENGINEERING_RESPONSIBILITY.md` | exact mirror |
| `VOLUME_IV_ENGINEERING_EVOLUTION.md` | `docs/engineering/VOLUME_IV_ENGINEERING_EVOLUTION.md` | `law/engineering/VOLUME_IV_ENGINEERING_EVOLUTION.md` | exact mirror |
| `VOLUME_V_ENGINEERING_CLOSURE.md` | `docs/engineering/VOLUME_V_ENGINEERING_CLOSURE.md` | `law/engineering/VOLUME_V_ENGINEERING_CLOSURE.md` | exact mirror |
| `DIAGRAMS/cqrs_tonesoul_flow.md` | `docs/engineering/DIAGRAMS/cqrs_tonesoul_flow.md` | `law/engineering/DIAGRAMS/cqrs_tonesoul_flow.md` | exact mirror |
| `DIAGRAMS/drift_score_visualization.md` | `docs/engineering/DIAGRAMS/drift_score_visualization.md` | `law/engineering/DIAGRAMS/drift_score_visualization.md` | exact mirror |
| `DIAGRAMS/three_vector_structure.md` | `docs/engineering/DIAGRAMS/three_vector_structure.md` | `law/engineering/DIAGRAMS/three_vector_structure.md` | exact mirror |
| `EXAMPLES/drift_score_example.md` | `docs/engineering/EXAMPLES/drift_score_example.md` | `law/engineering/EXAMPLES/drift_score_example.md` | exact mirror |
| `EXAMPLES/poav_report_example.md` | `docs/engineering/EXAMPLES/poav_report_example.md` | `law/engineering/EXAMPLES/poav_report_example.md` | exact mirror |
| `EXAMPLES/step_ledger_example.md` | `docs/engineering/EXAMPLES/step_ledger_example.md` | `law/engineering/EXAMPLES/step_ledger_example.md` | exact mirror |
| `EXAMPLES/time_island_example.md` | `docs/engineering/EXAMPLES/time_island_example.md` | `law/engineering/EXAMPLES/time_island_example.md` | exact mirror |

## Canonical-Only Surface

- `docs/engineering/prompt_hardening.md`
  - Currently has no `law/engineering/` mirror.
  - This is acceptable until the repo decides it belongs in the mirrored book set.

## Retrieval Guidance

- If you need the current engineering explanation, read `docs/engineering/`.
- If you are auditing mirror hygiene, read `docs/status/engineering_mirror_ownership_latest.json`.
- If the mirror family drifts again, fix the canonical file first and then resync the mirror.
