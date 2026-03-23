# ADR-001: Dual-Track Codebase Resolution

> Purpose: architectural decision record that resolves the old dual-track core layout and declares `tonesoul/` as canonical.
> Last Updated: 2026-03-23

## Status
Accepted

## Date
2026-01-10

## Context
The ToneSoul repository contained two parallel "core" structures:
1. `src/core/`: Containing `ToneSoul_Core_Architecture.py`, `decision_kernel.py`, and subdirectories (`dreaming`, `ethics`, etc.). This appeared to be conceptual skeletons or early heuristic prototypes.
2. `tonesoul/`: Containing the active, integrated implementation (`unified_core.py`, `time_island.py`, etc.) with over 87 modules.

This duality created significant risks:
- **Definition Drift**: Concepts defined in one place might diverge from the other.
- **Maintenance Overhead**: Uncertainty about which files to update.
- **Cognitive Load**: New contributors (and AI agents) struggle to identify the canonical source.

## Decision
We designate **`tonesoul/`** as the **Canonical Source of Truth** for the ToneSoul engine.

The contents of `src/core/` have been moved to `legacy/src_core_archive/`.
They are preserved for historical reference and conceptual inspiration but are **not** considered part of the active codebase.

## Consequences
### Positive
- **Clarity**: Single entry point for core logic.
- **Focus**: Development efforts concentrate on `tonesoul/` modules.
- **Consistency**: Unified imports and class definitions.

### Negative
- **Broken Links**: Any external documentation or scripts pointing to `src/core/` will break (must be updated).
- **Lost Prototypes**: Some heuristic ideas in `src/core/` might not yet be fully ported to `tonesoul/` (mitigated by keeping them in archive).

## Implementation
- `src/core/` moved to `legacy/src_core_archive/`.
- Healthchecks updated to target `tonesoul/`.
- Documentation should reference `tonesoul/` files.
