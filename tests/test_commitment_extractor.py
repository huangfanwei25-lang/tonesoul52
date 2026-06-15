from __future__ import annotations

import pytest

from tonesoul.tonebridge.commitment_extractor import (
    CommitmentExtractor,
    CommitmentStructure,
    create_commitment_extractor,
)


@pytest.fixture
def extractor():
    return CommitmentExtractor()


# ─── CommitmentStructure.to_dict ─────────────────────────────────────────────


class TestCommitmentStructureToDict:
    def test_returns_required_keys(self):
        cs = CommitmentStructure(
            raw_text="hello",
            core_verbs=["run"],
            core_nouns=["task"],
            commitment_type="commitment",
            confidence=0.85,
            temporal_weight=1.0,
            extracted_commitment="run task",
        )
        d = cs.to_dict()
        for key in (
            "raw_text",
            "core_verbs",
            "core_nouns",
            "commitment_type",
            "confidence",
            "temporal_weight",
            "extracted_commitment",
        ):
            assert key in d

    def test_raw_text_truncated_to_100(self):
        long_text = "x" * 200
        cs = CommitmentStructure(
            raw_text=long_text,
            core_verbs=[],
            core_nouns=[],
            commitment_type="none",
            confidence=0.2,
            temporal_weight=1.0,
            extracted_commitment="",
        )
        assert len(cs.to_dict()["raw_text"]) == 100

    def test_short_text_not_truncated(self):
        cs = CommitmentStructure(
            raw_text="short",
            core_verbs=[],
            core_nouns=[],
            commitment_type="none",
            confidence=0.2,
            temporal_weight=1.0,
            extracted_commitment="",
        )
        assert cs.to_dict()["raw_text"] == "short"


# ─── _calculate_temporal_weight ──────────────────────────────────────────────


class TestCalculateTemporalWeight:
    def test_zero_total_turns_returns_1(self, extractor):
        assert extractor._calculate_temporal_weight(0, 0) == 1.0

    def test_negative_total_turns_returns_1(self, extractor):
        assert extractor._calculate_temporal_weight(0, -5) == 1.0

    def test_first_of_one_returns_1(self, extractor):
        assert extractor._calculate_temporal_weight(0, 1) == 1.0

    def test_first_of_two_returns_0_75(self, extractor):
        # recency = 1/2 = 0.5; result = 0.5 + 0.5*0.5 = 0.75
        assert extractor._calculate_temporal_weight(0, 2) == 0.75

    def test_last_of_two_returns_1(self, extractor):
        # recency = 2/2 = 1.0; result = 0.5 + 0.5*1.0 = 1.0
        assert extractor._calculate_temporal_weight(1, 2) == 1.0

    def test_earlier_turns_lower_than_later(self, extractor):
        w_early = extractor._calculate_temporal_weight(0, 5)
        w_late = extractor._calculate_temporal_weight(4, 5)
        assert w_early < w_late


# ─── _extract_verbs / _extract_nouns ─────────────────────────────────────────


class TestExtractVerbs:
    def test_v_flag_extracted(self, extractor):
        segments = [("run", "v"), ("fast", "ad")]
        assert extractor._extract_verbs(segments) == ["run"]

    def test_vd_flag_extracted(self, extractor):
        assert "jumped" in extractor._extract_verbs([("jumped", "vd"), ("now", "t")])

    def test_vn_flag_extracted(self, extractor):
        assert "thinking" in extractor._extract_verbs([("thinking", "vn")])

    def test_d_flag_extracted(self, extractor):
        assert "very" in extractor._extract_verbs([("very", "d")])

    def test_p_flag_extracted(self, extractor):
        assert "from" in extractor._extract_verbs([("from", "p")])

    def test_non_verb_excluded(self, extractor):
        assert extractor._extract_verbs([("apple", "n"), ("big", "a")]) == []


class TestExtractNouns:
    def test_n_flag_extracted(self, extractor):
        assert "plan" in extractor._extract_nouns([("plan", "n")])

    def test_nr_flag_extracted(self, extractor):
        assert "Alice" in extractor._extract_nouns([("Alice", "nr")])

    def test_ns_flag_excluded_note_ns_starts_with_n(self, extractor):
        # ns starts with "n" so location nouns ARE included
        assert "Beijing" in extractor._extract_nouns([("Beijing", "ns")])

    def test_verb_excluded(self, extractor):
        assert extractor._extract_nouns([("run", "v"), ("task", "n")]) == ["task"]


