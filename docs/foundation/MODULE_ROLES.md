# Foundation Layer: Module Roles

> Purpose: give one compact map of the load-bearing runtime surfaces and the main council roles.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to runtime code and canonical contracts.

---

## Runtime Surfaces

| Surface | Responsibility |
|---|---|
| `tonesoul/runtime_adapter.py` | session load/commit bridge, governance posture, continuity handoff |
| `tonesoul/unified_pipeline.py` | orchestration hub for runtime flow and integration points |
| `tonesoul/tonebridge/*` | interpret input tone, motive, and context before downstream handling |
| `tonesoul/council/*` + `tonesoul/deliberation/*` | preserve dissent, review depth, and verdict structure before output |
| `tonesoul/vow_system.py` + `tonesoul/gates/*` | commitment checks, boundary checks, and blocking/repair posture |
| `tonesoul/memory/*` | bounded continuity, compaction, persistence, and promotion rules |
| `apps/web/` + `examples/quickstart.py` | operator/demo surfaces for observing or proving the system behavior |

## Council Roles

| Role | Responsibility |
|---|---|
| `Guardian` | safety, boundary, and harm-sensitive blocking posture |
| `Analyst` | factual and logical pressure against weak claims |
| `Critic` | counterexample, weakness discovery, and dissent preservation |
| `Advocate` | constructive utility and user-facing progress pressure |
| `Axiomatic` | constitutional consistency with axioms and vows |

## Human / Agent Responsibilities

| Actor | Responsibility |
|---|---|
| Human operator | ratifies scope, public/private boundary, and non-routine architectural direction |
| AI collaborator | implements, verifies, and reports honestly without silently promoting theory into runtime truth |

## Source Anchors

- [docs/CORE_MODULES.md](../CORE_MODULES.md)
- [docs/COUNCIL_RUNTIME.md](../COUNCIL_RUNTIME.md)
- [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](../architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md)
- [examples/quickstart.py](../../examples/quickstart.py)
