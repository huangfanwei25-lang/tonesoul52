# Git Hygiene Latest

- generated_at: 2026-07-20T05:32:48Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000
- max_tracked_ignored: 28

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.00 | `git count-objects -vH` |
| fsck | PASS | 0 | 0.38 | `git fsck --no-reflogs` |
| tracked_ignored | PASS | 0 | 0.01 | `git ls-files -ci --exclude-standard` |

## Metrics
- loose_count: 0
- in_pack: 2852
- packs: 1
- size: 0 bytes
- size_pack: 25.21 MiB
- dangling_count: 0
- fsck_unexpected_count: 0
- tracked_ignored_count: 9

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
