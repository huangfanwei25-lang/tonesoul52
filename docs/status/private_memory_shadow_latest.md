# Private Memory Shadow Latest

- generated_at: 2026-03-22T16:10:56Z
- primary_status_line: `private_memory_shadow_contract | pairs=2 divergent=2 missing=0 registry_entry=1`
- runtime_status_line: `active_root=memory/.hierarchical_index | shadow_root=memory/memory/.hierarchical_index defer_mutation=1 review=0`
- artifact_policy_status_line: `shadow_policy=observe_report_do_not_mutate | cleanup_scope=private_memory_phase_only`

## Contract
- active_root: `memory/.hierarchical_index`
- shadow_root: `memory/memory/.hierarchical_index`
- source_of_truth_rule: `Prefer memory/.hierarchical_index as the active lane in public convergence work.`
- public_cleanup_rule: `Do not mutate either lane during public document convergence; report only.`
- deferred_cleanup_phase: `private_memory_lane_cleanup`

## Metrics
- `active_file_count`: `2`
- `shadow_file_count`: `2`
- `pair_count`: `2`
- `divergent_pair_count`: `2`
- `exact_match_count`: `0`
- `needs_review_count`: `0`

## Registry Alignment
- `entry_present`: `True`
- `tracked_basename`: `vows_meta.json`
- `paths_match_expected`: `True`
- `missing_paths`: `[]`
- `extra_paths`: `[]`

## Pairs
- `hierarchical.index` mode=`binary_hash_compare` exact=`false` needs_review=`false`
  - active: `memory/.hierarchical_index/hierarchical.index`
  - shadow: `memory/memory/.hierarchical_index/hierarchical.index`
  - policy: `defer_private_cleanup`
  - sizes: active=`24811` shadow=`12475`
- `vows_meta.json` mode=`json_structural_compare` exact=`false` needs_review=`false`
  - active: `memory/.hierarchical_index/vows_meta.json`
  - shadow: `memory/memory/.hierarchical_index/vows_meta.json`
  - policy: `defer_private_cleanup`
  - sizes: active=`1034` shadow=`713`
  - item_counts: active=`8` shadow=`3`
  - key_shape_match: `false` similarity=`0.317`

## Issues
