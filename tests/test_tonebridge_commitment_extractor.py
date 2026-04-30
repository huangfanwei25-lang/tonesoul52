"""Tests for tonesoul.tonebridge.commitment_extractor — pure helpers."""

from __future__ import annotations

import pytest

from tonesoul.tonebridge.commitment_extractor import (
    CommitmentExtractor,
    CommitmentStructure,
    create_commitment_extractor,
)

# ── CommitmentStructure.to_dict ───────────────────────────────────────────────


class TestCommitmentStructureToDict:
    def _make(self, **kw) -> CommitmentStructure:
        defaults = {
            "raw_text": "I will complete the task.",
            "core_verbs": ["will", "complete"],
            "core_nouns": ["task"],
            "commitment_type": "commitment",
            "confidence": 0.85,
            "temporal_weight": 0.75,
            "extracted_commitment": "I will complete the task.",
        }
        defaults.update(kw)
        return CommitmentStructure(**defaults)

    def test_to_dict_has_all_keys(self):
        d = self._make().to_dict()
        assert "raw_text" in d
        assert "core_verbs" in d
        assert "core_nouns" in d
        assert "commitment_type" in d
        assert "confidence" in d
        assert "temporal_weight" in d
        assert "extracted_commitment" in d

    def test_raw_text_truncated_to_100(self):
        long_text = "x" * 200
        d = self._make(raw_text=long_text).to_dict()
        assert len(d["raw_text"]) == 100

    def test_short_text_not_truncated(self):
        d = self._make(raw_text="short").to_dict()
        assert d["raw_text"] == "short"

    def test_confidence_preserved(self):
        d = self._make(confidence=0.42).to_dict()
        assert d["confidence"] == pytest.approx(0.42)


# ── CommitmentExtractor._calculate_temporal_weight ────────────────────────────


class TestCalculateTemporalWeight:
    def setup_method(self):
        self.extractor = CommitmentExtractor()

    def test_zero_total_turns_returns_one(self):
        assert self.extractor._calculate_temporal_weight(0, 0) == pytest.approx(1.0)

    def test_last_turn_highest_weight(self):
        w_last = self.extractor._calculate_temporal_weight(9, 10)
        w_first = self.extractor._calculate_temporal_weight(0, 10)
        assert w_last > w_first

    def test_first_turn_weight(self):
        w = self.extractor._calculate_temporal_weight(0, 10)
        assert w == pytest.approx(0.5 + 0.5 * (1 / 10))

    def test_only_turn_has_full_weight(self):
        w = self.extractor._calculate_temporal_weight(0, 1)
        assert w == pytest.approx(1.0)

    def test_range_is_0_5_to_1(self):
        for turn in range(10):
            w = self.extractor._calculate_temporal_weight(turn, 10)
            assert 0.5 <= w <= 1.0


# ── CommitmentExtractor._classify_commitment_type ────────────────────────────


class TestClassifyCommitmentType:
    def setup_method(self):
        self.extractor = CommitmentExtractor()

    def test_boundary_verb_gives_boundary(self):
        ctype, conf = self.extractor._classify_commitment_type(["不會", "做"], ["事"])
        assert ctype == "boundary"
        assert conf == pytest.approx(0.9)

    def test_commitment_verb_gives_commitment(self):
        ctype, conf = self.extractor._classify_commitment_type(["會", "完成"], ["任務"])
        assert ctype == "commitment"
        assert conf == pytest.approx(0.85)

    def test_definitional_verb_gives_definitional(self):
        ctype, conf = self.extractor._classify_commitment_type(["是", "認為"], ["觀點"])
        assert ctype == "definitional"
        assert conf == pytest.approx(0.7)

    def test_exploratory_verb_gives_exploratory(self):
        ctype, conf = self.extractor._classify_commitment_type(["也許", "嘗試"], ["方向"])
        assert ctype == "exploratory"
        assert conf == pytest.approx(0.4)

    def test_high_weight_noun_gives_definitional(self):
        ctype, conf = self.extractor._classify_commitment_type([], ["承諾"])
        assert ctype == "definitional"
        assert conf == pytest.approx(0.6)

    def test_no_match_gives_none_type(self):
        ctype, conf = self.extractor._classify_commitment_type(["跑", "走"], ["貓"])
        assert ctype == "none"
        assert conf == pytest.approx(0.2)

    def test_boundary_takes_priority_over_commitment(self):
        ctype, _ = self.extractor._classify_commitment_type(["不會", "會"], [])
        assert ctype == "boundary"


# ── CommitmentExtractor._build_core_commitment ───────────────────────────────


