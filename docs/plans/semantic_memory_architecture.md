# Semantic Memory & Atlas — 語義記憶與圖冊架構

> Purpose: consolidate semantic-memory and atlas addenda into one architecture-side planning surface.
> Last Updated: 2026-03-23

> 合併日期：2026-03-19
> 原始 addendum 數：8
> 時間跨度：2026-03-15 ~ 2026-03-16
> 合併者：痕 (Hén)

語義圖冊設計、生物記憶類比、ICL 概念翻譯、檢索協議、文件線索索引。

---

## 目錄

1. `repo_semantic_atlas_addendum_2026-03-15.md`
2. `icl_task_recognition_semantic_translation_addendum_2026-03-16.md`
3. `repo_document_threads_addendum_2026-03-16.md`
4. `repo_intelligence_semantic_protocol_addendum_2026-03-16.md`
5. `repo_intelligence_settlement_mirror_addendum_2026-03-16.md`
6. `repo_semantic_atlas_governance_mirror_addendum_2026-03-16.md`
7. `repo_semantic_memory_contract_addendum_2026-03-16.md`
8. `semantic_protocol_handoff_parity_addendum_2026-03-16.md`

---

## 1. 原始檔案：`repo_semantic_atlas_addendum_2026-03-15.md`

## Repo Semantic Atlas Addendum (2026-03-15)

### Why

`repo_intelligence_latest.json` already tells later agents which status surfaces to
open first, and `skill_topology.*` already captures a low-level file graph.

But there is still a missing middle layer:

- humans remember articles, metaphors, and lanes
- agents need canonical paths, entrypoints, and neighboring surfaces
- the repository currently has no bounded artifact that bridges those two

This gap shows up in a simple way: a human can remember "ToneSoul Chronicles"
without remembering that the first concrete file is
`docs/chronicles/scribe_chronicle_20260312_232804.md`.

### Decision

Add a compact `repo_semantic_atlas_latest.*` artifact family.

It should not attempt a full dependency graph or dynamic vector search.
Instead, it should publish three bounded layers:

1. semantic aliases
   - human-facing names or remembered phrases
   - canonical paths
   - short reasons why those paths matter
2. semantic neighborhoods
   - a small number of system lanes
   - their key files
   - their neighboring lanes and preferred status surfaces
3. a simple graph view
   - domain-level links only
   - enough to act like a "nerve map"
   - not a raw every-file topology

### Constraints

- keep this artifact passive and source-declared
- do not make it reparse all status artifacts for derived truth
- do not duplicate `skill_topology` or pretend to replace code search
- keep the first version deterministic and human-readable

### First Scope

The first version should:

- index the `docs/chronicles/` lane, including the first chronicle title
- register `ToneSoul Chronicles` as a semantic alias
- define bounded neighborhoods for:
  - wakeup / dream
  - Scribe / chronicles
  - weekly verification
  - subjectivity review
  - repo governance
  - market mirror
- emit:
  - JSON
  - Markdown
  - Mermaid graph

### Success Criteria

Later agents can answer questions like:

- "Where was the first ToneSoul Chronicle?"
- "If I need the wakeup lane, which files and status surfaces should I open?"
- "What is the neighboring relationship between dream, weekly, Scribe, and repo governance?"

without re-deriving that structure from raw filenames alone.

---

## 2. 原始檔案：`icl_task_recognition_semantic_translation_addendum_2026-03-16.md`

## ICL Task Recognition Semantic Translation Addendum (2026-03-16)

### Why

The semantic memory contract already borrows from:

- biological indexing
- retrieval literature

But one more result matters for ToneSoul:

- in-context protocol can become an internal task-routing signal
- this is stronger than "prompt wording matters"
- it supports the idea that protocol can act like a lightweight temporary organ

### Source

Primary source:

- Sia et al., 2024, *Where does In-context Learning Happen in Large Language Models?*
- NeurIPS 2024 proceedings
- https://proceedings.neurips.cc/paper_files/paper/2024/file/3979818cdc7bc8dbeec87170c11ee340-Paper-Conference.pdf

Operator-provided secondary pointer:

- https://open.substack.com/pub/symboisislab/p/in-context-learning-ai?r=7wdhz8&utm_medium=ios

### ToneSoul Translation

We should not import the paper's wording directly as ontology.

Instead, translate it into ToneSoul language:

- `task recognition point` -> `protocol recognition seam`
- `context redundancy after recognition` -> `post-seam context release`
- `prompt examples locating the task` -> `protocol cueing a lane`
- `layer-wise recognition` -> `where protocol becomes an active routing organ`

### What We Accept

This paper supports:

- protocol can become an executable internal cue
- context does not stay equally necessary at every stage
- structured protocol matters as more than cosmetic prompt phrasing

### What We Do Not Overclaim

