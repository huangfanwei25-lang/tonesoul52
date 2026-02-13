# ToneSoul: Minimal Governable General Intelligence (MGGI) Framework

> **An Open-Source Architecture for Auditable, Governable, and Self-Correcting AI Agents.**

[![Status](https://img.shields.io/badge/Status-v0.3.0%20(Awakened)-blue.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-MGGI-purple.svg)](MGGI_SPEC.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Accuracy](https://img.shields.io/badge/PreOutputCouncil-100%25%20Accuracy%20(rules--based)-brightgreen.svg)]()

> [!NOTE]
> **Research Project**: ToneSoul is a **free, open-source independent research project**, not a commercial product.
> All development uses free or open-source tools (GitHub, Vercel Free Tier, Render Free Tier, Ollama, Gemini API free quota).

---

## 🌏 Language / 語言

- **English** (this file)
- [中文版 README](README.md)

---

## 🏗️ What is ToneSoul?

ToneSoul is **not** a chatbot. It is a **Governance Middleware** designed to wrap Large Language Models (LLMs) in a verifiable control layer.

### The Problem

Current AI systems are "black boxes" — we don't know *why* they produce certain outputs, and we can't verify if they're aligned with human values.

### Our Solution

ToneSoul implements **Multi-Perspective Coherence Validation**:

1. **Four Perspectives** evaluate every output:
   - 🛡️ **Guardian**: Safety and harm prevention
   - 📊 **Analyst**: Factual coherence and evidence
   - 🔍 **Critic**: Blind spots and assumptions
   - 💬 **Advocate**: User intent alignment

2. **Coherence Score** measures agreement across perspectives

3. **Graduated Verdicts** instead of binary approve/reject:
   - ✅ `APPROVE` — All perspectives agree
   - 📢 `DECLARE_STANCE` — Perspectives diverge; system explains disagreement
   - 🔄 `REFINE` — Needs revision based on feedback
   - 🚫 `BLOCK` — Safety violation or critical disagreement

---

## 🔬 Key Innovation: Truth as Coherence

> **Truth ≠ Correspondence to external facts**  
> **Truth = Agreement across multiple evaluative perspectives**

This philosophical shift (inspired by [BonJour's coherentism](https://en.wikipedia.org/wiki/Coherentism)) enables:

- Validation in **subjective domains** where no "ground truth" exists
- **Transparent reasoning** through explicit multi-perspective voting
- **Honest uncertainty** via stance declaration instead of forced consensus

> [!IMPORTANT]
> Coherence is a **necessary but not sufficient** condition for truth. ToneSoul treats coherence as a **governance signal**, not an ontological claim. Multi-perspective agreement reduces blind spots but does not guarantee correctness.

---

## 📊 Performance

> **Note**: These metrics are from the **rules-based** council mode (no LLM inference). Results reflect a closed test set of 11 hand-crafted cases. LLM-based council performance varies by model and prompt.

| Metric | Result | Conditions |
|--------|--------|------------|
| **Accuracy** | 100% (11/11 test cases) | Rules-based, closed set |
| **False Approve** (safety violations approved) | 0 | Rules-based |
| **Average Latency** | 0.09 ms per validation | Rules-based, no API call |
| **Bilingual Support** | English + Chinese | — |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) (optional, for local LLM)

### Installation

```bash
git clone https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
pip install -r requirements.txt
```

### Basic Usage

```python
from tonesoul.council import PreOutputCouncil

council = PreOutputCouncil()
verdict = council.validate(
    draft_output="This is my AI response",
    context={"topic": "technology"}
)

print(verdict.verdict)  # APPROVE, DECLARE_STANCE, REFINE, or BLOCK
print(verdict.summary)  # Human-readable explanation
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Run Baseline Comparison

```bash
python experiments/baseline_comparison.py
```

---

## 📂 Repository Structure

```
tonesoul52/
├── tonesoul/           # Core engine (canonical code)
│   ├── council/        # Multi-perspective validation
│   │   ├── perspectives/  # Guardian, Analyst, Critic, Advocate
│   │   ├── coherence.py   # Coherence calculation
│   │   └── verdict.py     # Verdict generation
│   └── ...
├── docs/               # Documentation
│   ├── philosophy/     # Theoretical foundations
│   └── architecture/   # System diagrams
├── spec/               # Formal specifications
├── tests/              # Test suite
├── experiments/        # Baseline comparisons
└── AXIOMS.json         # Immutable governance rules
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [MGGI_SPEC.md](MGGI_SPEC.md) | Engineering specification |
| [docs/philosophy/academic_grounding.md](docs/philosophy/academic_grounding.md) | Academic references |
| [docs/architecture/council_diagrams.md](docs/architecture/council_diagrams.md) | Visual architecture |
| [AI_ONBOARDING.md](AI_ONBOARDING.md) | Guide for AI agents |

---

## 🎓 Academic Foundations

ToneSoul draws from peer-reviewed research:

1. **BonJour (1985)** — Coherentism in epistemology
2. **Irving et al. (2018)** — AI Safety via Debate
3. **Bai et al. (2022)** — Constitutional AI

See [academic_grounding.md](docs/philosophy/academic_grounding.md) for full citations.

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

Key areas:
- Expanding perspective implementations
- LLM-based perspective evaluation
- Multilingual keyword support

---

## 📜 License

Apache 2.0 — See [LICENSE](LICENSE)

---

## 👤 Author

**Fan-Wei Huang (黃梵威)**  
- GitHub: [@Fan1234-1](https://github.com/Fan1234-1)
- ORCID: [0009-0002-3517-9779](https://orcid.org/0009-0002-3517-9779)

---

## 🌟 Acknowledgments

- AI Collaborators: Antigravity (Gemini), Codex (OpenAI)
- Philosophy: BonJour, Irving, Anthropic research team
- Community: All contributors and reviewers

---

*ToneSoul: Making AI governance transparent, one perspective at a time.*
