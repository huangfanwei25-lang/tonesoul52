# ToneSoul Distillation From heddle, qmd, And obsidian-graph-query (2026-04-06)

> Purpose: distill only the parts of `heddle`, `qmd`, and `obsidian-graph-query` that materially help ToneSoul's runtime discipline, knowledge layers, and operator surfaces.
> Scope: not a generic repo review. This note exists to answer one question:
>
> `which patterns from these three repos should ToneSoul absorb, and which ones should remain external inspiration only?`
>
> Sources inspected: local clones under `external_research/heddle/`, `external_research/qmd/`, and `external_research/obsidian-graph-query/`, plus their public upstream READMEs.
> Status: research note
> Authority: design aid only. This note does not outrank runtime code, tests, or canonical ToneSoul architecture contracts.

---

## Compressed Verdict

These three repos are useful for three different reasons:

1. `heddle`
   - teaches `minimal agent runtime discipline`
   - useful as a counterweight against ToneSoul workflow sprawl

2. `qmd`
   - teaches `knowledge-layer retrieval discipline`
   - the strongest external reference for a future ToneSoul knowledge index

3. `obsidian-graph-query`
   - teaches `bounded graph query packaging`
   - useful as an operator/query skill pattern, not as a central runtime

The combined lesson is:

`ToneSoul should keep multi-agent governance, but reduce default surface area, separate retrieval from continuity, and expose graph-like operator queries only through bounded tools.`

---

## What Each Repo Actually Is

### 1. heddle

After source review, `heddle` is not mainly a prompt pack.
It is a small terminal agent runtime with:

- a minimal `runAgent` loop
- approval-gated shell execution
- remembered per-project approvals
- session persistence under `.heddle/`
- short-plan tracking
- lightweight chat compaction

The real center of gravity is:

- `src/run-agent.ts`
- `src/cli/chat/state/storage.ts`
- `src/cli/chat/state/compaction.ts`
- `src/cli/chat/state/approval-rules.ts`

Its strongest message is:

`do not make the runtime larger than the operator actually needs.`

### 2. qmd

`qmd` is not an agent shell.
It is an on-device retrieval engine for Markdown and adjacent document knowledge.

Its real center of gravity is:

- `src/store.ts`
- `src/db.ts`
- `src/collections.ts`
- `src/mcp/server.ts`

The key features are:

- BM25 + vector + RRF + reranker
- SQLite-centered storage
- YAML collection config
- context trees per collection/path prefix
- MCP and SDK-first usage

Its strongest message is:

`knowledge retrieval should be a first-class subsystem, not an afterthought hidden inside prompts.`

### 3. obsidian-graph-query

`obsidian-graph-query` is not a general knowledge platform.
It is a graph-query skill layer around Obsidian's resolved link graph.

Its real center of gravity is:

- `skills/obsidian-graph-query/SKILL.md`
- `skills/obsidian-graph-query/references/query-templates.md`
- `skills/obsidian-graph-query/references/relationship-types.md`

The pattern is:

- graph algorithms packaged as parameterized JS templates
- bounded output shapes
- query-selection guidance
- vault health / structure analysis

Its strongest message is:

`graph analysis becomes much more usable when exposed as a small set of operator queries instead of a vague “knowledge graph” claim.`

---

## The Strongest Things ToneSoul Should Absorb

## A. From heddle

### 1. Small runtime shells are a feature, not a weakness

`heddle` is useful because it does not pretend every task needs a workflow empire.

ToneSoul should absorb:

- smaller default runtime loops
- fast-path entry for bounded work
- fewer always-on surfaces in the first hop
- operator control over what gets expanded

This directly supports ToneSoul's recent tier model:

- Tier 0 = instant gate
- Tier 1 = orientation shell
- Tier 2 = deep governance drawer

### 2. Approval memory should stay narrow and project-local

`heddle`'s approval-rules layer is simple but strong:

- normalize command families
- remember approvals per project
- keep edit approvals separate from shell approvals
- do not pretend an approval ledger is a deeper identity system

ToneSoul should absorb:

- narrow remembered approval paths
- scoped mutation memory
- command-family approvals only for low-risk repeated verification flows

ToneSoul should not absorb:

- a general “approval everything” state sprawl

### 3. Compaction should stay lightweight and operator-oriented

`heddle`'s compaction is valuable mostly because it stays humble.
It exists to keep chat continuity usable, not to simulate identity permanence.

That aligns with ToneSoul's current direction:

- bounded handoff
- explicit closeout states
- observer-window attention surfaces
- hot-memory ladder

The useful lesson is:

`compaction is for carrying bounded work forward, not for silently upgrading summaries into truth.`

## B. From qmd

### 4. Retrieval should be its own subsystem, not mixed into continuity

`qmd` is the clearest external example of something ToneSoul still lacks:

`a serious knowledge index that is not confused with memory, identity, or governance.`

ToneSoul should absorb:

