**Core Value Proposition:**
1.  **Verifiability**: Third-party observers can verify agent consistency without trusting the model's "intent".
2.  **Responsibility**: Every action is cryptographically traced in an immutable ledger.
3.  **Autopoiesis**: The system can safely repair its own code (Self-Healing) within a sandbox environment.

---


## Positioning: Meaning Transfer Protocol
ToneSoul is not a rulebook. It is a meaning-transfer protocol.

* **Axioms encode values, not behaviors**: behaviors are derived, not prescribed.
* **Council forces multi-perspective reasoning** and exports structured, auditable output.
* **Isnad + drift_log capture "why"**: Council verdicts record reasoning, and handoff drift records why deviations occurred.

---

## Concrete Risk Model (Design Intent)
* **Governance misuse**: surface compliance without understanding.
* **Meaning loss at handoff**: instructions without reasons.
* **Responsibility breaks**: outputs without rationale or trace.

Design intent mitigations:
* Council issues `REFINE` / `DECLARE_STANCE` when rationale is weak.
* Isnad hash chain stores structured verdicts (including reasons).
* drift_log preserves continuity of choices across handoffs.

---



## 📐 System Architecture (L0-L5)

ToneSoul decouples **Intelligence** (The Brain) from **Governance** (The Soul).

| Layer | Component | Function | Engineering Implementation |
| :--- | :--- | :--- | :--- |
| **L0** | **Law** | The Constitution | `law/AXIOMS.json` (Immutable Rules) |
| **L1** | **Spine** | State Controller | `tonesoul/unified_controller.py` (Orchestrator) |
| **L2** | **Brain** | Intelligence | `tonesoul/tonesoul_llm.py` (LLM Integration) |
| **L3** | **Sensor** | Telemetry | `tonesoul/tsr_metrics.py` (STREI Vector Analysis) |
| **L4** | **Ledger** | Protocol | `memory/provenance_ledger.jsonl` (Append-Only Log) |
| **L5** | **Body** | I/O Interface | `apps/dashboard/frontend/app.py` (Streamlit / API) |

---

## Architecture Updates (2026-02)

*   **Council Facade**: The single entrypoint is `tonesoul/council/runtime.py` (legacy adapters are deprecated).
*   **SoulDB Backends**: `tonesoul/memory/soul_db.py` supports JSONL by default and an optional SQLite backend (`memory/soul.db`) with a migration helper.
*   **Isnād Auto-Write**: Every council verdict appends a structured record to `memory/provenance_ledger.jsonl` for auditability.

---

## 🔬 The MGGI Specification

We define "Soul" not as metaphysics, but as **Verifiable Self-Constraint**.
See [MGGI_SPEC.md](MGGI_SPEC.md) for the formal engineering constraints.

### The Governance Vector (STREI)
Every input is mapped to a 5-dimensional vector space $V \in \mathbb{R}^5$:
*   **S (Stability)**: Consistency of context.
*   **T (Tension)**: Entropic stress of the conversation.
*   **R (Responsibility)**: Risk probability (0.0 - 1.0).
*   **E (Ethics)**: Axiomatic alignment.
*   **I (Intent)**: Magnitude of action.

**Constraint Rule**: if $R > 0.6 \implies \text{BLOCK}$ (Hard Gate).

---

## 🚀 Key Capabilities (v0.3.0)

### 1. 👁️ Multimodal Vision (The All-Seeing Eye)
*   **Feature**: Integrates `llava` (Vision Model) into the governance loop.
*   **Benefit**: The agent can "see" images and apply ethical judgment to visual inputs.
*   **Usage**: Upload images via the Dashboard.

### 2. ⚡ Telemetry Cache ("Ghost in the Shell")
*   **Feature**: Local vector caching of STREI analysis.
*   **Benefit**: Reduces compute load by 90% for recurrent patterns. Allows efficient operation on older hardware.

### 3. 🔪 Test-Driven Autopoiesis (The Surgeon)
*   **Feature**: Self-Correction Pipeline.
*   **Benefit**: The agent can edit its own source code to fix bugs.
*   **Safety**: Uses a test-driven sandbox workflow. All edits must pass `pytest` before being applied.

---

## 💻 Getting Started

### Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.ai/) (Recommended for Local Privacy)
*   Models: `gemma3:4b`, `llava`, `nomic-embed-text`

### Installation
```bash
git clone https://github.com/Fan1234-1/ToneSoul-Architecture-Engine.git
cd ToneSoul-Architecture-Engine
pip install -r requirements.txt
```

### Run the Dashboard (The Cockpit)
```bash
python apps/dashboard/run_dashboard.py
```
Access the interface at `http://localhost:8501`.

### Legacy Monolith
This workspace does not include the legacy monolith runner. See `.archive/` if you have archived bundles.

---

## Repository Layout (Current)
*   `tonesoul/`: main ToneSoul engine (governance + integration).
*   `apps/`: dashboard + CLI entrypoints.
*   `docs/`: canonical docs (see docs/TRUTH_STRUCTURE.md).
*   `spec/`: formal specs and schemas.
*   `law/`: constitution, laws, and governance policies.
*   `.archive/`, `experiments/`, `examples/`: archived monoliths and experiments.
*   `memory/`, `reports/`, `run/`, `temp/`: runtime data, logs, and artifacts.

## 📂 Documentation Structure
*   **Engineering Spec**: [MGGI_SPEC.md](MGGI_SPEC.md)
*   **Governance Protocols**: [docs/governance/](docs/governance/) (Standard for STREI, NSC, and Temporal Audit)
*   **Engineering Journal**: [docs/engineering/](docs/engineering/) (Detailed technical volumes)
*   **Truth Structure**: [docs/TRUTH_STRUCTURE.md](docs/TRUTH_STRUCTURE.md) (Living source of sense-making)
*   **Operation Guide**: [HANDOFF.md](HANDOFF.md)

---

## 🛡️ License & Ethics
ToneSoul is Open Source (Apache 2.0). 
We believe that **Governance Logic** should be transparent, while **Memory Data** remains sovereign to the user.
