# ToneSoul Operator-Retrieval Query Contract

> Purpose: define how future operator-facing compiled-knowledge queries may work without letting retrieval answers masquerade as hot coordination state, canonical governance truth, or durable identity.
> Status: accepted architecture contract. Query runtime may come later.
> Authority: architecture contract for future operator retrieval. This file constrains scope, return shape, and non-promotion rules. It does not itself create a live retrieval runner.

---

## Why This Exists

ToneSoul now has:

- a knowledge-layer boundary
- a compiled-knowledge landing-zone spec
- dashboard retrieval preview cues
- a stronger split between:
  - hot coordination
  - compiled knowledge
  - exploratory residue
  - public teaching

That means the next missing piece is no longer "where should retrieval live?"

It is:

`if an operator queries compiled knowledge, how do we keep that answer useful without letting it impersonate live runtime truth?`

This line exists because retrieval is useful now, but still dangerous if its authority posture stays implicit.

---

## Compressed Thesis

Operator retrieval should be:

- auxiliary
- provenance-first
- collection-bounded
- non-promoting by default

It should help the operator think.
It should not silently rewrite the current runtime story.

---

## What This Is

This contract defines a future operator-facing query surface for:

- compiled research distillations
- compiled architecture aids
- future compiled collections and indexes

It tells ToneSoul:

- what may be queried
- what may be returned
- how results must be labeled
- how retrieval must relate to session-start, observer-window, and packet/operator truth

---

## What This Is Not

This is **not**:

- a replacement for `session-start`
- a replacement for `observer-window`
- a replacement for `r_memory_packet`
- a canonical-governance source
- a durable-identity source
- a free-form "search everything and trust the answer" lane

If a retrieval answer starts reading like runtime law, this contract has already been violated.

---

## Query Scope

Future operator retrieval may query only bounded compiled sources such as:

1. `compiled knowledge`
   - future `knowledge/compiled/collections/*`
   - future `knowledge/compiled/artifacts/*`
   - future `knowledge/compiled/indexes/*`

2. `compiled architecture and research aids`
   - `docs/research/*`
   - bounded architecture contracts that are already in the authority map

3. `operator-safe summaries`
   - future derived indexes or health-checked summaries

It must **not** query as first-class truth:

- raw `external_research/`
- parked external clones
- exploratory residue in `docs/plans/*design*`
- hot coordination state as if it were archival knowledge

---

## Query Classes

The contract supports only these bounded query classes:

### 1. `lookup`

Find a known concept, paper distillation, or contract section.

### 2. `compare`

Compare two or more compiled sources on one bounded question.

### 3. `summarize`

Produce a short operator-facing summary from already-compiled sources.

### 4. `trace_lineage`

Show where a concept or rule came from across compiled sources.

### 5. `health_check`

Check whether a compiled collection is present, indexed, version-aligned, or stale.

The contract does **not** authorize:

- open-ended world modeling
- identity inference
- hidden-state interpretation
- source promotion by rhetorical force

---

## Required Query Inputs

Every bounded operator-retrieval query should carry:

- `query_text`
- `query_class`
- `collection_scope`
- `consumer_surface`
- `tier_context`
- `max_results`

Optional but useful:

- `lineage_hint`
- `prefer_authority_contracts`
- `prefer_research_distillations`

If `collection_scope` is absent, the future runner should fail safe or default to a tightly bounded operator-safe scope.

---

## Return Shape

The result shape must be provenance-first.

Each result item should expose at least:

- `title`
- `path`
- `source_class`
- `authority_posture`
- `compiled_status`
- `why_returned`
- `promotion_rule`
- `summary`

Recommended extras:

- `lineage_reference`
- `health_posture`
- `version_reference`
- `staleness_note`

This keeps retrieval from becoming "confident paragraph first, source second."

---

## Allowed Authority Postures

Operator retrieval results must explicitly declare one of:

- `compiled_reference`
- `compiled_boundary_aid`
- `compiled_research_note`
- `compiled_status_aid`
- `exploratory_only`

It must **not** emit:

- `canonical_truth`
- `runtime_truth`
- `identity_truth`

unless the result is only quoting a stronger surface and labels that stronger surface explicitly.

---

## Non-Promotion Rule

The default rule is:

`retrieval answers may inform, but may not silently promote.`

That means a retrieval answer may:

- help orient an operator
- point to relevant contracts
- summarize compiled notes
- show lineage

But it may not, by itself:

- override session-start
- override observer-window
- override closeout grammar
- override packet/operator guidance
- refresh subject identity
- change vows or governance truth

If promotion is needed, the operator must follow a stronger lane.

---

## Runtime Fallback Rule

When retrieval results conflict with live runtime surfaces:

1. `session-start`
2. `observer-window`
3. `r_memory_packet` / operator guidance
4. closeout and preflight surfaces

take priority over compiled retrieval.

The retrieval result should then be marked:

- `conflicts_with_live_runtime = true`
- `promotion_rule = do_not_promote`

This keeps compiled knowledge from quietly outranking current operational truth.

---

## Canonical Fallback Rule

When the question is about governance or architecture truth, retrieval should prefer:

1. canonical architecture contracts
2. accepted boundary/spec contracts
3. compiled research distillations
4. exploratory residue never as default authority

If a lower-authority compiled note is returned, the result must say so.

---

## Identity Boundary

Operator retrieval must never answer identity-flavored questions by mining compiled notes and calling the result "who ToneSoul is."

It may support:

- design rationale
- boundary explanation
- lineage of a concept

It must not support:

- durable identity synthesis
- hidden personality claims
- vow inference
- subject-refresh by retrieval

Retrieval is for operator knowledge, not selfhood construction.

---

## Relationship To Workspace Tiers

### Tier 0

No retrieval answers should be required here.

Tier 0 is for:

- instant gate
- current short board
- immediate safety/orientation

### Tier 1

Retrieval may appear only as:

- bounded preview
- optional lineage cue
- operator-safe auxiliary context

### Tier 2

Retrieval may be pulled more deeply here, but still as:

- auxiliary reference
- not a competing control plane

This keeps retrieval aligned with the tier model rather than becoming a fourth hidden dashboard tier.

---

## Collection Hygiene Rule

Future retrieval should not query arbitrary compiled material unless the collection has:

- declared scope
- known source class
- known lineage
- basic health posture

If collection hygiene is absent, the safest answer is:

- `collection_not_ready`
- `compiled_status = unavailable_or_unhealthy`

instead of pretending retrieval is already mature.

---

## Consumer-Parity Rule

The same operator-retrieval contract should apply across:

- Codex-style shells
- Claude-compatible adapters
- dashboard/operator shells

Different consumers may render results differently.
They may not invent different authority stories.

---

## First Safe Use Cases

The first justified operator-retrieval uses are:

1. find the right contract or research distillation fast
2. compare two compiled notes without re-reading long prose
3. show lineage for a concept before a change is proposed
4. surface collection/index health to the operator

The wrong first uses are:

1. identity inference
2. runtime override
3. prediction inflation
4. experimental-note promotion

---

## One-Sentence Summary

`ToneSoul operator retrieval should return compiled, provenance-first guidance that helps an operator think, while remaining explicitly weaker than live runtime truth and canonical governance surfaces.`
