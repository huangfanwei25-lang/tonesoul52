# Codex Handoff (2026-03-31)

> Purpose: rotation checkpoint after completing the observer-window 3-day execution program.
> Scope: branch-local continuation handoff after observer-window baseline work.
> Status: current handoff note (supersedes `codex_handoff_2026-03-30.md`)

---

## 1. Current Branch State

- Branch: `codex/r-memory-compaction-lane-20260326`
- Launch posture:
  - `GO` for guided collaborator beta
  - `NO-GO` for public maturity claims
  - launch-default coordination remains `file-backed`

## 2. What Changed In This Wave (3-Day Observer Window Program)

### Observer window baseline — COMPLETE

The observer-window / low-drift-anchor bucket is now **baseline-complete**.

A fresh agent can run one command to see the system's center of gravity:

```bash
python scripts/run_observer_window.py --agent <your-id>
```

Output: `stable=5 contested=3 stale=1`

| Bucket | Items |
|--------|-------|
| **stable** | governance posture, launch tier (collaborator_beta), file-backed backend, evidence readout, session readiness |
| **contested** | council descriptive_only, compaction promotion hazard, subject snapshot advisory |
| **stale** | recent traces (>48h old) |

### Key fixes shipped

1. **Subprocess hang on Windows** — three scripts (`run_observer_window.py`, `run_launch_continuity_validation_wave.py`, `run_collaborator_beta_preflight.py`) were refactored from subprocess nesting to direct Python imports via `run_session_start_bundle()`.
2. **Import posture unwrapping** — `_build_import_posture()` surfaces were not being passed correctly to the observer window classification engine.
3. **Missing optional dependencies** — `pyproject.toml` now declares `[redis]`, `[aegis]`, `[monitoring]` optional groups.

### New files

| File | Purpose |
|------|---------|
| `docs/status/observer_window_latest.json` | Machine-readable observer readout |
| `docs/status/observer_window_latest.md` | Human-readable observer readout |
| `docs/status/architecture_dependency_diagnostic_2026-03-30.md` | Architecture/dependency audit |
| `docs/status/launch_continuity_validation_wave_latest.json` | 4-scenario validation wave results |
| `docs/status/collaborator_beta_preflight_latest.json` | Beta preflight results |

### Modified files

| File | Change |
|------|--------|
| `scripts/run_observer_window.py` | subprocess → direct import via `run_session_start_bundle` |
| `scripts/run_launch_continuity_validation_wave.py` | subprocess → direct import |
| `scripts/run_collaborator_beta_preflight.py` | subprocess → direct import |
| `scripts/start_agent_session.py` | extracted `run_session_start_bundle()` public API |
| `pyproject.toml` | added `[redis]`, `[aegis]`, `[monitoring]` optional-dependency groups |

## 3. Observer Window Baseline Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Discoverable** | ✅ | `scripts/run_observer_window.py --help` works, documented in this handoff |
| **Bounded** | ✅ | Output is advisory-only, receiver_note is explicit, never promotes into canonical truth |
| **Tested** | ✅ | 21 regression tests in `test_observer_window.py` + 11 in `test_start_agent_session.py` |
| **Used in validation** | ✅ | 17 synthetic scenarios pass, 4-scenario live validation wave pass, live vs manual reading: 9/9 match |

**Verdict: observer-window bucket reaches baseline. Freeze and rotate.**

## 4. Current Truths The Next Agent Should Not Forget

### Launch and honesty
- `collaborator_beta` is the current tier
- `public_launch` is only the next target tier, not current readiness
- `public_launch_ready = false`
- `launch_default_mode = file-backed`

### Council and evidence
- council confidence is **descriptive_only**, not calibrated
- agreement ≠ accuracy — do not restate coherence scores as precision
- council dossier in observer window is correctly marked as **contested**

### Observer window
- output is **advisory only** — do not promote into canonical governance truth
- `contested` items must not be treated as confirmed
- `stale` items should trigger a re-read before leaning on them

### Continuity and receiver posture
- session-start / packet / diagnose are aligned on `ack / apply / promote`
- working-style continuity is advisory-only
- subject snapshot is not canonical identity
- compaction carry-forward has promotion hazard — `must_not_promote`

## 5. Next Shortest Board

The observer-window bucket is done. The **next shortest board** is:

`broader collaborator-beta validation under more varied task shapes`

Specifically:
1. The current validation wave covers 4 scenarios (clean, claim conflict, stale compaction, contested dossier). More task shapes (e.g., multi-agent concurrent claims, long-running sessions, hot-path governance state updates) are untested.
2. The `stale` bucket currently shows `recent_traces` at 138h old — a compaction cycle should be run to exercise the trace-freshening path.
3. Working-style continuity has no live reinforcement data yet (always shows "insufficient" in validation).

**Do not rotate to this bucket until the observer-window freeze is committed.**

## 6. First 15 Minutes For The Successor Agent

Read, in this order:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `DESIGN.md`
4. **this handoff note**
5. `docs/plans/tonesoul_3day_execution_program_2026-03-30.md` (for context on what was just completed)

Then run:

```bash
python scripts/run_observer_window.py --agent <your-id>
python scripts/start_agent_session.py --agent <your-id> --no-ack
python scripts/run_collaborator_beta_preflight.py --agent <your-id>
```

## 7. Daily Command Baseline

```bash
# Quick observer readout
python scripts/run_observer_window.py --agent <your-id>

# Full session start
python scripts/start_agent_session.py --agent <your-id> --no-ack

# Beta preflight
python scripts/run_collaborator_beta_preflight.py --agent <your-id>

# Validation wave (4 scenarios)
python scripts/run_launch_continuity_validation_wave.py

# Regression tests
python -m pytest tests/test_observer_window.py tests/test_start_agent_session.py -v
```

## 8. What Still Must Not Be Touched Casually

- `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
- `OpenClaw-Memory`
- `.claude/` permission-locked local residue

## 9. If Work Starts Going Sideways

1. Stop widening claims
2. Re-run the observer window: `python scripts/run_observer_window.py --agent <your-id>`
3. If `contested` items appear that shouldn't, return to `DESIGN.md` and `docs/plans/`
4. Do not invent a new architecture lane — resume from the next shortest board

## 10. Compressed Thesis

The observer window is now baseline-complete. The next step is not bigger architecture or wider launch claims.

It is: `validate the current stack under more varied real task shapes before declaring broader maturity.`
