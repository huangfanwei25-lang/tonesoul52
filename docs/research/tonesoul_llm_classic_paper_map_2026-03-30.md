# ToneSoul LLM Classic Paper Map (2026-03-30)

> Purpose: keep only the classic LLM papers that materially help ToneSoul's current architecture, governance, continuity, retrieval, adapter, and council design.
> Scope: not a comprehensive history of LLMs. This is a selective map for ToneSoul use.
> Status: current research companion
> Authority: research map and design aid. Useful for technical lineage and reading order, but does not outrank runtime code, tests, or canonical architecture contracts.

---

## Why This Exists

There are many "classic LLM paper" lists.
Most are useful for orientation.
Very few answer the question ToneSoul actually needs answered:

`which papers still matter for this repo's real design decisions?`

ToneSoul does not need a museum wall.
It needs a working map for:
- why the stack separates governance from fluency
- why continuity is externalized instead of mythologized
- why adapters/distillation stay bounded
- why retrieval and memory are treated as separate but adjacent problems
- why council and verifier-first posture exist

This note keeps only the papers that still inform those questions.

## Compressed Thesis

For ToneSoul, the most useful classic-paper families are:

1. base model architecture
2. long-context and memory pressure
3. retrieval as a separate mechanism
4. responsible model reporting and governance
5. parameter-efficient adaptation
6. bounded reasoning / deliberation patterns

Everything else is optional until it changes a real architectural decision.

## Reading Order For ToneSoul

If a later agent wants the shortest useful reading ladder, use this order:

1. `Attention Is All You Need` (2017)
2. `Improving Language Understanding by Generative Pre-Training` (2018)
3. `BERT` (2018)
4. `Transformer-XL` (2019)
5. `Model Cards for Model Reporting` (2019)
6. `Adapter Modules for Transfer Learning` (2019)
7. `Retrieval-Augmented Generation` (2020)
8. `LoRA` (2021)
9. `Constitutional AI` (2022)
10. `ReAct` (2022)

That sequence is enough to understand most of ToneSoul's current architectural instincts.

## A. Base Architecture And Representation

### 1. Attention Is All You Need (Vaswani et al., 2017)

Why ToneSoul cares:
- this is the architectural root of the model family ToneSoul is actually steering
- it explains why "context" is expensive, positional, and structurally fragile
- it is the upstream reason continuity cannot simply be assumed to live inside one prompt window

What ToneSoul should retain:
- transformer intelligence is sequence-structured and attention-bounded
- long context is not free
- later continuity layers exist partly because base attention has limits

What ToneSoul should not over-read:
- this paper does not justify agency claims
- it does not solve memory, governance, or deliberation by itself

### 2. Improving Language Understanding by Generative Pre-Training (Radford et al., 2018)

Why ToneSoul cares:
- establishes the pretrain-then-adapt pattern that later motivates adapter and distillation lanes
- useful for understanding why a base model can be broad, fluent, and still underdetermined

### 3. BERT (Devlin et al., 2018)

Why ToneSoul cares:
- demonstrates that representation quality and downstream task behavior depend heavily on training objective
- helps explain why "one model behavior" is not one simple thing

ToneSoul implication:
- different surfaces can expose different strengths even when they share base architecture lineage

## B. Long Context, Memory, And State Pressure

### 4. Transformer-XL (Dai et al., 2019)

Why ToneSoul cares:
- early classic evidence that context windows alone are not enough
- introduces recurrence-style handling for longer dependencies

ToneSoul implication:
- continuity pressure is not a new problem
- packet / compaction / snapshot / working-style surfaces exist because long-horizon state needs explicit handling

### 5. RETRO / retrieval-enhanced transformer line (DeepMind, 2021-2022)

Why ToneSoul cares:
- sharpens the distinction between base model weights and external retrieval support
- supports ToneSoul's insistence that retrieval is not identical to memory, and neither is identical to identity

ToneSoul implication:
- externalized cognition is not a hacky afterthought; it is a legitimate architectural direction

### 6. Long-context / memory benchmark line

Useful names:
- `Lost in the Middle` (Liu et al., 2023)
- `LoCoMo` (2024)
- `LongMemEval` (2024)

Why ToneSoul cares:
- they show that long context, multi-session continuity, and retrieval quality must be measured instead of assumed
- they support ToneSoul's preference for bounded continuity surfaces plus evidence-backed validation

## C. Retrieval As Separate From Memory

### 7. Retrieval-Augmented Generation (Lewis et al., 2020)

Why ToneSoul cares:
- gives the cleanest classic framing for retrieval as a distinct mechanism
- helps prevent a common collapse:
  - "the model knows"
  - "the system retrieved"
  - "the system remembers"

