# Git Hygiene Latest

- generated_at: 2026-03-08T15:38:30Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000
- max_tracked_ignored: 28

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.07 | `git count-objects -vH` |
| fsck | PASS | 0 | 2.63 | `git fsck --no-reflogs` |
| tracked_ignored | PASS | 0 | 0.07 | `git ls-files -ci --exclude-standard` |

## Metrics
- loose_count: 912
- in_pack: 6976
- packs: 1
- size: 16.65 MiB
- size_pack: 100.53 MiB
- dangling_count: 6
- fsck_unexpected_count: 0
- tracked_ignored_count: 10

## Tracked Ignored Files
- `data/YuHun_v2.6_knowledgebase.json`
- `data/YuHun_v2.6_knowledgebase_extended.json`
- `data/semantic_spine_fixtures.json`
- `data/yuhun_academy_knowledgebase_v1.1.txt`
- `"data/\350\252\236\351\255\202\345\212\207\345\240\264_API_\346\234\200\347\265\202\347\211\210_v1.3.json"`
- `experiments/tsd1_pilot/data/prompts.json`
- `experiments/tsd1_pilot/data/responses.json`
- `spec/wfgy_semantic_control_spec.md`
- `zenodo_upload/paper_outline_multiperspective_truth.md`
- `"zenodo_upload/\344\270\212\345\202\263\346\214\207\345\215\227.md"`
