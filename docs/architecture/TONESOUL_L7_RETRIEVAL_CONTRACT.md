# ToneSoul L7 Retrieval Contract

> Status: engineering contract as of 2026-03-22
> Scope: L7 `compiled retrieval + verifier surfaces`
> Audience: AI agents, maintainers, and architecture reviews

## Why This Contract Exists

ToneSoul repeatedly degraded when agents were forced to:

- reread too many long markdown files
- infer authority from directory names alone
- guess whether to trust prose, status artifacts, code, or tests
- solve multi-hop joins in-context instead of through artifacts

L7 exists to reduce those failures.

This contract defines:

- which retrieval surface to open first
- which surface has authority for which kind of question
- when to stop reading and run a verifier instead

Machine-readable mirror:

- `docs/status/l7_retrieval_contract_latest.json`
- `docs/status/l7_retrieval_contract_latest.md`
- `docs/status/l7_operational_packet_latest.json`
- `docs/status/l7_operational_packet_latest.md`

## Core Rule

Do not start from raw prose if a compiled artifact or verifier already exists.

Prefer this order:

1. architecture anchor
2. status artifact
3. knowledge graph or boundary map
4. raw docs
5. implementation code
6. verifier or test execution

## Retrieval Surface Types

| Surface | What It Is For | Typical Examples |
| --- | --- | --- |
| `architecture anchor` | system-level meaning, north-star direction, layer boundaries | `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`, `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md` |
| `boundary map` | authority separation between similar-looking surfaces | `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`, this contract |
| `status artifact` | latest generated snapshot, health, graph, changed-surface output | `docs/status/tonesoul_knowledge_graph_latest.md`, `docs/status/changed_surface_checks_latest.md`, `docs/status/repo_healthcheck_latest.json` |
| `research note` | external inspiration, benchmark comparison, non-canonical evidence | `docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md` |
| `raw docs` | detailed prose, historical rationale, long-form specification | `docs/*.md`, `spec/*.md`, root-level conceptual docs |
| `implementation source` | actual runtime behavior | `tonesoul/*`, `apps/*`, `scripts/*` |
| `verifier` | executable truth check when prose may drift | `scripts/verify_docs_consistency.py`, `scripts/verify_protected_paths.py`, `scripts/run_changed_surface_checks.py` |

## Authority Order By Question Type

| Question Type | Open First | Open Second | Escalate To |
| --- | --- | --- | --- |
| "What is ToneSoul architecturally?" | architecture anchor | eight-layer map | implementation source |
| "Which knowledge-like directory should I trust?" | knowledge surfaces boundary map | docs index | code / scripts only if still ambiguous |
| "What changed recently?" | status artifacts | `task.md` | changed-surface checks |
| "Which files are protected or off-limits?" | protected-path verifier | AGENTS rules already in force | fail closed |
| "Which validations should run for this change?" | changed-surface checks | docs consistency | direct test commands |
| "What is the latest repo health state?" | machine-readable status JSON | status README | rerun verifier |
| "How should external research influence design?" | research evidence map | architecture anchor | human review |
| "What does the runtime actually do?" | source code | targeted tests | full regression |

## Default Retrieval Sequence

When the task is not yet clear:

1. open `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. open `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
3. open the relevant boundary map or status artifact
4. only then branch into detailed docs or code

When the task is code-change oriented:

1. run `scripts/run_changed_surface_checks.py`
2. inspect the planned checks
3. open only the files on the affected surface
4. run the mapped verifier or tests

When the task is repository-understanding oriented:

1. open `docs/status/tonesoul_knowledge_graph_latest.md`
2. open the relevant anchor or boundary map
3. avoid bulk-reading unrelated markdown

## When To Stop Reading And Run A Verifier

Stop reading prose and execute a verifier when:

- protected paths are involved
- latest status matters more than conceptual intent
- the question is about "what is true right now"
- there is known doc drift risk
- a claim can be checked mechanically

Examples:

- use `python scripts/verify_protected_paths.py --repo-root . --strict`
- use `python scripts/verify_docs_consistency.py --repo-root .`
- use `python scripts/run_changed_surface_checks.py --repo-root .`

## Forbidden Retrieval Habits

Do not:

- treat all markdown as equal authority
- collapse `knowledge/`, `knowledge_base/`, and `PARADOXES/` into one memory source
- assume a long document is newer than a generated status artifact
- use research notes as canonical architecture truth
- infer runtime behavior from prose when tests or code are available

## Engineering Implications

L7 should keep moving prose into smaller executable surfaces:

- `policy cards`
- `authority maps`
- `verification checklists`
- `status artifacts`
- `knowledge graph edges`

The goal is not to eliminate documents.
It is to stop forcing the model to reconstruct system truth from long-form prose every time.

## Relationship To Other Documents

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - explains why ToneSoul externalizes cognition at all
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - locates L7 inside the eight-layer architecture
- `docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md`
  - explains which external theories support this contract
- `docs/status/l7_retrieval_contract_latest.json`
  - machine-readable retrieval order, question routes, and verifier checklist
- `docs/status/l7_operational_packet_latest.json`
  - short route packet that turns this contract into one immediately usable retrieval handoff

## Canonical Instruction For Future Agents

If retrieval path is ambiguous, remember this sentence:

> Open the smallest authoritative artifact first, and switch from prose to executable verification as soon as the question becomes mechanically checkable.
