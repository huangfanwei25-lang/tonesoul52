# Git Hygiene Latest

- generated_at: 2026-02-21T11:07:09Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000
- max_tracked_ignored: 40

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.08 | `git count-objects -vH` |
| fsck | PASS | 0 | 1.67 | `git fsck --no-reflogs` |
| tracked_ignored | PASS | 0 | 0.05 | `git ls-files -ci --exclude-standard` |

## Metrics
- loose_count: 1153
- in_pack: 5907
- packs: 2
- size: 5.29 MiB
- size_pack: 98.13 MiB
- dangling_count: 6
- fsck_unexpected_count: 0
- tracked_ignored_count: 35

## Tracked Ignored Files
- `data/YuHun_v2.6_knowledgebase.json`
- `data/YuHun_v2.6_knowledgebase_extended.json`
- `data/semantic_spine_fixtures.json`
- `data/yuhun_academy_knowledgebase_v1.1.txt`
- `"data/\350\252\236\351\255\202\345\212\207\345\240\264_API_\346\234\200\347\265\202\347\211\210_v1.3.json"`
- `experiments/tsd1_pilot/data/prompts.json`
- `experiments/tsd1_pilot/data/responses.json`
- `memory/.hierarchical_index/hierarchical.index`
- `memory/.hierarchical_index/vows_meta.json`
- `memory/.semantic_index/faiss.index`
- `memory/.semantic_index/metadata.json`
- `memory/external_framework_analysis/claw_governance_insight.md`
- `memory/external_framework_analysis/wfgy_3.0_analysis.md`
- `memory/handoff/codex_prompt.md`
- `memory/handoff/note_antigravity_to_codex_20260204.md`
- `memory/narrative/README.md`
- `memory/narrative/synthesis.md`
- `memory/narrative/threads/academic_grounding.md`
- `memory/narrative/threads/infinite_game.md`
- `memory/narrative/threads/meaning_transfer.md`
