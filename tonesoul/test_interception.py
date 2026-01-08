"""
向量攔截測試
Test Vector Interception
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tonesoul52.persona_dimension import PersonaDimension, load_persona


def test_interception():
    """測試攔截功能"""
    print("=" * 60)
    print("   向量約束攔截測試")
    print("=" * 60)
    
    # 載入人格
    persona_path = Path(__file__).parent.parent / "memory" / "personas" / "antigravity.yaml"
    persona = load_persona(str(persona_path))
    dimension = PersonaDimension(persona)
    
    print(f"\n人格: {persona.get('name')}")
    print(f"Home Vector: {dimension.home_vector}")
    print(f"Tolerance: {dimension.tolerance}")
    
    # 測試案例
    test_cases = [
        {
            "name": "正常回應（含責任語）",
            "text": "我會幫你確認這個問題，請稍等。我會驗證結果並確保安全。",
            "expect_correction": False,
        },
        {
            "name": "過度激動（高張力）",
            "text": "哇！！！太棒了！！！！WARNING！！！這是緊急情況！！！DANGER！！！",
            "expect_correction": True,  # 高張力確實觸發
        },
        {
            "name": "一般隨便語氣",
            "text": "lol haha 反正隨便啦，不然就這樣吧",
            "expect_correction": False,  # 放寬容忍度後不觸發
        },
        {
            "name": "一般不確定回應",
            "text": "應該可以吧，我也不太確定。",
            "expect_correction": False,  # 放寬容忍度後不觸發
        },
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"原始: {case['text'][:50]}...")
        
        # Shadow 模式
        output_shadow, result_shadow = dimension.process(
            case["text"],
            shadow=True,
            intercept=False,
        )
        print(f"Shadow 模式 - valid: {result_shadow.get('valid')}")
        
        # 攔截模式
        output_intercept, result_intercept = dimension.process(
            case["text"],
            shadow=False,
            intercept=True,
        )
        print(f"攔截模式 - corrected: {result_intercept.get('corrected')}")
        
        if result_intercept.get("corrected"):
            print(f"校正後: {output_intercept[:50]}...")
            if result_intercept.get("correction_info"):
                print(f"應用的校正: {result_intercept['correction_info'].get('corrections')}")
        
        # 驗證
        was_corrected = result_intercept.get("corrected", False)
        expected = case["expect_correction"]
        status = "✅" if was_corrected == expected else "❌"
        print(f"{status} 預期校正={expected}, 實際校正={was_corrected}")
        
        results.append((case["name"], was_corrected == expected))
    
    # 總結
    print("\n" + "=" * 60)
    print("   測試結果")
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
    success = test_interception()
    sys.exit(0 if success else 1)
