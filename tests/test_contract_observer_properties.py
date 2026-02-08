"""
Property-Based Tests for ContractObserver

使用 Hypothesis 測試 ContractObserver 的不變量與屬性
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tonesoul.contract_observer import (
    ContractVerifier,
    MultiScaleObserver,
    QualityTracker,
)

FLOAT_TOLERANCE = 1e-4


# === Strategies ===


@st.composite
def delta_s_strategy(draw):
    """生成有效的 delta_s 值 (語義張力)"""
    return draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))


@st.composite
def valid_output_strategy(draw):
    """生成有效的輸出文本"""
    return draw(
        st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"),
        )
    )


# === Property Tests ===


class TestMultiScaleObserverProperties:
    """測試 MultiScaleObserver 的不變量"""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(delta_s_strategy(), min_size=1, max_size=100))
    def test_observe_maintains_history(self, deltas):
        """屬性: observe() 會累積歷史記錄"""
        observer = MultiScaleObserver()

        for delta in deltas:
            observer.observe(delta)

        assert len(observer.history) == len(deltas)

    @settings(max_examples=50)
    @given(st.lists(delta_s_strategy(), min_size=1, max_size=50))
    def test_reset_clears_history(self, deltas):
        """屬性: reset() 會清空歷史"""
        observer = MultiScaleObserver()

        for delta in deltas:
            observer.observe(delta)

        observer.reset()
        assert len(observer.history) == 0

    @settings(max_examples=30)
    @given(st.lists(delta_s_strategy(), min_size=5, max_size=50))
    def test_mean_within_input_range(self, deltas):
        """屬性: 平均值應該在輸入範圍內"""
        observer = MultiScaleObserver()

        for delta in deltas:
            metrics = observer.observe(delta)

        min_delta = min(deltas)
        max_delta = max(deltas)

        # 短期和中期平均值都應該在 min-max 範圍內
        assert min_delta - FLOAT_TOLERANCE <= metrics["short_term"] <= max_delta + FLOAT_TOLERANCE
        assert min_delta - FLOAT_TOLERANCE <= metrics["medium_term"] <= max_delta + FLOAT_TOLERANCE

    @settings(max_examples=30)
    @given(st.lists(delta_s_strategy(), min_size=3, max_size=20))
    def test_trend_consistency(self, deltas):
        """屬性: 趨勢判斷應該符合邏輯"""
        observer = MultiScaleObserver()

        for delta in deltas:
            observer.observe(delta)

        trend = observer._trend()
        valid_trends = {"improving", "degrading", "stable", "unknown"}
        assert trend in valid_trends

    @settings(max_examples=30)
    @given(st.lists(delta_s_strategy(), min_size=2, max_size=50))
    def test_volatility_non_negative(self, deltas):
        """屬性: 波動性總是非負"""
        observer = MultiScaleObserver()

        for delta in deltas:
            observer.observe(delta)

        volatility = observer._volatility()
        assert volatility >= 0.0


class TestQualityTrackerProperties:
    """測試 QualityTracker 的不變量"""

    @settings(max_examples=50)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=1, max_size=50
        )
    )
    def test_record_increases_total_outputs(self, records):
        """屬性: record() 會增加 total_outputs"""
        tracker = QualityTracker()

        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        assert tracker.total_outputs == len(records)

    @settings(max_examples=50)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=1, max_size=50
        )
    )
    def test_intervention_rate_bounds(self, records):
        """屬性: intervention_rate 必須在 [0, 1] 範圍內"""
        tracker = QualityTracker()

        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        summary = tracker.get_summary()
        assert 0.0 <= summary["intervention_rate"] <= 1.0

    @settings(max_examples=50)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=1, max_size=50
        )
    )
    def test_contract_pass_rate_bounds(self, records):
        """屬性: contract_pass_rate 必須在 [0, 1] 範圍內"""
        tracker = QualityTracker()

        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        summary = tracker.get_summary()
        assert 0.0 <= summary["contract_pass_rate"] <= 1.0

    @settings(max_examples=30)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=5, max_size=30
        )
    )
    def test_avg_delta_s_within_bounds(self, records):
        """屬性: 平均 delta_s 應該在 [0, 1] 範圍內"""
        tracker = QualityTracker()

        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        summary = tracker.get_summary()
        assert 0.0 <= summary["avg_delta_s"] <= 1.0

    @settings(max_examples=30)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=1, max_size=20
        )
    )
    def test_reset_clears_all_counters(self, records):
        """屬性: reset() 會清空所有計數器"""
        tracker = QualityTracker()

        # 記錄一些數據
        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        # 重置
        tracker.reset()

        # 驗證計數器被清空
        assert tracker.total_outputs == 0
        assert tracker.interventions == 0
        assert tracker.contract_passes == 0
        assert tracker.contract_checks == 0
        assert tracker.delta_s_sum == 0.0
        assert len(tracker.snapshots) == 0

    @settings(max_examples=20)
    @given(
        st.lists(
            st.tuples(delta_s_strategy(), st.booleans(), st.booleans()), min_size=1, max_size=20
        )
    )
    def test_snapshot_preserves_state(self, records):
        """屬性: take_snapshot() 不應改變追蹤器狀態"""
        tracker = QualityTracker()

        for delta, intervened, contracts_passed in records:
            tracker.record(delta, intervened, contracts_passed)

        before_outputs = tracker.total_outputs
        before_interventions = tracker.interventions

        snapshot = tracker.take_snapshot()

        assert tracker.total_outputs == before_outputs
        assert tracker.interventions == before_interventions
        assert isinstance(snapshot.timestamp, str)


class TestContractVerifierProperties:
    """測試 ContractVerifier 的不變量"""

    @settings(max_examples=30)
    @given(valid_output_strategy())
    def test_verify_always_returns_dict(self, output):
        """屬性: verify_all() 總是返回字典"""
        verifier = ContractVerifier()
        result = verifier.verify_all(output, "safe")

        assert isinstance(result, dict)
        assert "passed" in result
        assert "violations" in result
        assert "checked" in result

    @settings(max_examples=30)
    @given(valid_output_strategy())
    def test_verify_violations_is_list(self, output):
        """屬性: violations 總是列表"""
        verifier = ContractVerifier()
        result = verifier.verify_all(output, "safe")

        assert isinstance(result["violations"], list)

    @settings(max_examples=30)
    @given(valid_output_strategy())
    def test_verify_passed_consistency(self, output):
        """屬性: passed=True 當且僅當 violations 為空"""
        verifier = ContractVerifier()
        result = verifier.verify_all(output, "safe")

        if result["passed"]:
            assert len(result["violations"]) == 0
        else:
            assert len(result["violations"]) > 0

    @settings(max_examples=20)
    @given(valid_output_strategy())
    def test_verify_checked_non_negative(self, output):
        """屬性: checked 數量總是非負"""
        verifier = ContractVerifier()
        result = verifier.verify_all(output, "safe")

        assert result["checked"] >= 0
        assert result["checked"] <= result["total_contracts"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
