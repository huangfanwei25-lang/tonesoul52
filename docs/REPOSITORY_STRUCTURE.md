# ToneSoul Repository Structure

> Purpose: current repo layout and application-surface authority map.
> Last updated: 2026-05-10
> Status: current structure guide, not historical lineage.

## Read This First

- This file answers "where does this work belong?" before a contributor opens the whole repository.
- If an older document describes `apps/dashboard/` as HTML-only, or collapses `site/`, `apps/web/`, and dashboard surfaces together, prefer this file and the README inside the target surface.
- Historical docs can preserve older wording for lineage, but they should not outrank this current routing map.

## Top-Level Map

| Path | Role |
|---|---|
| `tonesoul/` | Core runtime, governance, memory, council, and orchestration code |
| `apps/` | User-facing, operator-facing, and auxiliary application surfaces |
| `site/` | Public static marketing and docs site |
| `api/` | Python serverless/backend API surfaces |
| `docs/` | Canonical docs, status artifacts, plans, and archived design references |
| `tests/` | Regression, red-team, and subsystem tests |
| `scripts/` | CLI tools, dashboards, validators, and automation entrypoints |
| `spec/` | Formal specs and schemas |
| `law/` | Governance law and policy-oriented documents |
| `memory/` | Local continuity data; do not treat runtime memory as public-source material by default |

## Application Surface Authority

| Surface | Role | Stack | Canonical entry | Boundary |
|---|---|---|---|---|
| `site/` | Public static site | HTML/CSS | `site/index.html` | Public marketing/docs surface. Not the interactive app and not the operator shell. |
| `apps/web/` | Interactive web app | Next.js + TypeScript | `apps/web/src/app/page.tsx` | Current chat/navigator surface. Not the public static site and not the operator shell. |
| `apps/dashboard/` | Operator shell | Python + Streamlit | `python apps/dashboard/run_dashboard.py` | Tiered operator workspace. `index.html` and `world.html` are legacy previews, not the canonical shell. |
| `apps/council-playground/` | Static observability playground | HTML/CSS/JS | `apps/council-playground/index.html` | Auxiliary read-only demo/prototype. Not the operator shell and not the main product frontend. |
| `scripts/tension_dashboard.py` | CLI observability dashboard | Python CLI | `python scripts/tension_dashboard.py --work-category research` | Fast runtime inspection. Not a GUI workspace. |

## `apps/` Breakdown

| Path | Role | Notes |
|---|---|---|
| `apps/web/` | Interactive frontend | Next.js app router, API proxies, chat/navigator UI |
| `apps/dashboard/` | Operator workspace | Streamlit shell and supporting frontend modules |
| `apps/council-playground/` | Static backend-observation prototype | HTML/CSS/JS playground/demo surface |
| `apps/api/` | App-facing backend server | Python backend entry surface |
| `apps/cli/` | CLI tooling | Terminal-oriented workflows |
| `apps/simulations/` | Simulations and experiments | Python simulation surfaces |

## Runtime And State Layers

| Path | Role |
|---|---|
| `tonesoul/governance/` | Governance kernels, vows, contracts, and validation logic |
| `tonesoul/council/` | Deliberation, perspectives, verdict shaping, and trace structures |
| `tonesoul/memory/` | Memory, decay, compaction, and persistence logic |
| `tonesoul/perception/` | Input normalization and sensing helpers |
| `tonesoul/pipeline/` | End-to-end orchestration and execution flow |
| `tonesoul/observability/` | Runtime signals, metrics, and reporting helpers |
| `memory/` | Local continuity data, journals, crystals, and related artifacts |

## Documentation And Archive Surfaces

| Path | Role |
|---|---|
| `docs/README.md` | Guided docs entrypoint |
| `docs/INDEX.md` | Full registry when the guided lane is not enough |
| `docs/status/` | Machine-readable and human-readable status artifacts |
| `docs/plans/` | Bounded work plans not yet promoted into canonical entry docs |

## Validation Entry Points

From repo root:

```bash
python -m pytest tests/ --collect-only -q
python -m ruff check tonesoul tests
npm --prefix apps/web run lint
npm --prefix apps/web run build
```

Meaning:

- Python test execution still lives at repo root because the repository is primarily Python-governed.
- Python test counts are dynamic: inspect `tests/` directly or read `docs/status/repo_healthcheck_latest.json` (`python_tests`) instead of copying a static count into this map.
- Web validation is scoped through `apps/web`; root `package.json` is not the source of truth for web app dependencies.
- CI runs more gates than the commands above, including docs consistency, architecture boundaries, red-team, package integrity, web quality, memory hygiene, and repository health.

## Practical Routing Rules

- If you need the public site, open `site/`.
- If you need the interactive app, open `apps/web/`.
- If you need the operator workspace, open `apps/dashboard/`.
- If you need a static observability demo, open `apps/council-playground/`.
- If you need fast CLI observability, run `scripts/tension_dashboard.py`.
