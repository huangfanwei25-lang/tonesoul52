# Basename Divergence Distillation Latest

- generated_at: 2026-03-22T16:11:01Z
- primary_status_line: `basename_divergence_distilled | entries=5 covered_manual_review=5 unresolved=1 issues=0`
- runtime_status_line: `distillation_registry | strategies=5 manual_review_baselines=5`
- artifact_policy_status_line: `registry_mode=curated | semantics=boundary_plus_namespace_plus_private_shadow`

## Metrics
- `entry_count`: `5`
- `manual_review_collision_count`: `5`
- `covered_manual_review_count`: `5`
- `unresolved_count`: `1`
- `issue_count`: `0`

## Status Counts
- `resolved_boundary`: `2`
- `resolved_generated_dual`: `1`
- `resolved_private_backend_dual`: `1`
- `unresolved_private_shadow`: `1`

## Strategy Counts
- `defer_private_shadow_cleanup`: `1`
- `keep_dual_boundary`: `1`
- `keep_generated_namespace_dual`: `1`
- `keep_private_backend_dual`: `1`
- `keep_public_private_boundary`: `1`

## Entries
- `manifesto.md` status=`resolved_boundary` strategy=`keep_dual_boundary`
  - authority_rule: Do not merge. Constitutional text governs system priority order; philosophy manifesto frames public ethical stance.
  - editing_rule: Cross-link and scope-label both files instead of deduping by basename.
  - path: `constitution/manifesto.md`
  - path: `docs/philosophy/manifesto.md`
- `academic_grounding.md` status=`resolved_boundary` strategy=`keep_public_private_boundary`
  - authority_rule: Do not sync by content. Public philosophy docs and private memory threads serve different retrieval audiences.
  - editing_rule: Only edit the public philosophy surface in this repository cleanup lane; do not treat the memory thread as a mirror.
  - path: `docs/philosophy/academic_grounding.md`
  - path: `memory/narrative/threads/academic_grounding.md`
- `autonomous_registry_schedule_latest.json` status=`resolved_generated_dual` strategy=`keep_generated_namespace_dual`
  - authority_rule: These are separate generated lanes and must stay namespaced by directory, not deduped by basename.
  - editing_rule: Do not hand-edit generated artifacts. If naming changes are needed, change generator output names later.
  - path: `docs/status/autonomous_registry_schedule_latest.json`
  - path: `docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json`
- `metadata.json` status=`resolved_private_backend_dual` strategy=`keep_private_backend_dual`
  - authority_rule: Backend metadata files are lane-specific. Treat them as separate runtime stores, not as mirrors.
  - editing_rule: Do not normalize or dedupe these files during public doc cleanup.
  - path: `memory/.semantic_index/metadata.json`
  - path: `memory/vectors/metadata.json`
- `vows_meta.json` status=`unresolved_private_shadow` strategy=`defer_private_shadow_cleanup`
  - authority_rule: Do not modify during public cleanup. Govern this pair through the dedicated private-memory shadow boundary contract until a later cleanup pass is explicitly in scope.
  - editing_rule: Read the dedicated shadow contract/report first, record drift, and defer any mutation until the private-memory lane is explicitly in scope.
  - path: `memory/.hierarchical_index/vows_meta.json`
  - path: `memory/memory/.hierarchical_index/vows_meta.json`

## Missing From Registry

## Issues
