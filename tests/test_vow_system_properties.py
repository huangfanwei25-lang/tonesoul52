"""
Property-Based Tests for VowSystem

使用 Hypothesis 測試 VowSystem 的不變量與屬性
"""

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis import assume
from tonesoul.vow_system import (
    Vow,
    VowAction,
    VowRegistry,
    VowEnforcer,
    VowCheckResult,
)


# === Strategies ===

@st.composite
def vow_strategy(draw):
    """生成有效的 Vow 實例"""
    return Vow(
        id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_-"))),
        title=draw(st.text(min_size=1, max_size=50)),
        description=draw(st.text(max_size=200)),
        expected=draw(st.dictionaries(
            keys=st.sampled_from(["truthfulness", "responsibility", "coherence", "safety"]),
            values=st.floats(min_value=0.0, max_value=1.0),
            min_size=1,
            max_size=4
        )),
        violation_threshold=draw(st.floats(min_value=0.0, max_value=1.0)),
        action_on_violation=draw(st.sampled_from([VowAction.PASS, VowAction.FLAG, VowAction.REPAIR, VowAction.BLOCK])),
        active=draw(st.booleans()),
    )


# === Property Tests ===

class TestVowProperties:
    """測試 Vow 的不變量"""
    
    @settings(max_examples=50)
    @given(vow_strategy())
    def test_vow_serialization_roundtrip(self, vow):
        """屬性: Vow 序列化後反序列化應該相等"""
        vow_dict = vow.to_dict()
        reconstructed = Vow.from_dict(vow_dict)
        
        assert reconstructed.id == vow.id
        assert reconstructed.title == vow.title
        assert reconstructed.description == vow.description
        assert reconstructed.expected == vow.expected
        assert abs(reconstructed.violation_threshold - vow.violation_threshold) < 1e-6
        assert reconstructed.action_on_violation == vow.action_on_violation
        assert reconstructed.active == vow.active
    
    @settings(max_examples=50)
    @given(vow_strategy())
    def test_vow_threshold_bounds(self, vow):
        """屬性: violation_threshold 必須在 [0, 1] 範圍內"""
        assert 0.0 <= vow.violation_threshold <= 1.0
    
    @settings(max_examples=50)
    @given(vow_strategy())
    def test_vow_to_dict_has_required_keys(self, vow):
        """屬性: to_dict() 必須包含所有必要鍵值"""
        vow_dict = vow.to_dict()
        required_keys = {"id", "title", "description", "expected", "violation_threshold", "action_on_violation", "active"}
        assert required_keys.issubset(vow_dict.keys())


class TestVowRegistryProperties:
    """測試 VowRegistry 的不變量"""
    
    @settings(max_examples=50)
    @given(st.lists(vow_strategy(), min_size=1, max_size=10, unique_by=lambda v: v.id))
    def test_registry_idempotency(self, vows):
        """屬性: 註冊同一個 vow 多次等同於註冊一次"""
        registry = VowRegistry()
        
        # 註冊第一次
        for vow in vows:
            registry.register(vow)
        count_after_first = len(registry.get_all())
        
        # 再註冊一次（覆蓋）
        for vow in vows:
            registry.register(vow)
        count_after_second = len(registry.get_all())
        
        assert count_after_first == count_after_second
    
    @settings(max_examples=50)
    @given(st.lists(vow_strategy(), min_size=1, max_size=10, unique_by=lambda v: v.id))
    def test_registry_get_returns_registered_vows(self, vows):
        """屬性: 註冊的 vow 一定可以被 get() 取回"""
        registry = VowRegistry()
        
        for vow in vows:
            registry.register(vow)
        
        for vow in vows:
            retrieved = registry.get(vow.id)
            assert retrieved is not None
            assert retrieved.id == vow.id
    
    @settings(max_examples=50)
    @given(st.lists(vow_strategy(), min_size=2, max_size=10, unique_by=lambda v: v.id))
    def test_registry_unregister_decreases_count(self, vows):
        """屬性: unregister 會減少 vow 數量"""
        registry = VowRegistry()
        
        for vow in vows:
            registry.register(vow)
        
        initial_count = len(registry.get_all())
        registry.unregister(vows[0].id)
        final_count = len(registry.get_all())
        
        assert final_count == initial_count - 1


class TestVowEnforcerProperties:
    """測試 VowEnforcer 的不變量"""
    
    @settings(max_examples=50)
    @given(st.text(min_size=1, max_size=500))
    def test_enforcer_always_returns_result_structure(self, text):
        """屬性: enforce() 總是返回完整的結果結構"""
        enforcer = VowEnforcer()
        result = enforcer.enforce(text)
        
        assert isinstance(result, dict)
        assert "allowed" in result
        assert "action" in result
        assert "violations" in result
        assert isinstance(result["violations"], list)
    
    @settings(max_examples=30)
    @given(st.text(min_size=1, max_size=500))
    def test_enforcer_determinism(self, text):
        """屬性: 相同輸入在相同配置下總是返回相同結果"""
        enforcer1 = VowEnforcer()
        enforcer2 = VowEnforcer()
        
        result1 = enforcer1.enforce(text)
        result2 = enforcer2.enforce(text)
        
        assert result1["allowed"] == result2["allowed"]
        assert result1["action"] == result2["action"]
        assert len(result1["violations"]) == len(result2["violations"])


class TestVowCheckResultProperties:
    """測試 VowCheckResult 的不變量"""
    
    @settings(max_examples=50)
    @given(
        st.booleans(),
        st.floats(min_value=0.0, max_value=1.0),
        st.one_of(st.none(), st.text(max_size=100)),
    )
    def test_check_result_score_bounds(self, passed, score, reason):
        """屬性: score 必須在 [0, 1] 範圍內"""
        result = VowCheckResult(passed=passed, score=score, reason=reason)
        assert 0.0 <= result.score <= 1.0
    
    @settings(max_examples=50)
    @given(
        st.booleans(),
        st.floats(min_value=0.0, max_value=1.0),
        st.one_of(st.none(), st.text(max_size=100)),
    )
    def test_check_result_to_dict_roundtrip(self, passed, score, reason):
        """屬性: VowCheckResult 序列化後反序列化應該相等"""
        result = VowCheckResult(passed=passed, score=score, reason=reason)
        result_dict = result.to_dict()
        
        assert result_dict["passed"] == passed
        assert abs(result_dict["score"] - score) < 1e-6
        assert result_dict["reason"] == reason


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