class TestBuildCoreCommitment:
    def setup_method(self):
        self.extractor = CommitmentExtractor()

    def test_finds_sentence_with_commitment_verb(self):
        text = "我會繼續工作。也許需要更多時間。"
        result = self.extractor._build_core_commitment(text, ["會"], ["工作"])
        assert "會" in result

    def test_fallback_to_nouns(self):
        text = "simple text with no special verbs here."
        result = self.extractor._build_core_commitment(text, [], ["主題"])
        assert "主題" in result

    def test_fallback_to_text_slice_when_no_nouns(self):
        text = "x" * 100
        result = self.extractor._build_core_commitment(text, [], [])
        assert len(result) <= 50

    def test_sentence_truncated_to_80(self):
        long_sentence = "我會" + "x" * 100
        result = self.extractor._build_core_commitment(long_sentence, ["會"], [])
        assert len(result) <= 80


# ── CommitmentExtractor._extract_verbs / _extract_nouns ──────────────────────


class TestExtractVerbsNouns:
    def setup_method(self):
        self.extractor = CommitmentExtractor()

    def test_extract_verbs_from_segments(self):
        segments = [("run", "v"), ("fast", "a"), ("jump", "vd"), ("here", "r")]
        verbs = self.extractor._extract_verbs(segments)
        assert "run" in verbs
        assert "jump" in verbs
        assert "fast" not in verbs

    def test_extract_nouns_from_segments(self):
        segments = [("cat", "n"), ("run", "v"), ("dog", "nr"), ("park", "ns")]
        nouns = self.extractor._extract_nouns(segments)
        assert "cat" in nouns
        assert "dog" in nouns
        assert "park" in nouns
        assert "run" not in nouns

    def test_empty_segments_gives_empty_lists(self):
        assert self.extractor._extract_verbs([]) == []
        assert self.extractor._extract_nouns([]) == []


# ── CommitmentExtractor._segment (jieba not available fallback) ───────────────


class TestSegmentFallback:
    def test_no_jieba_returns_empty(self, monkeypatch):
        import tonesoul.tonebridge.commitment_extractor as mod

        monkeypatch.setattr(mod, "JIEBA_AVAILABLE", False)
        extractor = CommitmentExtractor()
        result = extractor._segment("test text")
        assert result == []


# ── CommitmentExtractor.extract ───────────────────────────────────────────────


class TestExtract:
    def setup_method(self):
        self.extractor = CommitmentExtractor()

    def test_short_text_returns_none_type(self):
        result = self.extractor.extract("hi")
        assert result.commitment_type == "none"
        assert result.confidence == 0.0
        assert result.core_verbs == []
        assert result.core_nouns == []

    def test_empty_text_returns_none_type(self):
        result = self.extractor.extract("")
        assert result.commitment_type == "none"

    def test_result_has_correct_temporal_weight(self):
        result = self.extractor.extract(
            "Some longer text here for testing.", turn_index=4, total_turns=5
        )
        assert result.temporal_weight == pytest.approx(1.0)

    def test_result_is_commitment_structure(self):
        result = self.extractor.extract("I will complete the task fully.")
        assert isinstance(result, CommitmentStructure)

    def test_raw_text_preserved(self):
        text = "This is a longer test text for extraction."
        result = self.extractor.extract(text)
        assert result.raw_text == text

    def test_verbs_limited_to_10(self, monkeypatch):
        import tonesoul.tonebridge.commitment_extractor as mod

        monkeypatch.setattr(mod, "JIEBA_AVAILABLE", True)

        fake_segments = [(f"v{i}", "v") for i in range(20)]

        def _fake_segment(self_inner, text):
            return fake_segments

        monkeypatch.setattr(CommitmentExtractor, "_segment", _fake_segment)
        result = self.extractor.extract("Some longer text for testing.")
        assert len(result.core_verbs) <= 10

    def test_nouns_limited_to_10(self, monkeypatch):
        import tonesoul.tonebridge.commitment_extractor as mod

        monkeypatch.setattr(mod, "JIEBA_AVAILABLE", True)

        fake_segments = [(f"n{i}", "n") for i in range(20)]

        def _fake_segment(self_inner, text):
            return fake_segments

        monkeypatch.setattr(CommitmentExtractor, "_segment", _fake_segment)
        result = self.extractor.extract("Some longer text for testing.")
        assert len(result.core_nouns) <= 10


# ── create_commitment_extractor factory ───────────────────────────────────────


class TestFactory:
    def test_returns_extractor_instance(self):
        extractor = create_commitment_extractor()
        assert isinstance(extractor, CommitmentExtractor)
