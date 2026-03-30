# Local Residue Holding Area

> Status: non-canonical local holding area
> Purpose: keep clearly non-authoritative local leftovers out of the main repo narrative without pretending they are public architecture surfaces.

## What lives here

This folder is for:
- local sketches
- one-off diagrams
- temporary non-canonical reference material

It is **not** part of the ToneSoul authority lanes, runtime contracts, or public entry stack.

## Current Contents

### `architecture_sketches_local/`

Originally moved from a local Chinese-named sketch folder used for test architecture diagrams.

This folder stays here because it is:
- a local architecture-sketch artifact
- not part of the current authority/doc lanes
- still potentially useful as a local visual draft

Current files:
- `module_dependency_map_initial.md`
- `module_dependency_map_split_names.md`

## Residues intentionally not moved here

These remain outside this folder on purpose:

- `CLAUDE.md`
  - human/local companion note
  - tracked and intentionally left in place
- `OpenClaw-Memory/`
  - nested repo / submodule-like external memory surface
  - not a local draft folder
- `memory/autonomous/session_traces.jsonl`
- `memory/autonomous/zone_registry.json`
  - protected runtime memory data
  - must not be reorganized into public/local doc holding areas
- `.claude/`
  - OS-level permission-locked residue
  - currently not safely movable from normal repo operations

## Boundary Rule

If something in here becomes important enough to describe publicly, it should be rewritten into a proper ToneSoul-native document elsewhere instead of being promoted directly from this folder.
