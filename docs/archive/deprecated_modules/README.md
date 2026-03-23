# Deprecated Modules Archive

> Purpose: explain why deprecated runtime modules were moved into archive rather than treated as active production surfaces.
> Last Updated: 2026-03-23

**Date**: 2026-03-04 (Round 2 WEAK/CAUTION Deep Audit)
**Auditor**: Codex (analysis) + Antigravity (execution)

## Why These Were Archived

These modules had **zero runtime imports** and are no longer part of the active
production code path. They are preserved here for historical/research reference.

| Module | Lines | Reason |
|--------|------:|--------|
| `audit_dashboard.py` | 797 | Legacy dashboard; superseded by new API routes |
| `etcl_lifecycle.py` | 98 | ETCL lifecycle research tool; no runtime integration |
| `persistence.py` | 234 | Old persistence demo; replaced by current persistence paths |
| `persona_trace_report.py` | 149 | Legacy reporting; only referenced by old dashboard |
| `quick_council.py` | 244 | Heuristic council; replaced by full Council + Deliberation |
| `storage.py` (ystm) | 187 | YSTM serialization tool; concept archive only |
| `pipeline_context.py` | 80 | CAUTION-level; unconnected design artifact |

## Deleted Modules (not archived)

The following modules were fully deleted as they had zero value for reference:

- `append_council_event.py` — covered by council runtime
- `generate_patch.py` — static patch generator, no integration
- `persona_ledger_validator.py` — sample validator script
- `persona_registry_builder.py` — zero references
- `persona_registry_cleaner.py` — zero references
- `persona_registry_summary.py` — zero references
- `self_test.py` — outdated self-test script
- `simulate_council.py` — deprecated, replaced by council runtime
