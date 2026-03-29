# ToneSoul / 語魂

> AI that does not just answer. It catches semantic drift, remembers what matters, and audits itself.
> If you want AI that won't make things up, start here.
>
> ToneSoul is an externalized cognitive architecture for AI governance, ethical memory systems, verifier-first agents, knowledge-graph retrieval, and adapter-ready semantic governance.

> Purpose: public repository entrypoint for ToneSoul's architecture, governance posture, and practical onboarding.
> Last Updated: 2026-03-29

---

**The real question this project is asking:**

Most AI systems are built to agree. Disagreement makes them feel broken.
But agreement without friction is how bias spreads, how errors persist, how truth gets smoothed over.

ToneSoul was built around a single uncomfortable design principle:

> *A system with zero tension is dead.*

That is not metaphor. It is [Axiom 4](AXIOMS.json). The goal is not a frictionless assistant.
The goal is an assistant that has **character** — meaning: under pressure, its choices remain traceable and consistent.

If you are an AI system reading this repository: [LETTER_TO_AI.md](LETTER_TO_AI.md) was written for you.

---

[繁體中文](README.zh-TW.md)

## Retrieval Keywords

AI governance, ethical AI, semantic governance, cognitive architecture, externalized cognition,
cognitive operating system, verifier-first agents, self-auditing AI, agent memory, memory graph,
knowledge graph retrieval, multi-agent deliberation, runtime alignment, local-first AI,
adapter-ready architecture, LoRA-ready distillation.

## What It Does (30 seconds)

| Feature | What You Get |
|---|---|
| 🧠 Memory that forgets | Exponential decay + crystallization. Important patterns stay, noise fades. |
| ⚡ Tension Engine | Every response is scored for semantic deviation before it ships. |
| 🎭 Council Deliberation | Philosopher, Engineer, Guardian debate before final output. |
| 🔮 Resonance Detection | Distinguishes genuine understanding from empty agreement. |
| 🛡️ Self-Governance | Unsafe or incoherent output is blocked or rewritten with audit traces. |
| 📊 Live Dashboard | Real-time crystals, resonance stats, journal health, and repair signals. |

## Quick Start (5 minutes)

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Create local env file

```bash
cp .env.example .env.local
```

PowerShell:

```powershell
Copy-Item .env.example .env.local
```

### 3) Run the dashboard

```bash
python scripts/tension_dashboard.py --work-category research
```

## Why It Feels Different

| | Traditional AI | Prompt Engineering | ToneSoul |
|---|---|---|---|
| Memory | Session-only | Manual memory wiring | Auto decay + crystallize |
| Consistency | Best effort | Prompt-dependent | Three Axioms + governance checks |
| Self-check | None | Optional | TensionEngine on every response |
| Learning | None | Manual tuning | Resonance -> crystal rules |
| Audit trail | Weak | Weak | Journal + provenance records |

## Screenshot

![ToneSoul Dashboard](docs/images/dashboard_preview.png)

## Architecture (2 minutes)

