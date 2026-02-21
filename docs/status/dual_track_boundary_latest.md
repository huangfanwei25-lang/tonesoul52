# Dual-Track Boundary Latest

- generated_at: 2026-02-21T08:09:29Z
- overall_ok: false
- changed_path_count: 30
- violation_count: 4
- allow_private_paths: false

## Collection
- mode: git
- command: `git diff --name-only --diff-filter=ACMRD 218b309...HEAD`
- exit_code: 0

## Violations
| path | rule_type | rule |
| --- | --- | --- |
| `tonesoul_evolution/__init__.py` | prefix | `tonesoul_evolution/` |
| `tonesoul_evolution/adversarial/__init__.py` | prefix | `tonesoul_evolution/` |
| `tonesoul_evolution/consolidator/__init__.py` | prefix | `tonesoul_evolution/` |
| `tonesoul_evolution/consolidator/core.py` | prefix | `tonesoul_evolution/` |

## Issues
- detected 4 changed paths that violate dual-track boundary policy
