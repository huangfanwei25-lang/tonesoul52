# ToneSoul Observable-Shell Opacity Contract

> Status: architectural boundary contract
> Purpose: define what ToneSoul may claim as observable, partially observable, or opaque when describing runtime reasoning and auditability
> Last Updated: 2026-03-28
> Depends On:
>   - docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md
>   - docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md
>   - docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md
> Scope: observable-shell honesty for traces, packets, council outputs, and later-agent explanations

## How To Use This Document

If you are about to say that ToneSoul "saw", "audited", "verified", or "understood" some internal reasoning path:

1. identify the surface you actually have,
2. classify it as `observable`, `partially_observable`, or `opaque`,
3. keep your claim at that level,
4. do not promote shell evidence into hidden-mechanism certainty.

## Why This Exists

ToneSoul already has strong observable shells:

- `dispatch_trace`
- `SessionTrace`
- `r_memory_packet`
- contract-observer outputs
- council verdicts
- compactions, checkpoints, and subject snapshots

But these are not the same as direct access to model-internal reasoning.

Without an explicit opacity contract, later agents drift into two bad habits:

1. **overclaiming auditability**: treating clean traces as proof that hidden reasoning was fully inspected,
2. **false black-box despair**: acting as if nothing is observable just because hidden model internals remain opaque.

ToneSoul needs the middle posture:

`audit the shell honestly, name the opacity honestly, and do not smuggle one into the other.`

## Compressed Thesis

ToneSoul is an externalized cognitive architecture, not an internal-thought extractor.

It may strongly audit:

- what entered the system,
- what gates fired,
- what traces were written,
- what posture was emitted,
- what later agents can inherit.

It may not pretend to directly inspect raw latent cognition that was never externalized.

## Opacity Levels

| Level | Name | Meaning | Safe Claim |
|------|------|---------|-----------|
| `observable` | observable shell | the mechanism and emitted evidence are directly inspectable | "this path is auditable at the shell level" |
| `partially_observable` | bounded opacity | outputs and some intermediates are visible, but not the entire internal selection process | "this path is partially observable; hidden selection remains" |
| `opaque` | opaque internal | no direct evidence of the internal route exists beyond final behavior | "this internal path is not directly auditable" |

## Surface Classification

| Surface | Opacity Level | Why |
|--------|---------------|-----|
| `SessionTrace` | `observable` | append-only, Aegis-protected runtime shell record |
| `dispatch_trace` | `observable` | emitted runtime observability payload |
| `r_memory_packet` | `observable` | compact shared hot-state shell for later agents |
| `claim / checkpoint / compaction / perspective` | `observable` | explicit shared coordination surfaces |
| `subject_snapshot` | `observable` | durable non-canonical identity shell, explicitly written |
| `ContractObserver` results | `observable` | contract verdicts and violations are emitted directly |
| `Benevolence` / `Aegis` verdicts | `observable` | block/flag behavior is externally inspectable |
| council final verdict | `partially_observable` | verdict and some transcript evidence exist, but aggregation remains simplified/opaque |
| POAV low-risk baseline record | `partially_observable` | score and posture are visible, but not every latent contributing path |
| router heuristic selection | `partially_observable` | route outputs and telemetry are visible, but heuristic tradeoffs are compressed |
| computed `risk_posture` | `partially_observable` | derived from visible signals, but summarization compresses upstream details |
| raw model chain-of-thought | `opaque` | not a canonical ToneSoul surface |
| hidden token-level selection inside model inference | `opaque` | not directly exposed by current runtime |
| inferred "true motive" of an agent from prose alone | `opaque` | interpretation, not observable evidence |

## Hard Rules

### Rule 1: Shell Evidence Is Real

If a trace, gate, or packet field is emitted by runtime, later agents may rely on it as shell evidence.

Do not downgrade real observability into mysticism.

### Rule 2: Shell Evidence Is Not Total Access

A clean shell does not prove that hidden reasoning was fully inspected.

Do not upgrade observability into omniscience.

### Rule 3: Opaque Internals Must Be Named As Opaque

If the system lacks a direct emitted surface for a reasoning step, say so plainly.

Preferred language:

- "not directly observable"
- "shell evidence exists, but hidden selection remains opaque"
- "runtime behavior is auditable; latent route is not"

### Rule 4: Interpretation Must Not Fill Missing Mechanism

Narrative coherence, elegant philosophy, or a plausible explanation does not count as observability.

This is an A/B/C firewall rule:

- A = what mechanism exists
- B = what behavior/evidence is emitted
- C = how humans interpret it

Do not let C repair missing A or B.

## Safe And Unsafe Claims

| Claim Type | Safe? | Example |
|-----------|-------|---------|
| shell-auditable | Yes | "The output path is shell-auditable because dispatch trace, gate verdicts, and SessionTrace exist." |
| bounded-opacity | Yes | "The council verdict is partially observable: transcript evidence exists, but final aggregation is still compressed." |
| opaque-internal honesty | Yes | "The model's latent selection path is not directly observable from current runtime surfaces." |
| hidden-thought certainty | No | "We know exactly why the model chose this token path." |
| trace-as-total-proof | No | "Because the logs are clean, the reasoning was fully audited." |
| interpretation-as-mechanism | No | "The semantic field explains the actual hidden route." |

## If This Becomes Runtime Later

If ToneSoul later adds an explicit opacity marker to trace or packet surfaces, prefer names already native to the repository:

- `observability_posture`
- `opacity_level`
- `observable_shell_status`

Avoid importing foreign naming as canonical runtime terms unless they are translated into the existing A/B/C and observable-shell language first.

## Current Adoption Decision

This contract is adopted now as a writing, review, and claim-governance boundary.

It does **not** yet require:

- a new runtime gate,
- a new packet field,
- a new trace schema,
- a risk multiplier.

Those would be later feature-track questions.

## Practical Reading Rule

When in doubt:

1. open the trace or packet,
2. name what is actually visible,
3. name what remains opaque,
4. stop there.

That is ToneSoul's version of epistemic honesty.
