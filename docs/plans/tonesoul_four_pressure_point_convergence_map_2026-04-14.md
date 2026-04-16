# ToneSoul Four Pressure Point Convergence Map (2026-04-14)

> Purpose: turn the current consistency concerns into one bounded work order so later agents stop reopening the same repo-shape problems from scratch.
> Status: accepted planning aid for the next convergence pass.
> Authority: planning aid. Runtime truth remains in code, tests, `task.md`, and accepted architecture contracts.

---

## Compressed Thesis

The next highest-leverage move is not a large runtime rewrite.

It is to make ToneSoul more consistent at first hop, more honest about formula status, and stricter about authority boundaries.

That is because the current main pressures are coupled:

- duplication creates multiple plausible readings
- context bloat makes those readings expensive to align
- pseudo-formulas make descriptive language look more precise than it is
- layer confusion lets the same term drift between runtime, theory, and storage lanes

If these stay loose, later code cleanup will keep re-inflating.

---

## Current Baseline

The repo is not blocked by a missing core demonstration.

- `examples/quickstart.py` already provides a small runnable whole-path demo.
- blocking validation already has a defined lane: `python scripts/run_test_tier.py --tier blocking`
- the new Foundation Layer now provides one thin startup packet: `docs/foundation/README.md`

So the immediate deficit is not "nothing works."

It is "too many surfaces still tell roughly the same story in different ways."

---

## Scorecard

| Pressure point | Current severity | Evidence | Primary risk | First bounded move |
|---|---|---|---|---|
| duplication | high | `docs/*.md` = `538`; `docs/plans` = `167`; `README.md`, `DESIGN.md`, whole-system guide all act as overview entry surfaces | later agents re-explain instead of continuing | compress overview ownership and mirror policy |
| context bloat | critical | doc authority map tracks `25` groups / `103` files; first-hop routing still spans multiple lanes; `unified_pipeline.py` = `3284` lines, `runtime_adapter.py` = `3110` lines | retrieval cost and interpretation drift stay high | lock one startup order and one "open this first" packet |
| pseudo-formulas | medium-high | `README.md` is honest that much of the math is heuristic, but formula status is still scattered across `README`, `GLOSSARY`, and `MATH_FOUNDATIONS` | descriptive heuristics get mistaken for executable truth | add one formula taxonomy: `rigorous / heuristic / conceptual / retired` |
| layer confusion | high | repo already needs explicit boundary contracts for `knowledge/`, `knowledge_base/`, `PARADOXES/`, plus a 25-group authority structure report | runtime, storage, and theory claims silently swap lanes | publish and enforce one authority ladder per surface family |

---

## Pressure Point A: Duplication

### What is actually happening

- The repo already admits it needs "one durable design center over several overlapping overview files."
- `README.md` routes readers to the whole-system guide, `DESIGN.md`, and now the Foundation Layer.
- `DESIGN.md` explicitly says it is the current design center and complements `README.md` plus deeper contracts.

This is not uncontrolled chaos.

It is controlled overlap that has not yet been compressed far enough.

### Why it matters

- humans and agents can both find a plausible overview and stop too early
- overview files become semi-canonical by habit instead of by explicit ownership
- cleanup becomes politically expensive because every file feels important

### First cut

1. keep one owner per overview class:
   - entry packet: `docs/foundation/README.md`
   - durable design center: `DESIGN.md`
   - panoramic whole-system map: `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md`
2. mark every other overview-like surface as mirror, historical, or deep-read.
3. stop adding fresh overview prose unless it replaces an existing owner or mirror.

### Freeze rule

Do not create another repo-wide "what ToneSoul is" document until one existing overview surface is explicitly demoted or superseded.

---

## Pressure Point B: Context Bloat

### What is actually happening

- The authority structure is already retrieval-oriented, but it still spans `25` grouped lanes and `103` tracked files.
- The repo has `538` markdown files, with especially heavy pressure in `plans`, `status`, and `architecture`.
- Two key runtime surfaces exceed `3000` lines, which makes later explanation and boundary reading harder.

### Why it matters

