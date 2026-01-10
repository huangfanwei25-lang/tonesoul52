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
- CLI entry: apps/cli/app.py (imports yuhun from legacy/archives/ToneSoul-Repo)
- Constitution/axioms: AXIOMS.json and law/constitution.json
- Truth structure: docs/TRUTH_STRUCTURE.md captures the living governance + philosophy spine.

Known drift vs docs:
- README references body/ and src/core/, but there is no body/ and src/ is empty today.

Directory triage (tentative; confirm before deleting/moving):
- Core code: tonesoul/, apps/, tools/, scripts/, tests/
- Docs/specs: docs/, law/, spec/, constitution/, knowledge/, knowledge_base/
- Legacy/archive: legacy/ (non-doc artifacts after duplicates were pruned), experiments/, examples/, ?主悉/, tone-soul-integrity-main/,
  ToneSoul-Architecture-Engine-main/, tonesoul-codex-main/
- Data/logs/cache: data/, evidence/, memory/, memory_vault/, simulation_logs/, reports/, temp/, run/,
  __pycache__/, .pytest_cache/, .venv/

Working rules:
- Prefer edits in tonesoul/ and apps/ unless the user says to change legacy.
- Do not delete or move files without explicit user approval.
- If a path seems duplicated, ask which is canonical before changes.
- Update this file after major structural changes.
- Use legacy/ (archived_docs/ duplicates were removed) only for drift comparison, not as current canon—point findings back to docs/TRUTH_STRUCTURE.md.

Quick commands:
- Dashboard: python apps/dashboard/run_dashboard.py
- CLI: python apps/cli/app.py
