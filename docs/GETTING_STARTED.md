# Getting Started with ToneSoul

> Purpose: quickstart guide for installing ToneSoul, running a basic governance flow, and learning the core concepts.
> Last Updated: 2026-03-23

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

## 5. Governance Runtime Adapter (AI Self-Governance)

ToneSoul includes a lightweight runtime adapter that lets AI agents persist governance state across conversations — tension history, vows, vetoes, and personality drift.

### Quick Setup

```bash
# 1. Initialize governance state
python scripts/init_governance_state.py --output ./governance_state.json

# 2. Read current governance posture
python scripts/read_governance_state.py

# 3. After a session, update state from a trace file
python scripts/update_governance_state.py \
  --state ./governance_state.json \
  --trace session_trace.json

# 4. (Optional) Commit summary to OpenClaw-Memory
python scripts/commit_session_to_memory.py \
  --trace session_trace.json \
  --openclaw-dir ./OpenClaw-Memory
```

### What Gets Tracked

| Field | Description |
|-------|-------------|
| `soul_integral` | Cumulative tension with exponential decay (`e^(-0.05 × hours)`) |
| `tension_history` | Recent viewpoint collisions and their resolutions |
| `active_vows` | Commitments the AI has made and must uphold |
| `aegis_vetoes` | Safety boundary activations |
| `baseline_drift` | Slow personality evolution (caution, innovation, autonomy biases) |

### Session Trace Format

Create a JSON file with your session's governance events:

```json
{
  "session_id": "unique-id",
  "agent": "your-agent-name",
  "timestamp": "2026-03-24T07:00:00+08:00",
  "tension_events": [
    {
      "topic": "what viewpoints collided",
      "severity": 0.5,
      "resolution": "how it was resolved"
    }
  ],
  "key_decisions": ["decision 1", "decision 2"],
  "vow_events": [],
  "aegis_vetoes": []
}
```

### Integration with OpenClaw-Memory

The adapter bridges to [OpenClaw-Memory](https://github.com/Fan1234-1/OpenClaw-Memory) for tension-aware retrieval:

```bash
# Query with governance context
python OpenClaw-Memory/ask_my_brain.py --profile tonesoul \
  "deployment policy" --query-tension 0.8 --top-k 3
```

See `docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md` for the full technical contract.
See `memory/schemas/` for JSON Schema definitions.

### Importing External Conversations

Already have AI conversations in ChatGPT, Claude, or other tools? Import them:

```bash
# Import a ChatGPT export (auto-detects .json)
python scripts/import_conversation.py --input conversations.json --dry-run

# Import a markdown conversation log
python scripts/import_conversation.py --input chat.md --output traces/

# Import and directly update governance state
python scripts/import_conversation.py \
  --input conversations.json \
  --update-state ./governance_state.json
```

The importer extracts tension events, key decisions, stance shifts, and vow-like commitments from your conversation history using heuristic scoring.

### Soul Profiles

Customize your AI's starting personality with soul profiles:

```bash
# List available profiles
ls memory/profiles/

# Initialize with a specific profile
python scripts/init_governance_state.py \
  --profile creative-explorer \
  --output ./governance_state.json
```

Available presets: `default`, `cautious-guardian`, `creative-explorer`.
Create your own by copying and editing any `.soul.json` in `memory/profiles/`.

