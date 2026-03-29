# ToneSoul Task Track And Readiness Contract

> Status: architectural discipline contract
> Purpose: define readiness states, task tracks, exploration depth, and claim/review requirements so later agents can classify work before starting instead of treating every task as a full-system refactor
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (shared surface semantics)
>   - docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md (identity refresh discipline)
>   - docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md (plan change discipline)
>   - scripts/start_agent_session.py (session-start bundle shape)
>   - tonesoul/runtime_adapter.py (claim_task, r_memory_packet)
> Scope: 3 readiness states, 3 task tracks, 4 exploration depths, 18 task pattern classifications

## How To Use This Document

If you are an AI agent about to start a task:

1. Run `python scripts/start_agent_session.py --agent <your-id>` and read the output
2. Check **Readiness States** to determine if you are `pass`, `needs_clarification`, or `blocked`
3. Look up your task in the **Track Assignment Matrix** to find the recommended track
4. Follow the track's **exploration depth**, **claim requirement**, and **review requirement**
5. If the matrix says `needs_clarification` or `blocked`, stop and handle the condition before beginning work

## Why This Document Exists

ToneSoul's shared-memory infrastructure solves how agents share state. What it does not yet solve is three coordination failures that happen before work begins:

1. **False readiness**: an agent receives a full session-start bundle and assumes it is ready, but has not checked for claim conflicts, critical risk, or ambiguous scope.

2. **Track collapse**: every task — from a typo fix to an architecture contract — gets the same exploration depth and claim overhead. Typo fixes get x3 deep scans; architecture contracts get x0 blind starts.

3. **Exploration waste**: without a depth signal, agents either over-explore (reading 50 files for a one-line fix) or under-explore (missing a critical dependency for a cross-cutting change).

This contract addresses all three by classifying tasks into tracks with explicit readiness gates, exploration depths, and claim/review requirements.

## Compressed Thesis

Know what kind of work you are doing before you start doing it. A typo fix does not need a claim, a deep scan, or a review. An architecture contract needs all three. The session-start bundle tells you whether you are ready; this contract tells you what "ready" means for your specific task.

---

## Readiness States

### pass

The agent may begin work. All of the following must hold:

- Session-start bundle executed successfully and returned a `contract_version: "v1"` payload
- No active claim conflicts: `claim_view.claims` contains no claim by another agent on the same task_id or overlapping paths
- `posture.risk_posture.level` is not `"critical"`
- The agent has read the task's objective source (the relevant Phase in `task.md`, or the relevant deliverable in a work order)
- For `feature_track` and `system_track`: the agent has completed the track's minimum exploration depth

### needs_clarification

The agent has context but lacks sufficient authority or evidence to start. Any of the following triggers this state:

- Task objective references an ambiguous path or term with multiple possible interpretations
- Success criteria include quantified metrics whose values are undefined
- Delta feed shows a previous agent's compaction with an unresolved `next_action` or conflicting `carry_forward`
- Task requires modifying protected files (AGENTS.md, MEMORY.md, .env, AXIOMS.json) without explicit authorization in the work order
- Schema change is involved but no consumer list exists

**Action**: ask the human or leave a compaction with the specific clarification question.

### blocked

The agent must not begin work. Any of the following triggers this state:

- Session-start bundle execution failed (storage backend unavailable)
- Another agent holds a conflicting claim whose TTL has not expired
- `posture.risk_posture.level` is `"critical"` and the task is not fixing that critical condition
- Previous agent's compaction explicitly marked `next_action: "STOP: requires human decision"`
- Task depends on a Phase whose objectives are not all marked `[x]`

**Action**: wait for the blocking condition to resolve, or escalate to the human.

---

## Task Tracks

### quick_change

Narrow, low-risk corrections completable within a single session. Typically affects 1-2 files.

Examples: typo fix, narrow wording correction, single-file doc edit, single import fix, adding one guidance line to onboarding, fixing a broken bootstrap path, adding a single test for existing behavior.

### feature_track

Bounded new functionality or extensions. Typically affects 2-5 files and has clear success criteria.

Examples: new script entrypoint, new packet section, bounded implementation ticket from a work order, new schema field, regression test suite, contract observer or gate wiring.

### system_track

Cross-cutting architectural changes that define new boundaries or affect 5+ files. High persistence, high blast radius.

