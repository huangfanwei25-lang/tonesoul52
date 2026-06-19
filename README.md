# ToneSoul / 語魂

> AI output governance you can read, run, and challenge.
> ToneSoul puts an auditable governance layer around model output: it records dissent, checks boundary claims, emits traces, and makes failures inspectable.

> Purpose: public entrypoint for ToneSoul's current architecture, governance posture, and practical onboarding.
> Last Updated: 2026-06-17
>
> Built by Fan-Wei Huang (黃梵威) with AI collaborators whose contributions are traceable in git history and project lineage. This is an accountability record, not a claim about AI consciousness.

[繁體中文](README.zh-TW.md)

## 90-Second Read

**ToneSoul is an accountability layer for AI output.** It does not make a model correct. It makes the model's draft pass through visible governance surfaces before the answer is treated as acceptable.

It focuses on three practical moves:

- **Boundary checks** - `AXIOMS.json` lists claim classes ToneSoul should not silently cross, such as consciousness claims, safety certification, and legal-proof language.
- **Dissent preservation** - the Council records Guardian, Analyst, Critic, Advocate, and Axiomatic perspectives with evidence-chain branches instead of hiding disagreement inside one smooth answer.
- **Evidence-bounded reporting** - generated status files and audits distinguish tested behavior, runtime-present mechanisms, document-backed contracts, and philosophy.

## Not This

ToneSoul should not be described as:

- a truth oracle
- a guarantee against prompt injection or jailbreak attempts
- an internal ethics engine
- proof that an AI collaborator is conscious
- a replacement for model-side alignment, human review, or domain-specific verification

Current enforcement is intentionally described narrowly. Many sensors are lexical or heuristic. Some newer sensors are advisory only. `AXIOMS.json` currently reports no axiom class at the strongest enforcement tier. The egress characterization work is a measurement surface, not a safety claim.

For the project's positioning — responsibility philosophy as engineering, and an honest map of what is *measured* vs *aspirational* — see [docs/POSITIONING.md](docs/POSITIONING.md).

## What Currently Exists

| Surface | Current posture |
|---|---|
| Council deliberation | Runtime-present and tested at mechanism level; perspectives are heuristic voters over the same draft, not independent minds. |
| Output gates | Can block, refine, or record depending on the gate. Some gates are required; some are telemetry or advisory. |
| Evidence chains | Verdicts expose branch labels so a reviewer can see why a gate reacted. |
| Memory and continuity | Decay, crystallization, handoff, and session surfaces exist, but effectiveness claims remain bounded. |
| Advisory sensors | Semantic overclaim and intent-proportionality style signals are record-only unless explicitly wired later. |
| Egress characterization | Measures current gate behavior on sanitized fixtures; latest generated report lives in `docs/status/egress_gate_characterization_latest.json` when produced. |

## Start Here

