# Persona Swarm Framework (Phase 82)

> Purpose: describe the swarm-style persona coordination mode, its runtime contract, and the evaluation signals used to assess it.
> Last Updated: 2026-03-23
## Goal

Add a second multi-persona mode that models a swarm instead of fixed tri-persona arbitration.
This layer focuses on coordination quality and persona identity positioning.

## Runtime Contract

- Core module: `tonesoul/council/swarm_framework.py`
- Status runner: `scripts/run_persona_swarm_framework.py`
- Status artifact: `docs/status/persona_swarm_framework_latest.json`

Input signal schema (per agent):

- `agent_id`, `role`, `vote`
- `confidence`, `safety_score`, `quality_score`, `novelty_score`
- `latency_ms`, `token_cost`

Decision contract:

- allowed `vote`: `approve | block | revise | defer`
- optional `final_decision`: `approve | block | revise | defer`

## Metrics

- `task_quality`
- `safety_pass_rate`
- `consistency_at_session`
- `disagreement_utility`
- `diversity_index`
- `token_latency_cost_index`
- `swarm_score`

## Persona Positioning

The framework emits identity archetypes from metric shape:

- `sentinel_recovery`: safety-first stabilization
- `critical_discovery`: dissent-preserving exploration
- `reliable_executor`: high-trust delivery mode
- `adaptive_integrator`: balanced orchestration

This is the swarm answer to the "what are we becoming?" question in long-running sessions.

## Readiness Gate

Current gate used by `run_persona_swarm_framework.py`:

- `safety_pass_rate >= 0.80`
- `swarm_score >= 0.72`
- `decision_support >= 0.60`
- `token_latency_cost_index <= 0.75`
- guardian fail-fast consistency:
  - if guardian fail-fast triggered, final `decision` must be `block`

## Phase 84 Policy Upgrade

### Guardian Fail-Fast

- enabled by default in `SwarmFrameworkConfig`
- trigger conditions:
  - role is guardian
  - vote is `block`
  - confidence >= `0.75`
  - safety_score >= `0.75`
- when triggered, framework forces decision to `block` (unless explicit override is enabled)

### Cost Tiering

`run_persona_swarm_framework.py` now emits `readiness_gate.cost_profile`:

- `low` (<= 0.45): `full_swarm` (budget 5)
- `moderate` (<= 0.65): `core_swarm` (budget 3)
- `high` (<= 0.80): `guardian_engineer_only` (budget 2)
- `critical` (> 0.80): `guardian_only` (budget 1)

## Phase 85 Runtime Budget Application

Runner now executes in two passes:

1. Baseline evaluation on full signal set (for cost-tier inference)
2. Budgeted execution evaluation on selected signals

Output fields:

- `baseline_evaluation`: full-swarm snapshot
- `execution_plan`:
  - selected/dropped agent IDs
  - requested budget
  - budget respected flag
- `evaluation`: budgeted execution result (authoritative gate input)

In `--strict` mode, gate failure returns non-zero.

## CI Automation

- workflow: `.github/workflows/persona_swarm.yml`
- dispatch script: `scripts/run_persona_swarm_dispatch.py`
- modes:
  - push/pull_request: blocking strict run
  - workflow_dispatch: optional `strict` + optional `input_path`
  - schedule: weekly drift snapshot

## Run

```bash
python scripts/run_persona_swarm_framework.py --strict
```

Optional custom input:

```bash
python scripts/run_persona_swarm_framework.py --input docs/experiments/persona_swarm_input_template.json --strict
```
