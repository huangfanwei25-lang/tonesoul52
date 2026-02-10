# Git Hygiene Latest

- generated_at: 2026-02-10T08:12:55Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.03 | `git count-objects -vH` |
| fsck | PASS | 0 | 38.45 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 29
- in_pack: 4508
- packs: 1
- size: 62.06 KiB
- size_pack: 3.53 GiB
- dangling_count: 1
- fsck_unexpected_count: 0