Examples: architecture contract creation, multi-file refactor, schema version migration, cross-cutting concern (e.g., all scripts' bootstrap), work order creation, meta-governance changes.

---

## Track Assignment Matrix

| Task Pattern | Track | Default Readiness | Min Evidence | Depth | Claim | Review | Ask Human When |
|---|---|---|---|---|---|---|---|
| Typo / wording fix in docs | quick_change | pass | explicit path in ticket | x0 | no | no | path is unclear |
| Single import / bootstrap fix | quick_change | pass | error message + file path | x1 | no | no | error is ambiguous |
| New test for existing behavior | quick_change | pass | behavior + file reference | x1 | no | no | behavior spec is unclear |
| Onboarding / quickstart line edit | quick_change | pass | explicit wording change | x0 | no | no | edit changes meaning |
| Compaction / checkpoint fix | quick_change | pass | failing test or broken output | x1 | no | no | fix changes TTL or retention semantics |
| New script entrypoint | feature_track | pass | spec + output shape | x2 | yes | no | output overlaps existing surface |
| New packet section | feature_track | pass | schema + use case | x2 | yes | no | section overlaps existing |
| Bounded implementation ticket | feature_track | pass | work order + acceptance criteria | x2 | yes | no | acceptance criteria ambiguous |
| Regression test suite | feature_track | pass | hypothesis + surface under test | x1 | no | no | hypothesis unclear |
| Contract observer / gate wiring | feature_track | pass | verifier + call site | x2 | yes | yes | blocking severity unclear |
| New schema field | feature_track | needs_clarification | use case + consumer list | x2 | yes | yes | no clear consumer identified |
| Subject snapshot field change | feature_track | needs_clarification | boundary contract + lane assignment | x2 | yes | yes | field touches Durable Identity lane |
| Architecture contract | system_track | needs_clarification | full dependency scan | x3 | yes | yes | scope touches AXIOMS or canonical posture |
| Multi-file refactor | system_track | needs_clarification | diff impact estimate | x3 | yes | yes | more than 10 files affected |
| Schema version migration | system_track | blocked | migration plan + backward compat test | x3 | yes | yes | always — schema versioning is governance |
| Cross-cutting doc convergence | system_track | needs_clarification | inventory + rename map | x3 | yes | yes | more than 5 renames across authority lanes |
| Work order creation | system_track | pass | gap analysis + deliverable list | x2 | yes | no | gap analysis shows > 3 competing concerns |
| Readiness / track system itself | system_track | needs_clarification | full current-surface audit | x3 | yes | yes | always — meta-governance |

**Note**: the Track column is a recommendation. An agent may override the track if it can justify the override in its compaction. The override itself is not a violation; failing to record the override is.

---

## Exploration Depth Definitions

| Depth | Name | Typical File Count | When To Use | Minimum Reading After Session-Start |
|---|---|---|---|---|
| **x0** | Minimal | 0-1 | Ticket provides explicit path and exact change | Target file only |
| **x1** | Targeted | 1-3 | Symptom is clear, fix location is bounded | Target file + its direct test file + direct callers |
| **x2** | Contextual | 5-10 | Need to understand affected surface and consumers | x1 + Grep for related patterns + schema/contract + existing similar features |
| **x3** | Comprehensive | 10+ | Cross-cutting concern, architecture contract, or meta-governance | x2 + all architecture contracts' Relationship sections + full Glob for affected surfaces; may require subagent exploration |

Exploration depth is a minimum, not a maximum. An agent may always explore more if it discovers unexpected complexity. However, if a quick_change task seems to require x3 exploration, the agent should reconsider whether the task was correctly classified — it may actually be a feature_track or system_track task.

---

## Claim And Review Requirements

| Track | Claim Required | Review Required | Rationale |
|---|---|---|---|
| quick_change | No | No | Quick changes should complete well within a claim's 30-minute TTL. The claim overhead is not worth it for 1-2 file changes. |
| feature_track | Yes | Only if touching schema or gate | Prevents two agents from building the same feature. Review is needed only when the change has high persistence (schema fields, blocking gates). |
| system_track | Yes | Yes (always) | Cross-cutting changes need claim to prevent conflicts and review to prevent boundary drift. System track tasks define constraints that later agents must follow. |

### When Review Is Required

"Review" means: before finalizing the deliverable, the agent should write a checkpoint or perspective summarizing what it intends to deliver, and either wait for human confirmation or explicitly note in compaction that review was deferred.

Review does not mean the agent cannot begin exploration or drafting. It means the agent should not commit a final deliverable without a review checkpoint.

---

## Alignment With Existing Session Flow

The readiness gate does not replace or modify the session-start bundle. It adds a classification layer on top of the bundle's output:

```
Session-Start Bundle (scripts/start_agent_session.py)
  ├── compact_diagnostic (soul_integral, risk, vows, tensions)
  ├── claim_view (active claims)
  ├── packet (full R-memory state)
  └── delta_feed (since-last-seen changes)
         │
         ▼
  Readiness Classification (this contract)
  ├── Check claim conflicts → blocked?
  ├── Check risk level → blocked?
  ├── Check delta_feed for unresolved carry_forward → needs_clarification?
  ├── Check task source (task.md / work order) → ambiguous? → needs_clarification?
  └── Track assignment → exploration depth + claim + review requirements
```

This classification is currently advisory — the agent reads the bundle and applies this contract mentally. Future phases may surface a machine-readable `readiness` section in the bundle output (see followup candidates).

---

## Relationship To Other Documents

Implementation note (2026-03-29): `scripts/start_agent_session.py` now surfaces a machine-readable `readiness` section and a bounded `task_track_hint` derived from visible session-start scope. The hint remains advisory; the explicit task objective or work order may still justify an override.

| Document | Relationship |
|----------|-------------|
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines the shared surfaces this contract's readiness gate reads from |
| `TONESOUL_PLAN_DELTA_CONTRACT.md` | Companion contract — once readiness is established and track is assigned, plan delta rules govern how to manage scope changes |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Subject snapshot field changes require `feature_track` + `needs_clarification` per this contract's matrix |
| `TONESOUL_CLAIM_AUTHORITY_MATRIX.md` | Provides term-level authority context that informs the `needs_clarification` trigger for ambiguous terms |
| `AI_ONBOARDING.md` | Current onboarding flow; this contract adds discipline on top of onboarding's reading stack |
| `task.md` | The canonical progress record this contract's track system classifies |

---

## Canonical Handoff Line

Before starting any task, classify it: what track, what depth, what readiness state. If you skip classification, you are guessing. Guessing is how typo fixes become three-hour explorations and architecture contracts become blind one-liners.
