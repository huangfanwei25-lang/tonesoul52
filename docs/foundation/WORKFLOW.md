# Foundation Layer: Workflow

> Purpose: define the default work loop for human/AI collaboration in this repo.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to `AGENTS.md`, `docs/AI_QUICKSTART.md`, and task/readiness contracts.

---

## Default Work Loop

`understand -> test -> implement -> refactor -> verify`

This repo does not want blind edits or theory-first overreach.

## New Conversation Start

1. Read this Foundation Layer.
2. Read [task.md](../../task.md) for the active short board.
3. If the task is operational or code-touching, use [docs/AI_QUICKSTART.md](../AI_QUICKSTART.md).
4. If the task changes boundaries, open the relevant architecture contract before editing.

## Task Classification

Before starting, classify the task:

- `quick_change`: narrow, low-risk, 1-2 files
- `feature_track`: bounded feature or extension
- `system_track`: cross-cutting or architectural work

If the classification is unclear, the task is not ready yet.

## Planning Rule

For multi-step work, express the task as a small phase or task card with explicit success criteria.

## Three-Failure Rule

After three failed attempts, stop and reassess:

- what was tried
- what failed
- which assumption was wrong
- what smaller or simpler angle exists

## When To Stop

Stop and escalate when:

- the task touches protected or human-owned boundaries
- runtime truth and documentation clearly disagree
- the change crosses from feature work into architectural mutation without explicit ratification

## Source Anchors

- [AGENTS.md](../../AGENTS.md)
- [docs/AI_QUICKSTART.md](../AI_QUICKSTART.md)
- [docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](../architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
- [task.md](../../task.md)
