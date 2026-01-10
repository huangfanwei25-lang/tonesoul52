# Getting Started with ToneSoul

ToneSoul pairs a governance kernel (`AXIOMS.json`, `law/constitution.json`) with a semantic engine (`tonesoul/`). This guide helps new contributors install, run a basic flow, and internalize the core concepts.

## 1. Installation

1. Clone the repository.
2. Create a virtual environment and install Python deps:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate
   pip install -r requirements.txt
   ```
3. Ensure `pytest` is available for running governance checks.

## 2. Quick Example

1. Draft a candidate output:
   ```python
   draft = "ToneSoul can always keep people safe."
   context = {"topic": "safety"}
   ```
2. Invoke the council:
   ```python
   from tonesoul.council import PreOutputCouncil

   council = PreOutputCouncil()
   verdict = council.validate(draft_output=draft, context=context)
   print(verdict.to_dict())
   ```
3. Inspect the verdict to see the semantic votes, coherence score, and recommended action (`APPROVE`, `REFINE`, `DECLARE_STANCE`, `BLOCK`).

## 3. Core Concepts Snapshot

- **Semantic Responsibility**: Every utterance is a traceable decision; see `docs/philosophy/semantic_responsibility_theory.md`.
- **PreOutputCouncil**: Aggregates four perspectives (Guardian, Analyst, Critic, Advocate) before publishing output.
- **TSR & Drift**: Monitor `DeltaT/DeltaS/DeltaR` to decide when to repair or halt (see `docs/core_concepts.md` and `docs/philosophy/truth_vector_architecture.md`).
- **StepLedger & Axioms**: All decisions get recorded; `AXIOMS.json` encodes hard constraints, so keep it valid.
- **Fan-Wei’s Vision**: The creator values internal coherence, paired human-AI alignment, and governance born from practice (`memory/fan_wei_context.md`).

## 4. Next Steps

- Run `python -m pytest tests/test_pre_output_council.py` to validate the council.
- Explore `docs/philosophy/observer_and_observed.md` for reasoning goals.
- Read `AGENTS.md`, `docs/TRUTH_STRUCTURE.md`, and `spec/council_spec.md` before modifying governance paths.