This paper does **not** by itself prove:

- stable subjectivity
- long-term memory
- governance closure
- semantic responsibility

So in ToneSoul terms, this is support for:

- `ProtocolIsTheNewParameter`
- temporary routing plasticity
- structured cueing

It is not yet proof of full soulhood.

### Implementation Decision

Encode one new retrieval basis principle into the semantic atlas:

- `protocol_recognition_seam`

Keep the takeaway phrased in ToneSoul terms rather than generic prompt-engineering language.

---

## 3. 原始檔案：`repo_document_threads_addendum_2026-03-16.md`

## Repo Document Threads Addendum (2026-03-16)

### Why

The semantic atlas can already answer:

- which lane a remembered phrase belongs to
- which status surface should be opened first
- which neighboring lane likely matters next

But there is still one missing memory layer:

- the repository has many `docs/plans/*`, `docs/status/*`, and
  `docs/chronicles/*` files
- humans often remember those as a thread, not as isolated filenames
- later agents should be able to follow those filename threads directly

### Decision

Extend `repo_semantic_atlas_latest.*` with `document_threads`.

Each thread should:

- group filenames by a normalized semantic stem
- preserve directory category (`plans`, `status`, `chronicles`)
- expose the full relative paths inside that thread
- link the thread to nearby semantic neighborhoods
- show cross-directory siblings when a similar thread exists elsewhere

### Examples

- `chronicles/scribe_chronicle`
- `plans/repo_semantic_memory_contract`
- `status/repo_healthcheck`
- `status/true_verification_weekly_true_verification_task_status`

### Constraint

Do not attempt a full semantic embedding pass here.
This first version should stay deterministic and filename-driven.

### Success Criteria

Later agents can answer questions like:

- "Which files belong to the same document line?"
- "Where are the plan/status/chronicle variants of this idea?"
- "Which semantic neighborhood is this filename thread closest to?"

without reopening the entire docs tree by hand.

---

## 4. 原始檔案：`repo_intelligence_semantic_protocol_addendum_2026-03-16.md`

## Repo Intelligence Semantic Protocol Addendum (2026-03-16)

### Why

`repo_intelligence_latest.*` already points later agents toward:

- repo governance surfaces
- protected files
- watched directories

But after the semantic atlas landed, repo intelligence still only says
"open this file", not "follow this retrieval protocol".

### Decision

Pass a compact semantic-memory handoff through `repo_intelligence` itself.

This handoff should stay passive:

- do not rebuild aliases or document threads in repo intelligence
- only mirror the atlas' declared retrieval protocol and first neighborhood
- keep the protocol backend-agnostic so later search-oriented agents can reuse it

### Fields

Expose:

- atlas path
- retrieval protocol id
- preferred first neighborhood
- chronicle collection path
- compact status lines from the source atlas

### Success Criteria

Any later agent that opens `repo_intelligence_latest.json` can learn:

- which semantic surface to open first
- which retrieval protocol to follow
- which lane is the preferred first neighborhood

without separately reopening the full atlas artifact first.

---

## 5. 原始檔案：`repo_intelligence_settlement_mirror_addendum_2026-03-16.md`

## Repo Intelligence Settlement Mirror Addendum (2026-03-16)

### Why

`repo_intelligence_latest.*` now source-declares semantic retrieval guidance, and
that guidance already survives through:

- refreshable previews
- repo healthcheck mirrors

But settlement still lacks a dedicated `repo_intelligence` focus surface. That
creates a parity gap:

- higher-level governance can see `repo_semantic_atlas`
- but it cannot directly see the retrieval protocol that tells later agents how
  to search before opening raw files

### Decision

Add a passive `repo_intelligence_focus_preview` to settlement:

- worktree settlement selects it from refreshable handoff previews
- repo-governance settlement mirrors it from worktree settlement
- upper layers render only source-declared fields:
  - `primary_status_line`
  - `runtime_status_line`
  - `semantic_retrieval_protocol`
  - `semantic_preferred_neighborhood`
  - `artifact_policy_status_line`

### Success Criteria

If `repo_intelligence` declares semantic retrieval guidance, settlement mirrors
must preserve that guidance without recomputing different wording or silently
dropping the retrieval protocol.

---

## 6. 原始檔案：`repo_semantic_atlas_governance_mirror_addendum_2026-03-16.md`

## Repo Semantic Atlas Governance Mirror Addendum (2026-03-16)

### Why

`repo_semantic_atlas_latest.*` now defines:

- stable aliases
- semantic neighborhoods
- document threads
- a backend-agnostic retrieval protocol

But later agents will still miss it if the atlas only lives as a standalone status
artifact.

### Decision

Mirror the atlas into the existing governance chain:

- `repo_healthcheck`
- `worktree_settlement`
- `repo_governance_settlement`

