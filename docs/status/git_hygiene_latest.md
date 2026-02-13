# Git Hygiene Latest

- generated_at: 2026-02-13T17:18:51Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.06 | `git count-objects -vH` |
| fsck | PASS | 0 | 1.87 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 388
- in_pack: 5907
- packs: 2
- size: 1011.54 KiB
- size_pack: 98.13 MiB
- dangling_count: 5
- fsck_unexpected_count: 0
