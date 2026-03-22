# ToneSoul Architecture Memory Anchor (2026-03-22)

## Purpose

This is a repo-safe memory anchor for later agents.

Do not treat ToneSoul as a larger prompt bundle or a loose collection of markdown notes.
Treat it as an externalized cognitive operating system.

## Highest-Priority Architecture Source

Canonical path:

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`

If future work is ambiguous, open the externalized architecture anchor first, then the eight-layer convergence map.

## Memory Rule

Store this architecture direction in repo memory as the primary interpretation:

- external modules are the source of truth
- markdown should be compiled into artifacts before runtime use
- stable public behavior may later be distilled into adapters
- private memory must remain external, deletable, and auditable

## Operational Consequence

When choosing between:

- longer prompts vs structured artifacts
- hidden model behavior vs explicit verifiers
- raw private memory in weights vs external vault retrieval

prefer:

- structured artifacts
- explicit verifiers
- external vault retrieval

## Reading Order

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
3. `docs/status/tonesoul_knowledge_graph_latest.md`
4. `docs/status/changed_surface_checks_latest.md`
5. `AI_ONBOARDING.md`

## Note

This anchor exists because later agents repeatedly lost the architecture thread when relying only on large markdown context windows.
