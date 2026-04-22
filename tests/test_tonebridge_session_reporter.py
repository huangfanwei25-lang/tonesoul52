"""Tests for tonesoul.tonebridge.session_reporter — pure helpers and SessionReporter."""
from __future__ import annotations

import pytest

from tonesoul.tonebridge.session_reporter import (
    SessionReporter,
    ThemeCluster,
    TurningPoint,
)


# ── TurningPoint.to_dict ──────────────────────────────────────────────────────

class TestTurningPointToDict:
    def test_all_keys_present(self):
        tp = TurningPoint(
            turn_index=3,
            description="shift",
            before_state="calm",
            after_state="frustrated",
            trigger="message",
            significance=0.8,
        )
        d = tp.to_dict()
        for key in ("turn_index", "description", "before_state", "after_state",
                    "trigger", "significance"):
            assert key in d

    def test_values_preserved(self):
        tp = TurningPoint(1, "desc", "calm", "excited", "trigger", 0.5)
        d = tp.to_dict()
        assert d["turn_index"] == 1
        assert d["significance"] == pytest.approx(0.5)


# ── ThemeCluster.to_dict ──────────────────────────────────────────────────────

class TestThemeClusterToDict:
    def test_all_keys_present(self):
        tc = ThemeCluster(
            name="技術問題", keywords=["程式", "代碼"], turn_count=3, emotional_tone="curious"
        )
        d = tc.to_dict()
        for key in ("name", "keywords", "turn_count", "emotional_tone"):
            assert key in d

    def test_keywords_is_list(self):
        tc = ThemeCluster(name="test", keywords=["a", "b"], turn_count=1, emotional_tone="calm")
        assert isinstance(tc.to_dict()["keywords"], list)


# ── SessionReporter._detect_emotion ──────────────────────────────────────────

class TestDetectEmotion:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_calm_keywords(self):
        assert self.reporter._detect_emotion("好，謝謝！") == "calm"

    def test_curious_keywords(self):
        assert self.reporter._detect_emotion("為什麼會這樣？") == "curious"

    def test_frustrated_keywords(self):
        assert self.reporter._detect_emotion("不是這樣的，但是...") == "frustrated"

    def test_neutral_when_no_keywords(self):
        assert self.reporter._detect_emotion("xyz abc 123") == "neutral"

    def test_empty_string_neutral(self):
        assert self.reporter._detect_emotion("") == "neutral"

    def test_excited_keywords(self):
        result = self.reporter._detect_emotion("太棒了！！！")
        assert result == "excited"


# ── SessionReporter._build_emotional_arc ──────────────────────────────────────

class TestBuildEmotionalArc:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_only_user_turns_counted(self):
        history = [
            {"role": "user", "content": "謝謝"},
            {"role": "assistant", "content": "好"},
            {"role": "user", "content": "為什麼"},
        ]
        arc = self.reporter._build_emotional_arc(history)
        assert len(arc) == 2

    def test_empty_history(self):
        assert self.reporter._build_emotional_arc([]) == []

    def test_arc_order_preserved(self):
        history = [
            {"role": "user", "content": "謝謝"},
            {"role": "user", "content": "為什麼"},
        ]
        arc = self.reporter._build_emotional_arc(history)
        assert arc[0] == "calm"
        assert arc[1] == "curious"


# ── SessionReporter._calculate_volatility ────────────────────────────────────

class TestCalculateVolatility:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_empty_arc_zero(self):
        assert self.reporter._calculate_volatility([]) == pytest.approx(0.0)

    def test_single_emotion_zero(self):
        assert self.reporter._calculate_volatility(["calm"]) == pytest.approx(0.0)

    def test_constant_arc_zero(self):
        assert self.reporter._calculate_volatility(["calm", "calm", "calm"]) == pytest.approx(0.0)

    def test_alternating_arc_high_volatility(self):
        arc = ["calm", "frustrated", "calm", "frustrated"]
        v = self.reporter._calculate_volatility(arc)
        assert v == pytest.approx(1.0)

    def test_one_change_out_of_three(self):
        arc = ["calm", "calm", "curious"]
        v = self.reporter._calculate_volatility(arc)
        assert v == pytest.approx(0.5)

    def test_capped_at_one(self):
        arc = ["a", "b"] * 10
        v = self.reporter._calculate_volatility(arc)
        assert v <= 1.0


