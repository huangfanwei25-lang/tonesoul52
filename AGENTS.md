# AGENTS.md
Purpose: a short, stable onboarding snapshot for any AI or new contributor.

If you are an AI assistant:
- Read this file first.
- Then read README.md and MGGI_SPEC.md for the high-level architecture.
- Use HANDOFF.md for the most recent milestone/changes.
- Use docs/GETTING_STARTED.md and docs/CORE_MODULES.md if you touch architecture.

Current source of truth (filesystem check):
- Active engine code: tonesoul/ (governance + core services, many run_* scripts).
- Dashboard entry: apps/dashboard/run_dashboard.py -> apps/dashboard/frontend/app.py
- CLI entry: apps/cli/app.py (imports yuhun from repo root; falls back to legacy/archives/ToneSoul-Repo if present)
- Constitution/axioms: AXIOMS.json and law/constitution.json
- Truth structure: docs/TRUTH_STRUCTURE.md captures the living governance + philosophy spine.

Known drift vs docs:
- Some docs (e.g. docs/ADR-001-dual-track-resolution.md, docs/TRUTH_STRUCTURE.md) reference legacy paths like body/, src/core/, or legacy/ for historical context; those directories are not present in this workspace.

Directory triage (tentative; confirm before deleting/moving):
- Core code: tonesoul/, apps/, api/, tests/
- Docs/specs: docs/, law/, spec/, constitution/, knowledge/, knowledge_base/
- Legacy/archive: .archive/, experiments/, examples/, PARADOXES/, soul/
- Data/logs/cache: data/, evidence/, memory/, memory_vault/, simulation_logs/, reports/, temp/, run/,
  __pycache__/, .pytest_cache/, .venv/

Working rules:
- Prefer edits in tonesoul/ and apps/ unless the user says to change legacy.
- Do not delete or move files without explicit user approval.
- If a path seems duplicated, ask which is canonical before changes.
- Update this file after major structural changes.
- Use .archive/ only for drift comparison, not as current canon—point findings back to docs/TRUTH_STRUCTURE.md.

Quick commands:
- Dashboard: python apps/dashboard/run_dashboard.py
- CLI: python apps/cli/app.py
