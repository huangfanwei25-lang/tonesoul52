# Git Hygiene Latest

- generated_at: 2026-02-10T10:00:24Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.03 | `git count-objects -vH` |
| fsck | PASS | 0 | 38.50 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 67
- in_pack: 4508
- packs: 1
- size: 126.88 KiB
- size_pack: 3.53 GiB
- dangling_count: 1
- fsck_unexpected_count: 0
