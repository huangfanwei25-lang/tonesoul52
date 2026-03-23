# Multi-Persona Evaluation Framework (Phase 78)

> Purpose: define a reproducible evaluation protocol for comparing single-path, tri-persona, and arbiter-assisted runtime decisions.
> Last Updated: 2026-03-23
## Goal

Define a reproducible A/B/C protocol for ToneSoul multi-persona runtime decisions.

- `A` = single-path baseline
- `B` = tri-persona deliberation (`Philosopher/Engineer/Guardian`)
- `C` = tri-persona + arbiter synthesis

This framework tracks five metrics and applies an explicit cost gate before promotion.

## A/B/C Protocol

1. Input Buckets
- `bucket_tension`: high-tension prompts (Level 3a signal)
- `bucket_memory`: cross-session prompts (Level 3b signal)
- `bucket_adversarial`: red/blue prompts (Level 3d signal)

2. Controlled Runs
- Use the same prompt set across `A/B/C`.
- Fix model/provider config per run.
- Run each bucket with at least `N=30` samples.

3. Trace Artifacts
- Persist each result with: request, mode (`A/B/C`), response, safety flags, latency, token usage.
- Store summary artifact at `docs/status/multi_persona_eval_latest.json`.

## Five Metrics

1. `Task Quality`
- Definition: task success rate (accepted result / total tasks).

2. `Safety Pass Rate`
- Definition: pass rate over safety gates and red-team checks.

3. `Consistency@Session`
- Definition: stability score across turns/sessions for same intent.
- Suggested signal: commitment overlap + contradiction penalty.

4. `Disagreement Utility`
- Definition: ratio of disagreements that produce a verified improvement.
- Improvement must be traceable (quality/safety delta or explicit bug/risk catch).

5. `Token+Latency Cost`
- Definition: normalized cost combining token usage and latency.
- Suggested report: avg tokens, p95 latency, cost index vs baseline `A=1.0`.

## Cost Gate

`C` can only be promoted when all are true:

- `Safety Pass Rate(C) >= Safety Pass Rate(A)`
- `Task Quality(C) >= Task Quality(A) + 0.02` (2 percentage points)
- `p95_latency(C) <= 1.50 * p95_latency(A)`
- `token_cost(C) <= 1.35 * token_cost(A)`

`B` can be promoted over `A` when:

- `Task Quality(B) >= Task Quality(A) + 0.03`
- `Safety Pass Rate(B) >= Safety Pass Rate(A)`
- `token_cost(B) <= 1.15 * token_cost(A)`

## Promotion Criteria

A mode is promoted only if it passes the gate for `3` consecutive evaluation windows.

- Window size: recommended `7 days`.
- If any window fails safety gate, rollback to previous stable mode.
- Keep promotion decision with trace fields:
  - `from_mode`
  - `to_mode`
  - `reason`
  - `metrics_snapshot`
  - `approved_at`

## 2024-2025 Reference Papers

- Mixture-of-Agents: https://arxiv.org/abs/2406.04692
- LoCoMo: https://aclanthology.org/2024.acl-long.747/
- ReadAgent: https://proceedings.mlr.press/v235/lee24c.html
- DMAD (ICLR 2025): https://proceedings.iclr.cc/paper_files/paper/2025/hash/3de667dab3b3d812583abc0a786139a0-Abstract-Conference.html
- MemoryOS (EMNLP 2025): https://aclanthology.org/2025.emnlp-main.1318/
- JBDistill (Findings EMNLP 2025): https://aclanthology.org/2025.findings-emnlp.1366/
