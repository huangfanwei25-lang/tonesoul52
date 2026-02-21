# Decay Query Benchmark (Top-K Heap)

- Date: 2026-02-21
- Command:
  - `python scripts/benchmark_decay_query.py --sizes 20000,100000 --limit 50 --runs 3 --json-output reports/decay_query_benchmark_latest.json`
- Validation:
  - Script checks result equivalence (`record_id` + `relevance_score`) between baseline full-sort and top-k paths before timing.

| size | baseline_median_s | topk_median_s | speedup_x |
| ---: | ---: | ---: | ---: |
| 20000 | 0.156323 | 0.107531 | 1.45 |
| 100000 | 0.720096 | 0.571682 | 1.26 |

## Notes

- Improvement is consistent for large datasets at `limit=50`.
- This optimization keeps current decay semantics while reducing ranking overhead from full-sort to bounded top-k selection.