# ─── _classify_commitment_type ───────────────────────────────────────────────


class TestClassifyCommitmentType:
    def test_boundary_verb_returns_boundary(self, extractor):
        ctype, conf = extractor._classify_commitment_type(["不會", "提供"], ["建議"])
        assert ctype == "boundary"
        assert conf == 0.9

    def test_boundary_takes_priority_over_commitment(self, extractor):
        ctype, _ = extractor._classify_commitment_type(["會", "不會"], [])
        assert ctype == "boundary"

    def test_commitment_verb_returns_commitment(self, extractor):
        ctype, conf = extractor._classify_commitment_type(["會", "完成"], ["任務"])
        assert ctype == "commitment"
        assert conf == 0.85

    def test_definitional_verb_returns_definitional(self, extractor):
        ctype, conf = extractor._classify_commitment_type(["是", "代表"], [])
        assert ctype == "definitional"
        assert conf == 0.7

    def test_exploratory_verb_returns_exploratory(self, extractor):
        ctype, conf = extractor._classify_commitment_type(["也許", "嘗試"], [])
        assert ctype == "exploratory"
        assert conf == 0.4

    def test_high_weight_noun_fallback_definitional(self, extractor):
        ctype, conf = extractor._classify_commitment_type([], ["承諾", "意義"])
        assert ctype == "definitional"
        assert conf == 0.6

    def test_no_matches_returns_none(self, extractor):
        ctype, conf = extractor._classify_commitment_type(["走", "說"], ["蘋果"])
        assert ctype == "none"
        assert conf == 0.2


# ─── _build_core_commitment ──────────────────────────────────────────────────


class TestBuildCoreCommitment:
    def test_sentence_with_commitment_verb_returned(self, extractor):
        text = "我會完成這個任務。請繼續。"
        result = extractor._build_core_commitment(text, ["會"], ["任務"])
        assert "會" in result or "任務" in result

    def test_fallback_to_nouns_when_no_verb_matches(self, extractor):
        text = "這是一段沒有承諾動詞的文字內容。"
        result = extractor._build_core_commitment(text, [], ["主題", "內容"])
        assert "主題" in result or "內容" in result

    def test_fallback_to_text_when_no_nouns(self, extractor):
        text = "plain english sentence without any matching words here."
        result = extractor._build_core_commitment(text, [], [])
        assert result == text[:50]

    def test_long_sentence_truncated_to_80(self, extractor):
        long_sentence = "我會" + "x" * 100 + "。"
        result = extractor._build_core_commitment(long_sentence, ["會"], [])
        assert len(result) <= 80


# ─── extract (main method) ───────────────────────────────────────────────────


class TestExtract:
    def test_empty_text_returns_none_type(self, extractor):
        result = extractor.extract("")
        assert result.commitment_type == "none"
        assert result.confidence == 0.0

    def test_short_text_returns_none_type(self, extractor):
        result = extractor.extract("hi")
        assert result.commitment_type == "none"
        assert result.confidence == 0.0

    def test_result_has_all_fields(self, extractor):
        result = extractor.extract("這是一段測試文字，用於驗證輸出結構。")
        for attr in (
            "raw_text",
            "core_verbs",
            "core_nouns",
            "commitment_type",
            "confidence",
            "temporal_weight",
            "extracted_commitment",
        ):
            assert hasattr(result, attr)

    def test_raw_text_preserved(self, extractor):
        text = "這是一段足夠長的測試文字，用於驗證 raw_text 保留。"
        result = extractor.extract(text)
        assert result.raw_text == text

    def test_temporal_weight_applied(self, extractor):
        text = "這是一段足夠長的測試文字，用於驗證時間權重計算是否正確。"
        r0 = extractor.extract(text, turn_index=0, total_turns=3)
        r2 = extractor.extract(text, turn_index=2, total_turns=3)
        assert r2.temporal_weight > r0.temporal_weight

    def test_core_verbs_capped_at_10(self, extractor):
        result = extractor.extract("這是一段足夠長的測試文字，用於驗證動詞列表長度限制。")
        assert len(result.core_verbs) <= 10

    def test_core_nouns_capped_at_10(self, extractor):
        result = extractor.extract("這是一段足夠長的測試文字，用於驗證名詞列表長度限制。")
        assert len(result.core_nouns) <= 10


# ─── factory ─────────────────────────────────────────────────────────────────


class TestCreateCommitmentExtractor:
    def test_returns_extractor_instance(self):
        assert isinstance(create_commitment_extractor(), CommitmentExtractor)
