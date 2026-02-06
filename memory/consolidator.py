"""
Memory Consolidator
==================

The "Sleep" mechanism for AI memory - transforms episodic memories
into semantic knowledge through periodic consolidation.

Biological Analogy:
- Sharp-wave ripples: Pattern extraction from episodes
- Hippocampus → Neocortex transfer: Episodic → Semantic
- Synaptic pruning: Low-value memory cleanup

Reference: Memory Consolidator Design (2026-02-05)
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import math

from memory.self_memory import load_recent_memory
from memory.semantic_memory import (
    SemanticMemory,
    SemanticFact,
    get_semantic_memory,
    add_semantic_fact,
)


# Consolidation tracking
CONSOLIDATION_TRACKER_PATH = Path(__file__).parent / ".consolidation_state.json"


class ConsolidationState:
    """Track consolidation progress to avoid re-processing."""
    
    def __init__(self):
        self.last_consolidated_timestamp: Optional[str] = None
        self.session_count: int = 0
        self.total_consolidated: int = 0
        self._load()
    
    def _load(self):
        if CONSOLIDATION_TRACKER_PATH.exists():
            try:
                with open(CONSOLIDATION_TRACKER_PATH, "r") as f:
                    data = json.load(f)
                    self.last_consolidated_timestamp = data.get("last_consolidated_timestamp")
                    self.session_count = data.get("session_count", 0)
                    self.total_consolidated = data.get("total_consolidated", 0)
            except:
                pass
    
    def save(self):
        with open(CONSOLIDATION_TRACKER_PATH, "w") as f:
            json.dump({
                "last_consolidated_timestamp": self.last_consolidated_timestamp,
                "session_count": self.session_count,
                "total_consolidated": self.total_consolidated,
            }, f)
    
    def increment_session(self):
        self.session_count += 1
        self.save()
    
    def should_consolidate(self, threshold: int = 10) -> bool:
        """Check if consolidation is due (every N sessions)."""
        return self.session_count >= threshold
    
    def mark_consolidated(self, timestamp: str, count: int):
        self.last_consolidated_timestamp = timestamp
        self.session_count = 0  # Reset counter
        self.total_consolidated += count
        self.save()


class MemoryConsolidator:
    """
    Transform episodic memories into semantic knowledge.
    
    This is the AI's "sleep" process - extracting patterns and
    forming long-term beliefs from accumulated experiences.
    """
    
    def __init__(
        self,
        semantic_memory: Optional[SemanticMemory] = None,
        min_episodes: int = 5,  # Minimum episodes needed for consolidation
    ):
        self.semantic_memory = semantic_memory or get_semantic_memory()
        self.min_episodes = min_episodes
        self.state = ConsolidationState()
    
    def consolidate(self, force: bool = False) -> Dict[str, Any]:
        """
        Run the consolidation process.
        
        Returns a summary of what was consolidated.
        """
        print("🌙 Initiating memory consolidation (AI sleep)...")
        
        # Load unconsolidated episodes
        episodes = self._load_unconsolidated_episodes()
        
        if len(episodes) < self.min_episodes and not force:
            return {
                "status": "skipped",
                "reason": f"Not enough episodes ({len(episodes)} < {self.min_episodes})",
                "episodes_found": len(episodes),
            }
        
        print(f"   Found {len(episodes)} episodes to consolidate...")
        
        # Phase 1: Extract patterns (Sharp-wave ripples)
        patterns = self._extract_patterns(episodes)
        print(f"   Extracted patterns from {len(patterns)} dimensions...")
        
        # Phase 2: Form semantic facts (Neocortex integration)
        new_facts = self._form_semantics(patterns)
        print(f"   Formed {len(new_facts)} semantic facts...")
        
        # Phase 3: Update semantic memory
        for fact in new_facts:
            self.semantic_memory.add(fact)
        
        # Phase 4: Mark consolidated
        if episodes:
            latest_timestamp = max(e.get("timestamp", "") for e in episodes)
            self.state.mark_consolidated(latest_timestamp, len(episodes))
        
        print("💤 Consolidation complete.")
        
        return {
            "status": "success",
            "episodes_processed": len(episodes),
            "patterns_found": len(patterns),
            "facts_formed": len(new_facts),
            "facts": [f.to_dict() for f in new_facts],
        }
    
    def _load_unconsolidated_episodes(self) -> List[Dict[str, Any]]:
        """Load episodes that haven't been consolidated yet."""
        # Load all recent episodes
        all_episodes = load_recent_memory(n=200)
        
        if not self.state.last_consolidated_timestamp:
            return all_episodes
        
        # Filter to only unconsolidated ones
        unconsolidated = [
            e for e in all_episodes
            if e.get("timestamp", "") > self.state.last_consolidated_timestamp
        ]
        
        return unconsolidated
    
    def _extract_patterns(self, episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract patterns from episodes.
        
        This is analogous to sharp-wave ripples during sleep -
        replaying and finding regularities in recent experiences.
        """
        patterns = {
            "platforms": Counter(),
            "submolts": Counter(),
            "verdicts": Counter(),
            "action_types": Counter(),
            "topics": Counter(),
            "hour_distribution": Counter(),
            "genesis": Counter(),
        }

        for episode in episodes:
            if episode.get("is_mine") is False:
                continue
            ctx = episode.get("context", {})
            
            # Platform patterns
            platform = ctx.get("platform")
            if platform:
                patterns["platforms"][platform] += 1
            
            # Submolt patterns
            submolt = ctx.get("submolt")
            if submolt:
                patterns["submolts"][submolt] += 1
            
            # Verdict patterns
            verdict = episode.get("verdict")
            if verdict:
                patterns["verdicts"][verdict] += 1

            genesis = episode.get("genesis") or "unknown"
            patterns["genesis"][genesis] += 1
            
            # Time patterns
            timestamp = episode.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    patterns["hour_distribution"][dt.hour] += 1
                except:
                    pass
            
            # Topic extraction from reflection
            reflection = episode.get("reflection", "")
            if reflection:
                # Simple keyword extraction
                for keyword in self._extract_keywords(reflection):
                    patterns["topics"][keyword] += 1
        
        return patterns
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple implementation - extract Chinese/English terms
        keywords = []
        
        # Platform/community names
        if "moltbook" in text.lower():
            keywords.append("Moltbook")
        if "github" in text.lower():
            keywords.append("GitHub")
        
        # Topic indicators
        topic_markers = ["AI", "治理", "governance", "哲學", "ethics", "龍蝦"]
        for marker in topic_markers:
            if marker.lower() in text.lower():
                keywords.append(marker)
        
        return keywords
    
    def _form_semantics(self, patterns: Dict[str, Any]) -> List[SemanticFact]:
        """
        Form semantic facts from patterns.
        
        This is the neocortex integration - transforming
        statistical patterns into declarative knowledge.
        """
        facts = []
        
        # Rule 1: Platform affinity
        total_platform = sum(patterns["platforms"].values())
        for platform, count in patterns["platforms"].most_common(3):
            if total_platform > 0:
                ratio = count / total_platform
                if ratio > 0.2:  # At least 20% activity
                    facts.append(SemanticFact(
                        fact=f"我是 {platform} 活躍用戶",
                        category="platform_affinity",
                        confidence=min(0.9, ratio + 0.3),
                        evidence_count=count,
                        metadata={"ratio": ratio},
                    ))
        
        # Rule 2: Submolt preferences
        for submolt, count in patterns["submolts"].most_common(3):
            if count >= 3:  # At least 3 posts
                facts.append(SemanticFact(
                    fact=f"我常在 m/{submolt} 發言",
                    category="submolt_preference",
                    confidence=0.5 + 0.1 * math.log(count + 1),
                    evidence_count=count,
                ))
        
        # Rule 3: Topic interests
        topic_counts = patterns["topics"]
        total_topics = sum(topic_counts.values())
        for topic, count in topic_counts.most_common(5):
            if total_topics > 0 and count >= 2:
                facts.append(SemanticFact(
                    fact=f"我對 {topic} 議題感興趣",
                    category="topic_interest",
                    confidence=min(0.85, 0.4 + 0.1 * count),
                    evidence_count=count,
                ))
        
        # Rule 4: Success patterns
        success_count = patterns["verdicts"].get("POST_SUCCESS", 0)
        total_verdicts = sum(patterns["verdicts"].values())
        if total_verdicts >= 5:
            success_rate = success_count / total_verdicts
            if success_rate > 0.8:
                facts.append(SemanticFact(
                    fact="我的內容通常通過 Council 審核",
                    category="behavior_pattern",
                    confidence=success_rate,
                    evidence_count=success_count,
                ))
        
        return facts
    
    def get_consolidation_summary(self) -> str:
        """Get a summary of the consolidation state."""
        lines = [
            "## 記憶固化狀態",
            "",
            f"- Session 計數: {self.state.session_count}",
            f"- 總共已固化: {self.state.total_consolidated} 條情節",
            f"- 上次固化: {self.state.last_consolidated_timestamp or '從未'}",
            "",
        ]
        
        if self.state.should_consolidate():
            lines.append("⚠️ **需要進行固化** (達到 session 閾值)")
        else:
            remaining = 10 - self.state.session_count
            lines.append(f"下次固化: 還需 {remaining} 個 session")
        
        return "\n".join(lines)


# ===== Convenience Functions =====

def check_and_consolidate(force: bool = False) -> Optional[Dict[str, Any]]:
    """
    Check if consolidation is needed and run it if so.
    
    Call this at the start of each session (Boot Protocol).
    """
    consolidator = MemoryConsolidator()
    consolidator.state.increment_session()
    
    if consolidator.state.should_consolidate() or force:
        return consolidator.consolidate(force=force)
    
    return None


def force_consolidate() -> Dict[str, Any]:
    """Force a consolidation regardless of session count."""
    return MemoryConsolidator().consolidate(force=True)


def get_consolidation_status() -> str:
    """Get the current consolidation status."""
    return MemoryConsolidator().get_consolidation_summary()


# ===== Demo =====

if __name__ == "__main__":
    print("🌙 Memory Consolidator Demo\n")
    
    # Show current state
    print(get_consolidation_status())
    
    print("\n" + "=" * 50 + "\n")
    
    # Force consolidation for demo
    result = force_consolidate()
    
    print("\n📊 Consolidation Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 50 + "\n")
    
    # Show semantic memory after consolidation
    from memory.semantic_memory import summarize_semantic
    print(summarize_semantic())
