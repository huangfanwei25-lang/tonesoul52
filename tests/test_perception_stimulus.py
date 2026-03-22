from types import SimpleNamespace

from tonesoul.perception.stimulus import (
    EnvironmentStimulus,
    StimulusProcessor,
    _normalize_observation_mode,
)


def test_normalize_observation_mode_accepts_known_and_unknown_values():
    assert _normalize_observation_mode(" sensor ") == "sensor"
    assert _normalize_observation_mode("SATELLITE") == "remote_feed"
    assert _normalize_observation_mode(None) == "remote_feed"


def test_extract_topic_prefers_heading_then_first_line():
    processor = StimulusProcessor(min_word_count=1)

    assert processor._extract_topic("", "# Architecture Review\nbody") == "Architecture Review"
    assert processor._extract_topic("", "First line only\nSecond line") == "First line only"


def test_extract_summary_skips_heading_images_and_rules():
    processor = StimulusProcessor(min_word_count=1)
    markdown = "\n".join(
        [
            "# Heading",
            "",
            "![diagram](https://example.com/diagram.png)",
            "---",
            "This is the first substantial paragraph worth keeping in the summary.",
            "Another line.",
        ]
    )

    summary = processor._extract_summary(markdown)

    assert summary == "This is the first substantial paragraph worth keeping in the summary."


def test_score_relevance_returns_zero_when_keywords_are_empty():
    processor = StimulusProcessor(min_word_count=1)
    processor._relevance_keywords = []

    assert processor._score_relevance("AI governance memory", "title") == 0.0


def test_score_novelty_distinguishes_short_and_structured_content():
    processor = StimulusProcessor(min_word_count=1)
    short_markdown = "word " * 50
    structured_markdown = (
        "word " * 120
    ) + "\n```py\nprint('x')\n```\n```py\nprint('y')\n```\n- item"

    assert processor._score_novelty(short_markdown) == 0.2
    assert processor._score_novelty(structured_markdown) == 0.8


def test_extract_tags_maps_multiple_domains():
    processor = StimulusProcessor(min_word_count=1)
    tags = processor._extract_tags(
        "AI governance memory architecture philosophy code github open source",
        "",
    )

    assert tags == [
        "ai",
        "governance",
        "memory",
        "architecture",
        "philosophy",
        "engineering",
    ]


def test_process_ingested_generates_hash_and_defaults():
    processor = StimulusProcessor(min_word_count=5, max_excerpt_length=25)
    markdown = "# Topic\n\nThis paragraph talks about governance, memory, and architecture. " * 3
    result = SimpleNamespace(
        url="https://example.com/post",
        title="",
        markdown=markdown,
        success=True,
        word_count=30,
    )

    stimuli = processor.process_ingested([result])

    assert len(stimuli) == 1
    stimulus = stimuli[0]
    assert stimulus.topic == "Topic"
    assert len(stimulus.content_hash) == 16
    assert stimulus.raw_excerpt == markdown[:25]
    assert stimulus.observation_mode == "remote_feed"
    assert stimulus.ingested_at


def test_environment_stimulus_payload_truncates_excerpt_and_preserves_valid_mode():
    stimulus = EnvironmentStimulus(
        source_url="https://example.com/post",
        topic="Topic",
        summary="Summary",
        content_hash="abc123",
        ingested_at="2026-03-20T00:00:00+00:00",
        raw_excerpt="x" * 800,
        observation_mode="sensor",
    )

    payload = stimulus.to_memory_payload()

    assert len(payload["raw_excerpt"]) == 500
    assert payload["observation_mode"] == "sensor"
