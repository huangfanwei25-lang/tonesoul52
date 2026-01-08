# Dependency Alignment Report (ToneSoul 5.2)

## Sources Checked
- `5.2/pyproject.toml`
- Import scan (5.2/tonesoul52): numpy, yaml, streamlit, pandas, plotly, cairosvg, PIL

## Observed Imports (runtime usage)
- `numpy`: `5.2/tonesoul52/ystm/representation.py`, `5.2/tonesoul52/ystm/terrain.py`, `5.2/tonesoul52/ystm/projection.py`, `5.2/tonesoul52/ystm/governance.py`
- `pyyaml`: `5.2/tonesoul52/context_compiler.py`, `5.2/tonesoul52/constraint_stack.py`, `5.2/tonesoul52/frame_router.py`, `5.2/tonesoul52/generation_orch.py`, `5.2/tonesoul52/memory_manager.py`, `5.2/tonesoul52/skill_gate.py`, `5.2/tonesoul52/skill_promoter.py`, `5.2/tonesoul52/yss_pipeline.py`, `5.2/tonesoul52/yss_gates.py`
- `streamlit`, `pandas`, `plotly`: `5.2/tonesoul52/audit_dashboard.py`
- `cairosvg`: `5.2/tonesoul52/ystm/demo.py` (PNG export)
- `PIL` (pillow): `5.2/tonesoul52/ystm/render.py` (fallback PNG renderer)

## Current Deps (5.2/pyproject.toml)
- Runtime: numpy, pyyaml, rich
- Optional: dashboard (streamlit, pandas, plotly)
- Optional: ystm_viz (cairosvg, pillow)
- Dev: pytest, black, ruff

## Alignment Summary
- Core runtime deps match required imports for YSTM/YSS.
- Optional extras cover dashboard and visualization paths.
- `rich` is available for CLI formatting (no direct imports yet).

## Recommendation
- Keep optional extras to avoid pulling UI/PNG dependencies unless needed.