This mirror stays passive:

- do not re-derive aliases or threads upstream
- only reuse the source-declared compact lines
- treat the atlas as a retrieval/governance surface, not a runtime lane

### Compact Lines

Use the existing shared grammar only:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`

No new atlas-specific top-level schema should be invented for upper layers.

### Success Criteria

Later search-oriented agents can discover the atlas from ordinary governance entry
surfaces, not only by remembering the script name or manually scanning `docs/status/`.

---

## 7. 原始檔案：`repo_semantic_memory_contract_addendum_2026-03-16.md`

## Repo Semantic Memory Contract Addendum (2026-03-16)

### Goal

The repository now has a compact semantic atlas, but it still needs one more
layer: a retrieval contract that any search-oriented AI can follow.

The contract should be:

- backend-agnostic
- grounded in biological memory principles
- informed by modern retrieval literature
- simple enough to survive handoff across different agents

### Biological Memory Principles We Borrow

1. hippocampal indexing
   - memories are not recalled by scanning the whole brain
   - compact indices route recall toward richer distributed traces
   - source: Goode et al., 2020, *An Integrated Index: Engrams, Place cells, and Hippocampal Memory*
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC7486247/

2. encoding-retrieval match
   - retrieval succeeds when cues match the structure of original encoding
   - source: Ritchey et al., 2013, *Neural Similarity Between Encoding and Retrieval is Related to Memory Via Hippocampal Interactions*
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC3827709/

3. replay strengthens weak traces
   - replay does not only repeat strong memories; it can prioritize weaker but important traces
   - source: Schapiro et al., 2018, *Human hippocampal replay during rest prioritizes weakly learned information and predicts memory performance*
   - https://pmc.ncbi.nlm.nih.gov/articles/PMC6156217/

### Retrieval Literature We Borrow

1. RAG
   - parametric memory should be complemented by explicit retrievable memory
   - https://arxiv.org/abs/2005.11401

2. REALM
   - retrieval should remain modular and interpretable
   - https://arxiv.org/abs/2002.08909

3. DPR
   - semantic retrieval often matters more than exact token overlap
   - https://arxiv.org/abs/2004.04906

4. ColBERT
   - retain detail after coarse retrieval; do not collapse too early
   - https://arxiv.org/abs/2004.12832

5. RAPTOR
   - large corpora need layered retrieval, not only flat chunk search
   - https://arxiv.org/abs/2401.18059

### Contract

Any search-oriented AI operating in this repo should follow this order:

1. alias first
   - map remembered phrases, metaphors, and titles to semantic aliases before raw grep or topology scan

2. neighborhood before file
   - identify the lane first (`wakeup`, `scribe`, `weekly`, `subjectivity`, `repo_governance`, `market`)

3. status surface before implementation source
   - if a source-declared latest artifact exists, read it before reopening raw implementation files

4. match the retrieval cue to the encoding structure
   - lane, role, and time horizon come before loose keyword matching

5. one-hop expansion before broad graph expansion
   - expand to nearest semantic neighbors first

6. preserve episodic / semantic separation
   - timestamped runs and chronicles are episodic
   - atlas / README / canonical entrypoints are semantic

7. reconsolidate after successful retrieval
   - if a fuzzy phrase repeatedly succeeds, promote it into a stable alias or memory hook

### Naming Rules

- every major lane must have one stable human-facing alias
- every lane must identify one canonical path and one latest status surface
- every alias must include a short memory hook
- every lane must declare nearby semantic neighbors

### Implementation Decision

Encode this contract directly into `repo_semantic_atlas_latest.*`, so later agents
can consume the rules as data rather than only as prose.

### Success Criteria

Later agents can answer fuzzy memory questions such as:

- "where was that first ToneSoul Chronicle?"
- "which lane owns this memory/governance artifact?"
- "what should I read first when I only remember the metaphor?"

without starting from raw file search every time.

---

## 8. 原始檔案：`semantic_protocol_handoff_parity_addendum_2026-03-16.md`

## Semantic Protocol Handoff Parity Addendum (2026-03-16)

### Why

`repo_intelligence_latest.*` now mirrors the semantic atlas' retrieval protocol,
but the shared preview chain still treats those fields as invisible metadata.

That means:

- source artifacts can declare `semantic_retrieval_protocol`
- upper mirrors can silently drop it

### Decision

Promote two optional fields into the shared compact handoff grammar:

- `semantic_retrieval_protocol`
- `semantic_preferred_neighborhood`

These fields remain optional and passive:

- only preserve source-declared values
- do not let upper layers invent or recompute semantic protocol labels

### Success Criteria

If `repo_intelligence` declares semantic retrieval guidance, the same guidance
survives through:

- refreshable previews
- repo healthcheck mirrors

without being silently dropped.

---
