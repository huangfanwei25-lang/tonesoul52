# ToneSoul Convergence Audit Latest

- generated_at: 2026-04-14T15:00:03Z
- source: `scripts/run_tonesoul_convergence_audit.py`
- top_risk: `context_bloat`
- critical_count: `1`
- high_count: `2`

| area | severity | summary |
| --- | --- | --- |
| context_bloat | CRITICAL | Context load is objectively high: the repo carries a very large docs surface and at least two runtime modules now exceed 2000 lines. |
| duplication | HIGH | Overview and entry surfaces are still structurally numerous, but most of them now self-label their role instead of silently competing for ownership. |
| layer_confusion | HIGH | Multiple knowledge, memory, and paradox lanes still coexist at the filesystem level. Boundary contracts exist for the main families, but the hierarchy remains cognitively expensive. |
| pseudo_formulas | LOW | Formula honesty improved in the main entry and glossary surfaces, but some formula mentions still float without a nearby status label or executable owner reference. |

## Context Bloat

- severity: `critical`
- `docs_markdown_file_count`: `540`
- `docs_plan_file_count`: `168`
- `doc_authority_group_count`: `25`
- `doc_authority_tracked_file_count`: `103`
- `python_files_over_2000_lines`: `3`
- evidence:
  - docs/**/*.md=540
  - docs/plans/*.md=168
  - doc authority groups=25
  - python files >=2000 lines=3
- samples:
  - `{"path": "tonesoul/unified_pipeline.py", "line_count": 3627}`
  - `{"path": "tonesoul/runtime_adapter.py", "line_count": 2545}`
  - `{"path": "tonesoul/dream_observability.py", "line_count": 2431}`
  - `{"path": "tonesoul/autonomous_schedule.py", "line_count": 1654}`
  - `{"path": "tonesoul/self_improvement_trial_wave.py", "line_count": 1560}`
- next_move: Hold the first-hop path fixed and split the largest runtime files only after boundary and entry pressure stay stable.

## Duplication

- severity: `high`
- `overview_surface_count`: `9`
- `entry_like_surface_count`: `7`
- `labeled_surface_count`: `9`
- `label_coverage`: `1.0`
- `max_pairwise_overlap`: `0.528`
- evidence:
  - tracked overview surfaces=9
  - entry-like surfaces=7
  - labeled surfaces=9
- samples:
  - `{"pair": ["docs/README.md", "docs/INDEX.md"], "similarity": 0.528}`
  - `{"pair": ["AI_ONBOARDING.md", "docs/AI_QUICKSTART.md"], "similarity": 0.5}`
  - `{"pair": ["DESIGN.md", "docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md"], "similarity": 0.356}`
- next_move: Keep one owner per overview class and reject new repo-wide explainers unless one old owner is demoted.

## Layer Confusion

- severity: `high`
- `family_count`: `3`
- `family_count_with_multiple_surfaces`: `3`
- `family_count_missing_contracts`: `0`
- `tracked_layer_surface_count`: `8`
- evidence:
  - layer families=3
  - families with >=2 surfaces=3
  - tracked layer surfaces=8
- samples:
  - `{"family": "knowledge", "surface_count": 2, "contract_count": 3, "surfaces": ["knowledge", "knowledge_base"]}`
  - `{"family": "memory", "surface_count": 4, "contract_count": 3, "surfaces": ["memory", "memory_base", "OpenClaw-Memory", "tonesoul/memory"]}`
  - `{"family": "paradox", "surface_count": 2, "contract_count": 2, "surfaces": ["PARADOXES", "tests/fixtures/paradoxes"]}`
- next_move: Treat boundary contracts as required companions for any rename, merge, or promotion across knowledge-like lanes.

## Pseudo-Formulas

- severity: `low`
- `formula_hit_count`: `33`
- `labeled_formula_count`: `33`
- `owner_linked_formula_count`: `33`
- `unlabeled_formula_count`: `0`
- `owner_gap_count`: `0`
- `unlabeled_ratio`: `0.0`
- `owner_gap_ratio`: `0.0`
- `locked_instruction_formula_hit_count`: `4`
- `locked_instruction_owner_gap_count`: `1`
- evidence:
  - formula hits=33
  - labeled hits=33
  - owner-linked hits=33
  - locked instruction residual hits=4 (not scored)
- next_move: Require status plus owner in the same local formula window before repeating a symbolic equation as runtime truth.
