# Git Hygiene Latest

- generated_at: 2026-02-13T15:21:50Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.05 | `git count-objects -vH` |
| fsck | PASS | 0 | 1.75 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 334
- in_pack: 5907
- packs: 2
- size: 851.35 KiB
- size_pack: 98.13 MiB
- dangling_count: 5
- fsck_unexpected_count: 0