- separate retrieval layer language
- collections as explicit scope boundaries
- context trees as path-sensitive knowledge hints
- MCP / SDK surfaces that are narrow and query-oriented

ToneSoul should not collapse:

- retrieval success
- continuity quality
- subject identity

Those are adjacent, not identical.

### 5. Context trees are more useful than flat collection labels

This is one of `qmd`'s best ideas.
Its collection contexts are not just global descriptions; they can vary by subpath.

That matters for ToneSoul because many future knowledge surfaces will not be uniform.
Examples:

- architecture vs plans vs status
- canonical contracts vs exploratory drafts
- operator guides vs public docs

ToneSoul should absorb:

- hierarchical context annotations
- scoped explanatory context that rides with retrieval results
- path-prefix context rather than one global summary per knowledge bucket

### 6. Knowledge health should be a runtime concern

`qmd` treats indexing, retrieval, status, and structure as things that can be checked.

This fits a missing ToneSoul lane:

`knowledge hygiene and retrieval operability`

ToneSoul should absorb:

- health/status readouts for future knowledge index layers
- collection coverage checks
- retrieval-surface diagnostics

## C. From obsidian-graph-query

### 7. Graph queries should be exposed as bounded operator tools

The most useful idea here is not “build a knowledge graph UI.”
It is:

`turn graph reasoning into a small menu of bounded, named queries.`

Examples from the repo:

- neighbors
- shortest path
- clusters
- hubs
- bridges
- orphans
- vault stats

ToneSoul should absorb:

- bounded query families
- explicit parameter validation
- output caps
- “choose the query based on the question” operator guidance

This is directly relevant for future:

- observer-window graph views
- knowledge-layer hygiene reports
- document lineage / dependency readouts
- subsystem relationship queries

### 8. Relationship inference should be layered

The repo's relationship-summary flow is useful because it separates:

- explicit graph structure
- frontmatter / metadata relations
- optional content-level inference

That layered approach matches ToneSoul's general discipline:

- explicit evidence first
- derived structure second
- model inference last

ToneSoul should absorb this ordering logic.

---

## What ToneSoul Should Not Copy

### 1. Do not copy external naming universes

None of these repos should donate their nouns directly into ToneSoul's canonical language.

Use their patterns.
Do not import their worldbuilding.

### 2. Do not turn retrieval into pseudo-memory

`qmd` is strong precisely because it is retrieval infrastructure.
If ToneSoul adopts similar capabilities, it must not start calling that:

- continuity
- subject persistence
- identity

### 3. Do not let graph tooling become a new surface tax

`obsidian-graph-query` works because it stays as a skill/query layer.
If ToneSoul copies the graph idea, it should remain:

- bounded
- opt-in
- operator-facing
- question-driven

Not a permanent always-on graph subsystem.

### 4. Do not respond to complexity by building another complexity layer

`heddle` is valuable partly because it resists overgrowth.
ToneSoul should take that warning seriously.

The correct reaction to a large governance runtime is not:

`add a second large shell to manage the first shell`

The correct reaction is:

`reduce the default path and escalate only when needed`

---

## Combined Distillation For ToneSoul

If these three repos are distilled together, the design lesson becomes:

### 1. Keep the default runtime small

Borrow from `heddle`:

- minimal first hop
- explicit operator approvals
- lightweight compaction

### 2. Build a real knowledge layer later

Borrow from `qmd`:

- retrieval as a subsystem
- collection contexts
- health/status surfaces
- narrow MCP/SDK interfaces

### 3. Expose graph structure through bounded queries, not mythology

Borrow from `obsidian-graph-query`:

- named graph queries
- bounded result sizes
- operator guidance for choosing query type

---

## Best Near-Term Follow-Ups For ToneSoul

### 1. Knowledge Layer Distillation Program

Not implementation yet.
First define:

- raw source layer
- compiled knowledge layer
- exploratory residue layer
- operator retrieval layer

This is the most valuable thing `qmd` suggests for ToneSoul.

### 2. Tier-0 / Tier-1 Runtime Slimming Review

Use `heddle` as a counterexample to surface sprawl.
Ask:

- which first-hop fields are truly necessary
- which can move to deep pull only
- which are still paying constant latency tax

### 3. Bounded Graph Query Spec For Observer And Knowledge Hygiene

Do not build UI first.
First define 4-6 query families, such as:

- neighbor surfaces
- source lineage path
- stale orphan detector
- bridge node detector
- subsystem dependency cluster

This is the part of `obsidian-graph-query` most worth translating.

---

## Final Judgment

These repos are helpful for different layers:

- `heddle` helps ToneSoul simplify the runtime shell
- `qmd` helps ToneSoul imagine a proper future knowledge index
- `obsidian-graph-query` helps ToneSoul package graph reasoning as bounded tools

The most important combined lesson is:

`keep governance deep, but keep default interaction thin.`

And the second most important lesson is:

`treat retrieval, continuity, and identity as separate subsystems even when they collaborate closely.`
