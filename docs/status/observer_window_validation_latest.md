# Observer Window — Day 2 Validation Wave

> Generated at `2026-03-30T13:38:23Z`. Advisory only.

**Status**: `needs_fix`  
**Scenarios**: 4 | **Passed**: 37 | **Failed**: 1 | **High-friction fails**: 0

**Top friction scenario**: `none`  
**Top friction checks**: `none`

## ✅ Scenario: `clean_state`

- Passed: 9 | Failed: 0 | High-friction: 0
- Counts: `{'stable': 5, 'contested': 1, 'stale': 0}`
- Summary: `observer_window stable=5 contested=1 stale=0 delta_has_updates=False`

| Check | Result | Friction |
|-------|--------|---------|
| `stable_bucket_nonempty` | pass | high |
| `contested_bucket_nonempty` | pass | high |
| `summary_has_stable_count` | pass | medium |
| `summary_has_contested_count` | pass | medium |
| `summary_has_stale_count` | pass | medium |
| `receiver_note_present` | pass | low |
| `stable_has_launch_tier` | pass | medium |
| `stale_is_empty_in_clean_state` | pass | medium |
| `no_false_all_clear` | pass | high |

## ❌ Scenario: `contested_dossier`

- Passed: 9 | Failed: 1 | High-friction: 0
- Counts: `{'stable': 5, 'contested': 2, 'stale': 0}`
- Summary: `observer_window stable=5 contested=2 stale=0 delta_has_updates=False`

| Check | Result | Friction |
|-------|--------|---------|
| `stable_bucket_nonempty` | pass | high |
| `contested_bucket_nonempty` | pass | high |
| `summary_has_stable_count` | pass | medium |
| `summary_has_contested_count` | pass | medium |
| `summary_has_stale_count` | pass | medium |
| `receiver_note_present` | pass | low |
| `stable_has_launch_tier` | pass | medium |
| `contested_has_council_calibration` | pass | high |
| `contested_has_suppression_note` | FAIL | medium |
| `no_false_all_clear` | pass | high |

## ✅ Scenario: `stale_compaction`

- Passed: 10 | Failed: 0 | High-friction: 0
- Counts: `{'stable': 4, 'contested': 2, 'stale': 3}`
- Summary: `observer_window stable=4 contested=2 stale=3 delta_has_updates=False`

| Check | Result | Friction |
|-------|--------|---------|
| `stable_bucket_nonempty` | pass | high |
| `contested_bucket_nonempty` | pass | high |
| `summary_has_stable_count` | pass | medium |
| `summary_has_contested_count` | pass | medium |
| `summary_has_stale_count` | pass | medium |
| `receiver_note_present` | pass | low |
| `stable_has_launch_tier` | pass | medium |
| `stale_has_compaction` | pass | high |
| `stale_has_absent_evidence` | pass | high |
| `no_false_all_clear` | pass | high |

## ✅ Scenario: `claim_collision`

- Passed: 9 | Failed: 0 | High-friction: 0
- Counts: `{'stable': 5, 'contested': 2, 'stale': 0}`
- Summary: `observer_window stable=5 contested=2 stale=0 delta_has_updates=True`

| Check | Result | Friction |
|-------|--------|---------|
| `stable_bucket_nonempty` | pass | high |
| `contested_bucket_nonempty` | pass | high |
| `summary_has_stable_count` | pass | medium |
| `summary_has_contested_count` | pass | medium |
| `summary_has_stale_count` | pass | medium |
| `receiver_note_present` | pass | low |
| `stable_has_launch_tier` | pass | medium |
| `contested_has_claim_conflict` | pass | high |
| `no_false_all_clear` | pass | high |

> [!NOTE]
> This validation wave is advisory. High-friction failures indicate places where a fresh agent may misread stable vs contested. Fix only the highest-friction misunderstanding per Day 2 plan.