# ── SessionReporter._detect_turning_points ───────────────────────────────────

class TestDetectTurningPoints:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_no_change_no_turning_points(self):
        arc = ["calm", "calm", "calm"]
        history = [{"role": "user", "content": "msg"}] * 3
        tps = self.reporter._detect_turning_points(history, arc)
        assert tps == []

    def test_one_change_one_turning_point(self):
        arc = ["calm", "frustrated"]
        history = [
            {"role": "user", "content": "hi"},
            {"role": "user", "content": "不是這樣"},
        ]
        tps = self.reporter._detect_turning_points(history, arc)
        assert len(tps) == 1
        assert tps[0].before_state == "calm"
        assert tps[0].after_state == "frustrated"

    def test_calm_to_frustrated_high_significance(self):
        arc = ["calm", "frustrated"]
        history = [{"role": "user", "content": "msg"}] * 2
        tps = self.reporter._detect_turning_points(history, arc)
        assert tps[0].significance == pytest.approx(0.8)

    def test_frustrated_to_calm_significance_0_7(self):
        arc = ["frustrated", "calm"]
        history = [{"role": "user", "content": "msg"}] * 2
        tps = self.reporter._detect_turning_points(history, arc)
        assert tps[0].significance == pytest.approx(0.7)


# ── SessionReporter._find_high_tension_moments ───────────────────────────────

class TestFindHighTensionMoments:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_no_tension_empty(self):
        history = [{"role": "user", "content": "hi"}] * 3
        result = self.reporter._find_high_tension_moments(history, ["calm", "calm", "calm"])
        assert result == []

    def test_frustrated_is_high_tension(self):
        result = self.reporter._find_high_tension_moments(
            [{"role": "user"}, {"role": "user"}],
            ["calm", "frustrated"],
        )
        assert 1 in result

    def test_anxious_is_high_tension(self):
        result = self.reporter._find_high_tension_moments(
            [{"role": "user"}],
            ["anxious"],
        )
        assert 0 in result

    def test_sad_is_high_tension(self):
        result = self.reporter._find_high_tension_moments(
            [{"role": "user"}],
            ["sad"],
        )
        assert 0 in result


# ── SessionReporter._classify_session ─────────────────────────────────────────

class TestClassifySession:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_calm_low_volatility_is_productive(self):
        result = self.reporter._classify_session([], volatility=0.2, dominant_emotion="calm")
        assert result == "productive"

    def test_curious_low_volatility_is_productive(self):
        result = self.reporter._classify_session([], volatility=0.1, dominant_emotion="curious")
        assert result == "productive"

    def test_many_turning_points_is_dynamic(self):
        tps = [None, None, None, None]  # 4 turning points
        result = self.reporter._classify_session(tps, volatility=0.5, dominant_emotion="neutral")
        assert result == "dynamic"

    def test_frustrated_dominant_is_challenging(self):
        result = self.reporter._classify_session([], volatility=0.5, dominant_emotion="frustrated")
        assert result == "challenging"

    def test_curious_is_exploratory(self):
        result = self.reporter._classify_session([], volatility=0.5, dominant_emotion="curious")
        assert result == "exploratory"

    def test_other_is_conversational(self):
        result = self.reporter._classify_session([], volatility=0.5, dominant_emotion="neutral")
        assert result == "conversational"


# ── SessionReporter._generate_summary_text ───────────────────────────────────

