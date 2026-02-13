# Persona Swarm Framework (Phase 82)

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

In `--strict` mode, gate failure returns non-zero.

## Run

```bash
python scripts/run_persona_swarm_framework.py --strict
```

Optional custom input:

```bash
python scripts/run_persona_swarm_framework.py --input path/to/swarm_signals.json --strict
```
