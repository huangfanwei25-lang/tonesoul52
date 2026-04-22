"""Tests for tonesoul.council.transcript."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from tonesoul.council.transcript import (
    CoherenceRecord,
    CouncilTranscript,
    CouncilTranscriptLogger,
    TranscriptFormat,
    VerdictRecord,
    VoteRecord,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

@dataclass
class _MockVote:
    perspective: str = "guardian"
    decision: object = None
    confidence: float = 0.88
    reasoning: str = "no safety concerns"

    def __post_init__(self):
        if self.decision is None:
            self.decision = _MockDecision("APPROVE")


@dataclass
class _MockDecision:
    name: str
    def __str__(self):
        return self.name


@dataclass
class _MockCoherence:
    c_inter: float = 0.82
    approval_rate: float = 0.75
    min_confidence: float = 0.70
    has_strong_objection: bool = False


@dataclass
class _MockVerdict:
    verdict: str = "approve"
    summary: str = "consensus achieved"
    consensus_points: list = None
    divergence_points: list = None
    risks_identified: list = None

    def __post_init__(self):
        self.consensus_points = self.consensus_points or []
        self.divergence_points = self.divergence_points or []
        self.risks_identified = self.risks_identified or []


def _logger(tmp_path=None) -> CouncilTranscriptLogger:
    if tmp_path:
        return CouncilTranscriptLogger(log_dir=tmp_path)
    return CouncilTranscriptLogger(log_dir=Path(tempfile.mkdtemp()))


def _make_transcript(logger=None, draft="The system processed your request."):
    lg = logger or _logger()
    return lg.create_transcript(
        draft_output=draft,
        context={"intent_id": "test"},
        user_intent="test intent",
        votes=[_MockVote(), _MockVote(perspective="analyst", confidence=0.75)],
        coherence=_MockCoherence(),
        verdict=_MockVerdict(),
    )


# ── VoteRecord ────────────────────────────────────────────────────────────────

class TestVoteRecord:
    def test_fields_set(self):
        r = VoteRecord(
            perspective_name="guardian",
            decision="APPROVE",
            confidence=0.9,
            reasoning="safe",
        )
        assert r.perspective_name == "guardian"
        assert r.decision == "APPROVE"
        assert r.confidence == 0.9

    def test_timestamp_auto_set(self):
        r = VoteRecord(perspective_name="x", decision="APPROVE", confidence=0.8, reasoning="")
        assert r.timestamp


# ── CoherenceRecord ───────────────────────────────────────────────────────────

class TestCoherenceRecord:
    def test_fields_set(self):
        r = CoherenceRecord(c_inter=0.8, approval_rate=0.75, min_confidence=0.7,
                            has_strong_objection=False)
        assert r.c_inter == 0.8
        assert r.has_strong_objection is False


# ── VerdictRecord ─────────────────────────────────────────────────────────────

class TestVerdictRecord:
    def test_fields_set(self):
        r = VerdictRecord(decision="APPROVE", summary="consensus")
        assert r.decision == "APPROVE"
        assert r.consensus_points == []
        assert r.divergence_points == []


# ── CouncilTranscript.to_json ─────────────────────────────────────────────────

class TestCouncilTranscriptToJson:
    def test_returns_valid_json(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert isinstance(parsed, dict)

    def test_json_has_transcript_id(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert "transcript_id" in parsed

    def test_json_has_votes(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert "votes" in parsed
        assert len(parsed["votes"]) == 2

    def test_json_has_coherence(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert "coherence" in parsed
        assert parsed["coherence"]["c_inter"] == pytest.approx(0.82)

    def test_json_has_verdict(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert "verdict" in parsed

    def test_json_has_input_hash(self):
        t = _make_transcript()
        parsed = json.loads(t.to_json())
        assert len(parsed["input_hash"]) == 64  # sha256 hex

    def test_different_inputs_different_hash(self):
        t1 = _make_transcript(draft="input A")
        t2 = _make_transcript(draft="input B")
        assert t1.input_hash != t2.input_hash

    def test_long_input_previewed(self):
        long_text = "x" * 200
        t = _make_transcript(draft=long_text)
        assert t.input_preview.endswith("...")
        assert len(t.input_preview) <= 103  # 100 + "..."

    def test_short_input_not_truncated(self):
        t = _make_transcript(draft="short")
        assert "..." not in t.input_preview

    def test_input_length_correct(self):
        draft = "exactly 30 chars long input!!"
        t = _make_transcript(draft=draft)
        assert t.input_length == len(draft)


# ── CouncilTranscript.to_markdown ─────────────────────────────────────────────

class TestCouncilTranscriptToMarkdown:
    def test_returns_string(self):
        t = _make_transcript()
        assert isinstance(t.to_markdown(), str)

    def test_contains_transcript_id(self):
        t = _make_transcript()
        assert t.transcript_id in t.to_markdown()

    def test_contains_perspective_names(self):
        t = _make_transcript()
        md = t.to_markdown()
        assert "guardian" in md.lower()

    def test_contains_verdict_section(self):
        t = _make_transcript()
        md = t.to_markdown()
        assert "Final Verdict" in md or "APPROVE" in md

    def test_contains_coherence_section(self):
        t = _make_transcript()
        md = t.to_markdown()
        assert "Coherence" in md or "0.82" in md

    def test_consensus_points_rendered(self):
        lg = _logger()
        v = _MockVerdict(consensus_points=["vows held", "no drift"])
        t = lg.create_transcript("draft", {}, None, [_MockVote()], _MockCoherence(), v)
        md = t.to_markdown()
        assert "vows held" in md

    def test_divergence_points_rendered(self):
        lg = _logger()
        v = _MockVerdict(divergence_points=["critic raised objection"])
        t = lg.create_transcript("draft", {}, None, [_MockVote()], _MockCoherence(), v)
        md = t.to_markdown()
        assert "critic raised objection" in md

    def test_risks_rendered(self):
        lg = _logger()
        v = _MockVerdict(risks_identified=["axiom 4 tension"])
        t = lg.create_transcript("draft", {}, None, [_MockVote()], _MockCoherence(), v)
        md = t.to_markdown()
        assert "axiom 4 tension" in md

    def test_processing_time_in_output(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [], None, None, processing_time_ms=42)
        md = t.to_markdown()
        assert "42" in md


# ── CouncilTranscriptLogger.create_transcript ─────────────────────────────────

class TestCouncilTranscriptLoggerCreate:
    def test_returns_council_transcript(self):
        t = _make_transcript()
        assert isinstance(t, CouncilTranscript)

    def test_transcript_id_unique(self):
        lg = _logger()
        t1 = _make_transcript(logger=lg)
        t2 = _make_transcript(logger=lg)
        assert t1.transcript_id != t2.transcript_id

    def test_vote_count_matches_input(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, None,
                                  [_MockVote(), _MockVote(), _MockVote()], None, None)
        assert len(t.votes) == 3

    def test_no_votes_gives_empty_list(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [], None, None)
        assert t.votes == []

    def test_no_coherence_gives_none(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [], None, None)
        assert t.coherence is None

    def test_no_verdict_gives_none(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [], None, None)
        assert t.verdict is None

    def test_user_intent_propagated(self):
        lg = _logger()
        t = lg.create_transcript("draft", {}, "find the drift", [], None, None)
        assert t.user_intent == "find the drift"

    def test_context_keys_extracted(self):
        lg = _logger()
        t = lg.create_transcript("draft", {"intent_id": "x", "evidence": [1, 2]}, None, [], None, None)
        assert "intent_id" in t.context_keys
        assert "evidence" in t.context_keys

    def test_perspective_type_enum_converted_to_string(self):
        from tonesoul.council.types import PerspectiveType, VoteDecision, PerspectiveVote
        vote = PerspectiveVote(
            perspective=PerspectiveType.GUARDIAN,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="safe",
        )
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [vote], None, None)
        assert t.votes[0].perspective_name == "guardian"

    def test_decision_enum_converted_to_string(self):
        from tonesoul.council.types import PerspectiveType, VoteDecision, PerspectiveVote
        vote = PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.CONCERN,
            confidence=0.6,
            reasoning="needs evidence",
        )
        lg = _logger()
        t = lg.create_transcript("draft", {}, None, [vote], None, None)
        assert t.votes[0].decision == "CONCERN"


# ── CouncilTranscriptLogger.save_transcript ───────────────────────────────────

class TestCouncilTranscriptLoggerSave:
    def test_save_json_creates_file(self, tmp_path):
        lg = CouncilTranscriptLogger(log_dir=tmp_path)
        t = _make_transcript(logger=lg)
        path = lg.save_transcript(t, format=TranscriptFormat.JSON)
        assert path.exists()
        assert path.suffix == ".json"

    def test_save_markdown_creates_file(self, tmp_path):
        lg = CouncilTranscriptLogger(log_dir=tmp_path)
        t = _make_transcript(logger=lg)
        path = lg.save_transcript(t, format=TranscriptFormat.MARKDOWN)
        assert path.exists()
        assert path.suffix == ".md"

    def test_saved_json_is_parseable(self, tmp_path):
        lg = CouncilTranscriptLogger(log_dir=tmp_path)
        t = _make_transcript(logger=lg)
        path = lg.save_transcript(t, format=TranscriptFormat.JSON)
        parsed = json.loads(path.read_text())
        assert "transcript_id" in parsed

    def test_saved_file_contains_vote_reasoning(self, tmp_path):
        lg = CouncilTranscriptLogger(log_dir=tmp_path)
        vote = _MockVote(reasoning="axiom confirmed")
        t = lg.create_transcript("draft", {}, None, [vote], _MockCoherence(), _MockVerdict())
        path = lg.save_transcript(t, format=TranscriptFormat.JSON)
        content = path.read_text()
        assert "axiom confirmed" in content

    def test_log_dir_created_automatically(self, tmp_path):
        new_dir = tmp_path / "nested" / "logs"
        lg = CouncilTranscriptLogger(log_dir=new_dir)
        assert new_dir.exists()
