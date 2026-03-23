# RFC-015: Self-Dogfooding Runtime Adapter

> **Status**: Canonical Draft v1.0
> **Authors**: Antigravity (Gemini), reviewed by Codex
> **Date**: 2026-03-23
> **Anchored by**: `docs/notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md`
> **Compatible with**: L7 Retrieval Contract, L8 Distillation Boundary, ABC Firewall Doctrine

---

## 1. Problem

ToneSoul is designed to give AI persistent governance state: tension, vows, vetoes, drift.

But the agents building ToneSoul (Antigravity, Codex) restart stateless every session.
They compensate by rereading `AGENTS.md` and KI files, but this is factual recall, not governance continuity.

**Gap**: no mechanism for developer agents to load prior governance posture at session start and write a session trace at session end.

---

## 2. Design Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | Observable shell, not latent-state intervention | We track externalized fields, not hidden model internals |
| 2 | Zero modification to `tonesoul/` core | Adapter lives alongside the engine, not inside it |
| 3 | State outside public repo | Dynamic state in local agent storage; only schemas are public |
| 4 | Incrementally useful | Each layer works independently |
| 5 | Narrow bridge to OpenClaw-Memory | Only safe summaries cross the boundary |

---

## 3. Architecture

```
Session Start
    |
    v
[1] Load governance_state.json (local agent storage)
[2] Query OpenClaw-Memory --profile tonesoul (optional)
[3] Read AGENTS.md + KI (static rules + knowledge)
    |
    v
--- conversation proceeds ---
    |
    v
[4] Produce session_trace record
    - tension events (which viewpoints collided)
    - vow triggers (committed / violated)
    - aegis vetoes
    - stance shifts
    |
    v
[5] Update governance_state.json
    - decay old tensions
    - update vow list
    - drift baseline
    |
    v
[6] Optionally inject safe summary into OpenClaw-Memory
```

---

## 4. Data Contracts

### 4.1 governance_state.json

**Location**: local agent storage (e.g. `~/.gemini/tonesoul/`, `~/.codex/memories/`)
**NOT** in the public repo. Only the JSON Schema is public.

```json
{
  "version": "0.1.0",
  "last_updated": "2026-03-23T21:30:00+08:00",
  "soul_integral": 0.42,
  "tension_history": [
    {
      "timestamp": "2026-03-23T21:30:00+08:00",
      "topic": "deploy safety vs speed",
      "severity": 0.75,
      "dominant_voice": "Aegis",
      "resolution": "Guardian veto"
    }
  ],
  "active_vows": [
    {
      "id": "vow-001",
      "content": "Do not commit personal memory data to public repo",
      "created": "2026-02-21",
      "source": "AGENTS.md"
    }
  ],
  "aegis_vetoes": [],
  "baseline_drift": {
    "caution_bias": 0.55,
    "innovation_bias": 0.62,
    "autonomy_level": 0.35
  },
  "session_count": 47
}
```

### 4.2 session_trace (append-only JSONL)

**Location**: local agent storage, one line per session.

```json
{
  "session_id": "970a6e54-00a8-4344-9947-90267fe8e9d3",
  "agent": "antigravity",
  "timestamp": "2026-03-23T21:30:00+08:00",
  "duration_minutes": 45,
  "tension_events": [
    {
      "topic": "SentiCore vs ToneSoul emotion model",
      "severity": 0.3,
      "type": "comparative_analysis",
      "resolution": "Preserve divergence"
    }
  ],
  "vow_events": [],
  "aegis_vetoes": [],
  "key_decisions": [
    "Analyzed ASMR/SentiCore/GameStudios architectures",
    "Decided to write RFC-015"
  ],
  "stance_shift": {
    "from": "ToneSoul too complex for self-use",
    "to": "ToneSoul self-usable with Runtime Adapter"
  }
}
```

---

## 5. Formulas

### 5.1 Tension Decay (at session start)

```
severity(t) = severity(t0) * e^(-alpha * hours_elapsed)
alpha = 0.05
prune if severity < 0.01
```

Matches ToneSoul core decay with `alpha = 0.15` per 10-turn unit,
scaled to `0.05` per hour for cross-session timescales.

### 5.2 Baseline Drift (at session end)

```
drift_rate = 0.001
bias_new = bias_old + drift_rate * (session_avg - bias_old)
```

Borrowed from SentiCore's 0.1%/turn model.
Applied per-session instead of per-turn to match conversation-level granularity.

### 5.3 Soul Integral Update

```
S_new = S_old * e^(-alpha * hours_since_last) + max_tension_this_session
```

---

## 6. Storage Boundary

| What | Where | Git-tracked |
|------|-------|-------------|
| JSON Schema definitions | `memory/schemas/` | Yes (public) |
| `init_governance_state.py` | `scripts/` | Yes (public) |
| `update_governance_state.py` | `scripts/` | Yes (public) |
| `commit_session_to_memory.py` | `scripts/` | Yes (public) |
| `governance_state.json` (data) | Local agent storage | No |
| `session_traces.jsonl` (data) | Local agent storage | No |
| OpenClaw-Memory summaries | `OpenClaw-Memory/memory_base/` | Gitignored |

This follows `MEMORY.md` public/private separation.

---

## 7. Implementation Phases

### Phase A: Schema + Init (minimum viable)

- [ ] `memory/schemas/governance_state.schema.json`
- [ ] `memory/schemas/session_trace.schema.json`
- [ ] `scripts/init_governance_state.py` -- generate initial state file
- [ ] Verify `.gitignore` excludes dynamic state files

### Phase B: Write-back Loop

- [ ] `scripts/update_governance_state.py` -- read trace, update state
- [ ] Tension decay calculation
- [ ] Baseline drift calculation
- [ ] Vow list reconciliation

### Phase C: OpenClaw-Memory Bridge

- [ ] `scripts/commit_session_to_memory.py` -- inject safe summary
- [ ] Integration test with `ask_my_brain.py --profile tonesoul`

### Phase D: Workflow Integration

- [ ] Add `.agent/workflows/session-end.md` workflow
- [ ] Add read-state step to `.agent/workflows/antigravity.md`
- [ ] Validate both Antigravity and Codex can read/write correctly

---

## 8. Constraints

Per the memory anchor, these constraints are non-negotiable:

1. Do not modify protected human-managed files to fake memory continuity
2. Do not store personal memory payloads in the public repo
3. Do not claim latent-state control over model internals
4. Do not bypass the L7 retrieval contract or L8 boundary contract
5. Do not let runtime-adapter language blur into philosophical overclaim

---

## 9. Success Criteria

The adapter is working when:

1. An agent starts a session and can read its prior `soul_integral`, `active_vows`, and `baseline_drift`
2. An agent ends a session and the state file reflects the conversation's tension events
3. Old tension events decay correctly across sessions separated by hours/days
4. A second agent (Codex after Antigravity, or vice versa) reads the same state file and inherits the governance posture
5. No dynamic state leaks into the public git history

---

*Canonical rewrite of the original draft. Clean UTF-8, no encoding damage.*
*Aligned with `TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md`.*