ToneSoul implication:
- L7 retrieval and continuity surfaces should stay explicit and inspectable
- retrieval success does not equal durable memory

### 8. REALM / retrieval-pretraining line (Guu et al., 2020)

Why ToneSoul cares:
- reinforces the same separation:
  - parametric knowledge
  - retrieved knowledge
  - runtime assembly

ToneSoul implication:
- useful background for keeping evidence posture and retrieval posture separate

## D. Governance, Reporting, And Honesty

### 9. Model Cards for Model Reporting (Mitchell et al., 2019)

Why ToneSoul cares:
- this is one of the cleanest early precedents for saying:
  - description
  - limitations
  - intended use
  - evidence
must be explicit

ToneSoul implication:
- evidence ladders, launch honesty gates, and reality-baseline docs are not random bureaucracy
- they belong to the same broad family of responsibility surfaces

### 10. Constitutional AI (Bai et al., 2022)

Why ToneSoul cares:
- not because ToneSoul copies CAI directly
- because it legitimizes the idea that model behavior may be shaped by explicit normative scaffolding rather than hidden prompt superstition

ToneSoul implication:
- governance and control-plane contracts are a reasonable design direction
- but ToneSoul still adds stronger distinctions between:
  - canonical truth
  - descriptive readout
  - advisory continuity

## E. Parameter-Efficient Adaptation

### 11. Adapter Modules for Transfer Learning (Houlsby et al., 2019)

Why ToneSoul cares:
- classic justification for adaptation without rewriting the full base model
- directly relevant to ToneSoul's L8 distillation and model-attachment lanes

ToneSoul implication:
- bounded adaptation is technically serious, not just an engineering workaround

### 12. LoRA (Hu et al., 2021)

Why ToneSoul cares:
- LoRA is the most practical bridge between ToneSoul's conceptual distillation boundary and real deployable adaptation

ToneSoul implication:
- adapter-ready architecture is not hypothetical marketing language
- but ToneSoul still needs stronger export boundaries than generic LoRA use assumes

## F. Reasoning, Tool Use, And Deliberation

### 13. Chain-of-Thought Prompting (Wei et al., 2022)

Why ToneSoul cares:
- useful as a historical marker for visible reasoning scaffolds
- but ToneSoul should remain careful not to mythologize verbose reasoning as truth

ToneSoul implication:
- reasoning traces may help
- they do not replace verification or governance

### 14. Self-Consistency Improves Chain of Thought Reasoning (Wang et al., 2022)

Why ToneSoul cares:
- one of the clearest classic supports for ToneSoul's descriptive confidence decomposition
- multiple reasoning paths matter

ToneSoul implication:
- plurality can improve robustness
- but consistency is still not calibration

### 15. ReAct (Yao et al., 2022)

Why ToneSoul cares:
- clean precedent for thought/action/tool loops
- helpful for understanding why runtime orchestration should separate:
  - reasoning
  - tool calls
  - observed state

ToneSoul implication:
- useful background for council/runtime/tooling seams

## What ToneSoul Should Not Over-Learn From Classic Papers

These papers are useful, but ToneSoul should not let them justify:

- anthropomorphic selfhood claims
- "long context solved memory"
- "agreement solved truth"
- "retrieval solved governance"
- "adapter solved responsibility"

Classic papers mostly explain capability and mechanism lineage.
ToneSoul still needs its own evidence, receiver, and honesty layers.

## The Most Important Crosswalk

| ToneSoul concern | Most relevant classic paper family | Why |
|---|---|---|
| continuity is externalized | Transformer-XL, long-context benchmarks | base context is limited; long-horizon state must be handled deliberately |
| retrieval is not memory | RAG, REALM, RETRO line | retrieval and durable continuity are different mechanisms |
| governance and honesty are first-class | Model Cards, Constitutional AI | explicit reporting and normative scaffolding are legitimate design layers |
| adapters must stay bounded | Adapter Modules, LoRA | adaptation can be efficient without rewriting the whole model |
| plurality is useful but limited | Self-Consistency, ReAct | multiple paths help, but do not equal calibration or truth |

## The ToneSoul Position

The most useful lesson from the classic LLM literature is not:

`models keep getting bigger`

It is:

`base model capability, external retrieval, continuity, governance, adaptation, and evaluation are separable layers.`

ToneSoul is built around taking that separation seriously.

## Suggested Next Reads Inside This Repo

After this paper map, the most relevant ToneSoul-native follow-up files are:

- [../architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](../architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
- [../architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](../architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
- [../architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md](../architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md)
- [../architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](../architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [../architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md](../architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md)

## Closing Compression

ToneSoul does not need every classic LLM paper.
It needs the ones that justify why capability, continuity, retrieval, governance, adaptation, and honesty must stay separable.