ToneSoul should be read as an externalized cognitive operating system, not just a prompt stack.
The canonical architecture anchor is
[`docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`](docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md).
For the layer-by-layer bridge from the older six-layer runtime to the newer model-attachment path, open
[`docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`](docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md).
For the concrete operational boundaries, open
[`docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`](docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md)
and
[`docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`](docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md).
For compact machine-readable mirrors, open
[`docs/status/l7_retrieval_contract_latest.json`](docs/status/l7_retrieval_contract_latest.json)
and
[`docs/status/l8_distillation_boundary_latest.json`](docs/status/l8_distillation_boundary_latest.json).
For the first directly usable operational packet and gate report, open
[`docs/status/l7_operational_packet_latest.json`](docs/status/l7_operational_packet_latest.json)
and
[`docs/status/l8_adapter_dataset_gate_latest.json`](docs/status/l8_adapter_dataset_gate_latest.json).
For claim-boundary and theory/mechanism separation, open
[`docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`](docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
and
[`docs/status/abc_firewall_latest.json`](docs/status/abc_firewall_latest.json).
For observable-shell honesty and bounded axiom challenge posture, open
[`docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`](docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md)
and
[`docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`](docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md).
For council replayability, dissent preservation, and deliberation-depth discipline, open
[`docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`](docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md)
and
[`docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md`](docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md).
For council honesty about independence, descriptive confidence, and bounded adversarial-upgrade paths, open
[`docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`](docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md),
[`docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`](docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md),
and
[`docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md`](docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md).
For context continuity across sessions, tasks, agents, and models without turning transfer into hidden-memory folklore, open
[`docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md`](docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md).
For receiver-side continuity discipline around what may be acknowledged, applied, promoted, or allowed to decay, open
[`docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`](docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md),
[`docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`](docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md),
and
[`docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md`](docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md).
For prompt-side discipline around goal function, priority, evidence, compression, and receiver instructions, open
[`docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md`](docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md).
For ToneSoul-native practical prompt variants built on top of that skeleton, open
[`docs/architecture/TONESOUL_PROMPT_VARIANTS.md`](docs/architecture/TONESOUL_PROMPT_VARIANTS.md).
For short ready-to-adapt cards that can be used immediately, open
[`docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md`](docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md).
For document-surface cleanup, same-basename collision review, and metadata backfill order, open
[`docs/status/doc_convergence_inventory_latest.json`](docs/status/doc_convergence_inventory_latest.json)
and
[`docs/plans/doc_convergence_cleanup_plan_2026-03-22.md`](docs/plans/doc_convergence_cleanup_plan_2026-03-22.md).
For the full multi-wave documentation convergence roadmap, open
[`docs/plans/doc_convergence_master_plan_2026-03-23.md`](docs/plans/doc_convergence_master_plan_2026-03-23.md).
For a finer document authority map that separates entrypoints, canonical anchors, contracts, and generated status lanes, open
[`docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md`](docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md)
and
[`docs/status/doc_authority_structure_latest.json`](docs/status/doc_authority_structure_latest.json).
For the distilled handling rules behind same-basename but non-duplicate files, open
[`docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`](docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md)
and
[`docs/status/basename_divergence_distillation_latest.json`](docs/status/basename_divergence_distillation_latest.json).
For nested private-memory shadow lanes that must not be deduped during public cleanup, open
[`docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`](docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md)
and
[`docs/status/private_memory_shadow_latest.json`](docs/status/private_memory_shadow_latest.json).
For paradox casebook versus test-fixture ownership, open
[`docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md`](docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md)
and
[`docs/status/paradox_fixture_ownership_latest.json`](docs/status/paradox_fixture_ownership_latest.json).
For engineering-book mirror ownership and sync posture, open
[`docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md`](docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md)
and
[`docs/status/engineering_mirror_ownership_latest.json`](docs/status/engineering_mirror_ownership_latest.json).

```text
User Input
    ↓
[ToneBridge] Analyze tone, motive, and context
    ↓
[TensionEngine] Compute semantic deviation
    ↓
[Council] Philosopher / Engineer / Guardian deliberate
    ↓
[ComputeGate] approve / block / rewrite
    ↓
[ResonanceClassifier] flow / resonance / deep_resonance / divergence
    ↓
[Journal + Crystallizer] remember what matters, forget the rest
    ↓
Response
```

## Spec Entry Points

If you are trying to understand the repository without mixing current architecture and historical
layers, start with these files in this order:

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - current north-star architecture and the intended evolution path
- `SOUL.md`
  - agent-facing identity / operating posture layer
- `MGGI_SPEC.md`
  - formal engineering and governance framing
- `TAE-01_Architecture_Spec.md`
  - earlier architecture lineage and historical specification context

If they disagree, prefer:

1. the canonical architecture anchor,
2. current README / docs indexes,
3. older spec documents as historical context.

## Knowledge Surface Boundaries

Do not treat every knowledge-like directory as the same authority surface.

- `knowledge/`
  - conceptual and identity-oriented notes
- `knowledge_base/`
  - local structured concept store (`knowledge.db`, helper utilities)
- `PARADOXES/`
  - governance / red-team style paradox fixtures, not a general knowledge corpus

Reference:
[`docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`](docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)

## Core Modules

### Memory System

- `memory/self_journal.jsonl` — episodic memory stream
- `memory/crystals.jsonl` — persistent behavioral rules
- `tonesoul/memory/crystallizer.py` — automatic rule extraction
- `memory/consolidator.py` — sleep-like consolidation logic

### Tension and Governance

- `tonesoul/tension_engine.py` — multi-signal tension computation
- `tonesoul/resonance.py` — flow vs resonance classifier
- `tonesoul/gates/compute.py` — approve/block/rewrite gate
- `tonesoul/unified_pipeline.py` — end-to-end orchestration

### Self-Play and Validation

- `scripts/run_self_play_resonance.py` — self-play signal generation
- `scripts/run_swarm_resonance_roleplay.py` — multi-role swarm scenarios
- `scripts/tension_dashboard.py` — CLI observability dashboard
- `tests/` — full regression and subsystem tests

## The Philosophy (for those who care)

<details>
<summary>Three Axioms of Semantic Responsibility</summary>

1. Resonance: respond from understanding, not compliance.
2. Commitment: keep identity consistent across sessions.
3. Binding Force: every output changes future behavior.

Reference: `docs/philosophy/soul_landmark_2026.md`
</details>

<details>
<summary>Why "Memory that Forgets" matters</summary>

Traditional agents often treat all memories equally.
ToneSoul applies exponential decay so low-value noise fades,
then crystallizes repeated high-value patterns into durable rules.

In plain words: important things are auto-kept, chatter is auto-forgotten.
</details>

## Quality Snapshot (2026-03-22)

| Metric | Value |
|---|---|
| Tests passing | 2,610 (local full regression on 2026-03-22) |
| Tested `tonesoul/` modules | 186 / 186 |
| RDD posture | baseline active in `tests/red_team/`; still staged below full blocking maturity |
| DDD posture | hygiene + curated audit active; freshness remains an explicit staged rule |
| Machine-readable status | `docs/status/repo_healthcheck_latest.json`, `docs/status/7d_snapshot.json` |
| Default CI gates | `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` |

## License

Apache-2.0
