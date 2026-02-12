# Git Hygiene Latest

- generated_at: 2026-02-11T18:49:18Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.05 | `git count-objects -vH` |
| fsck | PASS | 0 | 39.83 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 464
- in_pack: 4508
- packs: 1
- size: 874.74 KiB
- size_pack: 3.53 GiB
- dangling_count: 2
- fsck_unexpected_count: 0
