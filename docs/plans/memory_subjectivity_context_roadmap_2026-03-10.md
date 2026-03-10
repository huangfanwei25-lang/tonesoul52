# Memory Subjectivity Context + Roadmap Addendum (2026-03-10)

## Why This Note Exists

The recent memory-subjectivity work now spans more than one narrow patch:

- philosophy: `event -> meaning -> tension -> vow -> identity`
- contract split: `MemoryLayer` vs `subjectivity_layer`
- implementation seam: schema-backed gateway validation

That is enough surface area that the branch now needs an explicit context note and a long-horizon plan, not just isolated phase entries.

This addendum records:

- what is already true on the branch
- what should happen next
- how that plan is constrained by `MEMORY.md`
- how current repo reality should be interpreted without weakening the public/private boundary

## Current Context Snapshot

As of `2026-03-10`, the branch has completed six linked memory-subjectivity steps:

1. `docs/plans/memory_subjectivity_layer_addendum_2026-03-09.md`
   - defined the ladder:
   - `event -> meaning -> tension -> vow -> identity`
2. `docs/plans/memory_subjectivity_contract_addendum_2026-03-10.md`
   - split storage semantics from subjectivity semantics
   - kept `MemoryLayer` as the operational axis
   - introduced `subjectivity_layer` as the semantic promotion axis
3. `tonesoul/schemas.py` + `tonesoul/memory/write_gateway.py`
   - `SubjectivityLayer`
   - `MemorySubjectivityPayload.normalize_fields()`
   - gateway rejection for invalid subjectivity payloads
   - direct `vow` / `identity` writes blocked unless a review-strength `promotion_gate` is present
4. `tonesoul/dream_engine.py` + `tonesoul/memory/consolidator.py`
   - `DreamEngine` persisted collisions now emit `subjectivity_layer = tension`
   - `sleep_consolidate()` now emits candidate `event` / `meaning` / `tension` subjectivity fields without changing storage-layer promotion
5. `docs/plans/memory_subjectivity_reviewable_promotion_addendum_2026-03-10.md`
   - reviewable `tension -> vow` metadata is now explicit
   - `review_basis` is required for review-strength `vow` writes
   - a reviewed helper lane exists without introducing automatic vow promotion
6. `docs/plans/memory_subjectivity_reporting_addendum_2026-03-10.md`
   - operator-facing reporting helpers now summarize subjectivity distribution
   - unresolved `tension` records can be listed without widening HTTP/API contracts
   - read/report surfaces now exist even though subjectivity-ranked recall does not

Current validated baseline:

- `python -m pytest tests/ -x --tb=short -q` -> `1471 passed`
- `ruff check tonesoul tests` -> passed

Current runtime meaning of this work:

- ToneSoul can now speak a subjectivity vocabulary in public code
- the gateway can validate that vocabulary
- the runtime still does **not** auto-promote its own traces into vows or identity

That last point is intentional.

## What Is Still Not Done

The branch does **not** yet do these things:

- `DreamEngine` and `sleep_consolidate()` are not yet connected to a real reviewed-promotion workflow; they only emit candidates
- `SoulDB` does not yet index `subjectivity_layer` as a first-class column
- recall/query paths do not yet filter or rank on subjectivity semantics beyond operator-side reporting
- no public runtime is allowed to self-author `identity` memory from one cycle

That incompleteness is correct. The current state is a contract seam, not a full memory rewrite.

## Long-Term Plan

The next steps should stay narrow and ordered.

### Phase A: Producer Wiring

Scope:

- teach `DreamEngine` to emit `subjectivity_layer = tension` for qualified collision records
- teach `Consolidator` to emit `event` / `meaning` / `tension` candidates without changing current storage-layer behavior

Guardrail:

- no automatic `vow` / `identity` promotion in this phase

Status:

- completed on this branch

### Phase B: Reviewable Promotion Lane

Scope:

- define how `tension -> vow` happens under explicit review
- require review metadata in `promotion_gate`
- make the review basis auditable

Guardrail:

- promotion must remain exceptional
- a single vivid runtime fragment must not become a vow by default

Status:

- contract + helper lane now exist
- automatic runtime use is still intentionally deferred

### Phase C: Retrieval + Reporting

Scope:

- add read/report surfaces that can explain subjectivity-layer distribution
- allow operators to inspect which records are only events versus unresolved tensions

Guardrail:

- do not widen external HTTP/API contracts casually

Status:

- internal read/report helpers now exist for subjectivity distribution and unresolved tension inspection
- external HTTP/API contracts remain unchanged

### Phase D: Optional Persistence Upgrade

Scope:

- only if query pressure proves it necessary, consider a dedicated `subjectivity_layer` column or index in `SoulDB`

Guardrail:

- payload-first storage remains the default until performance or query complexity justifies schema widening

### Phase E: Private-Lane Integration

Scope:

- when reviewed memories or private corpora need syncing, use the private-repo path and not this public branch

Guardrail:

- public repo stores the contract
- private repo stores the intimate corpus

## MEMORY.md Cross-Check

`MEMORY.md` is explicit:

- public repo may contain code, tests, docs, schema, and interfaces
- private repo contains:
  - `memory/self_journal.jsonl`
  - `memory/soul.db`
  - `memory/vectors/`
  - Dream Engine generated constructive memory

That means the subjectivity plan is allowed to do these things publicly:

- define `subjectivity_layer`
- define promotion rules
- define gateway validation rules
- define migration strategy
- add tests proving the contract

And it must **not** do these things publicly:

- commit raw private memory corpora
- commit `soul.db`
- treat private runtime traces as public design artifacts
- let public contract work become an excuse to stage `.jsonl` / `.db` memory data

## Repo-Reality Cross-Check

The repo already carries historical memory-governance debt that should not be mistaken for a new policy.

`docs/status/private_memory_review_latest.md` currently places:

- `memory/crystals.jsonl` under the `Mirror Then Archive` lane with item type `mirrored_private_memory`

That matters for planning:

- `memory/crystals.jsonl` should be treated as private evidence with mirrored learnings, not as precedent for committing more memory data into the public branch
- future subjectivity work should extract public-safe rules, schemas, and summaries from memory artifacts, then leave the underlying corpus to the private lane

This note therefore treats the current local `memory/crystals.jsonl` dirtiness as settlement debt, not as an implementation input that should be normalized into public workflow.

## Practical Rule For Future Phases

When a future phase touches memory subjectivity, ask two questions separately:

1. Is this a public contract change?
2. Is this private memory evidence?

If the answer to the second question is yes, the data should not ride along with the code change.

## Architectural Conclusion

The branch now has enough context to move forward without re-litigating the same foundations each time:

- subjectivity is a semantic ladder
- storage and subjectivity are separate axes
- gateway validation exists
- promotion must get stricter as memory becomes more self-defining
- `MEMORY.md` still forbids treating private corpora as public payload

That is the stable context the next implementation phases should inherit.
