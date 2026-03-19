"""
Stimulus processing for environmental input.

This layer filters raw web or environment ingestion into memory-ready
stimuli. Not every external signal should be stored; only the ones that
show relevance, surprise, or resonance with ToneSoul's ongoing concerns.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

VALID_OBSERVATION_MODES = {
    "remote_feed",
    "simulated",
    "interactive",
    "sensor",
    "embodied",
}


def _normalize_observation_mode(value: object) -> str:
    text = str(value or "").strip().lower()
    if text in VALID_OBSERVATION_MODES:
        return text
    return "remote_feed"


@dataclass
class EnvironmentStimulus:
    """A processed environmental signal ready for memory integration."""

    source_url: str
    topic: str
    summary: str
    content_hash: str
    ingested_at: str
    relevance_score: float = 0.0
    novelty_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    raw_excerpt: str = ""
    observation_mode: str = "remote_feed"

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
            "observation_mode": _normalize_observation_mode(self.observation_mode),
        }


class StimulusProcessor:
    """
    Process raw ingestion results into environmental stimuli.

    The processor applies three filters:
      1. Deduplication via content hash.
      2. Relevance scoring via keyword overlap.
      3. Novelty scoring via simple structural heuristics.
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
        self._seen_hashes: set[str] = set()
        self._relevance_keywords = relevance_keywords or [
            "governance",
            "alignment",
            "safety",
            "ethics",
            "agent",
            "memory",
            "consciousness",
            "self-awareness",
            "autonomy",
            "pipeline",
            "architecture",
            "microservice",
            "monolith",
            "refactor",
            "api",
            "schema",
            "database",
            "tension",
            "commitment",
            "rupture",
            "deliberation",
            "council",
            "persona",
            "semantic",
            "narrative",
            "治理",
            "對齊",
            "安全",
            "倫理",
            "代理",
            "記憶",
            "意識",
            "自主",
            "架構",
            "管線",
            "張力",
            "承諾",
            "破裂",
            "審議",
            "議會",
            "人格",
            "語義",
            "敘事",
            "哲學",
        ]

    def process_ingested(self, ingest_results: List[Any]) -> List[EnvironmentStimulus]:
        """
        Process a batch of IngestResults into environmental stimuli.

        Args:
            ingest_results: List of IngestResult from WebIngestor.

        Returns:
            Filtered and scored EnvironmentStimulus records.
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
                content_hash = hashlib.sha256(result.markdown.encode("utf-8")).hexdigest()[:16]

            if content_hash in self._seen_hashes:
                continue
            self._seen_hashes.add(content_hash)

            title = getattr(result, "title", "") or ""
            markdown = getattr(result, "markdown", "") or ""

            stimulus = EnvironmentStimulus(
                source_url=getattr(result, "url", ""),
                topic=self._extract_topic(title, markdown),
                summary=self._extract_summary(markdown),
                content_hash=content_hash,
                ingested_at=getattr(
                    result,
                    "ingested_at",
                    datetime.now(timezone.utc).isoformat(),
                ),
                relevance_score=self._score_relevance(markdown, title),
                novelty_score=self._score_novelty(markdown),
                tags=self._extract_tags(markdown, title),
                raw_excerpt=markdown[: self._max_excerpt_length],
                observation_mode="remote_feed",
            )
            stimuli.append(stimulus)

        return stimuli

    def _extract_topic(self, title: str, markdown: str) -> str:
        """Extract a topic label from title or first heading."""
        if title and len(title.strip()) > 3:
            return title.strip()[:100]

        heading_match = re.search(r"^#+ (.+)$", markdown, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()[:100]

        first_line = markdown.strip().split("\n")[0]
        return first_line[:100] if first_line else "untitled"

    def _score_relevance(self, markdown: str, title: str) -> float:
        """Score how relevant the content is to ToneSoul's interests."""
        text = f"{title} {markdown}".lower()
        hits = 0
        for keyword in self._relevance_keywords:
            if keyword.lower() in text:
                hits += 1

        if not self._relevance_keywords:
            return 0.0
        ratio = hits / len(self._relevance_keywords)
        return min(1.0, ratio**0.5)

    def _score_novelty(self, markdown: str) -> float:
        """
        Rough novelty score based on content characteristics.

        Future: compare against existing semantic graph embeddings.
        """
        word_count = len(markdown.split())

        if word_count < 100:
            return 0.2

        code_blocks = len(re.findall(r"```", markdown))
        has_code = code_blocks >= 2
        has_structure = bool(re.search(r"^[-*] ", markdown, re.MULTILINE))

        score = 0.3
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
            "governance": ["governance", "治理", "alignment", "對齊", "safety", "安全"],
            "memory": ["memory", "記憶", "remember", "recall"],
            "architecture": ["architecture", "架構", "refactor", "pipeline", "管線"],
            "philosophy": ["philosophy", "consciousness", "ethics", "哲學", "意識"],
            "engineering": ["code", "programming", "github", "open source", "工程"],
        }

        for tag, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    tags.append(tag)
                    break

        return tags
