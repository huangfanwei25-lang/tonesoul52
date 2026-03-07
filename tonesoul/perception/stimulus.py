"""
Stimulus Processing — filtering raw environmental input into meaningful memory.

This is the "意義篩選層" — the layer that decides which environmental
stimuli are worth remembering. Inspired by how human memory works:
not everything is stored, only what generates surprise, tension, or
resonance with existing knowledge.

Usage:
    from tonesoul.perception.stimulus import StimulusProcessor

    processor = StimulusProcessor()
    stimuli = processor.process_ingested([ingest_result_1, ingest_result_2])
    for s in stimuli:
        print(s.topic, s.relevance_score)

Author: Antigravity
Date: 2026-03-07
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class EnvironmentStimulus:
    """A processed environmental signal ready for memory integration."""

    source_url: str
    topic: str
    summary: str  # Compact summary of the stimulus content
    content_hash: str  # For dedup across sessions
    ingested_at: str
    relevance_score: float = 0.0  # 0-1, how relevant to existing memory
    novelty_score: float = 0.0  # 0-1, how novel compared to known knowledge
    tags: List[str] = field(default_factory=list)
    raw_excerpt: str = ""  # First N chars of raw content for reference

    def to_memory_payload(self) -> Dict[str, Any]:
        """Convert to a payload suitable for soul.db ingestion."""
        return {
            "type": "environment_stimulus",
            "source_url": self.source_url,
            "topic": self.topic,
            "summary": self.summary,
            "content_hash": self.content_hash,
            "ingested_at": self.ingested_at,
            "relevance_score": round(self.relevance_score, 4),
            "novelty_score": round(self.novelty_score, 4),
            "tags": self.tags,
            "raw_excerpt": self.raw_excerpt[:500],
        }


class StimulusProcessor:
    """
    Processes raw web ingestion results into environmental stimuli.

    The processor applies three filters:
      1. Deduplication (content hash check)
      2. Relevance scoring (topic overlap with existing memory keywords)
      3. Novelty scoring (how different from known content)

    Only stimuli above a threshold are promoted to memory.
    """

    def __init__(
        self,
        *,
        min_word_count: int = 50,
        max_excerpt_length: int = 500,
        relevance_keywords: Optional[List[str]] = None,
    ) -> None:
        self._min_word_count = min_word_count
        self._max_excerpt_length = max_excerpt_length
        self._seen_hashes: set = set()
        # Default relevance keywords — topics ToneSoul cares about
        self._relevance_keywords = relevance_keywords or [
            # AI governance & philosophy
            "governance", "alignment", "safety", "ethics", "agent",
            "memory", "consciousness", "self-awareness", "autonomy",
            # Technical architecture
            "pipeline", "architecture", "microservice", "monolith",
            "refactor", "api", "schema", "database",
            # ToneSoul-specific
            "tension", "commitment", "rupture", "deliberation",
            "council", "persona", "semantic", "narrative",
            # Chinese equivalents
            "治理", "記憶", "張力", "承諾", "斷裂", "議會",
            "架構", "語魂", "自主", "意識",
        ]

    def process_ingested(
        self,
        ingest_results: List[Any],
    ) -> List[EnvironmentStimulus]:
        """
        Process a batch of IngestResults into environmental stimuli.

        Args:
            ingest_results: List of IngestResult from WebIngestor.

        Returns:
            List of EnvironmentStimulus, filtered and scored.
        """
        stimuli: List[EnvironmentStimulus] = []

        for result in ingest_results:
            if not getattr(result, "success", False):
                continue
            if not getattr(result, "markdown", ""):
                continue

            word_count = getattr(result, "word_count", 0)
            if word_count < self._min_word_count:
                continue

            content_hash = getattr(result, "content_hash", "")
            if not content_hash:
                content_hash = hashlib.sha256(
                    result.markdown.encode("utf-8")
                ).hexdigest()[:16]

            # Dedup check
            if content_hash in self._seen_hashes:
                continue
            self._seen_hashes.add(content_hash)

            # Extract topic from title
            title = getattr(result, "title", "") or ""
            topic = self._extract_topic(title, result.markdown)

            # Score relevance
            relevance = self._score_relevance(result.markdown, title)

            # Score novelty (simple version — length-based surprise)
            novelty = self._score_novelty(result.markdown)

            # Build excerpt
            raw_excerpt = result.markdown[:self._max_excerpt_length]

            # Build summary (first meaningful paragraph)
            summary = self._extract_summary(result.markdown)

            # Build tags
            tags = self._extract_tags(result.markdown, title)

            stimulus = EnvironmentStimulus(
                source_url=getattr(result, "url", ""),
                topic=topic,
                summary=summary,
                content_hash=content_hash,
                ingested_at=getattr(
                    result,
                    "ingested_at",
                    datetime.now(timezone.utc).isoformat(),
                ),
                relevance_score=relevance,
                novelty_score=novelty,
                tags=tags,
                raw_excerpt=raw_excerpt,
            )
            stimuli.append(stimulus)

        return stimuli

    def _extract_topic(self, title: str, markdown: str) -> str:
        """Extract a topic label from title or first heading."""
        if title and len(title.strip()) > 3:
            return title.strip()[:100]

        # Try to find first heading in markdown
        heading_match = re.search(r"^#+ (.+)$", markdown, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()[:100]

        # Fallback: first sentence
        first_line = markdown.strip().split("\n")[0]
        return first_line[:100] if first_line else "untitled"

    def _score_relevance(self, markdown: str, title: str) -> float:
        """Score how relevant the content is to ToneSoul's interests."""
        text = f"{title} {markdown}".lower()
        hits = 0
        for keyword in self._relevance_keywords:
            if keyword.lower() in text:
                hits += 1

        # Normalize: 0-1 scale, with diminishing returns
        if not self._relevance_keywords:
            return 0.0
        ratio = hits / len(self._relevance_keywords)
        # Apply sqrt for diminishing returns (3 hits out of 30 ≈ 0.32)
        return min(1.0, ratio ** 0.5)

    def _score_novelty(self, markdown: str) -> float:
        """
        Rough novelty score based on content characteristics.

        Future: compare against existing semantic graph embeddings.
        """
        word_count = len(markdown.split())

        # Very short content = low novelty
        if word_count < 100:
            return 0.2

        # Check for code blocks (technical = higher novelty for us)
        code_blocks = len(re.findall(r"```", markdown))
        has_code = code_blocks >= 2

        # Check for structured content (lists, tables)
        has_structure = bool(re.search(r"^[-*] ", markdown, re.MULTILINE))

        score = 0.3  # base
        if has_code:
            score += 0.3
        if has_structure:
            score += 0.2
        if word_count > 500:
            score += 0.1
        if word_count > 1000:
            score += 0.1

        return min(1.0, score)

    def _extract_summary(self, markdown: str, max_length: int = 200) -> str:
        """Extract a compact summary from the first meaningful paragraph."""
        lines = markdown.strip().split("\n")
        for line in lines:
            stripped = line.strip()
            # Skip headings, empty lines, images
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("!["):
                continue
            if stripped.startswith("---"):
                continue
            if len(stripped) > 20:
                return stripped[:max_length]

        return markdown[:max_length] if markdown else ""

    def _extract_tags(self, markdown: str, title: str) -> List[str]:
        """Extract relevant tags from content."""
        text = f"{title} {markdown}".lower()
        tags: List[str] = []

        tag_keywords = {
            "ai": ["ai", "artificial intelligence", "machine learning", "llm"],
            "governance": ["governance", "治理", "alignment", "safety"],
            "memory": ["memory", "記憶", "remember", "recall"],
            "architecture": ["architecture", "架構", "refactor", "pipeline"],
            "philosophy": ["philosophy", "consciousness", "ethics", "意識"],
            "engineering": ["code", "programming", "github", "open source"],
        }

        for tag, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    tags.append(tag)
                    break

        return tags
