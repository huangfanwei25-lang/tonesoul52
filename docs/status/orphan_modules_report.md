# Orphan Modules Report

- generated_at: 2026-03-03T14:25:39Z
- scope: `tonesoul` orphan candidates from CODEX_TASK (22 modules)
- method: AST import audit + token search (`*.py`, `*.yml`, `*.md`, `*.toml`) with task/report self-references excluded
- summary: ALIVE=4, WEAK=14, CAUTION=1, DEAD=3
- actions: KEEP=19, DELETE=3

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
