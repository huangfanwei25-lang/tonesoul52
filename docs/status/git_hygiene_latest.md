# Git Hygiene Latest

- generated_at: 2026-06-01T12:49:36Z
- overall_ok: false
- max_dangling: 50
- max_loose_count: 5000
- max_tracked_ignored: 28

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.10 | `git count-objects -vH` |
| fsck | FAIL | 0 | 2.88 | `git fsck --no-reflogs` |
| tracked_ignored | PASS | 0 | 0.11 | `git ls-files -ci --exclude-standard` |

## Metrics
- loose_count: 2304
- in_pack: 14133
- packs: 3
- size: 12.93 MiB
- size_pack: 116.27 MiB
- dangling_count: 78
- fsck_unexpected_count: 0
- tracked_ignored_count: 15

## Issues
- dangling objects 78 exceeds threshold 50

## Tracked Ignored Files
- `data/YuHun_v2.6_knowledgebase.json`
- `data/YuHun_v2.6_knowledgebase_extended.json`
- `data/semantic_spine_fixtures.json`
- `data/yuhun_academy_knowledgebase_v1.1.txt`
- `"data/\350\252\236\351\255\202\345\212\207\345\240\264_API_\346\234\200\347\265\202\347\211\210_v1.3.json"`
- `docs/chronicles/task_archive_phase_570-854.md`
- `docs/status/persona_swarm_framework_latest.json`
- `experiments/tsd1_pilot/data/prompts.json`
- `experiments/tsd1_pilot/data/responses.json`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- `memory/crystals.jsonl`
- `memory/memory_base/tonesoul_cognitive.index`
- `memory/memory_base/tonesoul_metadata.jsonl`
- `spec/wfgy_semantic_control_spec.md`
