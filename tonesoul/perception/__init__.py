"""
ToneSoul Perception Module — environmental input for AI subjectivity.

Provides the "eyes and ears" that allow the AI to receive environmental
stimuli rather than only responding to direct conversation.

Submodules:
  - web_ingest: Crawl4AI-based web content ingestion
  - stimulus: Environmental stimulus processing pipeline
"""

from .source_registry import CuratedSourceSelection, select_curated_registry_urls
from .stimulus import EnvironmentStimulus, StimulusProcessor

__all__ = [
    "CuratedSourceSelection",
    "EnvironmentStimulus",
    "StimulusProcessor",
    "select_curated_registry_urls",
]
