# L7 Retrieval Contract Latest

- generated_at: 2026-03-22T10:40:46Z
- contract_version: v1
- canonical_contract: `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`

## Default Reading Order
- `architecture_anchor`
- `boundary_map`
- `status_artifact`
- `research_note`
- `implementation_source`
- `verifier`

## Surfaces
- `architecture_anchor` (rank 1): north-star architecture, layer meaning, repo-wide interpretation
  - `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
- `boundary_map` (rank 2): surface separation and authority disambiguation
  - `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
  - `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
- `status_artifact` (rank 3): latest generated repo state, machine-readable operational truth
  - `docs/status/tonesoul_knowledge_graph_latest.md`
  - `docs/status/changed_surface_checks_latest.md`
  - `docs/status/repo_healthcheck_latest.json`
- `research_note` (rank 4): external evidence and non-canonical comparison
  - `docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md`
- `implementation_source` (rank 5): actual runtime behavior when prose is insufficient
  - `tonesoul/unified_pipeline.py`
  - `scripts/run_changed_surface_checks.py`
- `verifier` (rank 6): mechanical truth checks when drift risk is high
  - `scripts/verify_docs_consistency.py`
  - `scripts/verify_protected_paths.py`
  - `scripts/run_changed_surface_checks.py`

## Question Routes
- `architecture_meaning`: first `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`, then `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`, then `implementation_source`
- `knowledge_surface_authority`: first `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`, then `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`, then `status_artifact`
- `latest_repo_state`: first `docs/status/repo_healthcheck_latest.json`, then `docs/status/tonesoul_knowledge_graph_latest.md`, then `verifier`
- `change_validation`: first `scripts/run_changed_surface_checks.py`, then `docs/status/changed_surface_checks_latest.md`, then `verifier`
- `external_design_influence`: first `docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md`, then `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`, then `human_review`

## Verifier Checks
- `protected_paths`: `python scripts/verify_protected_paths.py --repo-root . --strict`
  - use_when: sensitive files, memory lanes, or protected docs are touched
- `docs_consistency`: `python scripts/verify_docs_consistency.py --repo-root .`
  - use_when: authority docs, status surfaces, or repo-facing descriptions changed
- `changed_surface_checks`: `python scripts/run_changed_surface_checks.py --repo-root .`
  - use_when: you need the check plan for current changes instead of guessing

## Stop Reading Triggers
- protected paths are involved
- the question is about what is true right now
- the claim can be checked mechanically
- status artifacts and prose may have drifted apart
- the task is code-change oriented and a verifier already maps the changed surface
