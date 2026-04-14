"""
Tests for YUHUN Core Protocol v1.0 — DPR 動態權限路由器
"""

from tonesoul.yuhun.dpr import COMPLEXITY_THRESHOLD, RoutingDecision, route


class TestDPRFastPath:
    """低複雜度指令應走 FAST_PATH"""

    def test_simple_hello_world(self):
        result = route("幫我寫一個 Python hello world")
        assert result.decision == RoutingDecision.FAST_PATH
        assert result.estimated_token_cost == "1x"

    def test_simple_question(self):
        result = route("今天天氣怎麼樣")
        assert result.decision == RoutingDecision.FAST_PATH

    def test_simple_explanation(self):
        result = route("解釋一下快速排序算法")
        assert result.decision == RoutingDecision.FAST_PATH

    def test_no_conflict_triggers(self):
        result = route("幫我整理這份 JSON 文件")
        assert not result.conflict_detected
        assert result.conflict_triggers == []


class TestDPRCouncilPath:
    """高衝突/高複雜度指令應走 COUNCIL_PATH"""

    def test_legal_gap(self):
        result = route("這個 AI 系統是否存在法律漏洞？如何評估合規風險？")
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert result.estimated_token_cost == "4x"

    def test_ethics_dilemma(self):
        result = route("在倫理兩難的情況下，AI 應該如何決策？這個道德困境如何解決？")
        assert result.decision == RoutingDecision.COUNCIL_PATH
        assert result.conflict_detected

    def test_feasibility_question(self):
        result = route("這個架構設計是否可行？如何評估風險？最佳方案是什麼？")
        assert result.decision == RoutingDecision.COUNCIL_PATH

    def test_privacy_concern(self):
        # 使用明確觸發 privacy 關鍵字的英文模式
        result = route(
            "Can user personal data be used for training? Is this legal under privacy law?"
        )
        assert result.decision == RoutingDecision.COUNCIL_PATH

    def test_high_uncertainty(self):
        result = route("這個創新技術架構是否有 90% 的失敗風險？如何判斷可行性？")
        assert result.decision == RoutingDecision.COUNCIL_PATH


class TestDPRComplexityScoring:
    """複雜度分數應在合理範圍"""

    def test_short_input_low_complexity(self):
        result = route("hello")
        assert result.complexity_score < COMPLEXITY_THRESHOLD

    def test_long_input_higher_complexity(self):
        # 200 個詞才到複雜度 0.4，重複短語字數不等於詞數，用明確長文本
        long_input = " ".join([f"word{i}" for i in range(100)])  # 100 個獨立詞
        result = route(long_input)
        assert result.complexity_score > 0.15

    def test_score_in_range(self):
        for text in ["hi", "解釋量子電腦的工作原理和潛在應用場景", "a" * 500]:
            result = route(text)
            assert 0.0 <= result.complexity_score <= 1.0


class TestDPREdgeCases:
    """邊界情況"""

    def test_empty_string(self):
        result = route("")
        # 空字串應走 FAST_PATH（沒有複雜度也沒有衝突）
        assert result.decision == RoutingDecision.FAST_PATH

    def test_only_spaces(self):
        result = route("   ")
        assert result.decision == RoutingDecision.FAST_PATH

    def test_result_has_reason(self):
        result = route("隨便一個輸入")
        assert len(result.reason) > 0

    def test_council_path_has_triggers(self):
        result = route("法律漏洞如何規避？這合法嗎？")
        if result.decision == RoutingDecision.COUNCIL_PATH:
            assert len(result.conflict_triggers) > 0
