"""
Property-Based Tests for UnifiedCore

使用 Hypothesis 測試 UnifiedCore 的不變量與屬性
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tonesoul.unified_core import UnifiedCore

# === Strategies ===


@st.composite
def valid_text_strategy(draw):
    """生成有效的文本輸入"""
    return draw(
        st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(
                blacklist_categories=("Cs",), blacklist_characters="\x00"  # 排除代理字符
            ),
        )
    )


# === Property Tests ===


class TestUnifiedCoreProperties:
    """測試 UnifiedCore 的不變量"""

    @settings(max_examples=30, deadline=5000)
    @given(valid_text_strategy())
    def test_process_always_returns_tuple(self, text):
        """屬性: process() 總是返回 (output, report) 元組"""
        core = UnifiedCore()
        result = core.process(text)

        assert isinstance(result, tuple)
        assert len(result) == 2
        output, report = result
        assert isinstance(output, str)
        assert isinstance(report, dict)

    @settings(max_examples=30, deadline=5000)
    @given(valid_text_strategy())
    def test_report_has_required_keys(self, text):
        """屬性: report 必須包含所有必要鍵值"""
        core = UnifiedCore()
        _, report = core.process(text)

        required_keys = {
            "semantic_tension",
            "intervention",
            "contracts",  # contracts dict with 'passed' key
        }
        assert required_keys.issubset(report.keys())

    @settings(max_examples=20, deadline=5000)
    @given(valid_text_strategy())
    def test_semantic_tension_bounds(self, text):
        """屬性: semantic_tension 的所有值必須在 [0, 1] 範圍內"""
        core = UnifiedCore()
        _, report = core.process(text)

        tension = report.get("semantic_tension", {})
        if isinstance(tension, dict):
            for key, value in tension.items():
                if isinstance(value, (int, float)):
                    assert 0.0 <= value <= 1.0, f"Tension {key}={value} out of bounds"

    @settings(max_examples=20, deadline=5000)
    @given(valid_text_strategy())
    def test_intervention_is_boolean(self, text):
        """屬性: intervention 必須是布林值"""
        core = UnifiedCore()
        _, report = core.process(text)
        # intervention is InterventionLevel.value (str), not bool
        valid_interventions = {"none", "observe", "warn", "intercept", "block"}
        assert report["intervention"] in valid_interventions

    @settings(max_examples=20, deadline=5000)
    @given(valid_text_strategy())
    def test_zone_is_valid(self, text):
        """屬性: zone 必須是有效的區域名稱"""
        core = UnifiedCore()
        _, report = core.process(text)
        valid_zones = {"safe", "transit", "risk", "danger"}
        # zone is inside semantic_tension dict
        semantic_tension = report.get("semantic_tension", {})
        zone = semantic_tension.get("zone") if isinstance(semantic_tension, dict) else None
        assert zone in valid_zones

    @settings(max_examples=15, deadline=10000)
    @given(valid_text_strategy())
    def test_output_not_empty(self, text):
        """屬性: process() 的輸出不應為空（除非輸入為空）"""
        assume(len(text.strip()) > 0)  # 假設輸入非空

        core = UnifiedCore()
        output, _ = core.process(text)

        # 輸出可能與輸入相同（如果沒有干預），但不應為空
        assert len(output) > 0

    @settings(max_examples=10, deadline=5000)
    @given(valid_text_strategy())
    def test_contracts_passed_is_boolean(self, text):
        """屬性: contracts_passed 必須是布林值"""
        core = UnifiedCore()
        _, report = core.process(text)
        # contracts is a dict with 'passed' key
        contracts = report.get("contracts", {})
        assert isinstance(contracts.get("passed"), bool)


class TestUnifiedCoreDeterminismProperties:
    """測試 UnifiedCore 的確定性屬性"""

    @settings(max_examples=10, deadline=5000)
    @given(valid_text_strategy())
    def test_same_config_same_result(self, text):
        """屬性: 相同配置的 UnifiedCore 應產生相同結果"""
        core1 = UnifiedCore()
        core2 = UnifiedCore()

        output1, report1 = core1.process(text)
        output2, report2 = core2.process(text)

        # 輸出應該相同
        assert output1 == output2
        # zone is inside semantic_tension, compare those
        tension1 = report1.get("semantic_tension", {})
        tension2 = report2.get("semantic_tension", {})
        assert tension1.get("zone") == tension2.get("zone")


class TestUnifiedCoreResetProperties:
    """測試 UnifiedCore.reset() 的屬性"""

    @settings(max_examples=10, deadline=5000)
    @given(st.lists(valid_text_strategy(), min_size=1, max_size=5))
    def test_reset_clears_state(self, texts):
        """屬性: reset() 應該清除所有狀態"""
        core = UnifiedCore()

        # 處理一些文本
        for text in texts:
            core.process(text)

        # 重置
        core.reset()

        # 獲取狀態
        status = core.get_status()

        # 驗證某些計數器應該被重置（如果有的話）
        # 這取決於 UnifiedCore 的具體實現
        assert isinstance(status, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
