# ToneSoul Knowledge Layer Source Taxonomy And Parking Contract

> Purpose: classify ToneSoul's current knowledge-bearing surfaces so raw sources, compiled notes, parked drafts, operator retrieval, and public teaching stop collapsing into one memory bucket.
> Authority: boundary aid only. Does not outrank runtime code, canonical anchors, or accepted architecture contracts.

---

## Why This Exists

ToneSoul now has at least five different kinds of knowledge-bearing material:

- raw external sources
- compiled internal distillations
- parked exploratory drafts
- bounded operator-facing retrieval surfaces
- public/demo teaching surfaces

If these are not separated, later agents make the same mistakes again:

1. parked theory gets treated like current truth
2. compiled notes get treated like hot runtime state
3. demo/teaching text gets mistaken for operator authority
4. raw source clones get treated like already-digested knowledge

This contract exists to stop that blur.

---

## The 5-Layer Taxonomy

### 1. Raw Sources

Examples:

- `external_research/`
- local repo clones such as `claw-code-main/`
- upstream papers, repos, and websites referenced by distillation notes
- historical source documents that have not yet been distilled

Use posture:

- read-only source material
- may inspire distillation

Must not become:

- runtime truth
- hot continuity
- compiled knowledge by default

### 2. Compiled Knowledge

Examples:

- `docs/research/tonesoul_*_distillation_*.md`
- `docs/research/tonesoul_recognized_paper_synthesis_*.md`

Use posture:

- distilled and repo-native knowledge notes
- suitable as future compiled-knowledge inputs

Must not become:

- current short-board truth
- runtime mutation authority

### 3. Exploratory Residue

Examples:

- parked `docs/plans/tonesoul_*_design_*.md`
- unratified sidecar drafts
- temporary cross-repo comparisons that have not yet been distilled

Use posture:

- parking lane for ideas that may still yield value

Must not become:

- canonical architecture
- compiled knowledge without a distillation step

### 4. Operator Retrieval

Examples:

- current bounded search preview in dashboard
- future graph/query tools
- future collection-aware operator query surfaces

Use posture:

- operator-facing access path into bounded compiled knowledge or auxiliary context

Must not become:

- a replacement for `session-start`
- hot coordination state
- identity or continuity

### 5. Public Teaching

Examples:

- `apps/web` educational tier cues
- public/demo walkthrough copy
- README-level teaching surfaces

Use posture:

- explain ToneSoul to humans and demo audiences

Must not become:

- operator truth
- mutation permission
- deep governance surface

---

## Current Repo Mapping

- `external_research/` -> `raw_sources`
- `claw-code-main/` -> `raw_sources`
- `docs/research/` -> `compiled_knowledge`
- parked `docs/plans/tonesoul_*_design_*.md` -> `exploratory_residue`
- dashboard search cue / retrieval preview -> `operator_retrieval`
- `apps/web` tier cue / public docs surfaces -> `public_teaching`

---

## Parking Rules

1. Raw sources stay parked until they are distilled.
2. Exploratory residue stays parked until one bounded idea is explicitly pulled into a live short board.
3. Compiled knowledge may inform design, but it still does not outrank canonical anchors or current runtime truth.
4. Operator retrieval stays auxiliary unless a future compiled-knowledge query layer is explicitly accepted.
5. Public teaching surfaces may explain the system, but they must never impersonate operator authority.

---

## Non-Goals

- moving parked files right now
- creating a retrieval runtime
- turning compiled knowledge into memory identity
- indexing every research note immediately
