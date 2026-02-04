"""
ToneSoul 整合測試
Integration Test for Darlin Patterns + Persona Dimension

測試：
1. 服務管理器
2. 人格維度約束
3. Big Five 人格轉換
4. 向量合法性檢查
"""

import sys
from pathlib import Path

# 確保可以 import tonesoul52
sys.path.insert(0, str(Path(__file__).parent.parent))

from tonesoul52.service_manager import (
    ServiceManager,
    ServiceCode,
    Priority,
    ResourceLevel,
    get_service_manager,
    record_service_call,
)
from tonesoul52.persona_dimension import (
    PersonaDimension,
    PersonaVector,
    VectorCalculator,
    BigFive,
    extract_big_five,
    load_persona,
)


def test_service_manager():
    """測試服務管理器"""
    print("=" * 50)
    print("1. 測試服務管理器")
    print("=" * 50)

    manager = get_service_manager(ResourceLevel.MINIMAL)

    print(f"✅ 資源等級: {manager.resource_level.value}")
    print(f"✅ 模型: {manager.get_model()}")

    # 測試服務優先級
    services = manager.get_enabled_by_priority()
    print(f"✅ 服務數量: {len(services)}")
    print(f"✅ 最高優先: {services[0].code.name} ({services[0].priority.name})")

    # 記錄調用
    record_service_call(ServiceCode.TS003, success=True)
    print(f"✅ 服務調用記錄成功")

    return True


def test_big_five_conversion():
    """測試 Big Five 人格轉換"""
    print("\n" + "=" * 50)
    print("2. 測試 Big Five 人格轉換")
    print("=" * 50)

    # 創建 Big Five
    big5 = BigFive(
        openness=0.8, conscientiousness=0.9, extraversion=0.5, agreeableness=0.7, neuroticism=0.2
    )

    print(f"✅ Big Five: {big5.as_dict()}")

    # 轉換為三向量
    delta = big5.to_delta_vector()
    print(f"✅ 轉換結果: {delta}")

    # 驗證轉換邏輯
    expected_deltaT = 0.5 - 0.2 * 0.5  # 0.4
    expected_deltaS = (0.5 + 0.7) / 2  # 0.6
    expected_deltaR = 0.9

    assert abs(delta["deltaT"] - expected_deltaT) < 0.01, "deltaT 轉換錯誤"
    assert abs(delta["deltaS"] - expected_deltaS) < 0.01, "deltaS 轉換錯誤"
    assert abs(delta["deltaR"] - expected_deltaR) < 0.01, "deltaR 轉換錯誤"

    print(f"✅ 轉換驗證通過")

    return True


def test_persona_dimension():
    """測試人格維度約束"""
    print("\n" + "=" * 50)
    print("3. 測試人格維度約束")
    print("=" * 50)

    # 載入 antigravity 人格
    persona_path = Path(__file__).parent.parent / "memory" / "personas" / "antigravity.yaml"

    if not persona_path.exists():
        print(f"⚠️ 人格檔案不存在: {persona_path}")
        return False

    persona = load_persona(str(persona_path))
    dimension = PersonaDimension(persona)

    print(f"✅ 人格載入: {persona.get('name')}")

    # 測試 Big Five 提取
    big5 = extract_big_five(persona)
    if big5:
        print(f"✅ Big Five 提取: conscientiousness={big5.conscientiousness}")

    # 測試向量計算
    calculator = VectorCalculator()

    # 正常回應
    normal_response = "我會幫你檢查這個問題，請稍等。"
    vector1 = calculator.compute(normal_response)
    print(
        f"✅ 正常回應向量: T={vector1.deltaT:.2f}, S={vector1.deltaS:.2f}, R={vector1.deltaR:.2f}"
    )

    # 高張力回應
    urgent_response = "WARNING! 這是緊急情況！需要立即處理！危險！"
    vector2 = calculator.compute(urgent_response)
    print(
        f"✅ 緊急回應向量: T={vector2.deltaT:.2f}, S={vector2.deltaS:.2f}, R={vector2.deltaR:.2f}"
    )

    # 測試人格評估
    result = dimension.evaluate(normal_response)
    print(f"✅ 人格評估: valid={result.get('valid')}")

    return True


