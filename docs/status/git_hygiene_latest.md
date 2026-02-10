# Git Hygiene Latest

- generated_at: 2026-02-10T10:52:49Z
- overall_ok: true
- max_dangling: 50
- max_loose_count: 5000

| check | status | exit | duration_s | command |
| --- | --- | ---: | ---: | --- |
| count_objects | PASS | 0 | 0.04 | `git count-objects -vH` |
| fsck | PASS | 0 | 38.06 | `git fsck --no-reflogs` |

## Metrics
- loose_count: 173
- in_pack: 4508
- packs: 1
- size: 353.39 KiB
- size_pack: 3.53 GiB
- dangling_count: 1
- fsck_unexpected_count: 0
