# Filename And Entry Index

> Purpose: give later agents one render-safe lookup sheet for the highest-traffic files when Windows terminal output, font support, or CJK path rendering makes path echoes hard to trust.
> Status: thin lookup aid, not a second docs registry.
> Last Updated: 2026-04-14
> Use When: PowerShell shows `??` or garbled path segments, or a later agent needs exact high-traffic paths without browsing the whole repo.

---

## Read This First

- The repo folder path may render noisily in some terminals because the parent directory uses CJK characters.
- Treat the relative paths below as canonical even if the shell renders the full absolute path badly.
- Render noise is not file corruption; see `docs/architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md`.

---

## First-Hop Files

| Lookup Key | Exact Relative Path | Job |
|---|---|---|
| `public-entry-en` | `README.md` | public English first hop |
| `public-entry-zh` | `README.zh-TW.md` | public Traditional Chinese first hop |
| `ai-start` | `docs/AI_QUICKSTART.md` | AI session first hop |
| `ai-routing` | `AI_ONBOARDING.md` | AI routing after session start |
| `foundation-packet` | `docs/foundation/README.md` | thin project packet |
| `docs-gateway` | `docs/README.md` | guided docs gateway |
| `docs-registry` | `docs/INDEX.md` | full docs registry |
| `short-board` | `task.md` | current accepted programs and short board |

## Current-Truth Files

| Lookup Key | Exact Relative Path | Job |
|---|---|---|
| `beta-preflight-md` | `docs/status/collaborator_beta_preflight_latest.md` | human-readable collaborator-beta posture |
| `beta-preflight-json` | `docs/status/collaborator_beta_preflight_latest.json` | machine-readable collaborator-beta posture |
| `convergence-audit-md` | `docs/status/tonesoul_convergence_audit_latest.md` | four-pressure convergence readout |
| `convergence-audit-json` | `docs/status/tonesoul_convergence_audit_latest.json` | machine-readable convergence readout |
| `phase722-sample` | `docs/status/phase722_external_operator_cycle_2026-04-10.md` | canonical strong external-pass sample |
| `handoff-latest-pattern` | `docs/status/codex_handoff_YYYY-MM-DD.md` | latest handoff pattern; open the newest date |

## Active Plan Files

| Lookup Key | Exact Relative Path | Job |
|---|---|---|
| `launch-short-board` | `task.md` | launch-readiness and active programs |
| `work-plan-v2` | `docs/plans/tonesoul_work_plan_v2_2026-04-14.md` | repo-aligned continuation plan |
| `four-pressure-map` | `docs/plans/tonesoul_four_pressure_point_convergence_map_2026-04-14.md` | convergence program map |

## Runtime Hotspots

| Lookup Key | Exact Relative Path | Job |
|---|---|---|
| `runtime-adapter-main` | `tonesoul/runtime_adapter.py` | public runtime-adapter API and orchestration |
| `runtime-adapter-normalization` | `tonesoul/runtime_adapter_normalization.py` | closeout/dossier normalization seam |
| `runtime-adapter-routing` | `tonesoul/runtime_adapter_routing.py` | routing classification and routing telemetry seam |
| `runtime-adapter-subject-refresh` | `tonesoul/runtime_adapter_subject_refresh.py` | subject-refresh heuristic seam |
| `unified-pipeline` | `tonesoul/unified_pipeline.py` | large pipeline runtime surface |

## Render-Safe Lookup Rules

1. If the shell shows `??`, keep using the relative path; do not rename the file in your head.
2. If a path is hard to read in terminal output, cite the lookup key plus the exact relative path from this file.
3. Use `docs/README.md` for guided routing and `docs/INDEX.md` only when the curated path is not enough.
4. If a file is not listed here, fall back to `docs/INDEX.md` rather than guessing from garbled output.