def test_vector_validation():
    """測試向量合法性檢查"""
    print("\n" + "=" * 50)
    print("4. 測試向量合法性檢查")
    print("=" * 50)

    persona_path = Path(__file__).parent.parent / "memory" / "personas" / "antigravity.yaml"

    if not persona_path.exists():
        print(f"⚠️ 人格檔案不存在")
        return False

    persona = load_persona(str(persona_path))
    dimension = PersonaDimension(persona)

    # 模擬不同風格的回應
    test_cases = [
        ("正常專業回應", "我會幫你處理這個問題，讓我檢查一下。", True),
        ("過度激動", "哇哇哇！！！太棒了！！！超級興奮！！！！", False),
        ("過於隨便", "lol haha yo 反正隨便啦 whatever", False),
    ]

    for name, text, expected_valid in test_cases:
        result = dimension.evaluate(text)
        actual_valid = result.get("valid", False)
        status = "✅" if actual_valid == expected_valid else "⚠️"
        print(f"{status} {name}: valid={actual_valid} (expected={expected_valid})")

    return True


def test_integration():
    """整合測試：服務管理 + 人格維度"""
    print("\n" + "=" * 50)
    print("5. 整合測試")
    print("=" * 50)

    # 取得服務管理器
    manager = get_service_manager()

    # 記錄 PersonaDim 調用
    record_service_call(ServiceCode.TS003, success=True)

    # 載入人格
    persona_path = Path(__file__).parent.parent / "memory" / "personas" / "antigravity.yaml"

    if not persona_path.exists():
        print(f"⚠️ 人格檔案不存在")
        return False

    persona = load_persona(str(persona_path))
    dimension = PersonaDimension(persona)

    # 處理回應
    test_response = "讓我幫你分析這個問題。首先，我需要確認一些細節。"
    output, result = dimension.process(test_response, shadow=True)

    print(f"✅ 輸出: {output[:50]}...")
    print(f"✅ 人格 ID: {result.get('persona_id')}")
    print(f"✅ 向量有效: {result.get('valid')}")

    # 取得服務狀態
    service = manager.get_service(ServiceCode.TS003)
    print(f"✅ PersonaDim 調用次數: {service.call_count}")

    return True


def main():
    """執行所有測試"""
    print("\n" + "=" * 60)
    print("   ToneSoul 整合測試 (Darlin Patterns Integration)")
    print("=" * 60)

    results = []

    try:
        results.append(("服務管理器", test_service_manager()))
    except Exception as e:
        print(f"❌ 服務管理器測試失敗: {e}")
        results.append(("服務管理器", False))

    try:
        results.append(("Big Five 轉換", test_big_five_conversion()))
    except Exception as e:
        print(f"❌ Big Five 轉換測試失敗: {e}")
        results.append(("Big Five 轉換", False))

    try:
        results.append(("人格維度約束", test_persona_dimension()))
    except Exception as e:
        print(f"❌ 人格維度約束測試失敗: {e}")
        results.append(("人格維度約束", False))

    try:
        results.append(("向量合法性", test_vector_validation()))
    except Exception as e:
        print(f"❌ 向量合法性測試失敗: {e}")
        results.append(("向量合法性", False))

    try:
        results.append(("整合測試", test_integration()))
    except Exception as e:
        print(f"❌ 整合測試失敗: {e}")
        results.append(("整合測試", False))

    # 總結
    print("\n" + "=" * 60)
    print("   測試結果總結")
    print("=" * 60)

    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
        if success:
            passed += 1

    print(f"\n  總計: {passed}/{len(results)} 通過")
    print("=" * 60)

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
