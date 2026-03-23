# 2026 Q2 Roadmap: Memory Governance Mainline

> Purpose: roadmap the Q2 memory-governance mainline across `tonesoul52` and `OpenClaw-Memory`.
> Last Updated: 2026-03-23

Date range: **2026-03-01 -> 2026-05-31**  
Scope: `tonesoul52` + `OpenClaw-Memory` dual-repo convergence around tension/friction governance.

## Objectives

1. Keep architecture stable while removing contract drift between repos.
2. Turn "memory of wave/friction" into auditable routing signals.
3. Preserve usability for normal users (simple defaults, no mandatory model downloads).

## Phase Plan

## Phase 118 (2026-03-01 -> 2026-03-14): Contract Freeze + Shared Vocabulary
- Deliverables:
  - `memory_governance_contract_v1` schema + example.
  - CI-verifiable contract check in `tonesoul52`.
  - Mapping table for `prior_tension / wave / friction / route` fields across both repos.
- Acceptance:
  - Contract checker passes in CI.
  - New memory-governance features must reference contract fields (no ad-hoc keys).
- Risks:
  - Existing historical JSONL uses mixed naming (`delta_t`, `tension_score`, `adjusted_tension`).
  - Mitigation: allow legacy aliases in readers, but output contract remains canonical.

## Phase 119 (2026-03-15 -> 2026-03-31): Friction-Aware Routing v1
- Deliverables:
  - Governance friction integrated into route selection (already seeded in `ComputeGate`).
  - Shadow-vs-active routing comparison report.
  - Friction-trigger reason traces in dispatch artifacts.
- Acceptance:
  - High-friction sessions escalate to council with explicit trace reasons.
  - No regression on free-tier safety/cost caps.
- Risks:
  - Over-escalation to council may increase latency/cost.
  - Mitigation: threshold calibration with replay benchmarks before widening rollout.

## Phase 120 (2026-04-01 -> 2026-04-20): Memory Quality + Replay Benchmarks
- Deliverables:
  - Expanded choice-boundary benchmark runs and baselines.
  - Reflection report trend dashboard inputs (`tension_threshold_effective`, unresolved topics).
  - Weekly drift report across repos.
- Acceptance:
  - `high_tension_top1_rate >= 0.90`
  - `obedience_leak_rate <= 0.10`
  - `reason_coverage_rate >= 0.90`
- Risks:
  - Metrics can be gamed by narrow synthetic samples.
  - Mitigation: maintain mixed real-history + synthetic benchmark sets.

## Phase 121 (2026-04-21 -> 2026-05-05): Productization for Normal Users
- Deliverables:
  - Profile presets (`basic`, `governance`) with sane defaults.
  - One-command validation entrypoint.
  - Failure-mode docs for offline/no-network environments.
- Acceptance:
  - Fresh user can run ingestion/query/validation under 5 minutes.
  - No mandatory heavyweight model download path.
- Risks:
  - Feature depth may leak into onboarding complexity.
  - Mitigation: strict "advanced flags optional" rule.

## Phase 122 (2026-05-06 -> 2026-05-20): Dual-Track Boundary Hardening
- Deliverables:
  - Public/private boundary manifest update for memory-governance modules.
  - Guard checks preventing private threshold internals from landing in public repo.
  - Handoff protocol for private evolution experiments.
- Acceptance:
  - Boundary checks block violating commits.
  - Public repo only contains explainable, auditable policy surfaces.
- Risks:
  - Accidental leakage through docs or scripts.
  - Mitigation: add path-level and token-level scanners in CI.

## Phase 123 (2026-05-21 -> 2026-05-31): External Narrative + Repro Pack
- Deliverables:
  - Engineering-focused reflection report (`reflection_mechanisms_report.md` aligned to data).
  - Reproducible benchmark bundle for public review.
  - Clear delta statement: "OpenClaw baseline vs ToneSoul governance layer".
- Acceptance:
  - External contributor can reproduce core claims from docs + scripts only.
  - Claims map to measurable artifacts, not metaphor-only narrative.

## Operating Cadence

- Weekly:
  - Run `python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion`
  - Review contract checker + reflection report diffs.
- Bi-weekly:
  - Threshold calibration review (`friction`, `tension_threshold_effective`).
- Monthly:
  - Consolidated governance review and rollback-readiness check.

## Immediate Next Actions (starting now)

1. Land `memory_governance_contract_v1` schema/example and CI check.
2. Tag current friction-routing implementation as `v1_baseline`.
3. Start shadow evaluation set for threshold tuning before broader policy changes.
