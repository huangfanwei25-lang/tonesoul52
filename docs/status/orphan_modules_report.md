# Orphan Modules Report

- generated_at: 2026-03-03T14:25:39Z
- scope: `tonesoul` orphan candidates from CODEX_TASK (22 modules)
- method: AST import audit + token search (`*.py`, `*.yml`, `*.md`, `*.toml`) with task/report self-references excluded
- summary: ALIVE=4, WEAK=14, CAUTION=1, DEAD=3
- actions: KEEP=19, DELETE=3
- note: the summary above is the Round 1 / pre-Round-2 baseline. See the Round 2 reconciliation section below for the final state after commit `ac1abef`.

## Classification
| Module | Class | Action | Notes |
| --- | --- | --- | --- |
| `tonesoul.adapters` | DEAD | DELETE | Zero references in code/docs/workflows after wrapper cleanup. |
| `tonesoul.append_council_event` | WEAK | KEEP | Standalone utility; no current runtime references. |
| `tonesoul.audit_dashboard` | WEAK | KEEP | Legacy dashboard module; no active import edges. |
| `tonesoul.config` | ALIVE | KEEP | Imported by inventory/healthcheck verification pipeline. |
| `tonesoul.etcl_lifecycle` | WEAK | KEEP | Referenced in research docs; no active runtime import. |
| `tonesoul.generate_patch` | WEAK | KEEP | Standalone patch helper; not wired into runtime. |
| `tonesoul.persistence` | WEAK | KEEP | Mentioned in docs only; no active import edges. |
| `tonesoul.persona_ledger_validator` | WEAK | KEEP | Validator utility kept for manual diagnostics. |
| `tonesoul.persona_registry_builder` | WEAK | KEEP | Registry maintenance utility kept for manual use. |
| `tonesoul.persona_registry_cleaner` | WEAK | KEEP | Registry maintenance utility kept for manual use. |
| `tonesoul.persona_registry_summary` | WEAK | KEEP | Registry maintenance utility kept for manual use. |
| `tonesoul.persona_trace_report` | WEAK | KEEP | Reporting utility retained for manual diagnostics. |
| `tonesoul.pipeline_context` | CAUTION | KEEP | Potential architectural boundary module; no safe-delete confidence. |
| `tonesoul.quick_council` | WEAK | KEEP | Deprecated lightweight council utility retained for now. |
| `tonesoul.self_test` | WEAK | KEEP | Legacy self-check utility retained for now. |
| `tonesoul.simulate_council` | WEAK | KEEP | Deprecated shim retained to avoid accidental behavior drift. |
| `tonesoul.test_integration` | DEAD | DELETE | Legacy tonesoul52 script with no references. |
| `tonesoul.test_interception` | DEAD | DELETE | Legacy tonesoul52 script with no references. |
| `tonesoul.tonesoul_llm` | ALIVE | KEEP | Referenced by healthcheck import probes. |
| `tonesoul.ystm.acceptance` | ALIVE | KEEP | Imported by yss_gates build_test_gate. |
| `tonesoul.ystm.storage` | WEAK | KEEP | No active call sites after CLI cleanup; retained conservatively. |
| `tonesoul.ystm_demo` | ALIVE | KEEP | Referenced by dashboard guidance commands. |

## Deleted In This Phase
- `tonesoul/adapters.py`
- `tonesoul/test_integration.py`
- `tonesoul/test_interception.py`

## Artifacts
- `docs/status/orphan_modules_audit_refs.json`
- `docs/status/orphan_modules_audit_detail.json`

## Round 2 Reconciliation (Verified 2026-03-07)

- source_of_truth_commit: `ac1abef` (`refactor: architecture cleanup round 2 + V2 runtime wiring`)
- reconciliation_method:
  - confirmed target files are no longer present under `tonesoul/`
  - confirmed archive files exist under `docs/archive/deprecated_modules/`
  - confirmed historical execution details from `git show --stat ac1abef`
- warning: Round 2 was committed together with V2 runtime wiring, so cleanup provenance should be read by path, not by commit title alone.

| Module | Round 2 Final Action | Current State | Reason |
| --- | --- | --- | --- |
| `tonesoul.append_council_event` | DELETE | absent from `tonesoul/` | Replaced by active council runtime / provenance path. |
| `tonesoul.audit_dashboard` | ARCHIVE | `docs/archive/deprecated_modules/audit_dashboard.py` | Legacy dashboard only. |
| `tonesoul.etcl_lifecycle` | ARCHIVE | `docs/archive/deprecated_modules/etcl_lifecycle.py` | Research helper with no runtime wiring. |
| `tonesoul.generate_patch` | DELETE | absent from `tonesoul/` | Static patch helper with no integration. |
| `tonesoul.persistence` | ARCHIVE | `docs/archive/deprecated_modules/persistence.py` | Old persistence demo retained for reference. |
| `tonesoul.persona_ledger_validator` | DELETE | absent from `tonesoul/` | Unused validator script. |
| `tonesoul.persona_registry_builder` | DELETE | absent from `tonesoul/` | Zero-reference registry trio removed by Task C. |
| `tonesoul.persona_registry_cleaner` | DELETE | absent from `tonesoul/` | Zero-reference registry trio removed by Task C. |
| `tonesoul.persona_registry_summary` | DELETE | absent from `tonesoul/` | Zero-reference registry trio removed by Task C. |
| `tonesoul.persona_trace_report` | ARCHIVE | `docs/archive/deprecated_modules/persona_trace_report.py` | Preserved with legacy dashboard/report flow. |
| `tonesoul.quick_council` | ARCHIVE | `docs/archive/deprecated_modules/quick_council.py` | Historical heuristic council implementation. |
| `tonesoul.self_test` | DELETE | absent from `tonesoul/` | Outdated self-test helper. |
| `tonesoul.simulate_council` | DELETE | absent from `tonesoul/` | Deprecated shim replaced by runtime council. |
| `tonesoul.ystm.storage` | ARCHIVE | `docs/archive/deprecated_modules/storage.py` | YSTM serialization archive. |
| `tonesoul.pipeline_context` | ARCHIVE | `docs/archive/deprecated_modules/pipeline_context.py` | CAUTION module archived by policy instead of deleted. |

### Round 2 Net Result

- Deleted modules: `8`
- Archived modules: `7`
- Reopened modules: `0`
- Notes:
  - This section supersedes the Round 1 `KEEP=19, DELETE=3` snapshot for the 15 Round 2 targets.
  - Historical Round 2 validation was recorded as `1201 passed, black clean` in commit `ac1abef`.
  - Current local test failures in a dirty workspace should be documented separately and must not be retroactively attached to the historical Round 2 cleanup.