class TestGenerateSummaryText:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_contains_turn_count(self):
        text = self.reporter._generate_summary_text(
            total_turns=5,
            dominant_emotion="calm",
            turning_points=[],
            commitments=0,
            session_quality="productive",
        )
        assert "5" in text

    def test_contains_quality_label(self):
        text = self.reporter._generate_summary_text(
            total_turns=3,
            dominant_emotion="calm",
            turning_points=[],
            commitments=0,
            session_quality="productive",
        )
        assert "有建設性的" in text

    def test_turning_points_mentioned_when_present(self):
        class _FakeTP:
            pass
        text = self.reporter._generate_summary_text(
            total_turns=3,
            dominant_emotion="calm",
            turning_points=[_FakeTP(), _FakeTP()],
            commitments=0,
            session_quality="productive",
        )
        assert "2" in text

    def test_commitments_mentioned_when_nonzero(self):
        text = self.reporter._generate_summary_text(
            total_turns=3,
            dominant_emotion="calm",
            turning_points=[],
            commitments=3,
            session_quality="productive",
        )
        assert "3" in text


# ── SessionReporter._detect_themes ───────────────────────────────────────────

class TestDetectThemes:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_empty_history_no_themes(self):
        clusters = self.reporter._detect_themes([], [])
        assert clusters == []

    def test_theme_repeated_detected(self):
        history = [
            {"role": "user", "content": "意義和存在是什麼"},
            {"role": "assistant", "content": "意義可以從多種角度理解"},
            {"role": "user", "content": "哲學上的意義很重要"},
        ]
        arc = ["curious", "neutral", "curious"]
        clusters = self.reporter._detect_themes(history, arc)
        names = [c.name for c in clusters]
        assert "哲學思辨" in names

    def test_infrequent_theme_not_included(self):
        history = [
            {"role": "user", "content": "意義是什麼"},  # Only once
        ]
        arc = ["curious"]
        clusters = self.reporter._detect_themes(history, arc)
        names = [c.name for c in clusters]
        assert "哲學思辨" not in names

    def test_sorted_by_frequency(self):
        # Create history where 學習成長 appears more than 技術問題
        history = [
            {"role": "user", "content": "學習很重要"},
            {"role": "user", "content": "我想理解這個"},
            {"role": "user", "content": "解釋給我聽"},
            {"role": "user", "content": "學習讓我知道很多"},
            {"role": "user", "content": "程式有bug"},
            {"role": "user", "content": "程式代碼怎麼做"},
        ]
        arc = ["curious"] * len([h for h in history if h["role"] == "user"])
        clusters = self.reporter._detect_themes(history, arc)
        if len(clusters) >= 2:
            assert clusters[0].turn_count >= clusters[1].turn_count


# ── SessionReporter.analyze integration ──────────────────────────────────────

class TestSessionReporterAnalyze:
    def setup_method(self):
        self.reporter = SessionReporter()

    def test_empty_history(self):
        summary = self.reporter.analyze([])
        assert summary.total_turns == 0
        assert summary.user_messages == 0
        assert summary.ai_responses == 0

    def test_counts_accurate(self):
        history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "thanks"},
        ]
        summary = self.reporter.analyze(history)
        assert summary.total_turns == 3
        assert summary.user_messages == 2
        assert summary.ai_responses == 1

    def test_summary_id_increments(self):
        s1 = self.reporter.analyze([])
        s2 = self.reporter.analyze([])
        assert s1.session_id != s2.session_id

    def test_to_dict_has_all_keys(self):
        history = [{"role": "user", "content": "謝謝"}, {"role": "assistant", "content": "好"}]
        summary = self.reporter.analyze(history)
        d = summary.to_dict()
        for key in (
            "session_id", "total_turns", "user_messages", "ai_responses",
            "emotional_arc", "dominant_emotion", "emotional_volatility",
            "turning_points", "high_tension_moments", "theme_clusters",
            "commitments_made", "ruptures_detected", "values_strengthened",
            "session_quality", "summary_text",
        ):
            assert key in d

    def test_commitments_counted(self):
        class _Commit:
            pass
        summary = self.reporter.analyze([], self_commits=[_Commit(), _Commit()])
        assert summary.commitments_made == 2

    def test_ruptures_counted(self):
        summary = self.reporter.analyze([], ruptures=["r1", "r2", "r3"])
        assert summary.ruptures_detected == 3

    def test_emergent_values_with_name(self):
        class _Val:
            name = "honesty"
        summary = self.reporter.analyze([], emergent_values=[_Val()])
        assert "honesty" in summary.values_strengthened
