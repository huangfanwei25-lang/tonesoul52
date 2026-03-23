# ToneSoul L8 Distillation Boundary Contract

> Status: engineering contract as of 2026-03-22
> Scope: L8 `model attachment + distillation boundary`
> Audience: AI agents, maintainers, and architecture reviews

## Why This Contract Exists

Once ToneSoul behavior becomes explicit, there is strong pressure to:

- train it into adapters
- export traces into RL loops
- compress governance style into model-attached behavior

That can be useful, but it is also where public and private boundaries are easiest to destroy.

This contract defines:

- what may be distilled
- what must stay external
- what gates must be passed before any adapter or RL-facing export is allowed

Machine-readable mirror:

- `docs/status/l8_distillation_boundary_latest.json`
- `docs/status/l8_distillation_boundary_latest.md`
- `docs/status/l8_adapter_dataset_gate_latest.json`
- `docs/status/l8_adapter_dataset_gate_latest.md`

## Core Rule

ToneSoul may distill stable public-safe behavior.

ToneSoul must not distill raw private memory, deletion-sensitive records, or governance-critical secrets into irreversible model weights.

## Distillation Surface Classes

| Class | Allowed? | Examples |
| --- | --- | --- |
| `public-safe behavior traces` | yes, after review | verifier-approved routing patterns, public governance posture, non-sensitive language style |
| `public philosophical priors` | yes, after review | published axiomatic stance, public semantic-governance posture |
| `tool-routing habits` | yes, after review | stable use of verifier-before-claim, retrieval-before-long-prompt patterns |
| `private vault memory` | no | personal memory, user-identifying history, private recall payloads |
| `record-level deletable data` | no | any datum that must remain individually erasable or auditable |
| `secret thresholds and red-team payloads` | no | internal guard thresholds, attack dictionaries, private jailbreak corpora |
| `raw conversation archives` | no by default | full journals, handoff logs, unredacted transcripts |

## Allowed Distillation Inputs

Inputs may be considered only if they are:

- public or explicitly release-safe
- stable across sessions and not tied to one person's private history
- provenance-linked to the repo or an approved public artifact
- already filtered through verifier or human review
- safe to retain even if later impossible to delete from weights

Good candidates:

- stable refusal posture patterns
- evidence-first answer structure
- verifier-first completion habits
- public-facing tone or rhetoric style
- public-safe summaries of governance outcomes

## Forbidden Distillation Inputs

Never distill:

- private memory vault contents
- raw personal journals
- identifiable user facts
- deletion-sensitive records
- private red-team payload collections
- internal security bypass probes
- unpublished threshold formulas that protect the system
- anything whose provenance cannot be reconstructed

## Export Gates

Before any trace enters adapter or RL preparation, it must pass all of these gates:

1. `public-safe review`
   - confirm the material is safe for irreversible retention
2. `provenance review`
   - confirm source path, generation path, and transformation chain
3. `privacy review`
   - confirm no personal or vault-level detail remains
4. `governance review`
   - confirm the trace represents a stable desired behavior, not a one-off patch
5. `evaluation plan`
   - define how the adapter or RL change will be measured and reversed

If any gate is unclear, the material stays external.

## Minimal Adapter Dataset Contract

If a future adapter dataset is created, every row should be able to answer:

- what public-safe source produced this row
- what transformation produced the final training example
- which verifier or reviewer approved it
- what capability it is meant to strengthen
- how it can be evaluated without relying on private data

If those fields cannot be stated, the row is not ready.

Schema anchor:

- `spec/governance/adapter_dataset_record_v1.schema.json`
- `spec/governance/adapter_dataset_record_v1.example.json`

## Cross-Repo Boundary

| Repository | Role | Distillation Posture |
| --- | --- | --- |
| `tonesoul52` | public engine and contracts | source of public-safe behavior patterns and explicit governance abstractions |
| `ToneSoul-Memory-Vault` | private sensitive memory repository | never a direct training dump; remains external and auditable |
| `OpenClaw-Memory` | public memory substrate experiment | safe place for memory-engineering patterns, not for private memory export |
| `OpenClaw-RL` | experiment rail for agentic RL | may consume approved public-safe traces, but must not become a bypass around this contract |

## What L8 Is For

L8 exists to create a controlled seam between software architecture and model adaptation.

It is for:

- adapters such as LoRA
- narrowly scoped RL experiments
- retrieval-native or memory-native attachment research
- public-safe behavioral compression

It is not for:

- shoving the whole system into weights
- hiding governance behind training
- collapsing the public/private repository boundary

## Relationship To Human-Authored Governance

ToneSoul's governance rules are human-authored.

That remains true even if some behaviors are later attached to a model.
Any adapter or RL export must preserve this boundary:

- human-authored governance remains the normative source
- model-attached behavior is an optimization layer, not the new constitution

## Evaluation Expectations

Any L8 experiment should be evaluated on:

- governance consistency
- verifier pass rate
- regression risk against public benchmarks
- auditability of training sources
- reversibility if the experiment causes drift

If the change improves fluency but reduces auditability, it fails the contract.

## Relationship To Other Documents

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - explains why only selective internalization is acceptable
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - locates L8 inside the overall architecture
- `docs/research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md`
  - explains which external theories support adapters, RL, and memory boundaries
- `spec/governance/adapter_dataset_record_v1.schema.json`
  - defines the minimum public-safe adapter dataset row shape
- `docs/status/l8_distillation_boundary_latest.json`
  - machine-readable export gates, forbidden surfaces, and evaluation dimensions
- `docs/status/l8_adapter_dataset_gate_latest.json`
  - first executable gate report for adapter-row review against this boundary

## Canonical Instruction For Future Agents

If model attachment feels tempting, remember this sentence:

> Distill only stable public-safe behavior, never the private history or secret guardrails that must remain inspectable, deletable, and externally governed.
