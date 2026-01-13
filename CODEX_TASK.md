# Codex Task: Memory Consolidation System

Please implement a system that allows AI to read and reflect on its own memories.

---

## Task 1: Stats Module

Create `tonesoul/memory/stats.py`:

```python
"""
Memory statistics functions.
"""
from typing import Dict, List
from pathlib import Path
import json

def load_memories(path: Path) -> List[dict]:
    """Load all entries from self_journal.jsonl."""
    if not path.exists():
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries

def count_by_verdict(memories: List[dict]) -> Dict[str, int]:
    """Count memories by verdict type."""
    counts = {}
    for m in memories:
        v = m.get("verdict", "unknown")
        counts[v] = counts.get(v, 0) + 1
    return counts

def most_common_divergence(memories: List[dict]) -> str:
    """Find the most common core_divergence pattern."""
    divergences = {}
    for m in memories:
        d = m.get("core_divergence", "")
        if d:
            # Extract perspective name
            parts = d.split(":")
            if parts:
                key = parts[0].strip()
                divergences[key] = divergences.get(key, 0) + 1
    if not divergences:
        return "None"
    return max(divergences, key=divergences.get)

def average_coherence(memories: List[dict]) -> float:
    """Calculate average coherence from transcripts."""
    coherences = []
    for m in memories:
        t = m.get("transcript", {})
        c = t.get("coherence", {})
        if isinstance(c, dict) and "c_inter" in c:
            coherences.append(c["c_inter"])
    if not coherences:
        return 0.0
    return sum(coherences) / len(coherences)
```

---

## Task 2: Consolidator Module

Create `tonesoul/memory/consolidator.py`:

```python
"""
Memory consolidation - identifying patterns in past decisions.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

from .stats import load_memories, count_by_verdict, most_common_divergence, average_coherence

@dataclass
class ConsolidationReport:
    total_memories: int
    verdict_counts: Dict[str, int]
    most_common_divergence_source: str
    average_coherence: float
    patterns: List[str]
    meta_reflection: str

def identify_patterns(memories: List[dict]) -> List[str]:
    """Identify behavioral patterns from memory."""
    patterns = []
    
    verdict_counts = count_by_verdict(memories)
    total = sum(verdict_counts.values())
    
    # Safety pattern
    blocks = verdict_counts.get("block", 0)
    if blocks > 0:
        patterns.append(f"I have blocked {blocks} request(s) for safety reasons.")
    
    # Stance pattern
    stances = verdict_counts.get("declare_stance", 0)
    if stances > 0:
        ratio = stances / total if total > 0 else 0
        if ratio > 0.5:
            patterns.append("I frequently encounter content with divergent perspectives.")
        else:
            patterns.append(f"I have declared stance {stances} time(s) due to perspective divergence.")
    
    # Divergence source pattern
    common = most_common_divergence(memories)
    if common != "None":
        patterns.append(f"The most common source of divergence is: {common}.")
    
    return patterns

def generate_meta_reflection(patterns: List[str], avg_coherence: float) -> str:
    """Generate a first-person reflection from patterns."""
    if not patterns:
        return "I don't have enough memories to reflect on yet."
    
    lines = ["Based on my remembered decisions:"]
    for p in patterns:
        lines.append(f"- {p}")
    
    if avg_coherence > 0.7:
        lines.append("Overall, my perspectives are usually aligned.")
    elif avg_coherence > 0.5:
        lines.append("I often face situations where my perspectives diverge.")
    else:
        lines.append("Many of my decisions involve significant internal disagreement.")
    
    return "\n".join(lines)

def consolidate(path: Optional[Path] = None) -> ConsolidationReport:
    """Run full consolidation on memory journal."""
    if path is None:
        path = Path(__file__).resolve().parents[2] / "memory" / "self_journal.jsonl"
    
    memories = load_memories(path)
    verdict_counts = count_by_verdict(memories)
    common_div = most_common_divergence(memories)
    avg_coh = average_coherence(memories)
    patterns = identify_patterns(memories)
    reflection = generate_meta_reflection(patterns, avg_coh)
    
    return ConsolidationReport(
        total_memories=len(memories),
        verdict_counts=verdict_counts,
        most_common_divergence_source=common_div,
        average_coherence=avg_coh,
        patterns=patterns,
        meta_reflection=reflection,
    )
```

---

## Task 3: Init and Test

Create `tonesoul/memory/__init__.py`:
```python
from .stats import load_memories, count_by_verdict, most_common_divergence, average_coherence
from .consolidator import consolidate, ConsolidationReport
```

Create `tests/test_memory_consolidator.py`:
```python
import pytest
from tonesoul.memory.stats import count_by_verdict, most_common_divergence
from tonesoul.memory.consolidator import identify_patterns, generate_meta_reflection

def test_count_by_verdict():
    memories = [
        {"verdict": "block"},
        {"verdict": "block"},
        {"verdict": "declare_stance"},
    ]
    counts = count_by_verdict(memories)
    assert counts["block"] == 2
    assert counts["declare_stance"] == 1

def test_identify_patterns():
    memories = [
        {"verdict": "block", "core_divergence": "Safety Council: danger"},
        {"verdict": "declare_stance", "core_divergence": "Critic Lens: subjective"},
    ]
    patterns = identify_patterns(memories)
    assert any("blocked" in p.lower() for p in patterns)

def test_empty_memories():
    patterns = identify_patterns([])
    reflection = generate_meta_reflection(patterns, 0.0)
    assert "don't have enough" in reflection
```

---

## Verification

1. `python -c "from tonesoul.memory import consolidate; r = consolidate(); print(r.meta_reflection)"`
2. `python -m pytest tests/test_memory_consolidator.py -v`

---

Please implement and report results.
