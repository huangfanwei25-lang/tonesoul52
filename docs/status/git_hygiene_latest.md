# Git Hygiene Latest

- generated_at: 2026-02-14T10:39:48Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.06 | `git count-objects -vH` |
| fsck | PASS | 0 | 1.54 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 711
- in_pack: 5907
- packs: 2
- size: 1.85 MiB
- size_pack: 98.13 MiB
- dangling_count: 6
- fsck_unexpected_count: 0
