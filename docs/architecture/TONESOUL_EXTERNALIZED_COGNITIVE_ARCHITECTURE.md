# ToneSoul Externalized Cognitive Architecture

> Status: Canonical architecture anchor as of 2026-03-22
> Audience: future AI agents, maintainers, and architecture reviews
> Purpose: define ToneSoul as an externalized cognitive operating system where governance, memory, verification, and distillation stay outside model weights.
> Last Updated: 2026-03-23

## Core Thesis

ToneSoul should not be treated as "a bigger prompt system."

ToneSoul is an externalized cognitive operating system:

- model-internal capabilities are kept small, replaceable, and auditable
- memory, governance, council, retrieval, and verification stay explicit
- markdown philosophy is compiled into machine-usable artifacts before runtime
- only stable, public, low-risk behavior should ever be distilled into adapters or weights

The engineering goal is to move hidden reasoning dependencies out of the model's opaque internals and into versioned, inspectable system modules.

Companion map:

- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - use this when you need the layer-by-layer bridge from the older six-layer runtime model to the newer retrieval and model-attachment path
- `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
  - use this when you need the operational rule for which retrieval surface to open first
- `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
  - use this when you need the operational rule for what may and may not be distilled into adapters or RL traces
- `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`
  - use this when you need the cross-cutting rule for separating mechanism, observability, and interpretation
- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`
  - use this when you need the narrower rule for what ToneSoul may honestly call observable versus opaque in runtime reasoning paths
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`
  - use this when you need to challenge or defend an axiom claim without rewriting `AXIOMS.json`
- `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
  - use this when you need the evidence-backed boundary between parallel perspective lanes, experimental field synthesis, and serialized canonical commit
- `docs/status/l7_retrieval_contract_latest.json`
  - machine-readable L7 retrieval order and verifier checklist
- `docs/status/l8_distillation_boundary_latest.json`
  - machine-readable L8 export gates and dataset boundary summary
- `docs/status/l7_operational_packet_latest.json`
  - short operational retrieval packet for later agents
- `docs/status/l8_adapter_dataset_gate_latest.json`
  - first executable L8 gate for adapter-row review
- `docs/status/abc_firewall_latest.json`
  - machine-readable posture for claim-governance and observable-shell honesty

## The Four-Layer Roadmap

### 1. External Soul

This is the current ToneSoul foundation.

- `tonesoul/memory/`: memory persistence, decay, crystallization, topology
- `tonesoul/governance/`: policy, adjudication, and safety boundaries
- `tonesoul/council/`: multi-perspective deliberation
- `tonesoul/unified_pipeline.py`: runtime assembly
- `docs/`, `spec/`, `tests/`: explicit philosophy, contracts, and verification

At this layer, behavior is mostly implemented outside the model.

### 2. Model-Readable Soul

Raw markdown is not enough. Long prose forces the model to perform too many implicit joins.

Important documents must be compiled into smaller, more reliable artifacts:

- `policy cards`: short runtime rules
- `knowledge graph artifacts`: lanes, authorities, dependencies, canonical paths
- `verification checklists`: tests, hooks, protected paths, success criteria
- `status surfaces`: compact latest-state artifacts that later agents can open first

The system should prefer compiled artifacts over repeated full-repo rereads.

### 3. Model-Attachable Soul

Once ToneSoul behavior becomes explicit and stable, some of it can be attached to models instead of only being prompted.

Examples:

- `Guardian adapter`: safety and refusal posture
- `Analyst adapter`: evidence-first reasoning posture
- `Tone adapter`: stable language style or communication posture
- routing preferences distilled from runtime traces
- verifier-guided behavior fine-tuning

This layer maps to adapters such as LoRA and other parameter-efficient tuning methods.

### 4. Model-Internalized Soul

Only the safest and most stable parts of ToneSoul should move into model weights.

Potentially distillable:

- public philosophical priors
- stable governance tendencies
- general reasoning style
- durable tool-routing habits
- non-sensitive domain skills

Must remain external:

- raw personal memory
- private vault content
- secret thresholds and red-team payloads
- attack dictionaries
- irreversible user history
- any data that must be deletable or auditable at the record level

ToneSoul should internalize principles, not private history.

## Public / Private Boundary

This architecture depends on strict separation between:

- public engine behavior
- private memory and sensitive data
- experimental adaptation logic

Rule:

- public repo stores the engine, contracts, and safe abstractions
- private vault stores personal memory, sensitive traces, and irreversible detail
- adapters may be trained from public-safe summaries, never from raw private memory dumps

## Engineering Implications

### A. Replace prose-only rules with enforceable controls

Do not rely on instructions like "please don't touch `.env`."

Instead use:

- pre-tool guards
- protected-path verifiers
- post-edit formatters
- stop verifiers
- changed-surface checks

The system should fail closed when boundaries are crossed.

### B. Reduce implicit joins

Models degrade when they must combine too many boolean conditions, distant document references, or multi-hop relationships at inference time.

Therefore:

- keep prompts short
- move structure into artifacts
- make authority order explicit
- encode dependencies in graphs, not only prose

### C. Retrieval before long prompting

Future agents should open:

1. one architecture anchor
2. one latest status surface
3. one compiled graph artifact
4. only then the full implementation sources

### D. Runtime traces become training material

The long-term value of ToneSoul is not only output quality.

It is the accumulated trace of:

- which verifier blocked what
- which council perspective corrected what
- which memory surface mattered
- which route succeeded

Those traces are the bridge from software architecture to adapter training and RL.

## What ToneSoul Is Becoming

ToneSoul is evolving toward:

- a graph-backed memory runtime
- an auditable verifier-first agent stack
- an adapter-ready governance layer
- a future retrieval-native / memory-native model interface

The system is best understood as a cognitive backplane, not a single monolithic model persona.

## Immediate Build Priorities

1. Preserve the external modules as the source of truth.
2. Compile markdown into structured runtime artifacts.
3. Expand hooks and verifiers so guardrails execute at the system layer.
4. Use knowledge-graph and status artifacts as the first retrieval surface.
5. Distill only stable and safe behavior into adapters.
6. Keep private memory external and deletable.

## Canonical Instruction For Future Agents

When architecture direction is ambiguous, prefer this interpretation:

> Build ToneSoul as an externalized cognitive operating system whose modules can later be compiled, attached, and selectively distilled into models, while keeping private memory and governance-critical control points outside irreversible model weights.

That sentence is the architecture north star.
