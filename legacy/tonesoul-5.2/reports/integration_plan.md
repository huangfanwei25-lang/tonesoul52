# Integration Plan (ToneSoul 5.2)

Goal: integrate and optimize across existing ToneSoul workspaces without modifying them.

## Scope
- Read-only access to legacy workspaces.
- All new code and reports live in `5.2`.

## Strategy
1. Inventory: detect workspaces and key entrypoints.
2. Interface adapters: create thin wrappers in 5.2 that call existing entrypoints.
3. Consistency checks: detect missing/invalid entrypoints and document risks.
4. Tests: run smoke checks via wrappers (optional).

## Proposed 5.2 Modules
- `tonesoul52.config`: workspace root and entrypoints registry.
- `tonesoul52.inventory`: workspace and entrypoint inventory report.
- `tonesoul52.run_audit`: generate inventory JSON/MD.

## Next Steps
- Add adapters for dashboard, yuhun CLI, and any new entrypoints.
- Add a compatibility layer for encoding and path issues.
- Expand review report with concrete fixes (without editing legacy).
