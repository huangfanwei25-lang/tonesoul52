# Foundation Layer: Task Card

> Purpose: define the minimum task-card shape for bounded, testable work.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to `task.md` and task/readiness contracts.

---

## Minimum Task Card

```markdown
# Task Card: <short title>

- Goal: <what should be true when done>
- Scope: <what is included>
- Non-goals: <what is explicitly excluded>
- Target Paths: <files / surfaces expected to change>
- Track: quick_change | feature_track | system_track
- Validation: <commands or checks>
- Success Criteria: <observable pass condition>
```

## `task.md` Phase Shape

```markdown
## Phase N: <name>
- [ ] Task 1
- [ ] Task 2
**Success Criteria**: <testable result>
```

## Good Task Cards Are

- narrow
- testable
- explicit about non-goals
- explicit about validation

## Bad Task Cards Usually

- mix architecture cleanup with feature delivery
- omit paths or validation
- use "improve" without a concrete pass condition
- hide major scope behind one vague bullet

## Source Anchors

- [task.md](../../task.md)
- [docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](../architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