- later agents spend tokens reconstructing routing instead of executing work
- first-hop reading order is still fragile under low-context handoff
- large core files attract "just read the whole thing" behavior, which scales badly

### First cut

1. treat `docs/foundation/README.md` as the default first-hop packet for new conversations.
2. keep first-hop work scoped to entry packet -> task board -> blocking checks, before deep maps.
3. define one short "core demo + blocking lane" path that later agents can run before opening large theory surfaces.

### Freeze rule

Do not add new entrypoint or onboarding surfaces unless they reduce the number of first-hop decisions instead of increasing them.

---

## Pressure Point C: Pseudo-Formulas

### What is actually happening

- `README.md` already states that cosine distance, exponential decay, and entropy have solid theory, while weighted sums and thresholds are tunable heuristics.
- Formula semantics are still distributed across multiple documents.
- Some formula-heavy docs are harder to trust operationally when wording quality or encoding quality is degraded.

### Why it matters

- symbolic notation can look more rigorous than the implementation deserves
- later agents may repeat a conceptual equation as if it were executable truth
- mathematical language becomes branding instead of an honesty contract

### First cut

1. add a repo-wide formula label set:
   - `rigorous`
   - `heuristic`
   - `conceptual`
   - `retired`
2. require every named formula to point to one executable owner or to explicitly say that no executable owner exists.
3. start with the small set repeated in entry surfaces before touching deep math prose.

### Freeze rule

Do not introduce a new symbolic formula into an entry or canonical doc unless its status label and executable owner are declared on the same page.

---

## Pressure Point D: Layer Confusion

### What is actually happening

- The repo already contains boundary maps for knowledge surfaces, authority roles, claim authority, and validation lanes.
- That means the problem is no longer absence of boundaries.
- The problem is that those boundaries are still too distributed to function as one shared mental model under fast handoff.

### Why it matters

- the same concept can drift between runtime object, theory note, and storage surface
- agents may edit the wrong layer because they can explain the right term
- retrieval can flatten boundaries that the repo already worked hard to distinguish

### First cut

1. keep the authority ladder explicit:
   - code, tests, `AXIOMS.json`
   - `task.md` and accepted architecture contracts
   - Foundation Layer
   - plans, status, chronicles
2. extend that same ladder into module families and knowledge surfaces.
3. require boundary-moving proposals to name:
   - source lane
   - target lane
   - authority reason
   - validation burden

### Freeze rule

Do not rename or merge knowledge-like surfaces just because their words sound similar; boundary changes need an explicit contract.

---

## Recommended Order

### Pass 1: Entry Compression

Goal:

- reduce duplication and context bloat at the same time

Likely outputs:

- overview ownership table
- mirror/superseded labels on overlapping overview docs
- one fixed startup path for humans and agents

### Pass 2: Formula Honesty

Goal:

- stop conceptual math from silently masquerading as runtime math

Likely outputs:

- formula taxonomy
- cleaned entry-surface formula labels
- executable-owner references for repeated formulas

### Pass 3: Authority And Layer Enforcement

Goal:

- make boundary decisions explicit before runtime refactors

Likely outputs:

- surface-family authority ladder
- boundary-change checklist
- module seam map for later runtime decomposition

### Pass 4: Runtime Decomposition

Goal:

- only after the above, split the largest runtime files with lower drift risk

Likely targets:

- `tonesoul/unified_pipeline.py`
- `tonesoul/runtime_adapter.py`

This pass should come later, not first.

---

## What Not To Do

- Do not start by rewriting the full runtime around a fresh ontology.
- Do not create another giant architecture lane to explain the cleanup.
- Do not treat every duplicate as accidental; some surfaces are mirrors by design.
- Do not let a formula earn precision just because it looks elegant in symbolic form.

---

## Immediate Next Move

The best next implementation step is:

`Pass 1: Entry Compression`

More specifically:

1. define overview ownership and mirror policy
2. reduce first-hop branching across entry surfaces
3. anchor one short runnable path: foundation -> `task.md` -> `examples/quickstart.py` -> blocking tier

That gives later agents a stable first move before touching the deeper cleanup buckets.
