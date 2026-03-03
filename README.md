# ToneSoul / 語魂

> AI that does not just answer. It catches semantic drift, remembers what matters, and audits itself.
> If you want AI that won't make things up, start here.

[繁體中文](README.zh-TW.md)

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

## Numbers (Snapshot: 2026-03-03)

| Metric | Value |
|---|---|
| Tests passing | 1,156 |
| Journal entries | 11,242 |
| Active crystals | 3 |
| Resonance convergences | 28 |
| Flow detections | 39 |
| Repair events logged | 74 |
| Pipeline size (`unified_pipeline.py`) | 1,517 lines |
| Paradox fixtures | 7 |

## License

Apache-2.0
