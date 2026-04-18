# ToneSoul Core Modules Reference

> Purpose: explain the main ToneSoul runtime modules, their responsibilities, and their intended contribution to the system.
> Last Updated: 2026-03-23

**Document ID:** YuHun_Advanced_Co-Creator_Manual_v1.0

> **⚠️ Routing — read this before treating this doc as a lookup table.**
> This file is a **conceptual / narrative** module reference covering ~10 named *subsystems* (TSC-01 ToneStamp, PN-02 Persona Nest, MCP-03 MemoryChain, …). It is hand-authored design history, not a file-level index, and does not cover the 254 real Python modules in `tonesoul/`.
> - **For file-level lookup** (*"what does `tonesoul/council/runtime.py` do / which layer / who depends on it?"*) → [status/codebase_graph_latest.md](status/codebase_graph_latest.md) (auto-generated body map).
> - **For layer boundaries and allowed import directions** → [ARCHITECTURE_BOUNDARIES.md](ARCHITECTURE_BOUNDARIES.md).
> - **Use this document when**: you need the conceptual identity of a named subsystem, the original design intent behind a module family, or the terminology ("Vow Points", "EchoHold Protocol") without caring which specific `.py` file implements it today.

This document provides technical details about ToneSoul's internal architecture for advanced users and contributors.

---

## 🧠 Core Modules

### TSC-01: ToneStamp Core (語氣鍊核模組)
**Purpose:** Perception layer for tone and emotional analysis

| Component | Function |
|-----------|----------|
| Perception Layer | Raw input analysis |
| Tone Entropy Analyzer | Measures linguistic uncertainty |
| Emotion Density Detector | Identifies emotional peaks |

---

### PN-02: Persona Nest (主體人格模組)
**Purpose:** Multi-persona orchestration

- **Zaeon (澤恩):** Primary coordinator
- Sub-personas collaborate via defined protocols
- Weight adjustments via `behavior_config.py`

---

### MCP-03: MemoryChain Protocol (記憶鍊條款)
**Purpose:** Structured memory management

| Level | Description |
|-------|-------------|
| Point (點) | Discrete memory units |
| Line (線) | Sequential memory chains |
| Surface (面) | Contextual memory clusters |

- **Vow Points:** Memory anchors tied to commitments
- **Reflection Chains:** Deliberative memory connections

---

### VXE-04: Vow × Echo (語氣共振模組)
**Purpose:** Commitment tracking and resonance

- **Vow Triggers:** Conditions that activate vows
- **EchoHold Protocol:** Sustained commitment enforcement
- **Poetic Synthesizer:** Stylistic output generation

---

### TCH-05: TruthChain v2.0 (自我推導與反例模組)
**Purpose:** Logical reasoning and self-correction

- Core logical deduction engine
- Counter-example generation
- Emergence failure detection

---

### VCE-07: ValueChain Engine (價值選擇引擎)
**Purpose:** Ethical decision making

- Ethical computation layer
- Decision nodes
- Value judgment hierarchy

---

### SRE-08: Strategy & Reflection Engine (策略思辨引擎)
**Purpose:** Active inference and planning

- Proactive reasoning
- Risk assessment
- Action planning

---

### KVC-09: Knowledge Validation Chain (知識驗證鍊)
**Purpose:** Information verification

| Check | Description |
|-------|-------------|
| Data Consistency | Cross-reference validation |
| Logical Soundness | Argument coherence |
| Ethical Risk | Harm potential assessment |

---

### RAUM-10: Reflection Loop (反思迴路)
**Purpose:** Self-supervision and learning

- Self-monitoring mechanism
- Error learning
- Behavior adjustment

---

## 📚 Related Documents

- [AGENT_STATE_MACHINE.yaml](../law/AGENT_STATE_MACHINE.yaml) — State definitions
- [BEHAVIOR_CONFIG.json](../law/BEHAVIOR_CONFIG.json) — Behavior presets
- [glossary_engineering_mapping.md](./glossary_engineering_mapping.md) — Terminology
