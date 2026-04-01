# ToneSoul Test Stratification Program (2026-04-02)

> Purpose: stop monthly/operational gates from behaving like a second full CI lane while keeping full regression coverage in the main CI path.

## Current Reality

- `pytest tests -q` currently covers `2823` tests and takes roughly `9` minutes on the current workstation.
- `scripts/run_monthly_consolidation.py --strict` calls `scripts/verify_7d.py`.
- `scripts/verify_7d.py` previously used `python -m pytest tests -q` as its TDD check.
- Result: monthly consolidation duplicated the repo's full regression lane instead of serving as an operational audit.

## Why This Needs Stratification

- Operational audits should answer: "are the current blocking contracts still intact?"
- Full regression should answer: "did the entire repo still survive?"
- Those are related, but not identical, questions.

When both questions reuse the same full-suite command, two bad things happen:

1. CI latency grows for no new signal.
2. Small stale tests inside peripheral surfaces turn the monthly audit red even when the operational story is still healthy.

## Tier Model

### Tier 0: Fast Local Loop

Use for tight edit cycles on high-change surfaces.

Command:

```bash
python scripts/run_test_tier.py --tier fast
```

Goals:

- keep the loop short
- cover current entry/readout contracts
- catch obvious regressions before broader runs

### Tier 1: Blocking Operational Tier

Use for `verify_7d.py` TDD and other bounded operational gates.

Command:

```bash
python scripts/run_test_tier.py --tier blocking
```

Goals:

- protect current operational contracts
- cover entry surfaces, observer-window, receiver posture, monthly/launch scripts, and unified dispatch/runtime edges
- avoid rerunning the entire suite inside monthly consolidation

### Tier 2: Full Regression

Use in the main CI lane and burn-in validation.

Command:

```bash
python -m pytest tests -q
```

Goals:

- catch repo-wide regressions
- preserve broad historical confidence
- remain the place where peripheral breakage is still surfaced

## Current Blocking Tier Contents

- `tests/test_runtime_adapter.py`
- `tests/test_receiver_posture.py`
- `tests/test_risk_calculator.py`
- `tests/test_start_agent_session.py`
- `tests/test_diagnose.py`
- `tests/test_run_r_memory_packet.py`
- `tests/test_observer_window.py`
- `tests/test_unified_pipeline_dispatch.py`
- `tests/test_unified_pipeline_v2_runtime.py`
- `tests/test_run_monthly_consolidation.py`
- `tests/test_run_collaborator_beta_preflight.py`
- `tests/test_run_launch_continuity_validation_wave.py`
- `tests/test_verify_7d.py`
- `tests/test_verify_incremental_commit_attribution.py`
- `tests/test_workflow_contracts.py`
- `tests/test_tonesoul_config.py`

## Immediate Outcome

- `verify_7d.py` TDD now runs the blocking tier.
- Full `pytest tests -q` still remains the repo-wide regression lane.
- `run_monthly_consolidation.py --strict` now answers an operational question instead of cloning full CI cost.

## Next Follow-Through

1. Measure Tier 0 and Tier 1 runtime on CI runners, not only local Windows.
2. Trim the blocking tier if it grows into another hidden full suite.
3. Add one explicit weekly/nightly burn-in lane if the existing full CI cadence is still too sparse for long-tail regressions.
4. Keep stale-test cleanup separate from tier definitions; the tier list should reflect important contracts, not recent annoyance.