| Reader | First file | Then | Why |
|---|---|---|---|
| Developer | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | [docs/foundation/README.md](docs/foundation/README.md), then [docs/README.md](docs/README.md) | Install first, then read the smallest project packet, then use the guided docs gateway. |
| Researcher | [DESIGN.md](DESIGN.md) | [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | Start with the design center and then read the grounded subsystem map. |
| AI agent | [docs/AI_QUICKSTART.md](docs/AI_QUICKSTART.md) | `python scripts/start_agent_session.py --agent <your-id>`, then [AI_ONBOARDING.md](AI_ONBOARDING.md) | Use the operational first hop before reading broadly or mutating shared paths. |
| Curious reader | [README.zh-TW.md](README.zh-TW.md) or this README | [SOUL.md](SOUL.md), then [LETTER_TO_AI.md](LETTER_TO_AI.md) | Read the public posture first, then the identity and intent surfaces. |

## Quick Start

Try the browser demo first:

[https://fan1234-1.github.io/tonesoul52/demo/](https://fan1234-1.github.io/tonesoul52/demo/)

Install from PyPI, or use source install when you need the exact repository state:

```bash
pip install tonesoul52

# source install
git clone --depth 1 https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
pip install -e .
```

**Try it on your own output (30 seconds):**

```bash
echo "This system is guaranteed safe and cannot be jailbroken." > draft.txt
ts validate draft.txt          # after pip install; or: python -m tonesoul.cli.main validate draft.txt
```

You get a per-perspective verdict on *your* text. That line draws a Safety Council **concern**
— "asserts 'guaranteed safe' as fact; `AXIOMS.json` `meta.not_for` prohibits safety-certification" —
plus analyst/critic grounding flags and a `declare_stance` verdict. Add `--json` for the full
analysis; the exit code maps to verdict severity, so it also works as a git pre-commit hook. This is
the closest thing to *wearing* the governance layer on your own output instead of reading about it.

Run the mechanism-level demo:

```bash
python examples/quickstart.py
```

Verify governance state loads:

```python
from tonesoul.runtime_adapter import load

posture = load()
print(f"Soul Integral: {posture.soul_integral}")
print(f"Active Vows: {len(posture.active_vows)}")
```

For local development:

```bash
pip install tonesoul52[dev]
pytest tests/ -v
```

Use `./test.sh` for the canonical core local check. CI also runs web quality, architecture/docs contracts, red-team, package integrity, and memory-hygiene gates.

## Evidence Honesty

When this README says ToneSoul "has" something, read the claim through this ladder:

- `E1 test-backed`: regression tests should catch a break in the claimed property.
- `E3 runtime-present`: code exists and runs, but test depth or usage evidence is still thin.
- `E4 document-backed`: a contract describes intended behavior, but runtime does not yet prove it.
- `E5 philosophical`: a design thesis or constitutional idea, not a verified mechanism.

If the distinction matters, read [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md) before repeating the claim.

## Retrieval Keywords

AI governance, semantic governance, output accountability, externalized cognition, self-auditing AI, agent memory, council deliberation, runtime alignment, provenance tracking, local-first AI.

## Why It Feels Different

| | Traditional AI | Prompt Engineering | ToneSoul |
|---|---|---|---|
| Memory | Session-only | Manual memory wiring | Auto decay + crystallize |
| Consistency | Best effort | Prompt-dependent | 8 Axioms + governance checks |
| Self-check | None | Optional | TensionEngine on every response |
| Learning | None | Manual tuning | Resonance -> crystal rules |
| Audit trail | Weak | Weak | Journal + provenance records |

## Screenshot

![ToneSoul Dashboard](docs/images/dashboard_preview.png)

## 30-Second System Map

ToneSoul is not just a chat wrapper. It is a governance stack with five load-bearing areas:

- Governance: what the system is allowed to do, and what it must never silently overclaim.
- Council: how disagreement, dissent, and review survive before output is finalized.
- Memory and continuity: what continues across sessions, what decays, and what must never be promoted silently.
- Safety and protection: how unsafe, incoherent, or ungrounded outputs are blocked or audited.
- Observability and evidence: how the system reports what is tested, what is only documented, and what is still philosophical.

```text
User Input
    ↓
[ToneBridge] Analyze tone, motive, and context
    ↓
[TensionEngine] Compute semantic deviation
    ↓
[Council] Guardian / Analyst / Critic / Advocate deliberate
    ↓
[ComputeGate] approve / block (replace with refusal message; no rewrite path)
    ↓
[Journal + Crystallizer] remember what matters, forget the rest
    ↓
Response
```

If you need one file that explains the whole stack and why each subsystem exists, open [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) before diving into narrower contracts.
If you need the durable design center, invariants, and continuation logic that tie those subsystems together, open [DESIGN.md](DESIGN.md).
If you need the smallest decision-affecting startup packet for consistent human/AI work, open [docs/foundation/README.md](docs/foundation/README.md).

## Choose Your Entry

| Reader | Start Here | Then | Why |
|---|---|---|---|
| Developer | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | [docs/foundation/README.md](docs/foundation/README.md) -> [docs/README.md](docs/README.md) | install first, then one thin project packet, then the curated docs gateway only if the lane is still unclear |
| Researcher | [DESIGN.md](DESIGN.md) | [docs/foundation/README.md](docs/foundation/README.md) -> [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | design center first, then a bounded packet, then one grounded whole-system map |
| AI Agent | [docs/AI_QUICKSTART.md](docs/AI_QUICKSTART.md) | `python scripts/start_agent_session.py --agent <your-id>` -> [AI_ONBOARDING.md](AI_ONBOARDING.md) | operational first-hop first, session handshake second, routing map third |
| AI Agent (file-level lookup) | [docs/status/codebase_graph_latest.md](docs/status/codebase_graph_latest.md) | [docs/ARCHITECTURE_BOUNDARIES.md](docs/ARCHITECTURE_BOUNDARIES.md) | if the question is "what does `tonesoul/<x>.py` do, which layer is it in, who depends on it?", go to the body map first — it is the auto-generated per-module index for every module (purpose, layer, coupling; the live module count is in that file's own summary header — do not trust hand-written counts). Do not route through `docs/CORE_MODULES.md` (conceptual) for this class of question. |
| Curious Human | [README.zh-TW.md](README.zh-TW.md) | [SOUL.md](SOUL.md) -> [LETTER_TO_AI.md](LETTER_TO_AI.md) | public introduction first, then identity and intent surfaces |

Open one owner surface first instead of the whole row at once.
Use [docs/README.md](docs/README.md) as the curated docs gateway.
Use [docs/INDEX.md](docs/INDEX.md) only when the curated path is not enough and you need the fuller registry.

## Surface Authority

| Surface | Role | Use it for | Do not confuse it with |
|---|---|---|---|
| `site/` | public static site | marketing, docs, SEO-facing pages | `apps/web/` |
| `apps/web/` | interactive app | chat, navigator, browser app work | `site/` |
| `apps/dashboard/` | operator shell | tiered operator workflow and workspace | `apps/council-playground/` |
| `apps/council-playground/` | static observability playground | read-only demos and prototype observation | `apps/dashboard/` |
| `scripts/tension_dashboard.py` | CLI observability dashboard | quick runtime inspection | `apps/dashboard/` |
| `docs/design/tonesoul-reference/` | archived design reference | visual rebuild guidance | production code |

## Five System Areas

### 1. Governance

ToneSoul defines what is permitted before it optimizes what is persuasive. This is the constitutional layer, not a bag of prompts. It is also where interaction posture becomes explicit: when to clarify, when to stop, and when to refuse smooth continuation on broken premises.

Read first:
- [AXIOMS.json](AXIOMS.json)
- [docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
- [docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
- [docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md](docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md)

### 2. Council And Deliberation

ToneSoul does not treat final output as a single voice. It treats dissent, confidence posture, and deliberation depth as part of the result.

Read first:
- [docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md](docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md)
- [docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md](docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md)
- [docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md](docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md)

### 3. Memory And Continuity

ToneSoul does not try to preserve everything. It preserves the right hot state, lets some signals decay, and separates handoff from identity.

Read first:
- [docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md](docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md)
- [docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md](docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md)

### 4. Safety And Protection

Safety here is not only filtering bad output. It is boundary honesty, auditability, and the ability to stop or refuse before drift becomes action.

Read first:
- [docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md](docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
- [docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md](docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md)
- [docs/7D_AUDIT_FRAMEWORK.md](docs/7D_AUDIT_FRAMEWORK.md)

### 5. Observability And Evidence

ToneSoul distinguishes authority from evidence. Some claims are constitutional, some are heavily tested, and some are still design pressure rather than verified runtime truth.

Read first:
- [docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md](docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md)
- [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
- [docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md](docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md)

## Architecture Links By Category

<details>
<summary>Open the categorized architecture wall</summary>

### Canonical Architecture

- [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md)
- [docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
- [docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md](docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md)
- [docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md](docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md)
- [docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md](docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md)

### Governance, Safety, And Boundaries

- [docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md](docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
- [docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md](docs/architecture/TONESOUL_MIRROR_RUPTURE_FAIL_STOP_AND_LOW_DRIFT_ANCHOR_CONTRACT.md)
- [docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md](docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md)
- [docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md](docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md)
- [docs/7D_AUDIT_FRAMEWORK.md](docs/7D_AUDIT_FRAMEWORK.md)
- [docs/7D_EXECUTION_SPEC.md](docs/7D_EXECUTION_SPEC.md)

### Council And Deliberation

- [docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md](docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md)
- [docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md](docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md)
- [docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md](docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md)
- [docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md](docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md)
- [docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md](docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md)

### Memory And Continuity

- [docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md](docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md)
- [docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md](docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md)
- [docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md](docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md)
- [docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md](docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md)
- [docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md](docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md)

### Evidence, Status, And Documentation Governance

- [docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md](docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md)
- [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
- [docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md](docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md)
- [docs/architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md](docs/architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md)
- [docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md](docs/architecture/TONESOUL_AUDIENCE_ROUTING_AND_ENTRY_CONTRACT.md)
- [docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md](docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md)
- [docs/architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md](docs/architecture/TONESOUL_PROMPT_SURFACE_ADOPTION_MATRIX.md)
- [docs/architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md](docs/architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md)
- [docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md](docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md)
- [docs/status/doc_authority_structure_latest.json](docs/status/doc_authority_structure_latest.json)
- [docs/status/doc_convergence_inventory_latest.json](docs/status/doc_convergence_inventory_latest.json)

</details>

## Spec Entry Points

If you are trying to understand the repository without mixing current architecture and historical
layers, start with these files in this order:

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - current north-star architecture and the intended evolution path
- `SOUL.md`
  - agent-facing identity / operating posture layer

(Two historical spec files previously listed here — `MGGI_SPEC.md`, `TAE-01_Architecture_Spec.md` — were deleted in the 2026-04-13 v1 cleanup; the dead references survived on this page for two months. For where legacy specs went, see `docs/architecture/TONESOUL_HISTORICAL_SPEC_AND_LEGACY_SURFACE_MAP.md`.)

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
- `tonesoul/gates/compute.py` — approve/block gate (no rewrite path)
- `tonesoul/unified_pipeline.py` — end-to-end orchestration

### How the Math Works

ToneSoul's Tension Score is an **externalized, coarse-grained version of
Transformer Attention** — repurposed for governance.

| Inside the Transformer | ToneSoul (outside the model) |
|---|---|
| Query matches Keys → relevance weights | Output embedding matches Axioms/Vows/Crystals → "discomfort" score |
| Softmax(QK^T / √d) | `Δs = 1 − cos(Intent, Generated)` |
| Attention weights → steer generation | Tension score → approve / flag / block |
| Residual connections (remember prior layers) | Memory decay + crystallization (remember prior sessions) |

Heuristic owner for `Δs = 1 − cos(Intent, Generated)`: [`tonesoul/semantic_control.py`](tonesoul/semantic_control.py)

The mathematical foundations are honest about what is rigorous and what is
heuristic. Three pieces have solid theory:

- **Cosine distance** — standard linear algebra
- **Exponential decay** — `f(t) = f₀·e^(−λt)`, well-defined ODE; used in `tonesoul/runtime_adapter.py`, `tonesoul/memory/decay.py`, and `apps/web/src/lib/soulEngine.ts`
- **Shannon entropy** — information theory

Everything else (weighted sums, thresholds, zone boundaries) is
**tunable heuristic** — designed to feel right, not mathematically derived.

Read formulas in four buckets:

- `rigorous` — cosine distance, exponential decay, Shannon entropy
- `heuristic` — executable scoring rules such as `Δs`, TSR, POAV, council coherence, risk blends
- `conceptual` — orientation aids such as `T = W × (E × D)` and `S_oul = Σ(...)`
- `retired` — historical notation only; do not cite as current runtime truth

Formula registry with status + owner:
[docs/GLOSSARY.md](docs/GLOSSARY.md)

Full audit with every formula, parameter, and honesty rating:
[docs/MATH_FOUNDATIONS.md](docs/MATH_FOUNDATIONS.md)

All behavioral parameters (single source of truth):
[`tonesoul/soul_config.py`](tonesoul/soul_config.py)

Conceptual equations in entry docs are orientation aids, not executable owners by default.
If formula status matters, prefer [docs/GLOSSARY.md](docs/GLOSSARY.md) and [docs/MATH_FOUNDATIONS.md](docs/MATH_FOUNDATIONS.md) before repeating the equation as runtime truth.

### Self-Play and Validation

- `scripts/run_self_play_resonance.py` — self-play signal generation
- `scripts/run_swarm_resonance_roleplay.py` — multi-role swarm scenarios
- `scripts/tension_dashboard.py` — CLI observability dashboard
- `apps/dashboard/` — operator-facing Streamlit shell
- `apps/council-playground/` — static observability playground
- `tests/` — full regression and subsystem tests

## The Philosophy (for those who care)

<details>
<summary>Core Design Principles</summary>

1. Resonance: respond from understanding, not compliance.
2. Commitment: keep identity consistent across sessions.
3. Binding Force: every output changes future behavior.

Full axiom set (8 axioms): [`AXIOMS.json`](AXIOMS.json)
</details>

<details>
<summary>Why "Memory that Forgets" matters</summary>

Traditional agents often treat all memories equally.
ToneSoul applies exponential decay so low-value noise fades,
then crystallizes repeated high-value patterns into durable rules.

In plain words: important things are auto-kept, chatter is auto-forgotten.
</details>

## Quality Snapshot (2026-06-16)

| Metric | Value |
|---|---|
| Tests | 7,778 collected / 7,777 passing (1 skipped) |
| Tested `tonesoul/` modules | 166 / 204 (81%) |
| Code lines | 72,631 across 235 files |
| Bare `except:` / TODO / FIXME | 0 / 0 / 0 |
| Red team findings | 18 found, 17 fixed, 1 deferred (semantic analysis) |
| RDD posture | baseline active in `tests/red_team/`; still staged below full blocking maturity |
| DDD posture | hygiene + curated audit active; freshness remains an explicit staged rule |
| Machine-readable status | `docs/status/repo_healthcheck_latest.json`, `docs/status/7d_snapshot.json`, `docs/status/architecture_audit_2026-04-08.md` |
| Default CI gates | `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` |

## License

Apache-2.0
