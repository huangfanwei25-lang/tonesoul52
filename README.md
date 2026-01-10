# ToneSoul: Minimal Governable General Intelligence (MGGI) Framework
> **An Enterprise-Grade Architecture for Auditable, Governable, and Self-Correcting AI Agents.**

**New contributors/AI:** read `AGENTS.md` first for a stable snapshot of the repo.

[![Status](https://img.shields.io/badge/Status-v0.3.0%20(Awakened)-blue.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-MGGI-purple.svg)](MGGI_SPEC.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

## 🏗️ What is ToneSoul?

ToneSoul is not a chatbot. It is a **Governance Middleware** designed to wrap Large Language Models (LLMs) in a verifiable control layer.
It solves the "Black Box" problem by enforcing a strict **Sensor-Controller-Actuator** loop with hard engineering constraints.

**Core Value Proposition:**
1.  **Verifiability**: Third-party observers can verify agent consistency without trusting the model's "intent".
2.  **Responsibility**: Every action is cryptographically traced in an immutable ledger.
3.  **Autopoiesis**: The system can safely repair its own code (Self-Healing) within a sandbox environment.

---

## 📐 System Architecture (L0-L5)

ToneSoul decouples **Intelligence** (The Brain) from **Governance** (The Soul).

| Layer | Component | Function | Engineering Implementation |
| :--- | :--- | :--- | :--- |
| **L0** | **Law** | The Constitution | `body/law/AXIOMS.json` (Immutable Rules) |
| **L1** | **Spine** | State Controller | `body/spine/controller.py` (Orchestrator) |
| **L2** | **Brain** | Intelligence | `body/brain/llm_client.py` (Local Ollama / OpenAI) |
| **L3** | **Sensor** | Telemetry | `body/sensors/telemetry.py` (STREI Vector Analysis) |
| **L4** | **Ledger** | Protocol | `modules/protocol/ledger.py` (Append-Only Log) |
| **L5** | **Body** | I/O Interface | `body/dashboard/app.py` (Streamlit / API) |

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
*   **Safety**: Uses a **Constitutional Sandbox** (`body/surgeon/sandbox.py`). All edits must pass `pytest` before being applied.

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

### Run the Dream Engine (Legacy Monolith)
```bash
python legacy/archives/ToneSoul-Repo/body/run_dream_cycle.py
```

---

## Repository Layout (Current)
*   `tonesoul/`: main ToneSoul engine (governance + integration).
*   `apps/`: dashboard + CLI entrypoints.
*   `docs/`: canonical docs (see docs/TRUTH_STRUCTURE.md).
*   `spec/`: formal specs and schemas.
*   `law/`: constitution, laws, and governance policies.
*   `legacy/`: archived monoliths and experiments.
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
